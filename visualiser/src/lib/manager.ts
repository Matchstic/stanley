interface IncomingMessage {
  type: 'reset' | 'update'
}

interface GeoLocation {
  latitude: number
  longitude: number
}

export interface ResetMessage extends IncomingMessage {
  type: 'reset'
}

export interface UpdateMessage extends IncomingMessage {
  type: 'update'
  vehicle: {
    heading: number
    coordinates: GeoLocation
  }
  core: {
    state: number
  }
  person?: {
    global: GeoLocation
    local: {
      z: number
      x: number
    }
  }
}

const EMPTY_MESSAGE = JSON.stringify({
  type: 'none'
})

class Manager {
  private socket: WebSocket = null
  private changeCallback = null
  private resetCallback = null
  private connectionCallback = null

  private pendingMessages = []

  constructor() {
    this.connect()
  }

  private connect() {
    console.log('Connecting socket...')
    this.socket = new WebSocket("ws://127.0.0.1:5678/")

    this.socket.onopen = () => {
      this.connectionCallback(true)
    }

    this.socket.onmessage = (event) => {
      this.onWebsocketMessage(event.data)
    }

    this.socket.onclose = () => {
      this.connectionCallback(false)
      setTimeout(() => {
        this.connect()
      }, 1000)
    }

    this.socket.onerror = () => {
      this.socket.close()
    }
  }

  private onWebsocketMessage(data: string) {
    try {
      const messages = data.split('\n')

      messages.forEach((data: string) => {
        const message: IncomingMessage = JSON.parse(data)

        if (message.type === 'update') {
          this.changeCallback(message)
        } else if (message.type === 'reset') {
          this.resetCallback(message)
        }
      })

      // Send any pending messages (even if none)
      const outgoing = this.pendingMessages.length > 0 ? this.pendingMessages.join('\n') : EMPTY_MESSAGE
      this.socket.send(outgoing)

      this.pendingMessages = []
    } catch (e) {
      console.error(data, e)
    }
  }

  public send(object: any): void {
    this.pendingMessages.push(JSON.stringify(object))
  }

  set onchange(fn: (data: UpdateMessage) => void) {
    this.changeCallback = fn
  }

  set onreset(fn: (data: ResetMessage) => void) {
    this.resetCallback = fn
  }

  set onconnected(fn: (connected: boolean) => void ) {
    this.connectionCallback = fn
  }
}

export default new Manager()