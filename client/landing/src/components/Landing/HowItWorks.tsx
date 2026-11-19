import SectionHeading from './SectionHeading'

const dim = 'text-muted-foreground'
const str = 'text-brand'
const accent = 'text-brand-foreground'

function CodeWindow() {
  return (
    <div className="group/window border-border bg-background w-full min-w-0 flex-1 overflow-hidden rounded-2xl border shadow-[0_24px_64px_-16px_rgba(0,0,0,0.35)]">
      <div className="bg-white/3">
        <div className="flex items-center justify-between px-4 py-3.5">
          <div className="flex gap-2">
            <span className="size-2.5 rounded-full bg-white/14 transition-colors duration-200 group-hover/window:bg-[#ff5f57]" />
            <span className="size-2.5 rounded-full bg-white/14 transition-colors duration-200 group-hover/window:bg-[#febc2e]" />
            <span className="size-2.5 rounded-full bg-white/14 transition-colors duration-200 group-hover/window:bg-[#28c840]" />
          </div>
          <p className={`${dim} font-mono text-xs leading-4`}>
            POST /v1/stars/buy
          </p>
        </div>
        <pre className="border-border overflow-x-auto border-t p-6 font-mono text-[13px] leading-6">
          <span className={accent}>curl</span>
          <span className={dim}> -X</span> POST
          https://api.fragapi.com/v1/stars/buy <span className={dim}>\</span>
          {'\n  '}
          <span className={dim}>-H</span>
          <span className={str}>
            &quot;Authorization: Bearer $FRAGAPI_TOKEN&quot;
          </span>
          <span className={dim}>\</span>
          {'\n  '}
          <span className={dim}>-H</span>
          <span className={str}>
            &quot;Content-Type: application/json&quot;
          </span>
          <span className={dim}>\</span>
          {'\n  '}
          <span className={dim}>-d</span>
          <span className={str}>
            {`'{"username": "synca", "quantity": 50}'`}
          </span>
        </pre>
        <div className="border-border flex flex-col gap-3 border-t px-6 pt-5 pb-6">
          <div className="flex items-center gap-2">
            <span className="size-2 rounded-full bg-green-400" />
            <p className={`${dim} font-mono text-xs leading-4`}>200 OK</p>
          </div>
          <pre className="overflow-x-auto font-mono text-[13px] leading-6">
            {'{\n  "transactionId": '}
            <span className={str}>
              &quot;8f14e45f-ceea-467f-a0e6-1b2c3d4e5f60&quot;
            </span>
            {',\n  "name": '}
            <span className={str}>&quot;Synca&quot;</span>
            {',\n  "amount": '}
            <span className={accent}>0.39</span>
            {',\n  "messageHash": '}
            <span className={str}>&quot;a3f9c1…&quot;</span>
            {'\n}'}
          </pre>
        </div>
      </div>
    </div>
  )
}

export default function HowItWorks() {
  const steps = [
    {
      title: 'Войдите через бота',
      text: 'Авторизация в один клик через Telegram — без паролей, KYC и seed фраз.',
    },
    {
      title: 'Пополните баланс',
      text: 'Переведите TON со своего кошелька — средства зачислятся автоматически.',
    },
    {
      title: 'Создайте токен и отправьте запрос',
      text: 'Токен выпускается в панели. Дальше — обычный HTTP-запрос с заголовком Authorization.',
    },
  ]

  return (
    <section className="w-full px-4 pt-20 sm:pt-32">
      <div className="mx-auto flex max-w-280 flex-col gap-12 lg:flex-row lg:items-center lg:gap-16">
        <div className="flex flex-col gap-10 lg:w-115 lg:shrink-0">
          <SectionHeading
            align="start"
            eyebrow="Как это работает"
            title="Первый запрос — за три шага"
          />
          <ol className="flex flex-col gap-7">
            {steps.map((step, index) => (
              <li key={step.title} className="flex gap-4">
                <span className="border-border text-brand flex size-9 shrink-0 items-center justify-center rounded-full border bg-white/4 text-sm font-medium">
                  {index + 1}
                </span>
                <div className="flex flex-col gap-1 pt-1">
                  <h3 className="text-lg leading-7 font-semibold">
                    {step.title}
                  </h3>
                  <p className="text-muted-foreground text-[15px] leading-6">
                    {step.text}
                  </p>
                </div>
              </li>
            ))}
          </ol>
        </div>
        <CodeWindow />
      </div>
    </section>
  )
}
