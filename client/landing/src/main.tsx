import { StrictMode } from 'react'
import { createRoot, hydrateRoot } from 'react-dom/client'
import App from './App'
import './styles/globals.css'
import './styles/utils.css'

const root = document.getElementById('root')!
const app = (
  <StrictMode>
    <App />
  </StrictMode>
)

if (root.querySelector('main')) {
  hydrateRoot(root, app)
} else {
  createRoot(root).render(app)
}
