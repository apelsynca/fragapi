export const siteConfig = {
  botUsername: process.env.VITE_BOT_USERNAME,
  github: process.env.VITE_GITHUB_URL || 'https://github.com/apelsynca/fragapi',
  docs: process.env.VITE_DOCS_URL || 'https://docs.fragapi.com',
  telegramChat:
    process.env.VITE_TELEGRAM_CHAT_URL || 'https://t.me/fragapichat',
  telegramChannel:
    process.env.VITE_TELEGRAM_CHANNEL_URL || 'https://t.me/frag_api',
}
