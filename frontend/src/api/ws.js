let socket = null
let connectPromise = null
let connectionId = null
let connectionIdPromise = null

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

    if (
        socket &&
        socket.readyState === WebSocket.CONNECTING &&
        connectPromise
    ) {
        return connectPromise
    }

    socket = new WebSocket('ws://localhost:8000/ws')

    connectionIdPromise = new Promise((resolve) => {
        const timeout = setTimeout(() => {
            resolve(null)
        }, 5000)

        const handleEstablished = (event) => {
            try {
                const msg = JSON.parse(event.data)

                if (msg?.type === 'connection_established') {
                    clearTimeout(timeout)

                    connectionId = msg.connection_id

                    socket.removeEventListener(
                        'message',
                        handleEstablished
                    )

                    resolve(connectionId)
                }
            }
            catch (e) {}
        }

        socket.addEventListener(
            'message',
            handleEstablished
        )
    })

    connectPromise = new Promise((resolve, reject) => {
        socket.onopen = () => {
            console.log('[WS] connected', {
                readyState: socket.readyState,
                state: getReadyStateLabel(socket.readyState)
            })

            resolve(socket)
        }

        socket.onerror = (err) => {
            console.error('[WS] error', err)

            connectPromise = null
            reject(err)
        }

        socket.onmessage = (event) => {
            try {
                const msg = JSON.parse(event.data)
                console.log('[WS ANSWER]', msg)
            }
            catch {
                console.warn('[WS] non-json message')
            }
        }

        socket.onclose = (event) => {
            console.warn('[WS] closed', event)

            socket = null
            connectPromise = null
            connectionId = null
            connectionIdPromise = null
        }
    })

    return connectPromise
}

export async function waitForConnectionId() {
    if (connectionId) {
        return connectionId
    }

    if (connectionIdPromise) {
        return connectionIdPromise
    }

    await connectWS()
    return connectionIdPromise
}
export function getConnectionId() {
    return connectionId
}

export function sendWS(payload) {
    if (!socket || socket.readyState !== WebSocket.OPEN) {
        console.warn('[WS] not connected')
        return
    }

    console.log('[SEND TO WS]', payload)
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
