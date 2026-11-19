import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    environment: 'jsdom',
    // Use the browser storage supplied by jsdom, including on Node 26.
    execArgv: ['--no-experimental-webstorage'],
  },
})
