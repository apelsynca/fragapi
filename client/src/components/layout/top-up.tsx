"use client";

import "~/polyfils";

import { PlusIcon } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";
import { SendTransactionRequest, useTonConnectUI } from "@tonconnect/ui-react";
import { comment as getCommentPayload, toNano } from "@ton/core";

import { Button } from "../ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTrigger,
} from "../ui/dialog";
import { Input } from "../ui/input";
import { useQuery } from "@tanstack/react-query";
import { meQueryOptions } from "~/lib/options/me";

const getTopUpTransaction = (
  amount: number,
  comment: string,
): SendTransactionRequest => {
  return {
    validUntil: Date.now() + 10 * 60 * 1000, // 10 mins
    messages: [
      {
        address: "UQAYDwZmrOOI0kOh0cd4emo7NxlDPqKiDvAVwR-Gom2xJvPQ",
        amount: toNano(amount).toString(),
        payload: getCommentPayload(comment).toBoc().toBase64(),
      },
    ],
  };
};

export const TopUp = () => {
  const [open, setOpen] = useState<boolean>(false);
  const [amount, setAmount] = useState<string>("");
  const [tonConnectUI] = useTonConnectUI();
  const { data: me } = useQuery(meQueryOptions());

  const handleTopUpClick = () => {
    if (!me) return;

    const numAmount = parseFloat(amount);
    if (!amount || isNaN(numAmount) || numAmount < 0.1) {
      toast.error("Введите правильную сумму пополнения", {
        richColors: true,
      });
      return;
    }

    const transaction = getTopUpTransaction(numAmount, me.id.toString());
    tonConnectUI.sendTransaction(transaction);
    setOpen(false);
  };

  return (
    <Dialog open={open} onOpenChange={(open) => setOpen(open)}>
      <DialogTrigger>
        <Button size="sm">
          <PlusIcon /> Пополнить
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>Пополнение баланса</DialogHeader>
        <div className="flex flex-col gap-4">
          <Input
            placeholder="100.00"
            value={amount}
            onChange={(e) => {
              setAmount(e.target.value.replace(/[^0-9.]/g, ""));
            }}
          />
          <Button
            disabled={isNaN(parseFloat(amount)) || parseFloat(amount) === 0}
            onClick={handleTopUpClick}
          >
            <PlusIcon /> Пополнить
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
};
