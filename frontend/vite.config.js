import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0',  // чтобы Vite слушал все IP внутри контейнера
    port: 5173,        // должен совпадать с проброшенным портом
    strictPort: true   // чтобы не менять порт автоматически
  }
})
