import { siteConfig } from '#/config'

export default function Footer() {
  return (
    <div className="w-full max-w-[640px] flex flex-col md:flex-row md:justify-between text-center pb-16">
      <h4 className="font-medium">FragAPI</h4>
      <div className="flex flex-col items-end gap-2">
        <a href={siteConfig.github} className="underline">
          GitHub
        </a>
        <a href={siteConfig.telegramChannel} className="underline">
          Telegram channel
        </a>
        <a href={siteConfig.telegramChat} className="underline">
          Telegram chat
        </a>
      </div>
    </div>
  )
}
