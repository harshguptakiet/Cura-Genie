import { Box, Text, Select, SimpleGrid } from '@chakra-ui/react';

// Mock data for advanced charts
const mockScores = [
  { disease: 'diabetes', timeline: [0.2, 0.3, 0.4, 0.5] },
  { disease: 'alzheimers', timeline: [0.5, 0.6, 0.7, 0.8] },
  { disease: 'cancer', timeline: [0.1, 0.2, 0.3, 0.4] },
];
const populationBaseline = 0.35;

export default function AdvancedRiskCharts() {
  return (
    <Box mt={8}>
      <Text fontSize="xl" fontWeight="bold" mb={2}>Advanced Risk Timelines</Text>
      <Select mb={4} placeholder="Filter by disease">
        {mockScores.map(({ disease }) => (
          <option key={disease} value={disease}>{disease}</option>
        ))}
      </Select>
      <SimpleGrid columns={3} spacing={4}>
        {mockScores.map(({ disease, timeline }) => (
          <Box key={disease} p={4} borderWidth={1} borderRadius="lg" boxShadow="md">
            <Text fontWeight="bold" mb={2}>{disease.charAt(0).toUpperCase() + disease.slice(1)}</Text>
            <Text fontSize="sm">Timeline: {timeline.map((v, i) => `${v}` + (i < timeline.length - 1 ? ' → ' : '')).join('')}</Text>
            <Text fontSize="xs" color="gray.500">Population baseline: {populationBaseline}</Text>
          </Box>
        ))}
      </SimpleGrid>
    </Box>
  );
}
