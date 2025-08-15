import { supabase } from "./supabaseClient";

/**
 * Upload a VCF file to Supabase Storage using a signed upload token from the backend.
 * Returns the storage path on success.
 */
export async function uploadVcf(file: File): Promise<{ path: string }> {
  const path = `vcf/${Date.now()}_${file.name}`;

  const apiUrl = process.env.NEXT_PUBLIC_API_URL;
  if (!apiUrl) throw new Error("NEXT_PUBLIC_API_URL is not set");

  const presignRes = await fetch(`${apiUrl}/api/upload/supabase/presign`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ path }),
  });
  if (!presignRes.ok) {
    const text = await presignRes.text().catch(() => "");
    throw new Error(`Failed to get presigned token (${presignRes.status}): ${text}`);
  }
  const { token } = (await presignRes.json()) as { token: string };

  const { error } = await supabase.storage.from("uploads").uploadToSignedUrl(path, token, file);
  if (error) throw error;

  return { path };
}
