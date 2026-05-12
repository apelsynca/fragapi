import type { BaseRecipient } from '~/server/models/recipient'
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
import { useTranslation } from 'react-i18next'

export const HandBuyStarsDialog: React.FC<{
  recipient: BaseRecipient
  quantity: string
  onClick: () => void
  onOpenChange: (open: boolean) => void
  open: boolean
}> = ({ recipient, quantity, onClick, onOpenChange, open }) => {
  const { t } = useTranslation()

  return (
    <Dialog onOpenChange={onOpenChange} open={open}>
      <DialogTrigger asChild>
        <Button disabled={!quantity} className="w-full">
          {quantity ? t('hand.buy', { quantity }) : 'Введите кол-во'}
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
            <Button variant="outline">{t('cancel')}</Button>
          </DialogClose>
          <Button onClick={onClick}>{t('iamsure')}</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
