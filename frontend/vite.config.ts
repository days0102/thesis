import path from "path";
import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'

const pathSrc = path.resolve(__dirname, 'src')

import Unocss from 'unocss/vite'
import {
  presetAttributify,
  presetIcons,
  presetUno,
  transformerDirectives,
  transformerVariantGroup,
} from 'unocss'

// https://vitejs.dev/config/
export default defineConfig({
  server: {
    host: "0.0.0.0",
    port: 8082,
    open: false,
    https: false,
    proxy: {
      "/api": "http://localhost:5000/",
      // "/ws":{
      //   //webSocket代理
      //   target: 'ws://localhost:9999/', // 内网
      //   /*target: 'ws://服务器地址/ws', // 外网*/
      //   /*target: 'ws://服务器地址/ws',//本地测试*/
      //   ws:true,//开启ws, 如果是http代理此处可以不用设置
      //   changeOrigin: true,
      //   pathRewrite: {
      //     '^/ws': '/'
      //   },
      // },
    }
  },
  resolve: {
    alias: {
      '~/': `${pathSrc}/`,
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  css: {
    preprocessorOptions: {
      scss: {
        additionalData: `@use "~/styles/element/index.scss" as *;`,
      },
    },
  },
  plugins: [
    vue(),
    AutoImport({
      resolvers: [ElementPlusResolver({
        importStyle: 'sass',
      })],
    }),
    Components({
      resolvers: [ElementPlusResolver({
        importStyle: 'sass',
      })],
    }),


    Unocss({
      presets: [
        presetUno(),
        presetAttributify(),
        presetIcons({
          scale: 1.2,
          warn: true,
        }),
      ],
      transformers: [
        transformerDirectives(),
        transformerVariantGroup(),
      ]
    }),
  ],
})
