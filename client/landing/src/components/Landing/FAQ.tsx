import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '#/components/ui/accordion'
import { Section } from '#/components/ui/section'
import { siteConfig } from '#/config'

export default function FAQ() {
  const items = [
    {
      question: 'Как автоматизировать покупку Telegram Stars?',
      answer:
        'Создайте API-токен в панели FragAPI и пополните баланс в TON. Отправьте запрос POST /v1/stars/buy с username получателя и количеством звёзд. Так можно встроить автоматическую покупку Telegram Stars в своего бота, магазин или сервис без ручной работы в интерфейсе Fragment.',
    },
    {
      question: 'Можно ли автоматически покупать Telegram Premium через API?',
      answer:
        'Да. Fragment API позволяет оформить Telegram Premium по username через запрос POST /v1/premium/buy. Перед покупкой проверяется получатель, а историю транзакций можно посмотреть в панели или получить через API.',
    },
    {
      question: 'Что такое Fragment API и для чего он нужен?',
      answer:
        'FragAPI — сервис с открытым исходным кодом для автоматизации Fragment. Через HTTP API можно покупать Telegram Stars и Telegram Premium, проверять баланс и получать историю транзакций. Подключите API к своему приложению или разверните FragAPI на своём сервере.',
    },
    {
      question: 'Почему FragAPI?',
      answer:
        'Полная автоматизация Fragment через API: не нужен KYC, низкая комиссия 1.8%, открытый исходный код, статистика, оповещения и многое другое.',
    },
    {
      question: 'Берёт ли сервис комиссию?',
      answer:
        'Да, 1.8% с каждой транзакции: с покупок на 1000 USD мы забираем 18 USD. При self-hosted комиссии сервиса нет. Сетевая комиссия ≈ $0.001 за транзакцию есть в обоих случаях.',
    },
    {
      question: 'Как пополнить баланс?',
      answer:
        'Переведите TON напрямую из подключённого кошелька в панели или обычным переводом с memo. Средства зачисляются автоматически.',
    },
    {
      question: 'Нужно ли проходить KYC или вводить seed фразу?',
      answer:
        'Нет. Вход выполняется через Telegram-бота, а баланс пополняется переводом TON — ни документы, ни seed фраза не нужны.',
    },
    {
      question: 'Можно ли развернуть FragAPI у себя?',
      answer:
        'Да. Весь код открыт под лицензией MIT: разверните FragAPI на своём сервере и пользуйтесь тем же API и той же панелью без комиссии сервиса.',
    },
  ]

  return (
    <Section className="w-full py-20">
      <div className="max-w-container mx-auto flex flex-col items-center gap-8">
        <h2 className="text-center text-3xl font-semibold tracking-[-0.02em] sm:text-5xl sm:leading-14">
          Вопросы и ответы
        </h2>
        <div className="flex w-full max-w-190 flex-col gap-6">
          <Accordion type="single" collapsible>
            {items.map((item, index) => (
              <AccordionItem key={item.question} value={`item-${index + 1}`}>
                <AccordionTrigger className="items-center py-4.5 text-base">
                  {item.question}
                </AccordionTrigger>
                <AccordionContent forceMount className="in-data-[state=closed]:hidden">
                  <p className="text-muted-foreground max-w-160 pb-2 text-[15px] leading-6">
                    {item.answer}
                  </p>
                </AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
          <p className="text-muted-foreground text-center text-sm">
            Смело задавайте интересующие вас вопросы или предложения в наш
            <a
              className="text-foreground font-medium"
              href={siteConfig.telegramChat}
            >
              телеграмм чат!
            </a>
          </p>
        </div>
      </div>
    </Section>
  )
}
