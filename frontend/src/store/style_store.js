import { reactive, watch } from 'vue'

const STYLE_OPTIONS = {
    fontSize: {
        normal: 14,
        large: 18
    },
    layoutWidth: {
        normal: 900,
        wide: 1200
    },
    primaryHue: {
        green: 160,
        blue: 210,
        purple: 270
    },
    theme: {
        light: 'light',
        dark: 'dark'
    },
    // Дополнительно можем добавить и другие настройки, например:
    // density: { comfortable: 'comfortable', compact: 'compact' }
}

/// backend

export const styles = reactive({
    fontSize: 'normal' ,        // normal | large
    layoutWidth: 'normal',     // normal | wide
    primaryHue: 'green',       // green | blue | purple
    theme: 'light',            // light | dark
    // Добавить новые настройки
    // density: 'comfortable'  // comfortable | compact
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