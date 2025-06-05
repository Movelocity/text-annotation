import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, './src')
    }
  },
  base: '/',
  build: {
    outDir: 'dist',
    assetsDir: 'assets', // 将资源放在assets子目录
    sourcemap: true,     // 生成sourcemap以便调试
    emptyOutDir: true,   // 清空输出目录前排除已有文件
  }
})
