import { redirect } from "@tanstack/react-router";
import { createServerFn } from "@tanstack/react-start";

import { useAppSession } from "./session";
import { request } from "./client";

const authTelegramBot = async (hash: string) => {
  const response = await request("/auth/tgbot", {
    method: "POST",
    body: { hash },
  });

  const json = await response.json();

  if (response.status !== 200) {
    console.log("Error in API request", json);
    throw new Error("Response is not 200");
  }

  return json["token"];
};

export const loginFn = createServerFn({ method: "POST" })
  .inputValidator((hash: string) => hash)
  .handler(async ({ data }) => {
    const token = await authTelegramBot(data);

    if (token === null) {
      throw new Error("Authorization failed, empty token");
    }

    console.debug("User logged in successfully!");

    const session = await useAppSession();
    await session.update({ token });

    throw redirect({ to: "/home" });
  });

export const verifySession = createServerFn({ method: "GET" }).handler(
  async () => {
    const session = await useAppSession();

    if (!session.data.token) {
      throw redirect({ to: "/" });
    }

    return session.data.token;
  },
);

export const getSession = createServerFn({ method: "GET" }).handler(
  async () => {
    const session = await useAppSession();
    return session.data;
  },
);
