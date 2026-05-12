import { createFileRoute } from '@tanstack/react-router'
import { HandBuyStars } from '~/components/HandBuyStars'

export const Route = createFileRoute('/dashboard/hand')({
  component: RouteComponent,
})

function RouteComponent() {
  return (
    <div className="flex flex-col items-center md:flex-row gap-4">
      <HandBuyStars />
    </div>
  )
}
