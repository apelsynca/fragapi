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
}> = ({ recipient, quantity, onClick }) => {
  const { t } = useTranslation()

  return (
    <Dialog>
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
