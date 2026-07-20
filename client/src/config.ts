export const siteConfig = {
  botUsername: import.meta.env.VITE_BOT_USERNAME || 'frag_api_bot',
  github:
    import.meta.env.VITE_REPOSITORY_URL ||
    'https://github.com/apelsynca/fragapi',
  docs: import.meta.env.VITE_DOCS_URL || 'https://docs.fragapi.com',
  telegramChat:
    import.meta.env.VITE_TELEGRAM_CHAT_URL || 'https://t.me/fragapichat',
  telegramChannel:
    import.meta.env.VITE_TELEGRAM_CHANNEL_URL || 'https://t.me/frag_api',
}
