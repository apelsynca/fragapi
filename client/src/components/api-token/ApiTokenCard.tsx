import { toast } from 'sonner'
import { ClipboardCopyIcon, TrashIcon } from 'lucide-react'
import { useServerFn } from '@tanstack/react-start'
import { deleteApiTokenFn } from '~/server/api-tokens'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import type { ApiToken } from '~/models/api-token'
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '../ui/card'
import { Button } from '../ui/button'

const ApiTokenCard = ({ apiToken }: { apiToken: ApiToken }) => {
  const queryClient = useQueryClient()

  const deleteApiToken = useServerFn(deleteApiTokenFn)
  const deleteTokenMutation = useMutation({
    mutationFn: () => deleteApiToken({ data: apiToken.id }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['api-tokens'] })
      toast.success('API Токен удален!')
    },
  })

  return (
    <Card className="max-w-108">
      <CardHeader>
        <CardTitle>{apiToken.name}</CardTitle>
        <CardDescription>
          Активен до: <span className="text-white">Бесконечно</span>
        </CardDescription>
      </CardHeader>
      <CardContent className="flex flex-col gap-2">
        <div className="flex gap-2">
          <div
            className="max-w-full flex items-center rounded-lg bg-muted pl-1 gap-1"
            onClick={() => {
              navigator.clipboard.writeText(apiToken.token)
              toast.success('Апи ключ скопирован')
            }}
          >
            <code className="relative rounded px-[0.3rem] py-[0.2rem] font-mono text-sm overflow-hidden text-ellipsis whitespace-nowrap">
              {apiToken.token}
            </code>
            <Button size="icon">
              <ClipboardCopyIcon />
            </Button>
          </div>
        </div>
      </CardContent>
      <CardFooter>
        <Button
          variant="destructive"
          onClick={() => deleteTokenMutation.mutateAsync()}
        >
          Удалить <TrashIcon />
        </Button>
      </CardFooter>
    </Card>
  )
}

export default ApiTokenCard
