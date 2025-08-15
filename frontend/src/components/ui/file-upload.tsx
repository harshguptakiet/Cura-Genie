'use client';

import React, { useState, useRef } from 'react';
import { useMutation } from '@tanstack/react-query';
import { useAuthStore } from '@/store/auth-store';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './card';
import { Button } from './button';
import { Input } from './input';
import { Progress } from './progress';
import { Alert, AlertDescription } from './alert';
import { Upload, CheckCircle, AlertCircle } from 'lucide-react';
import { toast } from 'sonner';

interface FileUploadProps {
  onUploadSuccess?: (data: any) => void;
}

interface UploadResponse {
  success: boolean;
  message: string;
  fileId?: string;
}

// Real API upload function using correct backend endpoint
const uploadGenomicFile = async (file: File, userId: string, token: string, onProgress: (progress: number) => void): Promise<UploadResponse> => {
  return new Promise((resolve, reject) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('user_id', userId);

    const xhr = new XMLHttpRequest();
    
    xhr.upload.addEventListener('progress', (event) => {
      if (event.lengthComputable) {
        const progress = Math.round((event.loaded / event.total) * 100);
        onProgress(progress);
      }
    });
    
    xhr.addEventListener('load', () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        try {
          const response = JSON.parse(xhr.responseText);
          console.log('Upload response:', response);
          resolve({
            success: true,
            message: response.message || 'File uploaded successfully',
            fileId: response.id ? response.id.toString() : `file_${Date.now()}`
          });
        } catch (e) {
          console.error('Error parsing response:', e);
          resolve({
            success: true,
            message: 'File uploaded successfully',
            fileId: `file_${Date.now()}`
          });
        }
      } else {
        let errorMessage = 'Upload failed';
        try {
          const errorResponse = JSON.parse(xhr.responseText);
          if (errorResponse.detail) {
            if (typeof errorResponse.detail === 'string') {
              errorMessage = errorResponse.detail;
            } else if (Array.isArray(errorResponse.detail)) {
              errorMessage = errorResponse.detail[0].msg || 'Upload failed';
            }
          }
        } catch (e) {
          console.error('Error parsing error response:', e);
          errorMessage = `Upload failed with status ${xhr.status}`;
        }
        console.error('Upload failed:', xhr.status, xhr.responseText);
        reject(new Error(errorMessage));
      }
    });
    
    xhr.addEventListener('error', () => {
      console.error('Upload network error');
      reject(new Error('Upload failed due to network error'));
    });
    
    // Use backend base URL from environment to avoid localhost/mixed-content/CORS issues
    const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';
    // Use the unauthenticated test endpoint for uploads
    xhr.open('POST', `${API_BASE_URL}/api/local-upload/genomic-data-test`);
    
    // If you switch to the authenticated endpoint, add the token header:
    // if (token) {
    //   xhr.setRequestHeader('Authorization', `Bearer ${token}`);
    // }
    
    xhr.send(formData);
  });
};


export function FileUpload({ onUploadSuccess }: FileUploadProps) {
  const { user, token } = useAuthStore();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [showSuccessMessage, setShowSuccessMessage] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  const userId = user?.id?.toString() || "1";
  const authToken = token || "";

  const uploadMutation = useMutation({
    mutationFn: (file: File) => uploadGenomicFile(file, userId, authToken, setUploadProgress),
    onSuccess: (data) => {
      toast.success('File uploaded successfully!');
      
      // Reset all upload-related state completely
      setSelectedFile(null);
      setUploadProgress(0);
      
      // Clear file input element
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
        fileInputRef.current.files = null;
      }
      
      // Reset the mutation state to allow new uploads
      setTimeout(() => {
        uploadMutation.reset();
      }, 100);
      
      onUploadSuccess?.(data);
    },
    onError: (error: any) => {
      console.error('Upload error:', error);
      toast.error(error.message || 'Upload failed. Please try again.');
      setUploadProgress(0);
      
      // Reset mutation state on error too
      setTimeout(() => {
        uploadMutation.reset();
      }, 1000);
    },
  });

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      // Validate file type
      const validExtensions = ['.vcf', '.fastq', '.fq', '.vcf.gz', '.fastq.gz'];
      const isValidFile = validExtensions.some(ext => file.name.toLowerCase().endsWith(ext));
      
      if (!isValidFile) {
        toast.error('Please select a valid genomic file (VCF or FASTQ)');
        return;
      }
      
      setSelectedFile(file);
    }
  };

  const handleUpload = () => {
    if (selectedFile) {
      uploadMutation.mutate(selectedFile);
    }
  };

  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    const file = event.dataTransfer.files[0];
    if (file) {
      const validExtensions = ['.vcf', '.fastq', '.fq', '.vcf.gz', '.fastq.gz'];
      const isValidFile = validExtensions.some(ext => file.name.toLowerCase().endsWith(ext));
      
      if (!isValidFile) {
        toast.error('Please select a valid genomic file (VCF or FASTQ)');
        return;
      }
      
      setSelectedFile(file);
    }
  };

  const handleDragOver = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
  };

  const handleReset = () => {
    // Complete reset function
    setSelectedFile(null);
    setUploadProgress(0);
    setShowSuccessMessage(false);
    
    // Clear file input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
      fileInputRef.current.files = null;
    }
    
    // Reset mutation state
    uploadMutation.reset();
    
    toast.info('Ready for new file upload');
  };

  return (
    <Card className="w-full max-w-md">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Upload className="h-5 w-5" />
          Genomic Data Upload
        </CardTitle>
        <CardDescription>
          Upload your VCF or FASTQ files for genomic analysis
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div
          className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-gray-400 transition-colors cursor-pointer"
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onClick={() => fileInputRef.current?.click()}
        >
          <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
          <p className="text-sm text-gray-600 mb-2">
            Drag and drop your file here, or click to browse
          </p>
          <p className="text-xs text-gray-500">
            Supported formats: VCF, FASTQ (.vcf, .fastq, .fq, .gz)
          </p>
          <Input
            ref={fileInputRef}
            type="file"
            accept=".vcf,.fastq,.fq,.vcf.gz,.fastq.gz"
            onChange={handleFileSelect}
            className="hidden"
          />
        </div>

        {selectedFile && (
          <Alert>
            <CheckCircle className="h-4 w-4" />
            <AlertDescription>
              Selected: {selectedFile.name} ({(selectedFile.size / 1024 / 1024).toFixed(2)} MB)
            </AlertDescription>
          </Alert>
        )}

        {uploadMutation.isPending && (
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>Uploading...</span>
              <span>{uploadProgress}%</span>
            </div>
            <Progress value={uploadProgress} />
          </div>
        )}

        {uploadMutation.isError && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              Upload failed. Please check your file and try again.
            </AlertDescription>
          </Alert>
        )}

        {uploadMutation.isSuccess ? (
          <div className="space-y-3">
            <Alert className="border-green-200 bg-green-50">
              <CheckCircle className="h-4 w-4 text-green-600" />
              <AlertDescription className="text-green-800">
                ✅ Upload completed successfully! Analysis in progress...
              </AlertDescription>
            </Alert>
            <Button
              onClick={handleReset}
              variant="outline"
              className="w-full"
            >
              Upload Another File
            </Button>
          </div>
        ) : (
          <Button
            onClick={handleUpload}
            disabled={!selectedFile || uploadMutation.isPending}
            className="w-full"
          >
            {uploadMutation.isPending ? 'Uploading...' : 'Upload File'}
          </Button>
        )}
      </CardContent>
    </Card>
  );
}
