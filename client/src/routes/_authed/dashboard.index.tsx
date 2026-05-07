import { fetchMe } from '#/lib/user'
import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/_authed/dashboard/')({
  component: RouteComponent,
  loader: async () => {
    return await fetchMe()
  },
})

function RouteComponent() {
  const user = Route.useLoaderData()

  return <div></div>
}
