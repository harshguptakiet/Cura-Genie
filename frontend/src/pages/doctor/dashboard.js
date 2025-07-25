import { Box, Text, List, ListItem, Button } from '@chakra-ui/react';
import { useState } from 'react';
import ErrorBoundary from '../../components/ErrorBoundary';

// Mock data for doctor portal
const patients = [
  { id: 'p1', name: 'Alice Smith' },
  { id: 'p2', name: 'Bob Jones' },
];

export default function DoctorDashboard() {
  const [globalError, setGlobalError] = useState('');

  return (
    <ErrorBoundary error={globalError}>
      <Box
        p={{ base: 4, md: 8 }}
        maxW={{ base: '100%', md: '3xl' }}
        mx="auto"
        mt={{ base: 4, md: 12 }}
        borderWidth={1}
        borderRadius="2xl"
        boxShadow="2xl"
        bgGradient="linear(to-br, blue.50, white)"
        minH={{ base: '40vh', md: '60vh' }}
        w="100%"
      >
        <Text fontSize={{ base: '2xl', md: '3xl' }} fontWeight="extrabold" color="blue.700" mb={6} textAlign="center" aria-label="Doctor Portal">Doctor Portal</Text>
        <Text mb={4} fontSize={{ base: 'md', md: 'lg' }} fontWeight="bold" aria-label="Assigned Patients">Assigned Patients:</Text>
        <List spacing={{ base: 2, md: 4 }} aria-label="Patient List">
          {patients.map((patient) => (
            <ListItem key={patient.id} p={{ base: 2, md: 4 }} borderWidth={1} borderRadius="xl" boxShadow="md" bg="white" aria-label={patient.name}>
              <Text fontWeight="bold" fontSize={{ base: 'md', md: 'lg' }}>{patient.name}</Text>
              <Button colorScheme="teal" size="sm" mt={2} aria-label={`View details for ${patient.name}`}>View Details</Button>
            </ListItem>
          ))}
        </List>
        <Button colorScheme="blue" mt={8} size="lg" borderRadius="xl" aria-label="Export PDF Report">Export PDF Report</Button>
        <Button as="a" href="/metrics_dashboard" colorScheme="teal" variant="outline" size="md" borderRadius="xl" mt={4} aria-label="View System Metrics & Logs">
          View System Metrics & Logs
        </Button>
      </Box>
    </ErrorBoundary>
  );
}
