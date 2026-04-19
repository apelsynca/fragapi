import { createServerFn } from "@tanstack/react-start";
import { verifySession } from "./auth";
import { request } from "./client";
import { type TokenRevoked, type User } from "./models/user";

export const fetchMe = createServerFn().handler(async () => {
  const token = await verifySession();
  const response = await request("/panel/users/me", {
    token,
  });

  const json = await response.json();
  if (response.status !== 200) {
    console.log("Error fetching user me", json);
    throw new Error("Error fetching user me");
  }

  return json as User;
});

export const revokeApiToken = createServerFn().handler(async () => {
  const token = await verifySession();
  const response = await request("/panel/users/revoke_api_token", {
    method: "POST",
    token,
  });

  const json = await response.json();
  if (response.status !== 200) {
    console.log("Error revoking api token", json);
    throw new Error("Error revoking api token");
  }

  return json as TokenRevoked;
});
