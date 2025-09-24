import { Link } from "@tanstack/react-router";
import { Button } from "../ui/button";
import { RefrigeratorIcon } from "lucide-react";

export function DefaultNotFound() {
  return (
    <div className="flex flex-col items-center gap-8 justify-center w-full h-screen">
      <div className="flex flex-col items-center gap-1">
        <RefrigeratorIcon size={48} />
        <h2 className="font-bold text-2xl">Не найдено</h2>
      </div>
      <Link to="/">
        <Button>На главную</Button>
      </Link>
    </div>
  );
}
