import { Button } from '#/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '#/components/ui/card'
import { fetchMe } from '#/lib/user'
import { createFileRoute } from '@tanstack/react-router'
import { ClipboardCopyIcon } from 'lucide-react'
import { toast } from 'sonner'

export const Route = createFileRoute('/_authed/dashboard/api-keys')({
  component: RouteComponent,
  loader: async () => {
    return await fetchMe()
  },
})

function RouteComponent() {
  const user = Route.useLoaderData()

  return (
    <div>
      <h2 className="text-lg mb-4">Ваши апи ключи:</h2>
      <Card className="max-w-lg">
        <CardHeader>
          <CardTitle>Пока только этот:</CardTitle>
        </CardHeader>
        <CardContent className="flex">
          <code className="px-4 py-2 truncate">{user.apiKey}</code>
          <Button
            size="icon-lg"
            onClick={() => {
              navigator.clipboard.writeText(user.apiKey)
              toast.success('Апи ключ скопирован', {})
            }}
          >
            <ClipboardCopyIcon />
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}
