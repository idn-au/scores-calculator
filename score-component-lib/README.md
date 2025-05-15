# Template for building your own Vue.js + TypeScript component library
A starter template for easily getting started with creating your own Vue.js component library with TypeScript.

## CSS
This template requires the consumer application to import the global CSS file from the component library (which is the default behaviour for Vite in library mode):

```typescript
// main.ts
import "vue-component-lib-template/vue-component-lib-template.css"
```

For injecting component styling into each component instead of importing a global CSS file, I recommend using [`vite-plugin-libcss`](https://github.com/wxsms/vite-plugin-libcss):

```typescript
// vite.config.ts
...
import libCss from "vite-plugin-libcss";

export default defineConfig({
    plugins: [vue(), vueDevTools(), dts(), libCss()],
...
```
