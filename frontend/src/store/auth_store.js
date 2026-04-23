import { ref } from 'vue';

export const currentUser = ref(null);

/* Функция для записи пользователя и его настроек */
export function setCurrentUser(user) {
    currentUser.value = user;
    currentUser.value.settings = normalizeSettings(user.settings); // убрали лишнюю вложенность
    applyStyles();
}
/* Очистка данных пользователя */
export function setUnauthorized() {
    currentUser.value = false;
}
/* Очистка данных о текущем пользователе */
export function clearCurrentUser() {
    currentUser.value = null;
}


/* === SETTINGS === */
const DEFAULT_SETTINGS = {
    fontSize: 'normal',
    layoutWidth: 'normal',
    primaryHue: 'green',
    theme: 'light'
};
/* Функция для нормализации настроек (применяем дефолтные значения) */
export function normalizeSettings(settings = {}) {
    return {
        fontSize: settings.fontSize ?? DEFAULT_SETTINGS.fontSize,
        layoutWidth: settings.layoutWidth ?? DEFAULT_SETTINGS.layoutWidth,
        primaryHue: settings.primaryHue ?? DEFAULT_SETTINGS.primaryHue,
        theme: settings.theme ?? DEFAULT_SETTINGS.theme
    };
}
// Функция для применения стилей на основе текущих настроек
export function applyStyles() {
    const root = document.documentElement;
    const settings = currentUser.value?.settings || DEFAULT_SETTINGS;

    const attributes = {
        'data-fontsize': settings.fontSize,
        'data-layoutwidth': settings.layoutWidth,
        'data-primaryhue': settings.primaryHue,
        'data-theme': settings.theme
    };

    for (const [key, value] of Object.entries(attributes)) {
        root.setAttribute(key, value);
    }
}
/* Функция для сохранения настроек пользователя в объекте */
export function updateUserSettings(settings) {
    if (currentUser.value) {
        currentUser.value.settings = normalizeSettings(settings);
        applyStyles();
    }
}
