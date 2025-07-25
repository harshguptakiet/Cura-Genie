
import { useEffect, useState } from 'react';
import { Box, Alert, AlertIcon, Text, Spinner } from '@chakra-ui/react';

export default function UserAlerts({ userId = "demo_user" }) {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    async function fetchAlerts() {
      setLoading(true);
      try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/alerts/${userId}`);
        const data = await res.json();
        if (res.ok && Array.isArray(data.alerts)) {
          setAlerts(data.alerts);
        } else {
          setError(data.error || 'Failed to fetch alerts');
        }
      } catch (err) {
        setError('Failed to fetch alerts');
      }
      setLoading(false);
    }
    fetchAlerts();
  }, [userId]);

  if (loading) return <Spinner />;
  if (error) return <Alert status="error"><AlertIcon />{error}</Alert>;

  return (
    <Box mt={8}>
      {alerts.map(alert => (
        <Alert status="warning" mb={2} key={alert.id}>
          <AlertIcon />
          <Text>{alert.message}</Text>
        </Alert>
      ))}
    </Box>
  );
}
