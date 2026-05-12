import { useServerFn } from '@tanstack/react-start'
import type { BaseRecipient } from '~/lib/models/recipient'
import { Button } from './ui/button'
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from './ui/dialog'

export const HandBuyStarsDialog: React.FC<{
  recipient: BaseRecipient
  quantity: string
  onClick: () => void
}> = ({ recipient, quantity, onClick }) => {
  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button disabled={!quantity} className="w-full">
          {quantity ? `Купить ${quantity} звезды` : 'Введите кол-во'}
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Вы уверенны?</DialogTitle>
          <DialogDescription>
            Что хотите купить {quantity} звезды для {recipient.name}?
          </DialogDescription>
        </DialogHeader>
        <DialogFooter>
          <DialogClose asChild>
            <Button variant="outline">Отмена</Button>
          </DialogClose>
          <Button onClick={onClick}>Да уверен</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
