import VcfUploader from "@/components/upload/VcfUploader";

export default function DebugUploadPage() {
  return (
    <main style={{ padding: 24 }}>
      <h1>VCF Upload (Supabase)</h1>
      <p>Pick a .vcf or .vcf.gz file to upload via signed URL.</p>
      <VcfUploader />
    </main>
  );
}
