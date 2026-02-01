import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'
import cssInjectedByJsPlugin from 'vite-plugin-css-injected-by-js'

export default defineConfig({
  plugins: [react(), cssInjectedByJsPlugin()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  build: {
    minify: false,
    outDir: "../src/pydgey/widget/dist",
    emptyOutDir: true,
    lib: {
      entry: "src/widget.tsx",
      name: "widget",
      fileName: "widget",
      formats: ["es"],
    },
    rollupOptions: {
      external: [], 
      output: {
          manualChunks: undefined,
      }
    }
  },
  define: {
    'process.env.NODE_ENV': '"production"'
  }
})
