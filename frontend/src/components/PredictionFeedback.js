import { useState } from 'react';
import { Box, Text, IconButton, Textarea, Button, HStack, Alert, AlertIcon } from '@chakra-ui/react';
import { CheckIcon, CloseIcon } from '@chakra-ui/icons';

export default function PredictionFeedback({ predictionId }) {
  const [isCorrect, setIsCorrect] = useState(null);
  const [comment, setComment] = useState('');
  const [status, setStatus] = useState('');
  const [error, setError] = useState('');

  const sendFeedback = async () => {
    setStatus('');
    setError('');
    try {
      const res = await fetch(process.env.NEXT_PUBLIC_API_URL + '/api/ml/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prediction_id: predictionId, is_correct: isCorrect, comment }),
      });
      const data = await res.json();
      if (res.ok) {
        setStatus('Feedback submitted!');
      } else {
        setError(data.error || 'Failed to submit feedback');
      }
    } catch (err) {
      setError('Network error');
    }
  };

  return (
    <Box mt={4} p={4} borderWidth={1} borderRadius="md" boxShadow="sm">
      <Text fontWeight="bold" mb={2}>Was this prediction correct?</Text>
      <HStack mb={2}>
        <IconButton icon={<CheckIcon />} colorScheme={isCorrect === true ? 'green' : 'gray'} onClick={() => setIsCorrect(true)} aria-label="Correct" />
        <IconButton icon={<CloseIcon />} colorScheme={isCorrect === false ? 'red' : 'gray'} onClick={() => setIsCorrect(false)} aria-label="Incorrect" />
      </HStack>
      <Textarea placeholder="Add a comment (optional)" value={comment} onChange={e => setComment(e.target.value)} mb={2} />
      <Button colorScheme="teal" onClick={sendFeedback} isDisabled={isCorrect === null}>Submit Feedback</Button>
      {status && <Alert status="success" mt={2}><AlertIcon />{status}</Alert>}
      {error && <Alert status="error" mt={2}><AlertIcon />{error}</Alert>}
    </Box>
  );
}
