// Synthetic fixture: static Astro site with an absolute site URL.
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://docs.example.org',
  integrations: [sitemap()],
});
