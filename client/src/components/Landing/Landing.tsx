import Hero from './Hero'

export default function Landing({ toPanel = false }: { toPanel?: boolean }) {
  return (
    <main className="flex flex-col min-h-screen items-center gap-8 md:justify-between">
      <Hero
        title={'land.title'}
        description={'land.description'}
        className="w-full"
        toPanel={toPanel}
      />
    </main>
  )
}
