import { useQuery } from "@tanstack/react-query";
import { createFileRoute } from "@tanstack/react-router";
import { ClipboardCopy } from "lucide-react";
import { toast } from "sonner";

import { Regenerate } from "~/components/api-keys/regenerate";
import { Button } from "~/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "~/components/ui/card";
import { meQueryOptions } from "~/lib/options/me";

export const Route = createFileRoute("/_panel/tonapi/api-keys")({
  component: APIKeysPage,
});

function APIKeysPage() {
  const { data: me } = useQuery(meQueryOptions());

  return (
    <div className="w-full max-w-[960px] mx-auto">
      <h1 className="scroll-m-20 text-4xl font-extrabold tracking-tight text-balance mb-16">
        API Ключи
      </h1>
      <Card className="max-w-[32rem]">
        <CardHeader>
          <CardTitle>API Ключ</CardTitle>
          <CardDescription>
            Секретный ключ для взаимодействия с Fragment API
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="bg-muted relative rounded-md font-mono text-sm flex justify-between items-center max-w-full">
            {me ? (
              <code className="px-4 py-2 truncate">{me.api_key}</code>
            ) : (
              "..."
            )}
            <Button
              onClick={() => {
                navigator.clipboard.writeText(me ? me.api_key : "");
                toast.success("API Ключ Скопирован!", {
                  richColors: true,
                });
              }}
            >
              <ClipboardCopy />
            </Button>
          </div>
          <div className="mt-4">
            <Regenerate />
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
