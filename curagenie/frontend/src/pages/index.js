
import { Box, Heading, Text, Button, VStack } from '@chakra-ui/react';
import Link from 'next/link';


export default function Home() {
  return (
    <Box p={8} textAlign="center">
      <Heading as="h1" size="xl" mb={4} color="teal.500">CuraGenie</Heading>
      <Text fontSize="lg" mb={8}>Welcome to the AI Genomics Platform. Access all features from the menu below.</Text>
      <VStack spacing={4}>
        <Link href="/login" passHref><Button colorScheme="teal" w="60%">Login</Button></Link>
        <Link href="/register" passHref><Button colorScheme="teal" w="60%">Register</Button></Link>
        <Link href="/logout" passHref><Button colorScheme="gray" w="60%">Logout</Button></Link>
        <Link href="/dashboard_placeholder" passHref><Button colorScheme="teal" variant="outline" w="60%">Dashboard</Button></Link>
        <Link href="/metrics_dashboard" passHref><Button colorScheme="teal" variant="outline" w="60%">Metrics</Button></Link>
      </VStack>
    </Box>
  );
}
