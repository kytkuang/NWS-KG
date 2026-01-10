import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  server: {
    port: 3000,
    host: 'localhost',
    open: true,
    proxy: {
      // 配置代理，用于连接后端API
      '/api': {
        target: 'http://localhost:5005',  // Flask后端地址
        changeOrigin: true
      }
    }
  }
})