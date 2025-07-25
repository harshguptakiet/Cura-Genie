import { useState } from 'react';
import { Box, Text, Checkbox, Switch, Button, Modal, ModalOverlay, ModalContent, ModalHeader, ModalBody, ModalFooter, useDisclosure, Alert, AlertIcon } from '@chakra-ui/react';
import ErrorBoundary from '../../components/ErrorBoundary';

const CONSENT_FEATURES = [
  { id: 'data_upload', label: 'Allow data upload' },
  { id: 'data_share', label: 'Allow data sharing' },
  { id: 'ml_prediction', label: 'Allow ML-based predictions' },
];

export default function ConsentManagement() {
  const [consents, setConsents] = useState({});
  const [status, setStatus] = useState('');
  const [error, setError] = useState('');
  const [globalError, setGlobalError] = useState('');
  const { isOpen, onOpen, onClose } = useDisclosure();

  const handleConsentChange = (featureId, value) => {
    setConsents({ ...consents, [featureId]: value });
    if (featureId === 'ml_prediction' && value) onOpen();
  };

  const submitConsents = async () => {
    setStatus('');
    setError('');
    try {
      // Send consents to backend
      for (const featureId of Object.keys(consents)) {
        await fetch(process.env.NEXT_PUBLIC_API_URL + '/api/consent/agree', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            user_id: 'demo_user',
            feature_id: featureId,
            version: 'v1',
            user_agreement_timestamp: new Date().toISOString(),
          }),
        });
      }
      setStatus('Consents updated!');
    } catch (err) {
      setError('Failed to update consents');
      setGlobalError('An unexpected error occurred. Please try again later.');
    }
  };

  return (
    <ErrorBoundary error={globalError}>
      <Box
        p={{ base: 4, md: 8 }}
        maxW={{ base: '100%', md: '2xl' }}
        mx="auto"
        mt={{ base: 4, md: 12 }}
        borderWidth={1}
        borderRadius="2xl"
        boxShadow="2xl"
        bgGradient="linear(to-br, teal.50, white)"
        minH={{ base: '40vh', md: '60vh' }}
        w="100%"
      >
        <Text fontSize={{ base: '2xl', md: '3xl' }} fontWeight="extrabold" color="teal.700" mb={6} textAlign="center" aria-label="Consent Management">Consent Management</Text>
        {CONSENT_FEATURES.map(f => (
          <Box key={f.id} mb={6} bg="white" p={{ base: 2, md: 4 }} borderRadius="lg" boxShadow="md">
            <Checkbox isChecked={!!consents[f.id]} onChange={e => handleConsentChange(f.id, e.target.checked)} fontWeight="bold" aria-label={f.label}>
              {f.label}
            </Checkbox>
            {f.id === 'ml_prediction' && (
              <Switch ml={4} isChecked={!!consents[f.id]} onChange={e => handleConsentChange(f.id, e.target.checked)} colorScheme="teal" aria-label="Enable ML Predictions">
                Enable ML Predictions
              </Switch>
            )}
          </Box>
        ))}
        <Button colorScheme="teal" size="lg" borderRadius="xl" onClick={submitConsents} aria-label="Save Consents">Save Consents</Button>
        <Button as="a" href="/metrics_dashboard" colorScheme="gray" variant="outline" size="md" borderRadius="xl" mt={4} aria-label="View System Metrics & Logs">
          View System Metrics & Logs
        </Button>
        {status && <Alert status="success" mt={4}><AlertIcon />{status}</Alert>}
        {error && <Alert status="error" mt={4}><AlertIcon />{error}</Alert>}
        <Modal isOpen={isOpen} onClose={onClose} isCentered>
          <ModalOverlay />
          <ModalContent>
            <ModalHeader>ML Prediction Consent</ModalHeader>
            <ModalBody>
              <Text>By enabling ML-based predictions, you agree to allow AI models to analyze your genomic and clinical data for health risk assessment.</Text>
            </ModalBody>
            <ModalFooter>
              <Button colorScheme="teal" onClick={onClose}>I Agree</Button>
            </ModalFooter>
          </ModalContent>
        </Modal>
      </Box>
    </ErrorBoundary>
  );
}
