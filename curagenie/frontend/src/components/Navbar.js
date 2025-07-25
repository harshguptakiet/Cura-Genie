import { Box, Button, Flex, Spacer, Link } from '@chakra-ui/react';
import firebase from 'firebase/compat/app';
import 'firebase/compat/auth';
import { useRouter } from 'next/router';

export default function Navbar() {
  const router = useRouter();
  const user = firebase.auth().currentUser;

  return (
    <Flex as="nav" p={4} bg="teal.500" color="white" align="center">
      <Box fontWeight="bold" fontSize="xl">CuraGenie</Box>
      <Spacer />
      <Link href="/" mr={4}>Home</Link>
      <Link href="/dashboard_placeholder" mr={4}>Dashboard</Link>
      <Link href="/metrics_dashboard" mr={4}>Metrics</Link>
      {user ? (
        <Button colorScheme="teal" variant="outline" onClick={() => router.push('/logout')}>Logout</Button>
      ) : (
        <>
          <Button colorScheme="teal" variant="outline" mr={2} onClick={() => router.push('/login')}>Login</Button>
          <Button colorScheme="teal" variant="outline" onClick={() => router.push('/register')}>Register</Button>
        </>
      )}
    </Flex>
  );
}
