import { Suspense } from 'react'
import { useTranslation } from 'react-i18next'
import { createFileRoute } from '@tanstack/react-router'
import TransactionsList from '~/components/transactions/TransactionsList'

export const Route = createFileRoute('/dashboard/transactions')({
  component: RouteComponent,
})

function RouteComponent() {
  const { t } = useTranslation()

  return (
    <div>
      <div className="mb-6 text-center">
        <h2 className="text-center font-semibold text-xl">
          {t('transactions')}
        </h2>
        <p className="text-muted-foreground text-sm">
          {t('transactions_desc')}
        </p>
      </div>
      <Suspense>
        <TransactionsList />
      </Suspense>
    </div>
  )
}
