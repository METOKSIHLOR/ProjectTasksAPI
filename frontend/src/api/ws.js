let socket = null
let connectPromise = null

function getReadyStateLabel(state) {
    switch (state) {
        case WebSocket.CONNECTING:
            return 'CONNECTING'
        case WebSocket.OPEN:
            return 'OPEN'
        case WebSocket.CLOSING:
            return 'CLOSING'
        case WebSocket.CLOSED:
            return 'CLOSED'
        default:
            return `UNKNOWN(${state})`
    }
}

export function connectWS() {
    if (socket && socket.readyState === WebSocket.OPEN) {
        return Promise.resolve(socket)
    }

    if (socket && socket.readyState === WebSocket.CONNECTING && connectPromise) {
        return connectPromise
    }

    socket = new WebSocket('ws://localhost:8000/ws')
    connectPromise = new Promise((resolve, reject) => {
        socket.onopen = () => {
            console.log('[WS] connected', {
                readyState: socket.readyState,
                state: getReadyStateLabel(socket.readyState)
            })
            resolve(socket)
        }

        socket.onerror = (err) => {
            console.error('[WS] error', {
                error: err,
                readyState: socket?.readyState,
                state: getReadyStateLabel(socket?.readyState)
            })
            reject(err)
        }

        socket.onmessage = (event) => {

            try {
                const msg = JSON.parse(event.data)
                console.log('[WS PARSED]', msg)
                console.log('[WS EVENT]', {
                    type: msg?.type ?? null,
                    success: msg?.success ?? null,
                    payload: msg
                })

                switch (msg?.type) {
                    case 'task_create':
                        console.log('[WS TASK CREATE]', msg)
                        break

                    case 'task_update':
                        console.log('[WS TASK UPDATE]', msg)
                        break

                    case 'task_delete':
                        console.log('[WS TASK DELETE]', msg)
                        break

                    case 'project_update':
                        console.log('[WS PROJECT UPDATE]', msg)
                        break

                    case 'member_remove':
                        console.log('[WS MEMBER REMOVE]', msg)
                        break

                    case 'project_delete':
                        console.log('[WS PROJECT DELETE]', msg)
                        break
                }
            } catch (e) {
                console.warn('[WS] non-json message')
            }
        }

        socket.onclose = (event) => {
            console.warn('[WS] closed', {
                code: event.code,
                reason: event.reason,
                wasClean: event.wasClean,
                readyState: socket?.readyState,
                state: getReadyStateLabel(socket?.readyState)
            })
            connectPromise = null
            socket = null
        }
    })

    return connectPromise
}

export function sendWS(payload) {
    if (!socket || socket.readyState !== WebSocket.OPEN) {
        console.warn('[WS] not connected')
        return
    }

    console.log('[WS OUT]', payload)
    socket.send(JSON.stringify(payload))
}

export function subscribe(room) {
    sendWS({
        action: 'subscribe',
        rooms: [room]
    })
}

export function unsubscribe(room) {
    sendWS({
        action: 'unsubscribe',
        rooms: [room]
    })
}
