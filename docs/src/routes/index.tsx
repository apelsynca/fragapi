import { createFileRoute, redirect } from "@tanstack/react-router";

export const Route = createFileRoute("/")({
  component: RouteComponent,
  beforeLoad: () => {
    throw redirect({
      to: "/$lang",
      params: {
        lang: "ru",
      },
    });
  },
});

function RouteComponent() {
  return <div>You should not see this page...</div>;
}
