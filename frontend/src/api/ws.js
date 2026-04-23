let socket = null

export function connectWS() {
    if (socket && socket.readyState === WebSocket.OPEN) {
        return socket
    }

    socket = new WebSocket('ws://localhost:8000/ws')

    socket.onopen = () => {
        console.log('[WS] connected')
    }

    socket.onmessage = (event) => {
        console.log('[WS RAW]', event.data)

        try {
            const msg = JSON.parse(event.data)
            console.log('[WS PARSED]', msg)
        } catch (e) {
            console.warn('[WS] non-json message')
        }
    }

    socket.onerror = (err) => {
        console.error('[WS] error', err)
    }

    socket.onclose = () => {
        console.warn('[WS] closed')
    }

    return socket
}

export function sendWS(payload) {
    if (!socket || socket.readyState !== WebSocket.OPEN) {
        console.warn('[WS] not connected')
        return
    }

    console.log('[WS OUT]', payload)
    socket.send(JSON.stringify(payload))
}

// подписка на комнату (только как команда)
export function subscribe(room) {
    sendWS({
        action: 'subscribe',
        rooms: [room]
    })
}