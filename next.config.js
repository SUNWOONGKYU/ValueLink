/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    domains: ['localhost'],
  },
  // Valuation_Company 폴더는 별도 프로젝트이므로 빌드에서 제외
  webpack: (config, { isServer }) => {
    config.module.rules.push({
      test: /\.tsx?$/,
      exclude: [
        /node_modules/,
        /Valuation_Company/,
      ],
    });
    return config;
  },
}

module.exports = nextConfig
