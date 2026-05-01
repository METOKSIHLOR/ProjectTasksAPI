import { reactive, watch } from 'vue'

const STYLE_OPTIONS = {
    font_size: {
        normal: 14,
        large: 18
    },
    layout_width: {
        normal: 900,
        wide: 1200
    },
    theme_color: {
        green: 160,
        blue: 210,
        purple: 270
    },
    theme: {
        light: 'light',
        dark: 'dark'
    }
}

export const styles = reactive({
    font_size: 'normal',        // normal | large
    layout_width: 'normal',     // normal | wide
    theme_color: 'green',       // green | blue | purple
    theme: 'light'            // light | dark
})

function applyStyles() {
    const root = document.documentElement;

    // Устанавливаем все атрибуты, которые есть в styles
    for (const key in styles) {
        root.setAttribute(`data-${key}`, styles[key]);
    }
}

watch(styles, applyStyles, { deep: true })
applyStyles()

export function getStyleOptions(key) {
    return Object.keys(STYLE_OPTIONS[key] || {})
}