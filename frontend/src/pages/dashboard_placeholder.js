import { useEffect, useState } from 'react';
import { Box, Text, Button, Spinner, VStack } from '@chakra-ui/react';
import FileUpload from '../components/FileUpload';
import PrsScoreDisplay from '../components/PrsScoreDisplay';
import RecommendationsDisplay from '../components/RecommendationsDisplay';
import GenomeBrowser from '../components/GenomeBrowser';
import PrsChart from '../components/PrsChart';
import ResultsTimeline from '../components/ResultsTimeline';
import LifestyleCorrelation from '../components/LifestyleCorrelation';
import AdvancedRiskCharts from '../components/AdvancedRiskCharts';
import UserAlerts from '../components/UserAlerts';
import ErrorBoundary from '../components/ErrorBoundary';

export default function DashboardPlaceholder() {
  const [status, setStatus] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [globalError, setGlobalError] = useState('');

  useEffect(() => {
    setLoading(true);
    fetch(process.env.NEXT_PUBLIC_API_URL + '/health')
      .then((res) => res.json())
      .then((data) => {
        setStatus(data.status);
        setLoading(false);
      })
      .catch((err) => {
        setError('Failed to fetch backend health status');
        setGlobalError(err);
        setLoading(false);
      });
  }, []);

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
      minH={{ base: '60vh', md: '80vh' }}
      w="100%"
    >
      <VStack spacing={{ base: 4, md: 8 }} align="stretch">
        <Text fontSize={{ base: '2xl', md: '3xl' }} fontWeight="extrabold" color="teal.700" textAlign="center" aria-label="CuraGenie Dashboard">CuraGenie Dashboard</Text>
        <Box bg="white" p={{ base: 2, md: 4 }} borderRadius="lg" boxShadow="md" aria-live="polite">
          <Text fontSize={{ base: 'md', md: 'lg' }} fontWeight="bold" aria-label="Backend Health Status">Backend Health Status:</Text>
          {loading ? <Spinner aria-label="Loading" /> : <Text color={status === 'healthy' ? 'green.500' : 'red.500'} aria-label={status || error}>{status || error}</Text>}
          <Button colorScheme="teal" variant="outline" mt={2} onClick={() => window.location.reload()} aria-label="Refresh Health Status">Refresh</Button>
        </Box>
        <FileUpload />
        <PrsScoreDisplay userId={"demo_user"} />
        <RecommendationsDisplay userId={"demo_user"} />
        <GenomeBrowser />
        <PrsChart />
        <ResultsTimeline />
        <LifestyleCorrelation />
        <AdvancedRiskCharts />
        <UserAlerts />
        <Button as="a" href="/metrics_dashboard" colorScheme="teal" variant="solid" size="lg" borderRadius="xl" mt={8}>
          View System Metrics & Logs
        </Button>
        <ErrorBoundary error={globalError} />
      </VStack>
    </Box>
  );
}
