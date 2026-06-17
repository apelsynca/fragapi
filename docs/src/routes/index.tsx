import { HomeLayout } from "fumadocs-ui/layouts/home";
import { createFileRoute, Link } from "@tanstack/react-router";
import { baseOptions } from "@/lib/layout.shared";

export const Route = createFileRoute("/")({
  component: Home,
});

function Home() {
  return (
    <HomeLayout {...baseOptions()}>
      <div className="flex flex-col flex-1 justify-center px-4 py-8 text-center">
        <div className="mb-4 flex flex-col gap-1">
          <h1 className="font-medium text-xl ">Документация FragAPI</h1>
          <p className="text-center italic text-sm">
            Тут будет красивое оформление (надеюсь)
          </p>
        </div>
        <Link
          to="/docs/$lang/$"
          params={{
            lang: "ru",
            _splat: "",
          }}
          className="px-3 py-2 rounded-lg bg-fd-primary text-fd-primary-foreground font-medium text-sm mx-auto"
        >
          Открыть документацию
        </Link>
      </div>
    </HomeLayout>
  );
}
