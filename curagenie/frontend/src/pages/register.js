import { useState } from 'react';
import { Box, Button, Input, Heading, Text } from '@chakra-ui/react';
import firebase from 'firebase/compat/app';
import 'firebase/compat/auth';

if (!firebase.apps.length) {
  firebase.initializeApp({
    apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
    authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
  });
}

export default function Register() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleRegister = async () => {
    try {
      await firebase.auth().createUserWithEmailAndPassword(email, password);
      window.location.href = '/dashboard_placeholder';
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <Box p={8} maxW="md" mx="auto" mt={12} borderWidth={1} borderRadius="lg" boxShadow="lg">
      <Heading mb={4} color="teal.500">Register</Heading>
      <Input mb={2} placeholder="Email" value={email} onChange={e => setEmail(e.target.value)} />
      <Input mb={4} placeholder="Password" type="password" value={password} onChange={e => setPassword(e.target.value)} />
      <Button colorScheme="teal" onClick={handleRegister} w="100%">Register</Button>
      {error && <Text color="red.500" mt={2}>{error}</Text>}
    </Box>
  );
}
