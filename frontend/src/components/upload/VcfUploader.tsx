"use client";

import { useState } from "react";
import { uploadVcf } from "@/lib/uploadVcf";
import { VCFUploadResult, UploadSuccessData } from "@/types";
import { handleError, createUploadError, getUserFriendlyMessage } from "@/lib/error-handling";

export default function VcfUploader() {
  const [status, setStatus] = useState<string>("");
  const [uploading, setUploading] = useState(false);

  async function onFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      setUploading(true);
      setStatus("Uploading...");

      const result: VCFUploadResult = await uploadVcf(file);

      if (result.upload_status === 'success') {
        setStatus(`Uploaded to: ${result.path}`);
      } else {
        throw new Error(result.error_message || 'Upload failed');
      }
    } catch (error: unknown) {
      const appError = handleError(error);
      const userMessage = getUserFriendlyMessage(appError);
      setStatus(`Upload failed: ${userMessage}`);

      // Log the error for debugging
      console.error('VCF upload error:', appError);
    } finally {
      setUploading(false);
    }
  }

  return (
    <div className="space-y-3">
      <input
        type="file"
        accept=".vcf,.vcf.gz"
        onChange={onFileChange}
        disabled={uploading}
      />
      <p>{status}</p>
    </div>
  );
}
