// vite.config.js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      // React 개발 서버에서 "/api"로 들어오는 요청은
      // Flask 서버(EC2의 IP)로 프록시한다.
      '/api': {
        target: 'http://172.31.37.242:5000', // 👉 EC2 내부 IP나 퍼블릭 IP
        changeOrigin: true,
        secure: false,
      },
    },
  },
})
