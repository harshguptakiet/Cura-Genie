import VcfUploader from "@/components/upload/VcfUploader";

export default function DebugUploadPage() {
  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const isSupabaseEnabled = supabaseUrl && supabaseUrl !== 'disabled-for-local-deployment';

  if (!isSupabaseEnabled) {
    return (
      <main style={{ padding: 24 }}>
        <h1>VCF Upload (Supabase)</h1>
        <p>Supabase upload is disabled for this deployment. Use the main upload functionality instead.</p>
        <p><a href="/">← Go back to main application</a></p>
      </main>
    );
  }

  return (
    <main style={{ padding: 24 }}>
      <h1>VCF Upload (Supabase)</h1>
      <p>Pick a .vcf or .vcf.gz file to upload via signed URL.</p>
      <VcfUploader />
    </main>
  );
}
