import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '../ui/card'

export default function PaymentHistory() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>История пополнений</CardTitle>
        <CardDescription>История пополнений вашего баланса</CardDescription>
      </CardHeader>
      <CardContent>
        <div>
          <p>Hello world</p>
        </div>
      </CardContent>
      <CardFooter></CardFooter>
    </Card>
  )
}
