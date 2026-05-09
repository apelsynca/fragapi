export const seo = ({
  title,
  description_en,
  description_ru,
  keywords,
  image,
}: {
  title: string
  description_en?: string
  description_ru?: string
  image?: string
  keywords?: string
}) => {
  const tags = [
    { title },
    { name: 'description', lang: 'en', content: description_en },
    { name: 'description', lang: 'ru', content: description_ru },
    { name: 'keywords', content: keywords },
    { name: 'twitter:title', content: title },
    { name: 'twitter:description', content: description_en },
    { name: 'twitter:creator', content: '@homocitrus' },
    { name: 'twitter:site', content: '@homocitrus' },
    { name: 'og:title', content: title },
    { name: 'og:type', content: 'website' },
    { name: 'og:description', content: description_en },
    ...(image
      ? [
          { name: 'twitter:image', content: image },
          { name: 'twitter:card', content: 'summary_large_image' },
          { name: 'og:image', content: image },
        ]
      : []),
  ]

  return tags
}
