import { createFileRoute } from '@tanstack/react-router'
import { useSuspenseQuery } from '@tanstack/react-query'
import { apiTokensOptions } from '~/lib/queries'
import ApiTokenCard from '~/components/api-token/ApiTokenCard'
import CreateApiTokenDialog from '~/components/api-token/CreateApiTokenDialog'

export const Route = createFileRoute('/dashboard/api-tokens')({
  component: RouteComponent,
  loader: ({ context }) => {
    context.queryClient.prefetchQuery(apiTokensOptions())
  },
})

function RouteComponent() {
  const { data: apiTokens } = useSuspenseQuery(apiTokensOptions())

  return (
    <div>
      <div className="flex flex-col items-center md:items-start gap-4 mb-4 md:mb-8">
        <div>
          <h2 className="text-center md:text-left text-xl font-medium">
            Ваши API Токены
          </h2>
          <p className="text-sm text-center text-muted-foreground">
            Каждый из этих ключей предоставляет доступ к нашему сервису
          </p>
        </div>
        <CreateApiTokenDialog haveZeroTokens={apiTokens.length === 0} />
      </div>

      <div className="flex flex-row flex-wrap gap-2 md:gap-4">
        {apiTokens.map((apiToken) => (
          <ApiTokenCard
            className="max-w-[455px]"
            key={apiToken.id}
            apiToken={apiToken}
          />
        ))}
      </div>
    </div>
  )
}
