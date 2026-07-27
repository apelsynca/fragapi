import { toast } from 'sonner'
import { TrashIcon } from 'lucide-react'
import { useServerFn } from '@tanstack/react-start'
import { deleteApiTokenFn } from '#/server-api/api-tokens'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import type { ApiToken } from '#/server-api/models/api-token'
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '../ui/card'
import { Button } from '../ui/button'
import { cn } from '#/lib/utils'
import { format } from 'date-fns'

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
          Активен до:{' '}
          <span className="text-white">
            {apiToken.expiresAt
              ? format(apiToken.expiresAt, 'dd.MM.yyyy')
              : 'Бесконечно'}
          </span>
        </CardDescription>
      </CardHeader>
      <CardContent className="flex flex-col gap-2">
        <div className="flex gap-2 hover:ring active:ring-gray-600 rounded-lg">
          <div
            className={cn(
              'md:[&_code]:text-transparent md:hover:[&_code]:text-foreground md:hover:[&_code]:bg-transparent',
              'max-w-full flex items-center rounded-lg bg-muted gap-1',
            )}
            onClick={() => {
              navigator.clipboard.writeText(apiToken.token)
              toast.success('Апи ключ скопирован')
            }}
          >
            <code
              className={cn(
                'transition-all relative rounded mx-2 my-1.5 leading-none',
                'font-mono text-sm overflow-hidden text-ellipsis whitespace-nowrap',
                'select-none leading-none md:bg-accent-foreground/80',
              )}
            >
              {apiToken.token}
            </code>
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
