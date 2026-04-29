import { useState, useRef, useEffect } from 'react'
import { useMutation } from '@tanstack/react-query'
import api from '@/services/api'
import { Send } from 'lucide-react'

interface Message { role: 'user' | 'assistant'; content: string; time: string }

const QUICK_CHIPS = [
  'Diet tips for PCOS 🥗', 'Hormone balance help 🌙',
  "I'm feeling stressed 💜", 'What supplements help?',
  'Explain insulin resistance', 'Cycle syncing tips',
]

const INIT_MSG: Message = {
  role: 'assistant',
  content: "Hi! I'm Nour 🌸 Your PCOS wellness companion. I'm here to help with diet, hormones, mental health, lifestyle tips, and emotional support. How are you feeling today?",
  time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([INIT_MSG])
  const [input, setInput]       = useState('')
  const [sessionId, setSessionId] = useState<string | null>(null)
  const endRef = useRef<HTMLDivElement>(null)

  useEffect(() => { endRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages])

  const send = useMutation({
    mutationFn: (msg: string) =>
      api.post('/chat/', { message: msg, session_id: sessionId }).then(r => r.data),
    onMutate: (msg) => {
      const t = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      setMessages(m => [...m, { role: 'user', content: msg, time: t }])
      setInput('')
    },
    onSuccess: (data) => {
      if (!sessionId) setSessionId(data.session_id)
      const t = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      setMessages(m => [...m, { role: 'assistant', content: data.reply, time: t }])
    },
    onError: () => {
      const t = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      setMessages(m => [...m, { role: 'assistant', content: "I'm here for you 🌸 Could you try again?", time: t }])
    },
  })

  const handleSend = (text?: string) => {
    const msg = (text ?? input).trim()
    if (!msg || send.isPending) return
    send.mutate(msg)
  }

  return (
    <div className="flex flex-col h-[calc(100vh-80px)]">
      {/* Header */}
      <div className="bg-plum text-white px-5 pt-14 pb-5 flex items-center gap-3 flex-shrink-0">
        <div className="w-11 h-11 rounded-full bg-white/20 border-2 border-white/40 flex items-center justify-center text-xl">🌸</div>
        <div>
          <p className="font-bold">Nour AI</p>
          <p className="text-xs opacity-75">Your PCOS wellness companion · Always here</p>
        </div>
        <div className="ml-auto w-2 h-2 rounded-full bg-green-400 animate-pulse" />
      </div>

      {/* Quick chips */}
      <div className="flex gap-2 px-4 py-3 overflow-x-auto flex-shrink-0 bg-plum-light/40 border-b border-plum/10">
        {QUICK_CHIPS.map(q => (
          <button
            key={q}
            onClick={() => handleSend(q)}
            className="whitespace-nowrap px-3 py-1.5 rounded-full text-xs font-semibold bg-plum-light text-plum border border-plum/10 flex-shrink-0"
          >
            {q}
          </button>
        ))}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4">
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] ${m.role === 'user' ? 'items-end' : 'items-start'} flex flex-col gap-1`}>
              {m.role === 'assistant' && (
                <div className="w-7 h-7 rounded-full bg-plum flex items-center justify-center text-sm">🌸</div>
              )}
              <div
                className={`px-4 py-3 rounded-2xl text-sm leading-relaxed ${
                  m.role === 'user'
                    ? 'bg-rose text-white rounded-br-sm'
                    : 'bg-white text-gray-800 shadow-card rounded-bl-sm border border-plum/5'
                }`}
              >
                {m.content}
              </div>
              <p className="text-[10px] text-gray-400 px-1">{m.time}</p>
            </div>
          </div>
        ))}

        {/* Typing indicator */}
        {send.isPending && (
          <div className="flex justify-start">
            <div className="flex flex-col gap-1 items-start">
              <div className="w-7 h-7 rounded-full bg-plum flex items-center justify-center text-sm">🌸</div>
              <div className="bg-white shadow-card rounded-2xl rounded-bl-sm px-4 py-3.5 border border-plum/5">
                <div className="flex gap-1.5 items-center">
                  {[0,1,2].map(i => (
                    <div key={i} className={`w-2 h-2 bg-gray-300 rounded-full typing-dot`} style={{ animationDelay: `${i*0.2}s` }} />
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
        <div ref={endRef} />
      </div>

      {/* Input */}
      <div className="flex gap-3 px-4 py-3 bg-white border-t border-plum/10 flex-shrink-0">
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend() } }}
          placeholder="Ask Nour anything..."
          className="flex-1 px-4 py-2.5 rounded-full border border-plum/10 bg-cream text-sm outline-none focus:border-plum/30"
        />
        <button
          onClick={() => handleSend()}
          disabled={!input.trim() || send.isPending}
          className="w-10 h-10 rounded-full bg-rose text-white flex items-center justify-center disabled:opacity-50 flex-shrink-0"
        >
          <Send size={16} />
        </button>
      </div>
    </div>
  )
}
