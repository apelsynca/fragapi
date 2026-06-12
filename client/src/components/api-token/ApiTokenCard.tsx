import { toast } from 'sonner'
import { ClipboardCopyIcon, TrashIcon } from 'lucide-react'
import { useServerFn } from '@tanstack/react-start'
import { deleteApiTokenFn } from '~/notserver/api-tokens'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import type { ApiToken } from '~/notserver/models/api-token'
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '../ui/card'
import { Button } from '../ui/button'
import { cn } from '~/lib/utils'

const ApiTokenCard = ({
  className,
  apiToken,
}: {
  className?: string
  apiToken: ApiToken
}) => {
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
    <Card className={cn('max-w-108', className)}>
      <CardHeader>
        <CardTitle>{apiToken.name}</CardTitle>
        <CardDescription>
          Активен до: <span className="text-white">Бесконечно</span>
        </CardDescription>
      </CardHeader>
      <CardContent className="flex flex-col gap-2">
        <div className="flex gap-2">
          <div
            className="[&_code]:blur-xs hover:[&_code]:blur-none max-w-full flex items-center rounded-lg bg-muted pl-1 gap-1"
            onClick={() => {
              navigator.clipboard.writeText(apiToken.token)
              toast.success('Апи ключ скопирован')
            }}
          >
            <code className="transition-all relative rounded mx-[0.3rem] my-[0.2rem] leading-none font-mono text-sm overflow-hidden text-ellipsis whitespace-nowrap">
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
