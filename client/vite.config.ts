import { defineConfig } from "vite";
import { tanstackStart } from "@tanstack/react-start/plugin/vite";
import viteReact from "@vitejs/plugin-react";
import { nitroV2Plugin } from "@tanstack/nitro-v2-vite-plugin";

export default defineConfig({
  server: {
    port: 3000,
    allowedHosts: true,
  },
  resolve: {
    tsconfigPaths: true,
  },
  plugins: [
    tanstackStart(),
    nitroV2Plugin({ preset: "bun", compatibilityDate: "latest" }),
    viteReact(),
  ],
});
