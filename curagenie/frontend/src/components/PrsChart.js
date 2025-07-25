import { useEffect, useRef } from 'react';
import { Box, Text } from '@chakra-ui/react';

export default function PrsChart({ scores }) {
  const canvasRef = useRef();

  useEffect(() => {
    // Simple bar chart using Canvas (mock data)
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, 300, 120);
    const diseases = scores || [
      { disease_type: 'diabetes', score: 0.2 },
      { disease_type: 'alzheimers', score: 0.7 },
      { disease_type: 'cancer', score: 0.5 },
    ];
    diseases.forEach((d, i) => {
      ctx.fillStyle = '#3182ce';
      ctx.fillRect(40 + i * 80, 100 - d.score * 80, 40, d.score * 80);
      ctx.fillStyle = '#2d3748';
      ctx.fillText(d.disease_type, 40 + i * 80, 115);
      ctx.fillText((d.score * 100).toFixed(1) + '%', 40 + i * 80, 95 - d.score * 80);
    });
  }, [scores]);

  return (
    <Box mt={8}>
      <Text fontSize="xl" fontWeight="bold" mb={2}>PRS Score Chart</Text>
      <canvas ref={canvasRef} width={300} height={120} style={{ border: '1px solid #CBD5E0', borderRadius: 8 }} />
    </Box>
  );
}
