import { createFileRoute } from "@tanstack/react-router";
import { loginFn } from "~/lib/auth";

export type LoginSearch = {
  hash: string;
};

export const Route = createFileRoute("/login")({
  validateSearch: (search: Record<string, unknown>): LoginSearch => {
    return {
      hash: (search.hash as string) || "",
    };
  },
  component: LoginPage,
  loaderDeps: ({ search }) => {
    return { hash: search.hash };
  },
  loader: async ({ deps }) => {
    if (!deps.hash) return;

    await loginFn({ data: deps.hash });
  },
});

function LoginPage() {
  return (
    <div className="text-center">
      <h1>Ошибка авторизации :(</h1>
    </div>
  );
}
