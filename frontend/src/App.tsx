import ChatWindow from './components/ChatWindow'
import ToolCallPanel from './components/ToolCallPanel'
import { useChat } from './hooks/useChat'

export default function App() {
  const { messages, toolEvents, isStreaming, statusMsg, sendMessage, newSession } = useChat()

  return (
    <div className="flex flex-col h-screen bg-slate-950 text-white">
      <header className="flex items-center justify-between px-6 py-4 bg-slate-900 border-b border-slate-800 shrink-0">
        <div className="flex items-center gap-3">
          <span className="text-2xl">✈️</span>
          <div>
            <h1 className="text-base font-bold text-white tracking-tight">Flight Tracker AI</h1>
            <p className="text-xs text-slate-400">Monroe Township NJ (08831) · PHL · EWR · JFK</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-sky-500 animate-pulse" />
            <span className="text-xs text-slate-400">Live</span>
          </div>
          <button
            onClick={newSession}
            className="text-xs text-slate-400 hover:text-white border border-slate-700 hover:border-slate-500 rounded-lg px-3 py-1.5 transition-colors"
          >
            New Search
          </button>
        </div>
      </header>

      <div className="flex flex-1 min-h-0">
        <div className="flex-1 min-w-0">
          <ChatWindow
            messages={messages}
            isStreaming={isStreaming}
            statusMsg={statusMsg}
            onSend={sendMessage}
          />
        </div>
        <div className="w-80 shrink-0 hidden lg:block">
          <ToolCallPanel
            events={toolEvents}
            statusMsg={statusMsg}
            isStreaming={isStreaming}
          />
        </div>
      </div>
    </div>
  )
}
