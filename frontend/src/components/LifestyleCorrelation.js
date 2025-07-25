import { Box, Text, SimpleGrid, Stat, StatLabel, StatNumber, Badge } from '@chakra-ui/react';

// Mock data for activity vs. risk
const mockData = [
  { activity: 'Steps', value: 8000, risk: 0.2 },
  { activity: 'Sleep (hrs)', value: 7, risk: 0.5 },
  { activity: 'Heart Rate', value: 72, risk: 0.7 },
];

export default function LifestyleCorrelation() {
  return (
    <Box mt={8}>
      <Text fontSize="xl" fontWeight="bold" mb={4}>Lifestyle Correlation</Text>
      <SimpleGrid columns={3} spacing={4}>
        {mockData.map(({ activity, value, risk }) => (
          <Stat key={activity} p={4} borderWidth={1} borderRadius="lg" boxShadow="md">
            <StatLabel>{activity}</StatLabel>
            <StatNumber>{value}</StatNumber>
            <Badge colorScheme={risk < 0.33 ? 'green' : risk < 0.66 ? 'yellow' : 'red'}>
              {risk < 0.33 ? 'Low Risk' : risk < 0.66 ? 'Medium Risk' : 'High Risk'}
            </Badge>
          </Stat>
        ))}
      </SimpleGrid>
    </Box>
  );
}
