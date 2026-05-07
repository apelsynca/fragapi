import { Button } from '#/components/ui/button'
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '#/components/ui/card'
import { Input } from '#/components/ui/input'
import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/_authed/dashboard/hand')({
  component: RouteComponent,
})

function RouteComponent() {
  return (
    <div className="flex flex-col md:flex-row gap-4">
      <Card className="w-full">
        <CardHeader>
          <CardTitle>Купить звезды</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col gap-2">
          <Input placeholder="monk" />
          <Input placeholder="50" />
        </CardContent>
        <CardFooter>
          <Button>Проверить получателя</Button>
        </CardFooter>
      </Card>
      <Card className="w-full">
        <CardHeader>
          <CardTitle>Подарить премиум</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col gap-2">
          <Input placeholder="monk" />
          <div>selector</div>
        </CardContent>
        <CardFooter>
          <Button>Проверить получателя</Button>
        </CardFooter>
      </Card>
    </div>
  )
}
