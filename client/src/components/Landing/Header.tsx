import { LanguagesIcon } from 'lucide-react'
import { getLocale, setLocale } from '#/paraglide/runtime'
import { Button } from '../ui/button'
// import { useTheme } from '../theme-provider'
// import { Tabs, TabsList, TabsTrigger } from '../ui/tabs'

// const HeaderThemeToggle = () => {
//   const { setTheme, theme } = useTheme()
//
//   return (
//     <Tabs
//       value={theme}
//       onValueChange={(value) => setTheme(value as 'light' | 'dark' | 'system')}
//     >
//       <TabsList>
//         <TabsTrigger value="light">Light</TabsTrigger>
//         <TabsTrigger value="dark">Dark</TabsTrigger>
//         <TabsTrigger value="system">System</TabsTrigger>
//       </TabsList>
//     </Tabs>
//   )
// }

const HeaderLanguageToggle = () => {
  const locale = getLocale()

  return (
    <Button
      variant="default"
      size="icon"
      onClick={() => {
        setLocale(locale === 'ru' ? 'en' : 'ru')
      }}
    >
      <LanguagesIcon />
    </Button>
  )
}

export default function Header() {
  return (
    <div className="pt-6 px-8 max-w-334 w-full">
      <div className="flex justify-end items-center gap-1.5">
        <HeaderLanguageToggle />
      </div>
    </div>
  )
}
