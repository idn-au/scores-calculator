import antfu from "@antfu/eslint-config";

export default antfu(
    {
        vue: true,
        typescript: true,
        pnpm: false,
        yaml: false,
        stylistic: {
            indent: 4,
            quotes: "double",
            semi: true,
        },
        formatters: {
            css: true,
        },
    },
    {
        rules: {
            "vue/block-order": ["error", {
                order: ["script", "template", "style"],
            }],
            "vue/attribute-hyphenation": ["error", "never", {
                ignore: ["custom-prop"],
            }],
        },
    },
);
