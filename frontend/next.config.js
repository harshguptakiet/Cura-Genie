/** @type {import('next').NextConfig} */
const nextConfig = {
  // Output configuration for production deployment
  output: 'standalone',
  outputFileTracingRoot: '.',
  
  // Production optimizations
  compress: true,
  productionBrowserSourceMaps: false,
  
  // Build configuration
  // Do not fail production builds on lint or type errors; log them instead
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  
  // Image optimization
  images: {
    domains: ['localhost', '127.0.0.1'],
    formats: ['image/webp', 'image/avif'],
  },
  
  // Security headers
  headers: async () => {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'Referrer-Policy',
            value: 'origin-when-cross-origin',
          },
          {
            key: 'Permissions-Policy',
            value: 'camera=(), microphone=(), geolocation=()',
          },
        ],
      },
    ];
  },
  
  // Rewrites for API calls
  rewrites: async () => {
    // If you need to proxy to the backend in non-Docker environments,
    // configure NEXT_PUBLIC_API_URL in Vercel/Env and add a rewrite there.
    return [];
  },
  
  // Bundle analyzer (development only)
  webpack: (config, { dev, isServer }) => {
    // Optimize bundle in production
    if (!dev && !isServer) {
      config.optimization.splitChunks = {
        chunks: 'all',
        cacheGroups: {
          framework: {
            chunks: 'all',
            name: 'framework',
            test: /(?!node_modules.*)[\/\\]node_modules[\/\\](react|react-dom|scheduler|prop-types|use-subscription)[\/\\]/,
            priority: 40,
            enforce: true,
          },
        },
      };
    }
    
    return config;
  },
  
  // Experimental features
  experimental: {
    optimizeCss: true,
    optimizePackageImports: ['lucide-react', '@radix-ui/react-icons'],
  },
};

module.exports = nextConfig;
