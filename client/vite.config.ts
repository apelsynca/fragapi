import { devtools } from '@tanstack/devtools-vite'
import { defineConfig } from 'vite'
import { nitro } from 'nitro/vite'
import viteReact from '@vitejs/plugin-react'
import { tanstackStart } from '@tanstack/react-start/plugin/vite'
import tailwindcss from '@tailwindcss/vite'

const config = defineConfig({
  server: {
    port: 3000,
  },
  resolve: { tsconfigPaths: true },
  plugins: [devtools(), tanstackStart(), tailwindcss(), nitro(), viteReact()],
  environments: {
    ssr: { build: { rollupOptions: { input: './server.ts' } } },
  },
})

export default config
