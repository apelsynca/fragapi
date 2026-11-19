import { LoaderCircleIcon, SendIcon } from 'lucide-react'
import { messageHash, purchaseAt, transactionId } from './demoState'
import type { DemoState } from './demoState'
import { Button } from '#/components/ui/button'
import { Card } from '#/components/ui/card'

const dim = 'text-muted-foreground'
const str = 'text-brand'
const num = 'text-brand-foreground'

function Field({
  name,
  value,
  last = false,
}: {
  name: string
  value: string | number
  last?: boolean
}) {
  return (
    <>
      {`  "${name}": `}
      {typeof value === 'number' ? (
        <span className={num}>{value}</span>
      ) : (
        <span className={str}>&quot;{value}&quot;</span>
      )}
      {last ? '\n' : ',\n'}
    </>
  )
}

/** The request the demo is about to send, and the response it got back. */
export default function DemoApiPanel({
  state,
  onSend,
}: {
  state: DemoState
  onSend: () => void
}) {
  const purchase = purchaseAt(state.step)
  const isStars = purchase.kind === 'stars'
  const isIdle = state.phase === 'idle'

  return (
    <Card className="hidden w-76 shrink-0 gap-0 self-start py-0 lg:flex">
      <div className="flex items-center gap-2 border-b px-4 py-3 font-mono text-xs">
        <span className="rounded bg-green-400/10 px-1.5 py-0.5 font-medium text-green-400">
          POST
        </span>
        <span className="truncate">/v1/{purchase.kind}/buy</span>
      </div>
      <pre
        key={state.step}
        className="animate-in fade-in px-4 py-3 font-mono text-[13px] leading-6 duration-300"
      >
        {'{\n'}
        <Field name="username" value={purchase.username} />
        <Field
          name={isStars ? 'quantity' : 'months'}
          value={purchase.quantity}
          last
        />
        {'}'}
      </pre>
      <div className="px-4 pb-4">
        <Button
          className="w-full"
          aria-disabled={!isIdle}
          onClick={isIdle ? onSend : undefined}
        >
          {state.phase === 'sending' ? (
            <LoaderCircleIcon className="animate-spin" />
          ) : (
            <SendIcon />
          )}
          Отправить запрос
        </Button>
      </div>
      <div
        className="flex min-h-47 flex-col gap-2 border-t px-4 py-3"
        aria-live="polite"
      >
        {state.phase === 'done' ? (
          <div className="animate-in fade-in slide-in-from-bottom-1 flex flex-col gap-2 duration-300">
            <p className={`${dim} flex items-center gap-2 font-mono text-xs`}>
              <span className="size-2 rounded-full bg-green-400" />
              200 OK
            </p>
            <pre className="overflow-hidden font-mono text-[13px] leading-6">
              {'{\n'}
              <Field
                name="transactionId"
                value={`${transactionId(state.step).slice(0, 13)}…`}
              />
              <Field name="name" value={purchase.name} />
              <Field name="amount" value={purchase.amount} />
              <Field name="messageHash" value={messageHash(state.step)} last />
              {'}'}
            </pre>
          </div>
        ) : (
          <p className={`${dim} flex items-center gap-2 font-mono text-xs`}>
            <span
              className={
                isIdle
                  ? 'bg-muted-foreground/40 size-2 rounded-full'
                  : 'bg-brand size-2 animate-pulse rounded-full'
              }
            />
            {isIdle ? 'Ожидание запроса' : 'Отправка…'}
          </p>
        )}
      </div>
    </Card>
  )
}
