import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  typescript: {
    tsconfigPath: "./tsconfig.json"
  },
  experimental: {
    optimizePackageImports: ["@taghdisilabs/*"]
  }
};

export default nextConfig;
