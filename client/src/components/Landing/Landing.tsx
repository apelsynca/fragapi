import Hero from './Hero'
import { m } from '~/paraglide/messages'

export default function Landing({ toPanel = false }: { toPanel?: boolean }) {
  return (
    <main className="flex flex-col min-h-screen items-center gap-8 md:justify-between">
      <Hero
        title={m.land_title()}
        description={m.land_description()}
        className="w-full"
        toPanel={toPanel}
      />
    </main>
  )
}
