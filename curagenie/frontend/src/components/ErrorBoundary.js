import { Alert, AlertIcon, AlertTitle, AlertDescription } from '@chakra-ui/react';

export default function ErrorBoundary({ error }) {
  if (!error) return null;
  return (
    <Alert status="error" borderRadius="xl" boxShadow="md" mt={4}>
      <AlertIcon />
      <AlertTitle>Error:</AlertTitle>
      <AlertDescription>{error.toString()}</AlertDescription>
    </Alert>
  );
}
