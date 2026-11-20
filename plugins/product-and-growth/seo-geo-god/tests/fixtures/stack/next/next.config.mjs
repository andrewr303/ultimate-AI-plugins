/** Synthetic fixture: static export of a Next.js App Router site. */
const nextConfig = {
  output: 'export',
  trailingSlash: true,
  env: {
    siteUrl: process.env.NEXT_PUBLIC_SITE_URL,
  },
};

export default nextConfig;
