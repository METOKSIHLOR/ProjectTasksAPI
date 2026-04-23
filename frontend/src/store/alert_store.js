import { reactive } from 'vue'

let idCounter = 0

export const alerts = reactive([])

/* дефолтные таймауты */
export const ALERT_TIMEOUTS = {
    info: 3000,
    success: 3000,
    error: 5000
}

export function removeAlert(id) {
    const index = alerts.findIndex(a => a.id === id)
    if (index !== -1) alerts.splice(index, 1)
}

export function pushAlert({
                              type = 'info',
                              title = '',
                              text = '',
                              timeout
                          }) {
    const id = ++idCounter

    const delay = timeout ?? ALERT_TIMEOUTS[type] ?? 3000

    const alert = {
        id,
        type,
        title,
        text,
        timeout: delay
    }

    alerts.push(alert)

    setTimeout(() => {
        removeAlert(id)
    }, delay)
}

/* short helpers */
export function alertInfo(title, text = '') {
    pushAlert({ type: 'info', title, text })
}

export function alertSuccess(title, text = '') {
    pushAlert({ type: 'success', title, text })
}

export function alertError(title, text = '') {
    pushAlert({ type: 'error', title, text })
}

export function clearAlerts() {
    alerts.splice(0, alerts.length)
}

export function parseApiError(err) {
    const status = err?.response?.status || 'Unknown status'

    const data = err?.response?.data

    if (!data) {
        return {
            title: `[${status}] Error`,
            message: err?.message || 'Unknown error'
        }
    }

    const detail = data.detail

    if (typeof detail === 'string') {
        return {
            title: `[${status}] Error`,
            message: detail
        }
    }

    if (Array.isArray(detail)) {
        return {
            title: `[${status}] Validation error`,
            message: detail
                .map(e => e?.msg || JSON.stringify(e))
                .join('\n')
        }
    }

    if (typeof detail === 'object' && detail !== null) {
        return {
            title: `[${status}] Error`,
            message: detail.msg || detail.detail || JSON.stringify(detail)
        }
    }

    return {
        title: `[${status}] Error`,
        message: String(detail || 'Unknown error')
    }
}