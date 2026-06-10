import { createFileRoute, redirect } from '@tanstack/react-router'

export const Route = createFileRoute('/{-$locale}')({
  component: RouteComponent,
  loader: ({ params }) => {
    if (!params.locale || ['ru', 'en'].includes(params.locale)) {
      throw redirect({
        to: '/{-$locale}',
        params: { locale: 'ru' },
      })
    }

    return params.locale
  },
})

function RouteComponent() {
  const locale = Route.useLoaderData()

  return <div>{locale}</div>
}
