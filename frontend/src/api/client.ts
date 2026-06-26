const BASE = 'http://localhost:8001'

export function streamChat(
  message: string,
  onEvent: (eventType: string, payload: unknown) => void
): () => void {
  let cancelled = false
  ;(async () => {
    const res = await fetch(`${BASE}/api/v1/flight/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message }),
    })
    if (!res.ok) {
      onEvent('error', { message: `HTTP ${res.status}` })
      return
    }
    if (!res.body) return
    const reader = res.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''
    while (!cancelled) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })
      const parts = buffer.split('\n\n')
      buffer = parts.pop() ?? ''
      for (const part of parts) {
        const lines = part.split('\n')
        let eventType = 'message'
        let dataStr = ''
        for (const line of lines) {
          if (line.startsWith('event: ')) eventType = line.slice(7).trim()
          if (line.startsWith('data: ')) dataStr = line.slice(6).trim()
        }
        if (dataStr) {
          try { onEvent(eventType, JSON.parse(dataStr)) } catch { /* ignore */ }
        }
      }
    }
  })()
  return () => { cancelled = true }
}
