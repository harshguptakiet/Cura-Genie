import { Box, Text, Button, VStack } from '@chakra-ui/react';

export default function MetricsDashboard() {
  return (
    <Box
      p={{ base: 4, md: 8 }}
      maxW={{ base: '100%', md: '4xl' }}
      mx="auto"
      mt={{ base: 4, md: 12 }}
      borderWidth={1}
      borderRadius="2xl"
      boxShadow="2xl"
      bgGradient="linear(to-br, teal.50, white)"
      minH={{ base: '40vh', md: '80vh' }}
      w="100%"
    >
      <VStack spacing={{ base: 4, md: 8 }} align="stretch">
        <Text fontSize={{ base: '2xl', md: '3xl' }} fontWeight="extrabold" color="teal.700" textAlign="center" aria-label="System Metrics & Logs">System Metrics & Logs</Text>
        <Text mb={4} fontSize={{ base: 'md', md: 'lg' }} aria-label="Metrics Description">View real-time metrics and logs for CuraGenie backend and infrastructure.</Text>
        <Button as="a" href="http://localhost:3001" target="_blank" colorScheme="teal" mb={4} size="lg" borderRadius="xl" aria-label="Open Grafana Dashboards">
          Open Grafana Dashboards
        </Button>
        <Text aria-label="Grafana Info">Grafana is running locally on port 3001. You can view Prometheus metrics and Elasticsearch logs in pre-built or custom dashboards.</Text>
        <Button as="a" href="/dashboard_placeholder" colorScheme="gray" variant="outline" size="md" borderRadius="xl" mt={8} aria-label="Back to Main Dashboard">
          Back to Main Dashboard
        </Button>
      </VStack>
    </Box>
  );
}
