import vue from "@vitejs/plugin-vue";
import { defineConfig } from "vite";
import dts from "vite-plugin-dts";
import { fileURLToPath, URL } from "node:url"
import { resolve } from "path";
import vueDevTools from "vite-plugin-vue-devtools";
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
    plugins: [vue(), vueDevTools(), dts(), tailwindcss()],
    build: {
        lib: {
            entry: resolve(__dirname, "src/index.ts"),
            name: "score-component-lib",
            fileName: "score-component-lib"
        },
        rollupOptions: {
            external: ["vue"],
            output: {
                globals: {
                    vue: "Vue"
                }
            }
        }
    },
    resolve: {
        alias: {
            "@": fileURLToPath(new URL("./src", import.meta.url))
        }
    }
});
