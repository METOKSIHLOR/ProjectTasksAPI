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
    }
}

export const styles = reactive({
    fontSize: 'normal',
    layoutWidth: 'normal',
    primaryHue: 'green',
    theme: 'light'
})

function applyStyles() {
    const root = document.documentElement

    /* typography */
    root.style.setProperty(
        '--font-size-base',
        `${STYLE_OPTIONS.fontSize[styles.fontSize]}px`
    )
    root.style.setProperty(
        '--font-size-title',
        `${STYLE_OPTIONS.fontSize[styles.fontSize] + 6}px`
    )
    /* layout */
    root.style.setProperty(
        '--layout-width',
        `${STYLE_OPTIONS.layoutWidth[styles.layoutWidth]}px`
    )
    /* theme color */
    const hue = STYLE_OPTIONS.primaryHue[styles.primaryHue]
    root.style.setProperty('--color-primary-h', hue)

    /* dark/light theme */
    root.setAttribute('data-theme', styles.theme)
}

watch(styles, applyStyles, { deep: true })
applyStyles()

export function getStyleOptions(key) {
    return Object.keys(STYLE_OPTIONS[key] || {})
}