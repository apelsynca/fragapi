import { useServerFn } from '@tanstack/react-start'
import { toast } from 'sonner'
import { useState } from 'react'
import { Button } from './ui/button'
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from './ui/card'
import { Input } from './ui/input'
import { searchStarsRecipientFn, buyStarsFn } from '~/lib/stars'
import type { BaseRecipient } from '~/lib/models/recipient'
import { XIcon } from 'lucide-react'
import { HandBuyStarsDialog } from './HandBuyStarsDialog'

export const HandBuyStars = () => {
  const [recipient, setRecipient] = useState<null | BaseRecipient>(null)
  const [username, setUsername] = useState<string>('')
  const [quantity, setQuantity] = useState<string>('')

  const buyStars = useServerFn(buyStarsFn)
  const searchStarsRecipient = useServerFn(searchStarsRecipientFn)

  const handleCheckRecipient = async () => {
    if (username.length < 4) {
      toast.error('Введите юзернейм больше 3х символов')
      return
    }

    // check recipient
    try {
      const responseRecipient = await searchStarsRecipient({
        data: {
          username,
        },
      })
      setRecipient(responseRecipient)
    } catch (e: any) {
      toast.error(e.message)
    }
  }

  const handleBuy = async () => {
    const qNum = parseInt(quantity)

    if (isNaN(qNum)) {
      console.log('quantity is somehow NaN', quantity, qNum)
      return
    }

    try {
      const buyResp = await buyStars({
        data: { username, quantity: qNum },
      })

      toast.success(`Купил ${quantity} звезды для @${username}`, {
        description: `Хэш: ${buyResp.messageHash}`,
      })
    } catch (e: any) {
      toast.error(e.message)
    }
  }

  return (
    <Card className="w-full max-w-72">
      <CardHeader>
        <CardTitle>Купить звезды</CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col gap-2">
        {recipient ? (
          <div className="flex justify-between items-center font-semibold h-8 px-2.5 py-1 border rounded-lg">
            {recipient.name}
            <Button onClick={() => setRecipient(null)} size="icon-xs">
              <XIcon />
            </Button>
          </div>
        ) : (
          <Input
            placeholder="monk"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
        )}
        <Input
          placeholder="50"
          value={quantity}
          onChange={(e) => setQuantity(e.target.value)}
        />
      </CardContent>
      <CardFooter>
        {recipient === null ? (
          <Button className="w-full" onClick={handleCheckRecipient}>
            Проверить получателя
          </Button>
        ) : (
          <HandBuyStarsDialog
            username={username}
            recipient={recipient}
            quantity={quantity}
            onClick={handleBuy}
          />
        )}
      </CardFooter>
    </Card>
  )
}
