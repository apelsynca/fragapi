import { Plus, Wallet } from "lucide-react";
import {
  toUserFriendlyAddress,
  useTonConnectUI,
  useTonWallet,
} from "@tonconnect/ui-react";

import { Button } from "../ui/button";
import { Popover, PopoverContent, PopoverTrigger } from "../ui/popover";
import { TopUp } from "./top-up";

const toShortAddress = (rawAddress: string) => {
  const userFriendly = toUserFriendlyAddress(rawAddress);

  return `${userFriendly.slice(0, 6)}...${userFriendly.slice(-4)}`;
};

export const TonWallet = () => {
  const [tonConnectUI] = useTonConnectUI();
  const wallet = useTonWallet();

  return wallet ? (
    <Popover>
      <PopoverTrigger>
        <Button variant="outline">
          <Wallet /> {toShortAddress(wallet.account.address)}
        </Button>
      </PopoverTrigger>
      <PopoverContent className="flex flex-col gap-4">
        <TopUp />
        <Button
          size="sm"
          variant="destructive"
          onClick={() => {
            tonConnectUI.disconnect();
          }}
        >
          Отключить
        </Button>
      </PopoverContent>
    </Popover>
  ) : (
    <Button variant="outline" onClick={() => tonConnectUI.openModal()}>
      <Plus /> Подключить кошелек
    </Button>
  );
};
