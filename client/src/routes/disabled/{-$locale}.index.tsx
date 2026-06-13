import { createFileRoute, redirect } from '@tanstack/react-router'

import en from '~/locales/en.json'
import ru from '~/locales/ru.json'

export const Route = createFileRoute('/disabled/{-$locale}/')({
  component: RouteComponent,
  loader: ({ params }) => {
    if (!params.locale || !['ru', 'en'].includes(params.locale)) {
      throw redirect({
        to: '/{-$locale}',
        params: { locale: 'en' },
      })
    }

    return {
      lang: params.locale,
    }
  },
})

function RouteComponent() {
  const { lang } = Route.useLoaderData()

  const locale = lang === 'en' ? en : ru

  return <div>{locale.land.title}</div>
}

// <Badge variant="outline" className="animate-appear">
//   <span className="text-muted-foreground">{t('land.badge')}</span>
// </Badge>
