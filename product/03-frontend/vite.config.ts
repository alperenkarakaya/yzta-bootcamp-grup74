import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Dev sunucusu /api isteklerini Django'ya (8000) proxy'ler — CORS'suz geliştirme.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": "http://localhost:8000",
    },
  },
  build: { outDir: "dist" },
});
