import { useMutation, useQueryClient } from '@tanstack/react-query'
import { createApiTokenFn } from '#/server-api/api-tokens'
import { useServerFn } from '@tanstack/react-start'
import { PlusIcon } from 'lucide-react'
import { Button } from '../ui/button'
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '../ui/dialog'
import { Field, FieldGroup, FieldLabel } from '../ui/field'
import { Input } from '../ui/input'
import { useState } from 'react'
import { toast } from 'sonner'
import { DatePicker } from './DatePicker'
import { m } from '#/paraglide/messages'

const CreateApiTokenDialog = ({
  haveZeroTokens,
}: {
  haveZeroTokens: boolean
}) => {
  const queryClient = useQueryClient()

  const [open, setOpen] = useState(false)

  const [name, setName] = useState<string>('')
  const [expiresAt, setExpiresAt] = useState<Date>()

  const createApiToken = useServerFn(createApiTokenFn)

  const createTokenMutation = useMutation({
    mutationFn: () => createApiToken({ data: { name, expiresAt } }),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ['api-tokens'],
      })
      toast.success('Создал апи токен')

      setName('')
      setExpiresAt(undefined)
    },
    onSettled: () => setOpen(false),
  })

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant={haveZeroTokens ? 'default' : 'secondary'}>
          <PlusIcon />{' '}
          {haveZeroTokens ? m.api_tokens_create() : m.api_tokens_add()}
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Создание API токена</DialogTitle>
        </DialogHeader>
        <div className="flex flex-col gap-2">
          <FieldGroup>
            <Field>
              <FieldLabel>Название</FieldLabel>
              <Input value={name} onChange={(e) => setName(e.target.value)} />
            </Field>
          </FieldGroup>
          <FieldGroup>
            <Field>
              <FieldLabel>Активен до</FieldLabel>
              <DatePicker date={expiresAt} setDate={setExpiresAt} />
            </Field>
          </FieldGroup>
        </div>
        <DialogFooter>
          <DialogClose asChild>
            <Button variant="outline">Отмена</Button>
          </DialogClose>
          <Button
            disabled={name.length < 3}
            onClick={async () => createTokenMutation.mutateAsync()}
          >
            {m.create()}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

export default CreateApiTokenDialog
