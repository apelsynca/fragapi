import { useServerFn } from '@tanstack/react-start'
import { toast } from 'sonner'
import { useState } from 'react'
import { Button } from './ui/button'
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from './ui/card'
import { Input } from './ui/input'
import { searchStarsRecipientFn } from '~/lib/stars'
import type { BaseRecipient } from '~/lib/models/recipient'
import { Avatar, AvatarImage } from './ui/avatar'

export const HandBuyStars = () => {
  const [recipient, setRecipient] = useState<null | BaseRecipient>(null)
  const [username, setUsername] = useState<string>('')
  const [quantity, setQuantity] = useState<string>('')

  const searchStarsRecipient = useServerFn(searchStarsRecipientFn)

  const handleCheckRecipient = async () => {
    if (username.length < 4) {
      toast.error('Введите юзернейм больше 3х символов')
      return
    }

    // check recipient
    const recipient = await searchStarsRecipient({
      data: {
        username,
      },
    })

    console.log(recipient)

    setRecipient(recipient)
  }

  return (
    <Card className="w-full max-w-72">
      <CardHeader>
        <CardTitle>Купить звезды</CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col gap-2">
        {recipient ? (
          <div className="font-semibold h-8 px-2.5 py-1 border rounded-lg">
            {recipient.name}
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
        <Button className="w-full" onClick={handleCheckRecipient}>
          Проверить получателя
        </Button>
      </CardFooter>
    </Card>
  )
}
