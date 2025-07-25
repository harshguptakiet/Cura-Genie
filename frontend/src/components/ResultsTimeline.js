
import { useEffect, useState } from 'react';
import { Box, Text, List, ListItem, Badge, Spinner, Alert, AlertIcon } from '@chakra-ui/react';

export default function ResultsTimeline({ userId = "demo_user" }) {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    async function fetchTimeline() {
      setLoading(true);
      try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/timeline/${userId}`);
        const data = await res.json();
        if (res.ok && Array.isArray(data.timeline)) {
          setResults(data.timeline);
        } else {
          setError(data.error || 'Failed to fetch timeline');
        }
      } catch (err) {
        setError('Failed to fetch timeline');
      }
      setLoading(false);
    }
    fetchTimeline();
  }, [userId]);

  if (loading) return <Spinner />;
  if (error) return <Alert status="error"><AlertIcon />{error}</Alert>;

  return (
    <Box mt={8}>
      <Text fontSize="xl" fontWeight="bold" mb={2}>Results Timeline</Text>
      <List spacing={3}>
        {results.map((item, idx) => (
          <ListItem key={idx} p={2} borderWidth={1} borderRadius="md" boxShadow="sm">
            <Badge colorScheme="blue" mr={2}>{item.date}</Badge>
            <Badge colorScheme="purple" mr={2}>{item.type}</Badge>
            {item.detail}
          </ListItem>
        ))}
      </List>
    </Box>
  );
}
