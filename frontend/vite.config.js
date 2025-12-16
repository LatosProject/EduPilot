import JavaScriptObfuscator from 'javascript-obfuscator'
import { defineConfig } from 'vite'
import path from 'path'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  base: './',

  plugins: [
    vue({
      template: {
        compilerOptions: {
          isCustomElement: tag => tag.startsWith('mdui-')
        }
      }
    }),

    {
      name: 'js-obfuscator',
      apply: 'build',
      generateBundle(_, bundle) {
        for (const fileName in bundle) {
          const chunk = bundle[fileName]

          // ✅ 只混淆 JS chunk
          if (chunk.type !== 'chunk' || !fileName.endsWith('.js')) continue

          // ❗❗核心：直接跳过第三方库
          if (
            fileName.includes('node_modules') ||
            fileName.includes('vue') ||
            fileName.includes('mdui') ||
            fileName.includes('lit') ||
            fileName.includes('vendor')
          ) {
            continue
          }

          const result = JavaScriptObfuscator.obfuscate(
            chunk.code,
            {
              compact: true,

              // ❌ 必须关：否则 Vue / WebComponent 直接炸
              controlFlowFlattening: false,
              deadCodeInjection: false,
              selfDefending: false,

              // ✅ 安全项
              stringArray: true,
              stringArrayEncoding: ['base64'],
              stringArrayThreshold: 0.7,

              renameGlobals: false,
              identifierNamesGenerator: 'hexadecimal',
            }
          )

          chunk.code = result.getObfuscatedCode()
        }
      }
    }
  ],

  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },

  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: path => path.replace(/^\/api/, '/api'),
      },
    },
  },
})
