import { Button } from '~/components/ui/button'
import { RefreshCwIcon, TriangleAlertIcon } from 'lucide-react'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogMedia,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '~/components/ui/alert-dialog'

const RegenerateKeyDialog: React.FC<{ onClick?: () => void }> = ({
  onClick,
}) => (
  <AlertDialog>
    <AlertDialogTrigger asChild>
      <Button variant="destructive">
        Регенерировать <RefreshCwIcon />
      </Button>
    </AlertDialogTrigger>
    <AlertDialogContent size="sm">
      <AlertDialogHeader>
        <AlertDialogMedia className="bg-[#ff9966]/10 text-[#ff9966] dark:bg-[#ff9966]/20 dark:text-[#ff9966]">
          <TriangleAlertIcon />
        </AlertDialogMedia>
        <AlertDialogTitle>
          Вы точно хотите регенерировать API ключ?
        </AlertDialogTitle>
        <AlertDialogDescription>
          Вы получите новый API ключ, а ваш старый будет удален навсегда.
        </AlertDialogDescription>
      </AlertDialogHeader>
      <AlertDialogFooter>
        <AlertDialogCancel>Отмена</AlertDialogCancel>
        <AlertDialogAction variant="destructive" onClick={onClick}>
          Регенерировать
        </AlertDialogAction>
      </AlertDialogFooter>
    </AlertDialogContent>
  </AlertDialog>
)

export default RegenerateKeyDialog
