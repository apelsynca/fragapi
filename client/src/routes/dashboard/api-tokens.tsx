import { createFileRoute } from '@tanstack/react-router'
import { useSuspenseQuery } from '@tanstack/react-query'
import CreateApiTokenDialog from '#/components/ApiTokens/CreateApiTokenDialog'
import { apiTokensOptions } from '#/lib/queries'
import ApiTokenCard from '#/components/ApiTokens/ApiTokenCard'
import { m } from '#/paraglide/messages'

export const Route = createFileRoute('/dashboard/api-tokens')({
  loader: ({ context }) => {
    context.queryClient.ensureQueryData(apiTokensOptions())
  },
  component: ApiTokensRouteComp,
})

function ApiTokensRouteComp() {
  const { data: apiTokens } = useSuspenseQuery(apiTokensOptions())

  return (
    <div>
      <div className="flex flex-col items-center md:items-start gap-4 mb-4 md:mb-8">
        <div>
          <h2 className="text-center md:text-left text-xl font-medium">
            {m.api_tokens_title()}
          </h2>
          <p className="text-sm text-center text-muted-foreground">
            {m.api_tokens_description()}
          </p>
        </div>
        <CreateApiTokenDialog haveZeroTokens={apiTokens.length === 0} />
      </div>

      <div className="flex flex-row flex-wrap gap-2 md:gap-4">
        {apiTokens.map((apiToken) => (
          <ApiTokenCard
            className="max-w-114"
            key={apiToken.id}
            apiToken={apiToken}
          />
        ))}
      </div>

      <p className="md:hidden mt-4 px-2 items-center [&_svg]:size-4 text-yellow-200/80 dark:text-yellow-500/80 text-xs">
        Не показывайте токены недоверенным лицам, токен дает доступ к покупкам!
      </p>
    </div>
  )
}
