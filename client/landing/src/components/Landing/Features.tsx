import {
  ChartColumnIcon,
  CrownIcon,
  GiftIcon,
  SendIcon,
  StarIcon,
  WalletIcon,
} from 'lucide-react'
import SectionHeading from './SectionHeading'

export default function Features() {
  const features = [
    {
      icon: StarIcon,
      title: 'Telegram Stars',
      text: 'Покупка звёзд любому пользователю по username — поштучно или сразу целым списком получателей.',
      chip: 'POST /v1/stars/buy',
    },
    {
      icon: CrownIcon,
      title: 'Telegram Premium',
      text: 'Оформление Premium по username с проверкой получателя перед покупкой.',
      chip: 'POST /v1/premium/buy',
    },
    {
      icon: GiftIcon,
      title: 'Подарки',
      text: 'Модели подарков: списки по коллекции и данные по конкретной модели.',
      chip: 'GET /v1/gifts/{short_name}/models',
    },
    {
      icon: WalletIcon,
      title: 'Пополнение в TON',
      text: 'Пополняйте баланс напрямую из кошелька или обычным переводом с memo.',
      chip: 'POST /v1/deposits/ton',
    },
    {
      icon: SendIcon,
      title: 'Логи в Telegram',
      text: 'Уведомление о каждой транзакции приходит в выбранный вами Telegram-чат.',
      chip: 'Telegram-бот',
    },
    {
      icon: ChartColumnIcon,
      title: 'Статистика',
      text: 'Баланс, расходы на Stars и Premium и история транзакций — в панели и через API.',
      chip: 'GET /v1/transactions',
    },
  ]

  return (
    <section className="w-full px-4 pt-20 sm:pt-32">
      <div className="mx-auto flex max-w-280 flex-col gap-14">
        <SectionHeading
          eyebrow="Возможности"
          title="Всё, что нужно от Fragment"
          subtitle="Один API для покупок, пополнений и аналитики — без ручной работы в интерфейсе Fragment."
        />
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {features.map(({ icon: Icon, title, text, chip }) => (
            <div
              key={title}
              className="border-border flex flex-col items-start gap-5 rounded-2xl border bg-white/3 p-7"
            >
              <div className="bg-brand/12 text-brand flex size-11 items-center justify-center rounded-xl">
                <Icon className="size-5" />
              </div>
              <div className="flex flex-col gap-2">
                <h3 className="text-xl leading-7 font-semibold">{title}</h3>
                <p className="text-muted-foreground text-[15px] leading-6">
                  {text}
                </p>
              </div>
              <code className="text-muted-foreground rounded-md bg-white/5 px-2 py-1 font-mono text-xs leading-4">
                {chip}
              </code>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
