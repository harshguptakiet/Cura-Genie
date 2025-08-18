"use client";

import { useState } from "react";
import { uploadVcf } from "@/lib/uploadVcf";
import { isSupabaseEnabled } from "@/lib/supabaseClient";

export default function VcfUploader() {
  const [status, setStatus] = useState<string>("");
  const [uploading, setUploading] = useState(false);

  async function onFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      setUploading(true);
      setStatus("Uploading...");

      if (!isSupabaseEnabled) {
        // Fallback to local upload if Supabase not configured
        setStatus("Supabase not configured - using local upload");
        // You can implement local file handling here
        return;
      }

      const { path } = await uploadVcf(file);
      setStatus(`Uploaded to: ${path}`);
    } catch (err: any) {
      setStatus(`Upload failed: ${err?.message ?? "Unknown error"}`);
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
      {!isSupabaseEnabled && (
        <p className="text-yellow-600 text-sm">
          ⚠️ Supabase not configured - file upload features are limited
        </p>
      )}
    </div>
  );
}
