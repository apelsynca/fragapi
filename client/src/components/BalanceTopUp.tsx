import { useTonConnectUI, useTonWallet } from '@tonconnect/ui-react'
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
import { Field, FieldGroup } from './ui/field'
import { Input } from './ui/input'
import { Label } from './ui/label'

export default function BalanceTopUp() {
  const [tonConnectUI] = useTonConnectUI()
  const wallet = useTonWallet()

  console.log(wallet)

  if (wallet === null) {
    return (
      <Button onClick={() => tonConnectUI.openModal()} className="w-full">
        Подключить кошелек
      </Button>
    )
  }

  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button className="w-full">Пополнить баланс</Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Пополнение баланса</DialogTitle>
          <DialogDescription>
            Пополнение баланса с кошелька TON
          </DialogDescription>
        </DialogHeader>
        <FieldGroup>
          <Field>
            <Label htmlFor="amount-1">Сумма</Label>
            <Input id="amount-1" name="name" defaultValue="3" />
          </Field>
        </FieldGroup>
        <DialogFooter>
          <DialogClose asChild>
            <Button variant="outline">Отмена</Button>
          </DialogClose>
          <Button>Пополнить</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
