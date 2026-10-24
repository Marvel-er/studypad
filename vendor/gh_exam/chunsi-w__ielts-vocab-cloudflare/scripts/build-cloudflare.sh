#!/bin/bash
# Build script for Cloudflare Pages deployment.
# Builds the Next.js app with static data mode (no server needed).
# Usage: bash scripts/build-cloudflare.sh

set -e

echo "=== Building for Cloudflare Pages (static mode) ==="

# Set static data mode
export NEXT_PUBLIC_STATIC_DATA=true

# Generate Prisma client (in case it's needed by any import)
echo "Generating Prisma client..."
npx prisma generate 2>/dev/null || true

# Temporarily switch next.config to export mode
cat > next.config.cf.ts << 'EOF'
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "export",
  images: {
    unoptimized: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  reactStrictMode: false,
  trailingSlash: true,
};

export default nextConfig;
EOF

# Backup original config and use cf config
mv next.config.ts next.config.dev.ts.bak
mv next.config.cf.ts next.config.ts

# Temporarily move API routes out of the app directory
# (API routes use Prisma and are not compatible with static export)
if [ -d "src/app/api" ]; then
  mv src/app/api /tmp/api_backup
  echo "Temporarily moved API routes to /tmp/api_backup"
fi

# Build (use npx next build directly to avoid package.json standalone copy commands)
echo "Running next build..."
npx next build 2>&1 || true

# Restore API routes
if [ -d "/tmp/api_backup" ]; then
  mv /tmp/api_backup src/app/api
  echo "Restored API routes"
fi

# Restore original config
mv next.config.ts next.config.cf.ts
mv next.config.dev.ts.bak next.config.ts

# Check if out directory exists
if [ ! -d "out" ]; then
  echo "ERROR: Build failed, out/ directory not found"
  exit 1
fi

# Copy static data to out directory
echo "Copying static data..."
cp -r public/data out/

# Copy PWA assets
cp public/manifest.json out/
cp public/sw.js out/
cp public/icon.svg out/
cp public/icon-192.png out/
cp public/icon-512.png out/
cp public/robots.txt out/ 2>/dev/null || true

echo "=== Build complete ==="
echo "Output: out/ directory"
