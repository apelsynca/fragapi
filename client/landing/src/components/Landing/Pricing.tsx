import { CheckIcon } from 'lucide-react'
import { GithubButton, LoginButton } from './LandingActions'
import SectionHeading from './SectionHeading'
import { cn } from '#/lib/utils'

interface PlanProps {
  name: string
  pill: string
  price: string
  priceNote: string
  text: string
  items: string[]
  action: React.ReactNode
  recommended?: boolean
}

function Plan({
  name,
  pill,
  price,
  priceNote,
  text,
  items,
  action,
  recommended = false,
}: PlanProps) {
  return (
    <div
      className={cn(
        'flex w-full max-w-110 flex-col gap-6 rounded-[20px] border p-8',
        recommended
          ? 'border-brand/40 from-brand/12 bg-white/2.5 bg-linear-to-b to-transparent to-60%'
          : 'border-border bg-white/3',
      )}
    >
      <div className="flex flex-wrap items-center justify-between gap-2">
        <p className="font-medium">{name}</p>
        <span
          className={cn(
            'rounded-full px-2.5 py-0.5 text-xs leading-5 font-medium',
            recommended
              ? 'bg-brand/14 text-brand'
              : 'border-border text-muted-foreground border bg-white/6',
          )}
        >
          {pill}
        </span>
      </div>
      <div className="flex flex-wrap items-baseline gap-x-2.5">
        <p className="text-[56px] leading-16 font-semibold tracking-[-0.03em]">
          {price}
        </p>
        <p className="text-muted-foreground text-[15px] leading-6">
          {priceNote}
        </p>
      </div>
      <p className="text-muted-foreground text-[15px] leading-6">{text}</p>
      <div className="bg-border h-px w-full" />
      <ul className="flex flex-col gap-3">
        {items.map((item) => (
          <li key={item} className="flex items-center gap-2.5">
            <CheckIcon className="text-brand size-5 shrink-0" />
            <span className="text-[15px] leading-6">{item}</span>
          </li>
        ))}
      </ul>
      <div className="mt-auto">{action}</div>
    </div>
  )
}

export default function Pricing() {
  return (
    <section className="w-full px-4 pt-20 sm:pt-32">
      <div className="mx-auto flex max-w-280 flex-col items-center gap-14">
        <SectionHeading
          eyebrow="Тарифы"
          title="Платите только за транзакции"
          subtitle="Никаких подписок и скрытых платежей. Или разверните сервис у себя — бесплатно."
        />
        <div className="flex w-full flex-col items-center justify-center gap-6 md:flex-row md:items-stretch">
          <Plan
            recommended
            name="Облако"
            pill="Рекомендуем"
            price="1.8%"
            priceNote="с каждой транзакции"
            text="Готовый сервис на fragapi.com. Мы следим за инфраструктурой — вы отправляете запросы."
            items={[
              'Старт за пару минут',
              'Панель со статистикой и API токенами',
              'Логи транзакций в Telegram',
              '+ сетевая комиссия ≈ $0.001',
            ]}
            action={<LoginButton className="w-full" />}
          />
          <Plan
            name="Self-hosted"
            pill="VPS, домен и прочее ≈ $40/мес"
            price="0%"
            priceNote="комиссии сервиса"
            text="Разверните FragAPI на своём сервере. Весь код открыт под лицензией MIT."
            items={[
              'Полный контроль над инфраструктурой',
              'Тот же API и та же панель',
              'Открытый исходный код',
              '+ сетевая комиссия ≈ $0.001',
            ]}
            action={<GithubButton label="Открыть GitHub" className="w-full" />}
          />
        </div>
      </div>
    </section>
  )
}
