import type { NextConfig } from "next";

const securityHeaders = [
  { key: "X-Content-Type-Options", value: "nosniff" },
  { key: "X-Frame-Options", value: "SAMEORIGIN" },
  { key: "X-DNS-Prefetch-Control", value: "on" },
  { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
  { key: "Permissions-Policy", value: "camera=(), microphone=(), geolocation=()" },
];

const nextConfig: NextConfig = {
  output: "standalone",
  compress: true,
  poweredByHeader: false,

  async headers() {
    return [{ source: "/(.*)", headers: securityHeaders }];
  },

  images: {
    remotePatterns: [
      { protocol: "https", hostname: "**.kontakt.az" },
      { protocol: "https", hostname: "**.irshad.az" },
      { protocol: "https", hostname: "**.w-t.az" },
      { protocol: "https", hostname: "**.bakuelectronics.az" },
    ],
  },
};

export default nextConfig;
