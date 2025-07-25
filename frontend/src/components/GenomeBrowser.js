import { useEffect, useRef } from 'react';
import { Box, Text } from '@chakra-ui/react';

export default function GenomeBrowser() {
  const svgRef = useRef();

  useEffect(() => {
    // Simple mock genome browser visualization
    const svg = svgRef.current;
    if (!svg) return;
    const width = 400, height = 80;
    svg.innerHTML = '';
    // Draw chromosome bar
    const bar = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    bar.setAttribute('x', 20);
    bar.setAttribute('y', 30);
    bar.setAttribute('width', 360);
    bar.setAttribute('height', 20);
    bar.setAttribute('fill', '#3182ce');
    svg.appendChild(bar);
    // Draw mock variant density
    for (let i = 0; i < 10; i++) {
      const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
      circle.setAttribute('cx', 40 + i * 36);
      circle.setAttribute('cy', 40);
      circle.setAttribute('r', 6);
      circle.setAttribute('fill', '#e53e3e');
      svg.appendChild(circle);
    }
  }, []);

  return (
    <Box mt={8}>
      <Text fontSize="xl" fontWeight="bold" mb={2}>Genome Browser (Mock)</Text>
      <svg ref={svgRef} width={400} height={80} style={{ border: '1px solid #CBD5E0', borderRadius: 8 }} />
    </Box>
  );
}
