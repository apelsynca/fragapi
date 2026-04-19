import { redirect } from "@tanstack/react-router";
import { useAppSession } from "./session";

const defaultHeaders = {
  "Content-Type": "application/json",
};

interface RequestOptions {
  method?: "GET" | "POST" | "DELETE" | "PATCH";
  token?: string;
  headers?: HeadersInit;
  timeout?: number;
  body?: object;
}

export const request = async (url: string, options: RequestOptions = {}) => {
  const headers = options.headers || defaultHeaders;

  const response = await Promise.race<Response>([
    fetch(`${process.env.API_BASE_URL}${url}`, {
      method: options.method || "GET",
      headers: options.token
        ? { Authorization: `Bearer ${options.token}`, ...headers }
        : headers,
      body: options.body ? JSON.stringify(options.body) : undefined,
    }),
    new Promise((_, reject): undefined => {
      setTimeout(
        () => reject(new Error("Request timeout")),
        options.timeout || 3000,
      );
    }),
  ]);

  if (response.status === 401) {
    const session = await useAppSession();
    await session.update({
      token: undefined,
    });
    throw redirect({ to: "/" });
  }

  return response;
};
