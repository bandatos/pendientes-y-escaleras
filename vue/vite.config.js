import { fileURLToPath, URL } from "node:url";
import dsv from "@rollup/plugin-dsv";

import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import vueDevTools from "vite-plugin-vue-devtools";

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue(), vueDevTools(), dsv()],
  server: {
    host: '0.0.0.0',
    allowedHosts: true,
    port: 5174,
  },
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
});
