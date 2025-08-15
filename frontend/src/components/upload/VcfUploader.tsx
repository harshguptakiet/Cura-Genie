"use client";

import { useState } from "react";
import { uploadVcf } from "@/lib/uploadVcf";

export default function VcfUploader() {
  const [status, setStatus] = useState<string>("");
  const [uploading, setUploading] = useState(false);

  async function onFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      setUploading(true);
      setStatus("Uploading...");
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
    </div>
  );
}
