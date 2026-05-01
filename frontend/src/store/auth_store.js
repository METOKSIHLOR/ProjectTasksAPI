import { ref } from 'vue';

export const currentUser = ref(null);

/* Функция для записи пользователя и его настроек */
export function setCurrentUser(user) {
    currentUser.value = user;
    currentUser.value.settings = normalizeSettings(user.settings); // убрали лишнюю вложенность
    applyStyles();
}
export function setWebsocketID(ID) {
    currentUser.value.WS_ID = ID
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
    font_size: 'normal',
    layout_width: 'normal',
    theme_color: 'green',
    theme: 'light'
};
/* Функция для нормализации настроек (применяем дефолтные значения) */
export function normalizeSettings(settings = {}) {
    return {
        font_size: settings.font_size ?? DEFAULT_SETTINGS.font_size,
        layout_width: settings.layout_width ?? DEFAULT_SETTINGS.layout_width,
        theme_color: settings.theme_color ?? DEFAULT_SETTINGS.theme_color,
        theme: settings.theme ?? DEFAULT_SETTINGS.theme
    };
}
// Функция для применения стилей на основе текущих настроек
export function applyStyles() {
    const root = document.documentElement;
    const settings = currentUser.value?.settings || DEFAULT_SETTINGS;

    const attributes = {
        'data-fontsize': settings.font_size,
        'data-layoutwidth': settings.layout_width,
        'data-primaryhue': settings.theme_color,
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
