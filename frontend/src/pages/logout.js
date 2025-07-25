import { useEffect } from 'react';
import { Box, Heading, Spinner, Text } from '@chakra-ui/react';
import firebase from 'firebase/compat/app';
import 'firebase/compat/auth';

export default function Logout() {
  useEffect(() => {
    firebase.auth().signOut().then(() => {
      window.location.href = '/login';
    });
  }, []);

  return (
    <Box p={8} textAlign="center">
      <Heading color="teal.500">Logging out...</Heading>
      <Spinner mt={4} />
      <Text mt={2}>Please wait.</Text>
    </Box>
  );
}
