import { LanguagesIcon } from 'lucide-react'
import { Button } from '../ui/button'
import { getLocale, setLocale } from '~/paraglide/runtime'

export default function Header() {
  const locale = getLocale()

  return (
    <div className="py-4">
      <div>
        <Button
          variant="outline"
          size="icon-lg"
          onClick={() => {
            setLocale(locale === 'ru' ? 'en' : 'ru')
          }}
        >
          <LanguagesIcon />
        </Button>
      </div>
    </div>
  )
}
