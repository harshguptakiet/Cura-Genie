'use client';

import React, { useRef, useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Play, Pause, RotateCcw, Zap, Eye, Settings } from 'lucide-react';

// Custom simple slider component as fallback
const SimpleSlider = ({ value, onValueChange, min, max, step, className = '' }: {
  value: number[];
  onValueChange: (value: number[]) => void;
  min: number;
  max: number;
  step: number;
  className?: string;
}) => {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onValueChange([parseFloat(e.target.value)]);
  };
  
  return (
    <input
      type="range"
      min={min}
      max={max}
      step={step}
      value={value[0] || min}
      onChange={handleChange}
      className={`w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer slider ${className}`}
      style={{
        background: `linear-gradient(to right, #3b82f6 0%, #3b82f6 ${((value[0] - min) / (max - min)) * 100}%, #374151 ${((value[0] - min) / (max - min)) * 100}%, #374151 100%)`
      }}
    />
  );
};

import { EnhancedDNAVisualizationProps, Particle, DNABase, GenomicDataArray } from '@/types/ui-types';

const EnhancedDNAVisualization: React.FC<EnhancedDNAVisualizationProps> = ({ 
  height = 500, 
  width = 700,
  showControls = true,
  genomicData = []
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<number>();
  const timeRef = useRef<number>(0);
  
  // Animation controls
  const [isPlaying, setIsPlaying] = useState(true);
  const [speed, setSpeed] = useState([1.5]);
  const [rotationSpeed, setRotationSpeed] = useState([2]);
  const [particleEffects, setParticleEffects] = useState(true);
  const [visualMode, setVisualMode] = useState<'helix' | 'flat' | 'spiral'>('helix');
  const [zoom, setZoom] = useState([1]);
  
  // Particles system
  const particles = useRef<Particle[]>([]);

  // Enhanced DNA base colors with vibrant gradients
  const baseColors = {
    A: { main: '#FF3B30', glow: '#FF6B6B', light: '#FF9999' }, // Vibrant Red
    T: { main: '#00E5FF', glow: '#40F8FF', light: '#80FFFF' }, // Electric Cyan
    G: { main: '#FF6EC7', glow: '#FF9EE5', light: '#FFCEF3' }, // Vibrant Pink
    C: { main: '#32D74B', glow: '#62E76B', light: '#92F79B' }, // Vibrant Green
  };

  const basePairs = { A: 'T', T: 'A', G: 'C', C: 'G' };

  // Generate realistic DNA sequence or use genomic data
  const generateDNASequence = (length: number) => {
    if (genomicData && genomicData.length > 0) {
      // Use real genomic data if available
      return genomicData.slice(0, length).map((variant, i) => ({
        x: 0,
        y: i * 15,
        z: 0,
        type: variant.ref || 'A',
        pair: basePairs[variant.ref as keyof typeof basePairs] || 'T',
        importance: variant.importance || Math.random(),
        position: variant.position || i,
        chromosome: variant.chromosome || '1'
      }));
    }
    
    // Generate sequence with biological patterns
    const sequence = [];
    const bases = ['A', 'T', 'G', 'C'] as const;
    
    for (let i = 0; i < length; i++) {
      // Add some biological realism - CpG islands, AT/GC content variation
      let baseType;
      if (i > 0 && sequence[i-1].type === 'C' && Math.random() < 0.7) {
        baseType = 'G'; // CpG island tendency
      } else if (Math.random() < 0.4) {
        baseType = Math.random() < 0.5 ? 'A' : 'T'; // AT rich regions
      } else {
        baseType = bases[Math.floor(Math.random() * bases.length)];
      }
      
      sequence.push({
        x: 0,
        y: i * 15,
        z: 0,
        type: baseType,
        pair: basePairs[baseType],
        importance: Math.random(),
        position: i * 3000, // Approximate bp position
        chromosome: '1'
      });
    }
    
    return sequence;
  };

  // Add particle effect
  const addParticle = (x: number, y: number, color: string) => {
    if (!particleEffects) return;
    
    particles.current.push({
      x: x + (Math.random() - 0.5) * 20,
      y: y + (Math.random() - 0.5) * 20,
      vx: (Math.random() - 0.5) * 4,
      vy: (Math.random() - 0.5) * 4,
      life: 0,
      maxLife: 60 + Math.random() * 40,
      color
    });
    
    // Limit particle count
    if (particles.current.length > 200) {
      particles.current = particles.current.slice(-200);
    }
  };

  // Update particles
  const updateParticles = (ctx: CanvasRenderingContext2D) => {
    particles.current = particles.current.filter(particle => {
      particle.life++;
      particle.x += particle.vx;
      particle.y += particle.vy;
      particle.vx *= 0.98;
      particle.vy *= 0.98;
      
      const alpha = Math.max(0, 1 - particle.life / particle.maxLife);
      ctx.globalAlpha = alpha * 0.6;
      ctx.fillStyle = particle.color;
      ctx.beginPath();
      ctx.arc(particle.x, particle.y, 2 * alpha, 0, Math.PI * 2);
      ctx.fill();
      
      return particle.life < particle.maxLife;
    });
    ctx.globalAlpha = 1;
  };

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Enhanced responsive sizing
    const container = canvas.parentElement;
    const containerWidth = container ? container.clientWidth : width;
    const containerHeight = Math.max(height, 600); // Ensure minimum height
    
    canvas.width = containerWidth;
    canvas.height = containerHeight;

    const dnaLength = Math.floor(containerHeight / 10); // More DNA bases for better visibility
    const dnaSequence = generateDNASequence(dnaLength);
    const centerX = containerWidth / 2;
    const centerY = containerHeight / 2;

    const animate = () => {
      if (!isPlaying) {
        animationRef.current = requestAnimationFrame(animate);
        return;
      }

      timeRef.current += 0.015 * speed[0];
      
      // Clear canvas with dark background
      ctx.fillStyle = '#0A0A0A';
      ctx.fillRect(0, 0, containerWidth, containerHeight);

      // Add background gradient
      const gradient = ctx.createRadialGradient(centerX, centerY, 0, centerX, centerY, containerWidth / 2);
      gradient.addColorStop(0, 'rgba(25, 25, 35, 0.8)');
      gradient.addColorStop(1, 'rgba(10, 10, 10, 1)');
      ctx.fillStyle = gradient;
      ctx.fillRect(0, 0, containerWidth, containerHeight);

      // Enhanced helix sizing - larger and more visible
      const helixRadius = Math.min(containerWidth * 0.2, containerHeight * 0.15) * zoom[0];
      
      // Draw DNA with FIXED POSITION like AnimatedDNAStrand
      dnaSequence.forEach((base, index) => {
        const y = centerY - (containerHeight * 0.4) + (index * (containerHeight * 0.8) / dnaLength); // FIXED Y POSITION
        
        let angle;
        switch (visualMode) {
          case 'helix':
            angle = (index * 0.3) + timeRef.current * rotationSpeed[0]; // Only rotation, no vertical movement
            break;
          case 'flat':
            angle = 0;
            break;
          case 'spiral':
            angle = (index * 0.2) + timeRef.current * rotationSpeed[0] * 0.5;
            break;
        }
        
        // 3D positions
        const x1 = centerX + Math.cos(angle) * helixRadius;
        const z1 = Math.sin(angle) * helixRadius;
        const x2 = centerX + Math.cos(angle + Math.PI) * helixRadius;
        const z2 = Math.sin(angle + Math.PI) * helixRadius;
        
        // Perspective projection
        const perspective = 300;
        const scale1 = perspective / (perspective + z1);
        const scale2 = perspective / (perspective + z2);
        
        const screenX1 = x1 * scale1;
        const screenY1 = (y - centerY) * scale1 + centerY;
        const screenX2 = x2 * scale2;
        const screenY2 = (y - centerY) * scale2 + centerY;

        // Draw all bases since they're now in fixed positions
        if (screenY1 > -20 && screenY1 < containerHeight + 20) {
          // Enhanced connection with gradient
          const connectionGradient = ctx.createLinearGradient(screenX1, screenY1, screenX2, screenY2);
          connectionGradient.addColorStop(0, `rgba(150, 150, 200, ${0.4 * scale1})`);
          connectionGradient.addColorStop(0.5, `rgba(100, 200, 255, ${0.6 * Math.min(scale1, scale2)})`);
          connectionGradient.addColorStop(1, `rgba(150, 150, 200, ${0.4 * scale2})`);
          
          ctx.strokeStyle = connectionGradient;
          ctx.lineWidth = 3 * Math.min(scale1, scale2);
          ctx.beginPath();
          ctx.moveTo(screenX1, screenY1);
          ctx.lineTo(screenX2, screenY2);
          ctx.stroke();

          // Enhanced bases with glow effects - larger and more visible
          const drawEnhancedBase = (x: number, y: number, baseType: string, scale: number) => {
            const colors = baseColors[baseType as keyof typeof baseColors];
            const radius = 15 * scale * (0.9 + base.importance * 0.3); // Larger base radius
            
            // Outer glow
            const glowGradient = ctx.createRadialGradient(x, y, 0, x, y, radius * 2);
            glowGradient.addColorStop(0, colors.glow + '60');
            glowGradient.addColorStop(0.3, colors.glow + '30');
            glowGradient.addColorStop(1, 'transparent');
            ctx.fillStyle = glowGradient;
            ctx.beginPath();
            ctx.arc(x, y, radius * 2, 0, Math.PI * 2);
            ctx.fill();
            
            // Main base
            const baseGradient = ctx.createRadialGradient(x - radius * 0.3, y - radius * 0.3, 0, x, y, radius);
            baseGradient.addColorStop(0, colors.light);
            baseGradient.addColorStop(0.7, colors.main);
            baseGradient.addColorStop(1, colors.main + 'CC');
            ctx.fillStyle = baseGradient;
            ctx.beginPath();
            ctx.arc(x, y, radius, 0, Math.PI * 2);
            ctx.fill();

            // Base letter with shadow
            ctx.shadowColor = 'rgba(0, 0, 0, 0.8)';
            ctx.shadowBlur = 4;
            ctx.shadowOffsetX = 1;
            ctx.shadowOffsetY = 1;
            ctx.fillStyle = '#FFFFFF';
            ctx.font = `bold ${14 * scale}px Arial`;
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText(baseType, x, y);
            ctx.shadowBlur = 0;
            
            // Add particle effects occasionally
            if (Math.random() < 0.02 * speed[0]) {
              addParticle(x, y, colors.main);
            }
          };

          drawEnhancedBase(screenX1, screenY1, base.type, scale1);
          drawEnhancedBase(screenX2, screenY2, base.pair, scale2);
        }
      });

      // Update particles
      updateParticles(ctx);

      // Add glowing effect around the DNA
      const glowGradient = ctx.createRadialGradient(centerX, centerY, helixRadius - 20, centerX, centerY, helixRadius + 40);
      glowGradient.addColorStop(0, 'rgba(64, 224, 255, 0.1)');
      glowGradient.addColorStop(1, 'rgba(64, 224, 255, 0)');
      ctx.fillStyle = glowGradient;
      ctx.fillRect(0, 0, containerWidth, containerHeight);

      // Draw helix backbone - FIXED POSITION
      for (let i = 0; i < containerHeight; i += 8) {
        const y = i; // FIXED Y POSITION
        const angle = (i * 0.02) + timeRef.current * rotationSpeed[0]; // Only rotation
        
        const x1 = centerX + Math.cos(angle) * helixRadius;
        const z1 = Math.sin(angle) * helixRadius;
        const x2 = centerX + Math.cos(angle + Math.PI) * helixRadius;
        const z2 = Math.sin(angle + Math.PI) * helixRadius;
        
        const perspective = 300;
        const scale1 = perspective / (perspective + z1);
        const scale2 = perspective / (perspective + z2);
        
        const screenX1 = x1 * scale1;
        const screenY1 = (y - centerY) * scale1 + centerY;
        const screenX2 = x2 * scale2;
        const screenY2 = (y - centerY) * scale2 + centerY;

        if (screenY1 > 0 && screenY1 < containerHeight) {
          // Strand 1 backbone
          ctx.fillStyle = `rgba(255, 255, 255, ${0.1 * scale1})`;
          ctx.beginPath();
          ctx.arc(screenX1, screenY1, 2 * scale1, 0, Math.PI * 2);
          ctx.fill();

          // Strand 2 backbone
          ctx.fillStyle = `rgba(255, 255, 255, ${0.1 * scale2})`;
          ctx.beginPath();
          ctx.arc(screenX2, screenY2, 2 * scale2, 0, Math.PI * 2);
          ctx.fill();
        }
      }

      animationRef.current = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [width, height, speed, rotationSpeed, isPlaying, visualMode, zoom, particleEffects]);

  const resetAnimation = () => {
    timeRef.current = 0;
    particles.current = [];
  };

  return (
    <Card className="bg-gray-900 border-gray-700 overflow-hidden">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-white flex items-center gap-2">
              <div className="w-3 h-3 bg-blue-400 rounded-full animate-pulse"></div>
              Enhanced DNA Helix Visualization
            </CardTitle>
            <CardDescription className="text-gray-300">
              Interactive 3D double helix with real-time genomic data integration
            </CardDescription>
          </div>
          <Badge variant="secondary" className="bg-blue-900 text-blue-200">
            Real-time
          </Badge>
        </div>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {showControls && (
          <div className="space-y-3 p-3 bg-gray-800 rounded-lg">
            <div className="flex items-center gap-2 flex-wrap">
              <Button
                size="sm"
                variant={isPlaying ? "secondary" : "default"}
                onClick={() => setIsPlaying(!isPlaying)}
              >
                {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
              </Button>
              <Button size="sm" variant="outline" onClick={resetAnimation}>
                <RotateCcw className="w-4 h-4" />
              </Button>
              <Button
                size="sm"
                variant={visualMode === 'helix' ? 'default' : 'outline'}
                onClick={() => setVisualMode('helix')}
              >
                3D
              </Button>
              <Button
                size="sm"
                variant={particleEffects ? 'default' : 'outline'}
                onClick={() => setParticleEffects(!particleEffects)}
              >
                <Zap className="w-4 h-4" />
              </Button>
            </div>
            
            <div className="grid grid-cols-3 gap-3 text-xs">
              <div className="space-y-1">
                <div className="flex items-center gap-1 text-white">
                  <Zap className="w-3 h-3" />
                  <span>Speed: {speed[0].toFixed(1)}x</span>
                </div>
                <SimpleSlider
                  value={speed}
                  onValueChange={setSpeed}
                  min={0.1}
                  max={3}
                  step={0.1}
                  className="w-full"
                />
              </div>
              
              <div className="space-y-1">
                <div className="flex items-center gap-1 text-white">
                  <RotateCcw className="w-3 h-3" />
                  <span>Spin: {rotationSpeed[0].toFixed(1)}x</span>
                </div>
                <SimpleSlider
                  value={rotationSpeed}
                  onValueChange={setRotationSpeed}
                  min={0}
                  max={5}
                  step={0.1}
                  className="w-full"
                />
              </div>
              
              <div className="space-y-1">
                <div className="flex items-center gap-1 text-white">
                  <Eye className="w-3 h-3" />
                  <span>Zoom: {zoom[0].toFixed(1)}x</span>
                </div>
                <SimpleSlider
                  value={zoom}
                  onValueChange={setZoom}
                  min={0.5}
                  max={2}
                  step={0.1}
                  className="w-full"
                />
              </div>
            </div>
          </div>
        )}
        
        <div className="relative flex justify-center items-center min-h-[400px]">
          <canvas 
            ref={canvasRef}
            className="w-full h-full rounded-lg border-2 border-blue-500/30 shadow-2xl"
            style={{ 
              background: 'radial-gradient(ellipse at center, #0f0f23 0%, #1a1a2e 50%, #000000 100%)',
              minHeight: '400px',
              maxWidth: '100%',
              aspectRatio: '4/3'
            }}
          />
          
          {/* Info overlays */}
          <div className="absolute top-4 left-4 text-white text-xs space-y-2">
            <div className="bg-black bg-opacity-60 rounded-lg p-3 backdrop-blur-sm">
              <h4 className="font-semibold mb-2 text-blue-300">DNA Base Pairs</h4>
              <div className="grid grid-cols-2 gap-2">
                {Object.entries(baseColors).map(([base, colors]) => (
                  <div key={base} className="flex items-center gap-2">
                    <div 
                      className="w-3 h-3 rounded-full shadow-lg" 
                      style={{ backgroundColor: colors.main }}
                    ></div>
                    <span>{base} - {base === 'A' ? 'Adenine' : base === 'T' ? 'Thymine' : base === 'G' ? 'Guanine' : 'Cytosine'}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
          
          <div className="absolute bottom-4 right-4 text-white text-xs bg-black bg-opacity-60 rounded-lg p-3 backdrop-blur-sm">
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                <span>Real-time visualization</span>
              </div>
              <div>🧬 Major groove: 22Å</div>
              <div>🔄 360° rotation per {(10.5).toFixed(1)} bp</div>
              <div>📏 3.4Å rise per bp</div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default EnhancedDNAVisualization;
