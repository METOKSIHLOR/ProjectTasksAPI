export const STATUS_MARK = '\u200B'

export const STATUS_META = {
    todo: {
        text: {
            full: '! To Do',
            short: 'To Do'
        },
        color: '#e53935',
        class: 'status-todo'
    },
    in_progress: {
        text: {
            full: '⧖ Work in progress',
            short: 'Work in progress'
        },
        color: '#1e88e5',
        class: 'status-in-progress'
    },
    done: {
        text: {
            full: '✓ Task completed',
            short: 'Task completed'
        },
        color: '#2ecc71',
        class: 'status-done'
    }
}

/* создание статус-комментария */
export function buildStatusComment(statusKey) {
    const short = STATUS_META[statusKey]?.text?.short
    if (!short) return ''

    return `set the status ${short}${STATUS_MARK}`
}

/* проверка статус-комментария */
export function isStatusComment(text = '') {
    return text.includes(STATUS_MARK)
}

/* определение статуса */
export function parseStatusFromComment(text = '') {
    if (!isStatusComment(text)) return null

    for (const key in STATUS_META) {
        const short = STATUS_META[key].text.short

        if (text.includes(short)) {
            return key
        }
    }

    return null
}

/* очистка текста для UI */
export function cleanStatusText(text = '') {
    return text.replace(STATUS_MARK, '')
}

/* helpers */
export function getStatusText(statusKey, mode = 'full') {
    return STATUS_META[statusKey]?.text?.[mode] || ''
}

export function getStatusColor(statusKey) {
    return STATUS_META[statusKey]?.color || ''
}

export function getStatusClass(statusKey) {
    return STATUS_META[statusKey]?.class || ''
}

/* статусный поток */
export const STATUS_FLOW = {
    todo: 'in_progress',
    in_progress: 'done'
}
export function getNextStatus(statusKey) {
    return STATUS_FLOW[statusKey] || null
}

/* status button logic */
export const STATUS_BUTTON_META = {
    todo: {
        text: 'Get to work'
    },

    in_progress: {
        text: 'Finish the task'
    }
}

export function getStatusButtonText(statusKey) {
    return STATUS_BUTTON_META[statusKey]?.text || ''
}

export function getStatusButtonColor(statusKey) {
    const next = getNextStatus(statusKey)
    return STATUS_META[next]?.color || ''
}

export function canAdvanceStatus(statusKey) {
    return !!getNextStatus(statusKey)
}