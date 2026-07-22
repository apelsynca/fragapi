import { HomeLayout } from "fumadocs-ui/layouts/home";
import { createFileRoute, Link } from "@tanstack/react-router";
import { baseOptions } from "@/lib/layout.shared";

export const Route = createFileRoute("/$lang/")({
  component: Home,
});

function Home() {
  const { lang } = Route.useParams();

  return (
    <HomeLayout {...baseOptions(lang)}>
      <div className="flex flex-col flex-1 justify-center px-4 py-8 text-center">
        <div className="mb-4 flex flex-col gap-1">
          <h1 className="font-semibold text-2xl">
            {lang === "ru" ? "Документация FragAPI" : "FragAPI Documentation"}
          </h1>
          <p className="text-center italic text-xs">
            {lang === "ru"
              ? "Тут будет красивое оформление скоро (надеемся)"
              : "Here will be a nice animated page soon (we hope)"}
          </p>
        </div>
        <Link
          to="/$lang/docs/$"
          params={{
            lang: lang,
            _splat: "",
          }}
          className="px-3 py-2 rounded-lg bg-fd-primary text-fd-primary-foreground font-medium text-sm mx-auto"
        >
          {lang === "ru" ? "Открыть документацию" : "Open docs"}
        </Link>
      </div>
    </HomeLayout>
  );
}
