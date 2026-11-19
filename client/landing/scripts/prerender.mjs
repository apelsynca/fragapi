import { mkdtemp, readFile, rm, writeFile } from 'node:fs/promises'
import { resolve } from 'node:path'
import { pathToFileURL } from 'node:url'
import { build } from 'vite'

// Keep the renderer beside the app so external dependencies resolve normally.
// Only the generated HTML and client assets are shipped in dist.
const rendererDirectory = await mkdtemp(resolve('.prerender-'))

try {
  await build({
    build: {
      ssr: 'src/entry-server.tsx',
      outDir: rendererDirectory,
    },
  })
  const { render } = await import(
    pathToFileURL(resolve(rendererDirectory, 'entry-server.js')).href
  )
  const htmlPath = resolve('dist/index.html')
  const template = await readFile(htmlPath, 'utf8')
  const marker = '<!--app-html-->'
  if (!template.includes(marker)) {
    throw new Error('Missing prerender marker in dist/index.html')
  }
  await writeFile(htmlPath, template.replace(marker, () => render()))
} finally {
  await rm(rendererDirectory, { recursive: true, force: true })
}
