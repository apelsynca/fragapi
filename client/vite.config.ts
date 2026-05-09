import { defineConfig } from 'vite'

import { tanstackStart } from '@tanstack/react-start/plugin/vite'

import viteReact from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { nitro } from 'nitro/vite'

const config = defineConfig({
  server: {
    port: 3000,
    allowedHosts: true,
  },
  resolve: { tsconfigPaths: true },
  plugins: [nitro(), tailwindcss(), tanstackStart(), viteReact()],
  environments: {
    ssr: { build: { rollupOptions: { input: './src/server.ts' } } },
  },
})

export default config
