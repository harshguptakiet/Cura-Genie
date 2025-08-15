import type { StorybookConfig } from "@storybook/react-vite"

const config: StorybookConfig = {
    stories: [
        "../src/**/*.mdx",
        "../src/**/*.stories.@(js|jsx|mjs|ts|tsx)",
        "../src/components/**/*.stories.@(js|jsx|mjs|ts|tsx)"
    ],
    addons: [
        "@storybook/addon-links",
        "@storybook/addon-essentials",
        "@storybook/addon-onboarding",
        "@storybook/addon-interactions",
        "@storybook/addon-a11y",
        "@storybook/addon-coverage",
        "@storybook/addon-docs",
        "@storybook/addon-controls",
        "@storybook/addon-viewport",
        "@storybook/addon-backgrounds",
        "@storybook/addon-measure",
        "@storybook/addon-outline",
    ],
    framework: {
        name: "@storybook/react-vite",
        options: {},
    },
    docs: {
        autodocs: "tag",
    },
    typescript: {
        check: false,
        reactDocgen: 'react-docgen-typescript',
        reactDocgenTypescriptOptions: {
            shouldExtractLiteralValuesFromEnum: true,
            propFilter: (prop) => (prop.parent ? !/node_modules/.test(prop.parent.fileName) : true),
        },
    },
    viteFinal: async (config) => {
        // Add any custom Vite config here
        return config
    },
}

export default config
