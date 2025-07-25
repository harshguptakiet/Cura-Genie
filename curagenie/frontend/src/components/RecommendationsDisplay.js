import { useEffect, useState } from 'react';
import { Box, Text, Alert, AlertIcon, List, ListItem, Badge, Spinner } from '@chakra-ui/react';

export default function RecommendationsDisplay({ userId }) {
  const [recs, setRecs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    async function fetchRecs() {
      setLoading(true);
      try {
        // Replace with actual API call
        const res = await fetch(process.env.NEXT_PUBLIC_API_URL + `/api/recommendations/${userId}`);
        const data = await res.json();
        if (res.ok && Array.isArray(data.recommendations)) {
          setRecs(data.recommendations);
        } else {
          setError(data.error || 'Failed to fetch recommendations');
        }
      } catch (err) {
        setError('Network error');
      }
      setLoading(false);
    }
    fetchRecs();
  }, [userId]);

  if (loading) return <Spinner />;
  if (error) return <Alert status="error"><AlertIcon />{error}</Alert>;

  return (
    <Box mt={8}>
      <Text fontSize="xl" fontWeight="bold" mb={4}>Personalized Recommendations</Text>
      {recs.length === 0 ? (
        <Alert status="info"><AlertIcon />No recommendations at this time.</Alert>
      ) : (
        <List spacing={3}>
          {recs.map((rec, idx) => (
            <ListItem key={idx} p={2} borderWidth={1} borderRadius="md" boxShadow="sm">
              <Badge colorScheme="red" mr={2}>High Priority</Badge>
              {rec}
            </ListItem>
          ))}
        </List>
      )}
    </Box>
  );
}
