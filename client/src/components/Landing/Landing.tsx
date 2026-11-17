import CTA from './CTA'
import FAQ from './FAQ'
import Features from './Features'
import Footer from './Footer'
import Header from './Header'
import Hero from './Hero'
import HowItWorks from './HowItWorks'
import Pricing from './Pricing'
import Stats from './Stats'

export default function Landing({ toPanel = false }: { toPanel?: boolean }) {
  return (
    <main className="flex min-h-screen flex-col items-center">
      <Header toPanel={toPanel} />
      <Hero toPanel={toPanel} />
      <Stats />
      <Features />
      <HowItWorks />
      <Pricing toPanel={toPanel} />
      <FAQ />
      <CTA toPanel={toPanel} />
      <Footer />
    </main>
  )
}
