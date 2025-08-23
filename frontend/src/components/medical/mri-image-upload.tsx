'use client';

import React, { useState, useRef, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  Upload,
  FileImage,
  CheckCircle,
  AlertTriangle,
  Brain,
  Loader2,
  X,
  Eye,
  Download,
  RefreshCw
} from 'lucide-react';
import { toast } from 'sonner';
import { uploadMRIImage as uploadToAPI } from '@/lib/mri-service';
import { MRIImageUploadProps, UploadedFile, MRIAnalysisResult, ProcessedMRIData } from '@/types/medical';

// Note: This component uses the MRI service from @/lib/mri-service.ts
// The duplicate uploadMRIImage function has been removed to avoid confusion

export function MRIImageUpload({ onUploadSuccess, onImageProcessed, onCompleteAnalysis, userId, compact = false }: MRIImageUploadProps) {
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const validateFile = (file: File): boolean => {
    // Check file type
    const validTypes = [
      'image/jpeg', 'image/png', 'image/tiff', 'image/bmp',
      'application/dicom', 'application/octet-stream'
    ];
    const validExtensions = ['.dcm', '.dicom', '.jpg', '.jpeg', '.png', '.tif', '.tiff', '.bmp'];

    const hasValidType = validTypes.includes(file.type);
    const hasValidExtension = validExtensions.some(ext =>
      file.name.toLowerCase().endsWith(ext)
    );

    if (!hasValidType && !hasValidExtension) {
      toast.error('Please upload a valid medical image file (DICOM, JPEG, PNG, TIFF)');
      return false;
    }

    // Check file size (max 50MB)
    const maxSize = 50 * 1024 * 1024; // 50MB
    if (file.size > maxSize) {
      toast.error('File size must be less than 50MB');
      return false;
    }

    return true;
  };

  const createFilePreview = (file: File): Promise<string> => {
    return new Promise((resolve) => {
      if (file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = (e) => resolve(e.target?.result as string);
        reader.readAsDataURL(file);
      } else {
        // For DICOM files, we'll use a placeholder
        resolve('/api/placeholder-mri-image');
      }
    });
  };

  const processFile = async (file: File) => {
    if (!validateFile(file)) return;

    const fileId = `file_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const preview = await createFilePreview(file);

    const uploadedFile: UploadedFile = {
      file,
      preview,
      id: fileId,
      status: 'uploading',
      progress: 0
    };

    setUploadedFiles(prev => [...prev, uploadedFile]);

    try {
      // Upload and process the file using the service
      const result = await uploadToAPI(file, userId, (progress) => {
        setUploadedFiles(prev => prev.map(f =>
          f.id === fileId ? { ...f, progress } : f
        ));
      });

      // Update to processing status
      setUploadedFiles(prev => prev.map(f =>
        f.id === fileId ? { ...f, status: 'processing', progress: 100 } : f
      ));

      // Remove artificial delay - use proper async operations
      // In real implementation, this would call the actual AI processing API

      // Mark as completed with results
      setUploadedFiles(prev => prev.map(f =>
        f.id === fileId
          ? { ...f, status: 'completed', analysisResult: result.analysis }
          : f
      ));

      toast.success('MRI analysis completed successfully!');
      onUploadSuccess?.(result);
      onImageProcessed?.(result.analysis);

      // Call the complete analysis callback with both result and file
      onCompleteAnalysis?.(result, file);

    } catch (error) {
      console.error('Upload/processing error:', error);
      setUploadedFiles(prev => prev.map(f =>
        f.id === fileId ? { ...f, status: 'error', progress: 0 } : f
      ));
      toast.error('Failed to process MRI image. Please try again.');
    }
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files || []);
    files.forEach(processFile);

    // Reset input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleDrop = useCallback((event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setIsDragging(false);

    const files = Array.from(event.dataTransfer.files);
    files.forEach(processFile);
  }, [userId]);

  const handleDragOver = useCallback((event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setIsDragging(false);
  }, []);

  const removeFile = (fileId: string) => {
    setUploadedFiles(prev => prev.filter(f => f.id !== fileId));
  };

  const retryUpload = (fileId: string) => {
    const file = uploadedFiles.find(f => f.id === fileId);
    if (file) {
      removeFile(fileId);
      processFile(file.file);
    }
  };

  const getStatusIcon = (status: UploadedFile['status']) => {
    switch (status) {
      case 'uploading':
        return <Loader2 className="h-4 w-4 animate-spin text-blue-600" />;
      case 'processing':
        return <Brain className="h-4 w-4 animate-pulse text-purple-600" />;
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case 'error':
        return <AlertTriangle className="h-4 w-4 text-red-600" />;
      default:
        return null;
    }
  };

  return (
    <div className="space-y-6">
      {/* Upload Area */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileImage className="h-5 w-5 text-blue-600" />
            Upload MRI Brain Scans
          </CardTitle>
          <p className="text-sm text-gray-600">
            Upload DICOM files, JPEG, PNG, or TIFF images for AI-powered brain tumor analysis
          </p>
        </CardHeader>

        <CardContent>
          <div
            className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors cursor-pointer ${isDragging
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-300 hover:border-gray-400'
              }`}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onClick={() => fileInputRef.current?.click()}
          >
            <div className="flex flex-col items-center gap-4">
              <div className="p-4 bg-blue-100 rounded-full">
                <Upload className="h-8 w-8 text-blue-600" />
              </div>

              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  Drop MRI images here or click to browse
                </h3>
                <p className="text-sm text-gray-600 mb-4">
                  Supports DICOM (.dcm), JPEG, PNG, TIFF formats up to 50MB
                </p>

                <div className="flex flex-wrap justify-center gap-2 text-xs text-gray-500">
                  <Badge variant="outline">DICOM</Badge>
                  <Badge variant="outline">JPEG</Badge>
                  <Badge variant="outline">PNG</Badge>
                  <Badge variant="outline">TIFF</Badge>
                  <Badge variant="outline">Max 50MB</Badge>
                </div>
              </div>
            </div>

            <input
              ref={fileInputRef}
              type="file"
              accept=".dcm,.dicom,.jpg,.jpeg,.png,.tif,.tiff,.bmp,image/*,application/dicom"
              onChange={handleFileSelect}
              multiple
              className="hidden"
            />
          </div>
        </CardContent>
      </Card>

      {/* Medical Disclaimer */}
      <Alert className="border-red-200 bg-red-50">
        <AlertTriangle className="h-4 w-4 text-red-600" />
        <AlertDescription className="text-red-800">
          <strong>Medical Disclaimer:</strong> This AI analysis is for educational purposes only.
          Results should be reviewed by qualified medical professionals. Do not use for clinical diagnosis.
        </AlertDescription>
      </Alert>

      {/* Uploaded Files */}
      {uploadedFiles.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Brain className="h-5 w-5 text-purple-600" />
              Processing Queue ({uploadedFiles.length})
            </CardTitle>
          </CardHeader>

          <CardContent className="space-y-4">
            {uploadedFiles.map((uploadedFile) => (
              <div
                key={uploadedFile.id}
                className="flex items-center gap-4 p-4 border rounded-lg bg-gray-50"
              >
                {/* Image Preview */}
                <div className="flex-shrink-0">
                  {uploadedFile.file.type.startsWith('image/') ? (
                    <img
                      src={uploadedFile.preview}
                      alt="MRI Preview"
                      className="w-16 h-16 object-cover rounded border"
                    />
                  ) : (
                    <div className="w-16 h-16 bg-gray-200 rounded border flex items-center justify-center">
                      <FileImage className="h-6 w-6 text-gray-400" />
                    </div>
                  )}
                </div>

                {/* File Info */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <h4 className="font-medium text-gray-900 truncate">
                      {uploadedFile.file.name}
                    </h4>
                    {getStatusIcon(uploadedFile.status)}
                  </div>

                  <div className="text-sm text-gray-600 mb-2">
                    {(uploadedFile.file.size / 1024 / 1024).toFixed(2)} MB
                  </div>

                  {/* Progress Bar */}
                  {(uploadedFile.status === 'uploading' || uploadedFile.status === 'processing') && (
                    <div className="space-y-1">
                      <Progress value={uploadedFile.progress} className="h-2" />
                      <div className="text-xs text-gray-500">
                        {uploadedFile.status === 'uploading'
                          ? `Uploading... ${uploadedFile.progress}%`
                          : 'AI Analysis in progress...'}
                      </div>
                    </div>
                  )}

                  {/* Analysis Results */}
                  {uploadedFile.status === 'completed' && uploadedFile.analysisResult && (
                    <div className="bg-green-50 border border-green-200 rounded p-2 mt-2">
                      <div className="text-xs text-green-800 font-medium mb-1">
                        Analysis Complete
                      </div>
                      <div className="text-xs text-green-700">
                        {uploadedFile.analysisResult.detected_regions?.length || 0} region(s) detected •
                        Confidence: {((uploadedFile.analysisResult.overall_confidence || 0) * 100).toFixed(1)}%
                      </div>
                      {/* Visualization Display */}
                      {uploadedFile.analysisResult.annotated_image && (
                        <div className="mt-2">
                          <div className="text-xs text-green-800 font-medium mb-1">
                            🎨 Annotated Visualization
                          </div>
                          <img
                            src={uploadedFile.analysisResult.annotated_image}
                            alt="Annotated MRI Analysis"
                            className="w-full max-w-xs rounded border border-green-300 shadow-sm"
                            style={{ maxHeight: '200px', objectFit: 'contain' }}
                          />
                          <div className="text-xs text-green-600 mt-1">
                            Detected regions highlighted with bounding boxes
                          </div>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Error State */}
                  {uploadedFile.status === 'error' && (
                    <div className="bg-red-50 border border-red-200 rounded p-2 mt-2">
                      <div className="text-xs text-red-800 font-medium">
                        Processing failed. Please try again.
                      </div>
                    </div>
                  )}
                </div>

                {/* Actions */}
                <div className="flex items-center gap-2">
                  {uploadedFile.status === 'completed' && (
                    <>
                      <Button variant="outline" size="sm">
                        <Eye className="h-3 w-3 mr-1" />
                        View
                      </Button>
                      <Button variant="outline" size="sm">
                        <Download className="h-3 w-3 mr-1" />
                        Report
                      </Button>
                    </>
                  )}

                  {uploadedFile.status === 'error' && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => retryUpload(uploadedFile.id)}
                    >
                      <RefreshCw className="h-3 w-3 mr-1" />
                      Retry
                    </Button>
                  )}

                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => removeFile(uploadedFile.id)}
                  >
                    <X className="h-3 w-3" />
                  </Button>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
