import { useEffect, useState } from 'react';
import { Box, Text, SimpleGrid, Stat, StatLabel, StatNumber, Badge, Spinner, Alert, AlertIcon } from '@chakra-ui/react';

const DISEASES = ['diabetes', 'alzheimers', 'cancer'];

function getRiskLevel(score) {
  if (score < 0.33) return { label: 'Low', color: 'green' };
  if (score < 0.66) return { label: 'Medium', color: 'yellow' };
  return { label: 'High', color: 'red' };
}

export default function PrsScoreDisplay({ userId }) {
  const [scores, setScores] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    async function fetchScores() {
      setLoading(true);
      try {
        const res = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/api/prs/user/${userId}`
        );
        const data = await res.json();
        if (res.ok && Array.isArray(data.scores)) {
          setScores(data.scores);
        } else {
          setError('Failed to fetch PRS scores');
        }
      } catch (err) {
        setError('Failed to fetch PRS scores');
      }
      setLoading(false);
    }
    fetchScores();
  }, [userId]);

  if (loading) return <Spinner />;
  if (error) return <Alert status="error"><AlertIcon />{error}</Alert>;

  return (
    <Box mt={8}>
      <Text fontSize="xl" fontWeight="bold" mb={4}>Polygenic Risk Scores</Text>
      <SimpleGrid columns={3} spacing={4}>
        {scores.map(({ disease_type, score }) => {
          const risk = getRiskLevel(score);
          return (
            <Stat key={disease_type} p={4} borderWidth={1} borderRadius="lg" boxShadow="md">
              <StatLabel>{disease_type.charAt(0).toUpperCase() + disease_type.slice(1)}</StatLabel>
              <StatNumber>{(score * 100).toFixed(1)}%</StatNumber>
              <Badge colorScheme={risk.color}>{risk.label}</Badge>
            </Stat>
          );
        })}
      </SimpleGrid>
    </Box>
  );
}
