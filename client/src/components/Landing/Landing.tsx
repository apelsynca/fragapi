import FAQ from './FAQ'
import Footer from './Footer'
import Header from './Header'
import Hero from './Hero'
import { m } from '#/paraglide/messages'

export default function Landing({ toPanel = false }: { toPanel?: boolean }) {
  return (
    <main className="flex flex-col min-h-screen items-center md:justify-between">
      <Header />
      <Hero
        title={m.land_title()}
        description={m.land_description()}
        className="w-full"
        toPanel={toPanel}
      />
      <FAQ />
      <Footer />
    </main>
  )
}
