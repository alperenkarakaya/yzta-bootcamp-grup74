import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Dev sunucusu /api isteklerini Django'ya (8000) proxy'ler — CORS'suz geliştirme.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      // 127.0.0.1 (not "localhost"): avoids Node resolving to ::1 when the
      // Django dev server is only bound to the IPv4 loopback on some hosts.
      "/api": "http://127.0.0.1:8000",
    },
  },
  build: { outDir: "dist" },
});
