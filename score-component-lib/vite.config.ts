import { resolve } from "node:path";
import { fileURLToPath, URL } from "node:url";
import tailwindcss from "@tailwindcss/vite";
import vue from "@vitejs/plugin-vue";
import { defineConfig } from "vite";
import dts from "vite-plugin-dts";
import vueDevTools from "vite-plugin-vue-devtools";

export default defineConfig({
    plugins: [vue(), vueDevTools(), dts(), tailwindcss()],
    build: {
        lib: {
            entry: resolve(import.meta.dirname, "src/index.ts"),
            name: "score-component-lib",
            fileName: "score-component-lib",
        },
        rollupOptions: {
            external: ["vue"],
            output: {
                globals: {
                    vue: "Vue",
                },
            },
        },
    },
    resolve: {
        alias: {
            "@": fileURLToPath(new URL("./src", import.meta.url)),
        },
    },
});
