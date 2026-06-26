import { useEffect, useRef } from 'react'
import { useState } from 'react'
import Message from './Message'
import type { Message as MessageType } from '../hooks/useChat'

interface Props {
  messages: MessageType[]
  isStreaming: boolean
  statusMsg: string
  onSend: (text: string) => void
}

const STARTER_QUESTIONS: string[] = [
  'What flights are overhead right now?',
  'Any flights heading to Newark?',
  "What's coming in to Philadelphia?",
]

export default function ChatWindow({ messages, isStreaming, statusMsg, onSend }: Props) {
  const [input, setInput] = useState('')
  const bottomRef = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  function handleSend() {
    if (!input.trim() || isStreaming) return
    onSend(input.trim())
    setInput('')
  }

  function handleKey(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const showStarters = messages.length === 0

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto p-4">
        {showStarters && (
          <div className="flex flex-col items-center justify-center h-full text-center px-8">
            <div className="text-5xl mb-4">✈️</div>
            <h2 className="text-xl font-bold text-white mb-2">Flight Tracker AI</h2>
            <p className="text-slate-400 text-sm mb-8 max-w-md">
              Ask me about flights currently on approach over Monroe Township, NJ heading to PHL, EWR, or JFK.
            </p>
            <div className="grid grid-cols-1 gap-2 w-full max-w-lg">
              {STARTER_QUESTIONS.map((q, i) => (
                <button
                  key={i}
                  onClick={() => onSend(q)}
                  className="text-left text-sm bg-slate-800 hover:bg-slate-700 border border-slate-700 hover:border-sky-500 text-slate-300 hover:text-white rounded-lg px-4 py-3 transition-all"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map(msg => (
          <Message key={msg.id} msg={msg} userRole="user" />
        ))}

        {isStreaming && statusMsg && messages[messages.length - 1]?.role !== 'assistant' && (
          <div className="flex items-center gap-2 text-xs text-slate-500 px-2 mb-4">
            <div className="w-2 h-2 rounded-full bg-sky-500 animate-pulse" />
            {statusMsg}
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      <div className="px-4 py-4 border-t border-slate-800">
        <div className="flex gap-3 items-end">
          <textarea
            rows={1}
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKey}
            placeholder="Ask about flights overhead..."
            disabled={isStreaming}
            className="flex-1 bg-slate-800 border border-slate-700 focus:border-sky-500 rounded-xl px-4 py-3 text-white placeholder-slate-500 text-sm resize-none focus:outline-none transition-colors disabled:opacity-50 max-h-36"
            style={{ overflowY: 'auto' }}
          />
          <button
            onClick={handleSend}
            disabled={isStreaming || !input.trim()}
            className="bg-sky-500 hover:bg-sky-400 text-white font-bold px-5 py-3 rounded-xl transition-colors disabled:opacity-40 whitespace-nowrap text-sm"
          >
            {isStreaming ? '...' : 'Ask'}
          </button>
        </div>
        <p className="text-xs text-slate-600 mt-2 text-center">
          OpenSky Network · OpenFlights DB · Claude Sonnet · Monroe Township NJ (08831)
        </p>
      </div>
    </div>
  )
}
