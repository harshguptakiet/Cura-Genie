import { useState } from 'react';
import { Box, Button, Input, Progress, Alert, AlertIcon, Text } from '@chakra-ui/react';

export default function FileUpload({ userId = "demo_user" }) {
  const [file, setFile] = useState(null);
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState('');
  const [error, setError] = useState('');
  const [metadata, setMetadata] = useState(null);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setStatus('');
    setError('');
    setProgress(0);
    setMetadata(null);
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file to upload.');
      return;
    }
    setStatus('');
    setError('');
    setProgress(10);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('user_id', userId);
    try {
      const res = await fetch(process.env.NEXT_PUBLIC_API_URL + '/api/genomic-data/upload', {
        method: 'POST',
        body: formData,
      });
      setProgress(80);
      const data = await res.json();
      if (res.ok) {
        setStatus(`Upload successful! ID: ${data.id}`);
        setMetadata(data.metadata);
        setProgress(100);
      } else {
        setError(data.error || 'Upload failed.');
        setProgress(0);
      }
    } catch (err) {
      setError('Network error.');
      setProgress(0);
    }
  };

  return (
    <Box p={6} borderWidth={1} borderRadius="lg" boxShadow="md" maxW="md" mx="auto" mt={8}>
      <Text fontSize="lg" mb={2}>Upload Genomic Data (VCF/FASTQ)</Text>
      <Input type="file" accept=".vcf,.fastq" onChange={handleFileChange} mb={2} />
      <Button colorScheme="teal" onClick={handleUpload} isDisabled={!file} mb={2}>Upload</Button>
      {progress > 0 && <Progress value={progress} size="sm" mb={2} />}
      {status && <Alert status="success" mb={2}><AlertIcon />{status}</Alert>}
      {error && <Alert status="error" mb={2}><AlertIcon />{error}</Alert>}
      {metadata && (
        <Box mt={2} p={2} borderWidth={1} borderRadius="md" bg="gray.50">
          <Text fontWeight="bold">File Metadata:</Text>
          <pre>{JSON.stringify(metadata, null, 2)}</pre>
        </Box>
      )}
    </Box>
  );
}
