import { Button } from '~/components/ui/button'
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '~/components/ui/card'
import { fetchMe, revokeApiTokenFn } from '~/server/user'
import { createFileRoute, useRouter } from '@tanstack/react-router'
import {
  ClipboardCopyIcon,
  RefreshCwIcon,
  TriangleAlertIcon,
} from 'lucide-react'
import { toast } from 'sonner'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogMedia,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '~/components/ui/alert-dialog'
import { useMutation, useQueryClient } from '@tanstack/react-query'

const RegenerateKeyDialog: React.FC<{ onClick?: () => void }> = ({
  onClick,
}) => (
  <AlertDialog>
    <AlertDialogTrigger asChild>
      <Button variant="destructive">
        Регенерировать <RefreshCwIcon />
      </Button>
    </AlertDialogTrigger>
    <AlertDialogContent size="sm">
      <AlertDialogHeader>
        <AlertDialogMedia className="bg-[#ff9966]/10 text-[#ff9966] dark:bg-[#ff9966]/20 dark:text-[#ff9966]">
          <TriangleAlertIcon />
        </AlertDialogMedia>
        <AlertDialogTitle>
          Вы точно хотите регенерировать API ключ?
        </AlertDialogTitle>
        <AlertDialogDescription>
          Вы получите новый API ключ, а ваш старый будет удален навсегда.
        </AlertDialogDescription>
      </AlertDialogHeader>
      <AlertDialogFooter>
        <AlertDialogCancel>Отмена</AlertDialogCancel>
        <AlertDialogAction variant="destructive" onClick={onClick}>
          Регенерировать
        </AlertDialogAction>
      </AlertDialogFooter>
    </AlertDialogContent>
  </AlertDialog>
)

export const Route = createFileRoute('/dashboard/api-keys')({
  component: RouteComponent,
  loader: async () => {
    return await fetchMe()
  },
})

function RouteComponent() {
  const user = Route.useLoaderData()

  const router = useRouter()
  const queryClient = useQueryClient()

  const revokeApiToken = useMutation({
    mutationFn: () => revokeApiTokenFn(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users', 'me'] })
      toast.success('API Ключ был регенерирован')
      router.invalidate()
    },
    onError: () => {
      toast.error('Ошибка!')
    },
  })

  return (
    <div>
      <h2 className="text-lg mb-4">Апи ключи:</h2>
      <Card className="max-w-128">
        <CardHeader>
          <CardTitle>Ваш апи ключ</CardTitle>
          <CardDescription>Пока только этот:</CardDescription>
        </CardHeader>
        <CardContent className="flex">
          <div
            className="max-w-full flex items-center rounded-lg bg-muted pl-1 gap-1"
            onClick={() => {
              navigator.clipboard.writeText(user.apiKey)
              toast.success('Апи ключ скопирован')
            }}
          >
            <code className="relative rounded px-[0.3rem] py-[0.2rem] font-mono text-sm overflow-hidden text-ellipsis whitespace-nowrap">
              {user.apiKey}
            </code>
            <Button size="icon">
              <ClipboardCopyIcon />
            </Button>
          </div>
        </CardContent>
        <CardFooter>
          <RegenerateKeyDialog onClick={() => revokeApiToken.mutateAsync()} />
        </CardFooter>
      </Card>
    </div>
  )
}
