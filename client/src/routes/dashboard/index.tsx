import { createFileRoute } from '@tanstack/react-router'
import Dashboard from '#/components/Dashboard'

export const Route = createFileRoute('/dashboard/')({
  component: () => <Dashboard className="flex flex-col gap-1.5 md:gap-2.5" />,
})
