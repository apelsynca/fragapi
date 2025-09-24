import { useQueryClient } from "@tanstack/react-query";
import { useServerFn } from "@tanstack/react-start";
import { RefreshCcw } from "lucide-react";
import { toast } from "sonner";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "~/components/ui/alert-dialog";
import { Button } from "~/components/ui/button";
import { revokeApiToken as revokeApiTokenFn } from "~/lib/user";

export function Regenerate() {
  const revokeApiToken = useServerFn(revokeApiTokenFn);
  const queryClient = useQueryClient();

  return (
    <AlertDialog>
      <AlertDialogTrigger asChild>
        <Button variant="destructive">
          <RefreshCcw /> Регенерировать
        </Button>
      </AlertDialogTrigger>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Вы уверенны?</AlertDialogTitle>
          <AlertDialogDescription>
            Регенерацию API ключа нельзя отменить. Это действие навсегда удалит
            ваш текущий API ключ и создаст новый!
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>Отменить</AlertDialogCancel>
          <AlertDialogAction
            onClick={async () => {
              await revokeApiToken();
              queryClient.invalidateQueries({ queryKey: ["me"] });
              toast.warning("API ключ регенерирован");
            }}
          >
            Регенерировать
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
