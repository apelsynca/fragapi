import { toast } from 'sonner'
import { useState } from 'react'
import { LoaderIcon } from 'lucide-react'
import { useServerFn } from '@tanstack/react-start'
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
import { requestTonPayment as requestTonPaymentFn } from '#/lib/payments'

export default function BalanceTopUp() {
  const [tonConnectUI] = useTonConnectUI()
  const wallet = useTonWallet()

  const requestTonPayment = useServerFn(requestTonPaymentFn)

  const [amount, setAmount] = useState<string>('')
  const [loading, setLoading] = useState<boolean>(false)

  const handlePayment = async () => {
    if (wallet === null) {
      tonConnectUI.openModal()
      return
    }

    setLoading(true)

    const numAmount = parseFloat(amount)
    if (!amount || isNaN(numAmount) || numAmount < 0.1) {
      toast.error('Введите правильную сумму пополнения', {
        richColors: true,
      })
      return
    }

    try {
      const message = await requestTonPayment({ data: numAmount })

      await tonConnectUI.sendTransaction({
        messages: [message],
        validUntil: Math.floor(Date.now() / 1000) + 300,
        from: wallet.account.address,
      })
    } catch (e: any) {
      console.error(e)
      toast.error(e.message || 'Payment failed')
    } finally {
      setLoading(false)
    }
  }

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
            <Input
              id="amount-1"
              name="name"
              defaultValue="5"
              value={amount}
              onChange={(e) => {
                setAmount(e.target.value.replace(/[^0-9.]/g, ''))
              }}
            />
          </Field>
        </FieldGroup>
        <DialogFooter>
          <DialogClose asChild>
            <Button variant="outline">Отмена</Button>
          </DialogClose>
          <Button
            className="min-w-24"
            type="button"
            onClick={handlePayment}
            disabled={loading}
          >
            {loading ? <LoaderIcon /> : 'Пополнить'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
