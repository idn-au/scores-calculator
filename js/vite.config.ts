import { resolve } from "node:path";
import { fileURLToPath, URL } from "node:url";
import { defineConfig } from "vite";
import dts from "vite-plugin-dts";

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [dts()],
    define: {
        __APP_VERSION__: JSON.stringify(process.env.npm_package_version),
    },
    resolve: {
        alias: {
            "@": fileURLToPath(new URL("./src", import.meta.url)),
        },
    },
    build: {
        lib: {
            entry: resolve(import.meta.dirname, "src/index.ts"),
            name: "scores-calculator-js",
            fileName: "scores-calculator-js",
        },
    },
});
