import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  /* config options here */
  reactCompiler: true,
  images: {
    // Next.js 16+: images.domains は非推奨のため remotePatterns に移行
    remotePatterns: [
      { protocol: 'https', hostname: 'firebasestorage.googleapis.com' },
      { protocol: 'https', hostname: 'firebasestorage.app' },
      { protocol: 'https', hostname: 'postown-ea4a4.firebasestorage.app' },
      { protocol: 'https', hostname: 'storage.googleapis.com' },
    ],
  },
  output: 'standalone',
}

export default nextConfig
