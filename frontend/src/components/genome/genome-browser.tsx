'use client';

import React, { useRef, useEffect, useState, useCallback } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Slider } from '@/components/ui/slider';
import { Loader2, Play, Pause, Zap, Dna2, RotateCcw, ZoomIn, ZoomOut, Filter } from 'lucide-react';
import * as d3 from 'd3';

interface Variant {
  id: number;
  chromosome: string;
  position: number;
  reference: string;
  alternative: string;
  variant_type: string;
  quality: number;
  variant_id: string;
  is_real_data: boolean;
}

interface GenomeBrowserProps {
  userId: string;
}

// API function to fetch real genomic variants
const fetchGenomicVariants = async (userId: string): Promise<Variant[]> => {
  const response = await fetch(`http://127.0.0.1:8000/api/genomic/variants/${userId}`);
  if (!response.ok) {
    throw new Error('Failed to fetch genomic variants');
  }
  return response.json();
};

const GenomeBrowser: React.FC<GenomeBrowserProps> = ({ userId }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [selectedChromosome, setSelectedChromosome] = useState<string>('all');
  const [isAnimating, setIsAnimating] = useState(false);
  const [qualityFilter, setQualityFilter] = useState([0]);
  const [zoomLevel, setZoomLevel] = useState(1);
  const [viewMode, setViewMode] = useState<'scatter' | 'circular' | 'manhattan'>('circular');

  const { data: variants, isLoading, error } = useQuery({
    queryKey: ['genomic-variants', userId],
    queryFn: () => fetchGenomicVariants(userId),
    enabled: !!userId,
    retry: 1
  });

  const filteredVariants = React.useMemo(() => {
    if (!variants) return [];
    let filtered = variants.filter(v => v.quality >= qualityFilter[0]);
    if (selectedChromosome !== 'all') {
      filtered = filtered.filter(v => v.chromosome === selectedChromosome);
    }
    return filtered;
  }, [variants, selectedChromosome, qualityFilter]);

  const chromosomes = React.useMemo(() => {
    if (!variants) return [];
    return Array.from(new Set(variants.map(v => v.chromosome))).sort((a, b) => {
      const numA = parseInt(a);
      const numB = parseInt(b);
      if (!isNaN(numA) && !isNaN(numB)) return numA - numB;
      if (!isNaN(numA)) return -1;
      if (!isNaN(numB)) return 1;
      return a.localeCompare(b);
    });
  }, [variants]);

  const animateVisualization = useCallback(() => {
    setIsAnimating(true);
    setTimeout(() => setIsAnimating(false), 3000);
  }, []);

  useEffect(() => {
    if (containerRef.current && filteredVariants.length > 0) {
      drawModernGenomeBrowser(containerRef.current, filteredVariants, {
        viewMode,
        zoomLevel,
        isAnimating,
        chromosomes
      });
    }
  }, [filteredVariants, viewMode, zoomLevel, isAnimating, chromosomes]);

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Genome Browser</CardTitle>
          <CardDescription>Visualize genomic variants across chromosomes</CardDescription>
        </CardHeader>
        <CardContent className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin" />
          <span className="ml-2">Loading genomic variants...</span>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Genome Browser</CardTitle>
          <CardDescription>Visualize genomic variants across chromosomes</CardDescription>
        </CardHeader>
        <CardContent>
          <Alert variant="destructive">
            <AlertDescription>
              No genomic data available. Upload your VCF file to visualize variants.
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    );
  }

  if (!variants || variants.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Genome Browser</CardTitle>
          <CardDescription>Visualize genomic variants across chromosomes</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-12 text-gray-500">
            <p>No genomic variants found.</p>
            <p className="text-sm mt-2">Upload your genomic data to see visualization.</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="shadow-lg border-2">
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-2xl font-bold text-blue-900">🧬 Interactive Genome Browser</CardTitle>
            <CardDescription className="text-lg mt-1">Explore {variants.length} genomic variants across chromosomes with interactive visualization</CardDescription>
          </div>
          <div className="text-right">
            <div className="text-sm text-gray-600 mb-1">
              <span className="font-medium">Total Variants:</span> {variants.length}
            </div>
            <div className="text-sm text-gray-600">
              <span className="font-medium">Chromosomes:</span> {Array.from(new Set(variants.map(v => v.chromosome))).length}
            </div>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="bg-gradient-to-br from-blue-50 to-indigo-100 rounded-lg p-4 mb-4">
          <p className="text-sm text-blue-800 font-medium mb-2">📊 Visualization Guide:</p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-red-500 rounded-full"></div>
              <span className="text-blue-700">Disease-associated variants highlighted in red</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-green-400 rounded-full"></div>
              <span className="text-blue-700">Circle size indicates variant quality score</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-purple-400 rounded-full"></div>
              <span className="text-blue-700">Hover for detailed variant information</span>
            </div>
          </div>
        </div>
        <div ref={containerRef} className="w-full h-[500px] bg-white rounded-lg border-2 border-gray-200 shadow-inner"></div>

        {/* Summary statistics */}
        <div className="mt-6 grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="text-center p-4 bg-blue-50 rounded-lg">
            <div className="text-2xl font-bold text-blue-900">{variants.length}</div>
            <div className="text-sm text-blue-700">Total Variants</div>
          </div>
          <div className="text-center p-4 bg-green-50 rounded-lg">
            <div className="text-2xl font-bold text-green-900">{Array.from(new Set(variants.map(v => v.chromosome))).length}</div>
            <div className="text-sm text-green-700">Chromosomes</div>
          </div>
          <div className="text-center p-4 bg-purple-50 rounded-lg">
            <div className="text-2xl font-bold text-purple-900">{Math.round(variants.reduce((sum, v) => sum + v.quality, 0) / variants.length)}</div>
            <div className="text-sm text-purple-700">Avg Quality</div>
          </div>
          <div className="text-center p-4 bg-orange-50 rounded-lg">
            <div className="text-2xl font-bold text-orange-900">{variants.filter(v => ['rs7903146', 'rs1801282', 'rs5219', 'rs13266634', 'rs12255372'].includes(v.variant_id)).length}</div>
            <div className="text-sm text-orange-700">Disease SNPs</div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

function drawGenomeBrowser(container: HTMLDivElement, variants: Variant[]) {
  // Define dimensions
  const width = container.clientWidth || 800;
  const height = container.clientHeight || 400;
  const margins = { top: 40, right: 80, bottom: 60, left: 80 };

  console.log(`Drawing genome browser with ${variants.length} variants`);
  console.log('Sample variant:', variants[0]);

  // Clear previous content
  d3.select(container).select('svg').remove();

  // Create SVG container with enhanced styling
  const svg = d3.select(container)
    .append('svg')
    .attr('width', width)
    .attr('height', height)
    .style('background', 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)')
    .style('border-radius', '8px');

  // Sort chromosomes naturally (1, 2, 3, ... 22, X, Y)
  const chromosomes = Array.from(new Set(variants.map(v => v.chromosome)))
    .sort((a, b) => {
      const numA = parseInt(a);
      const numB = parseInt(b);
      if (!isNaN(numA) && !isNaN(numB)) return numA - numB;
      if (!isNaN(numA)) return -1;
      if (!isNaN(numB)) return 1;
      return a.localeCompare(b);
    });

  console.log('Chromosomes:', chromosomes);

  // Create scales
  const xScale = d3.scaleLog()
    .domain([1, d3.max(variants, d => d.position) || 1000000])
    .range([margins.left, width - margins.right]);

  const yScale = d3.scalePoint()
    .domain(chromosomes)
    .range([margins.top, height - margins.bottom])
    .padding(0.1);

  // Color scale based on quality scores
  const qualityExtent = d3.extent(variants, d => d.quality) as [number, number];
  const colorScale = d3.scaleSequential(d3.interpolateViridis)
    .domain(qualityExtent);

  // Size scale based on quality (better quality = larger dots)
  const sizeScale = d3.scaleLinear()
    .domain(qualityExtent)
    .range([3, 8]);

  // Add title
  svg.append('text')
    .attr('x', width / 2)
    .attr('y', 20)
    .attr('text-anchor', 'middle')
    .style('font-size', '16px')
    .style('font-weight', 'bold')
    .style('fill', '#333')
    .text(`Genomic Variants (${variants.length} variants)`);

  // X-axis
  svg.append('g')
    .attr('transform', `translate(0, ${height - margins.bottom})`)
    .call(d3.axisBottom(xScale)
      .tickFormat(d3.format('.0s')))
    .selectAll('text')
    .style('font-size', '11px');

  // X-axis label
  svg.append('text')
    .attr('x', width / 2)
    .attr('y', height - 10)
    .attr('text-anchor', 'middle')
    .style('font-size', '12px')
    .style('fill', '#666')
    .text('Genomic Position');

  // Y-axis
  svg.append('g')
    .attr('transform', `translate(${margins.left}, 0)`)
    .call(d3.axisLeft(yScale))
    .selectAll('text')
    .style('font-size', '11px')
    .text(d => `Chr ${d}`);

  // Y-axis label
  svg.append('text')
    .attr('transform', 'rotate(-90)')
    .attr('x', -height / 2)
    .attr('y', 20)
    .attr('text-anchor', 'middle')
    .style('font-size', '12px')
    .style('fill', '#666')
    .text('Chromosome');

  // Disease-associated SNPs for highlighting
  const diseaseSnps = ['rs7903146', 'rs1801282', 'rs5219', 'rs13266634', 'rs12255372'];

  // Create tooltip
  const tooltip = d3.select('body').append('div')
    .attr('class', 'genome-tooltip')
    .style('position', 'absolute')
    .style('padding', '10px')
    .style('background', 'rgba(0, 0, 0, 0.8)')
    .style('color', 'white')
    .style('border-radius', '5px')
    .style('pointer-events', 'none')
    .style('opacity', 0)
    .style('font-size', '12px');

  // Draw variants
  svg.selectAll('.variant')
    .data(variants)
    .enter()
    .append('circle')
    .attr('class', 'variant')
    .attr('cx', d => xScale(d.position))
    .attr('cy', d => yScale(d.chromosome) ?? 0)
    .attr('r', d => sizeScale(d.quality))
    .attr('fill', d => diseaseSnps.includes(d.variant_id) ? '#ff6b6b' : colorScale(d.quality))
    .attr('stroke', d => diseaseSnps.includes(d.variant_id) ? '#ff0000' : 'none')
    .attr('stroke-width', d => diseaseSnps.includes(d.variant_id) ? 2 : 0)
    .style('cursor', 'pointer')
    .style('opacity', 0.8)
    .on('mouseover', function (event, d) {
      d3.select(this).style('opacity', 1).attr('r', sizeScale(d.quality) + 2);
      tooltip.style('opacity', 1)
        .html(`
          <strong>${d.variant_id || 'Variant ID Unavailable'}</strong><br/>
          Chr: ${d.chromosome}<br/>
          Position: ${d.position.toLocaleString()}<br/>
          Change: ${d.reference} → ${d.alternative}<br/>
          Quality: ${d.quality}<br/>
          Type: ${d.variant_type}
          ${diseaseSnps.includes(d.variant_id) ? '<br/><strong style="color: #ff6b6b;">Disease-associated SNP</strong>' : ''}
        `)
        .style('left', (event.pageX + 10) + 'px')
        .style('top', (event.pageY - 10) + 'px');
    })
    .on('mouseout', function (event, d) {
      d3.select(this).style('opacity', 0.8).attr('r', sizeScale(d.quality));
      tooltip.style('opacity', 0);
    });

  // Legend for disease SNPs
  const legend = svg.append('g')
    .attr('class', 'legend')
    .attr('transform', `translate(${width - margins.right + 10}, ${margins.top})`);

  legend.append('text')
    .attr('x', 0)
    .attr('y', 0)
    .style('font-size', '12px')
    .style('font-weight', 'bold')
    .style('fill', '#333')
    .text('Legend');

  legend.append('circle')
    .attr('cx', 5)
    .attr('cy', 20)
    .attr('r', 4)
    .attr('fill', '#ff6b6b')
    .attr('stroke', '#ff0000')
    .attr('stroke-width', 2);

  legend.append('text')
    .attr('x', 15)
    .attr('y', 25)
    .style('font-size', '10px')
    .style('fill', '#666')
    .text('Disease SNP');

  legend.append('circle')
    .attr('cx', 5)
    .attr('cy', 40)
    .attr('r', 4)
    .attr('fill', colorScale(qualityExtent[1]));

  legend.append('text')
    .attr('x', 15)
    .attr('y', 45)
    .style('font-size', '10px')
    .style('fill', '#666')
    .text('Regular variant');

  console.log('Genome browser visualization complete');
}

export default GenomeBrowser;

