import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [sveltekit()],
  server: {
    proxy: {
      '/coins': 'http://127.0.0.1:8000',
      '/watchlist': 'http://127.0.0.1:8000'
    }
  },
  build: {
    outDir: 'build',
    assetsInlineLimit: 0  // force all icons/images to be emitted as separate files
  }
});
