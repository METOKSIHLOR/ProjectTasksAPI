import { reactive } from 'vue'

/* Default Styles (fallback values) */
export const DEFAULT_STYLES = Object.freeze({
    fontSize: 'normal',         // normal | large
    layoutWidth: 'normal',      // normal | wide
    primaryHue: 'green',        // green | blue | purple
    theme: 'light'              // light | dark
})

/* Helper: Normalize Styles (merge with default values) */
export function normalizeStyles(input = {}) {
    return {
        fontSize: input.fontSize ?? DEFAULT_STYLES.fontSize,
        layoutWidth: input.layoutWidth ?? DEFAULT_STYLES.layoutWidth,
        primaryHue: input.primaryHue ?? DEFAULT_STYLES.primaryHue,
        theme: input.theme ?? DEFAULT_STYLES.theme
    }
}

/* Apply Styles to Root */
export function applySettings(styles) {
    const root = document.documentElement

    // Apply the settings to the root element as data attributes
    root.setAttribute('data-fontsize', styles.fontSize)
    root.setAttribute('data-layoutwidth', styles.layoutWidth)
    root.setAttribute('data-primaryhue', styles.primaryHue)
    root.setAttribute('data-theme', styles.theme)
}

/* Load Settings from Local Storage or Server */
export function loadSettings() {
    const saved = JSON.parse(localStorage.getItem('userSettings'))

    // Normalize and return settings (if not available, use default)
    return normalizeStyles(saved)
}

/* Save Settings to Local Storage */
export function saveSettings(styles) {
    localStorage.setItem('userSettings', JSON.stringify(styles))
}

/* Reactive Style Object (for use within Vue components) */
export const selectedStyles = reactive({
    fontSize: DEFAULT_STYLES.fontSize,
    layoutWidth: DEFAULT_STYLES.layoutWidth,
    primaryHue: DEFAULT_STYLES.primaryHue,
    theme: DEFAULT_STYLES.theme
})

/* Function to Initialize Settings (load and apply them) */
export function initializeSettings() {
    const settings = loadSettings()

    // Update reactive object with loaded settings
    Object.assign(selectedStyles, settings)

    // Apply the settings to the root element
    applySettings(settings)
}