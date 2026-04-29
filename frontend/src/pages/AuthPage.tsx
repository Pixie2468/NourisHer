import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/hooks/useAuthStore'
import toast from 'react-hot-toast'
import { Eye, EyeOff } from 'lucide-react'

const SYMPTOMS = [
  'Irregular periods','Weight gain','Acne','Hair loss',
  'Fatigue','Mood swings','Bloating','Insomnia','Anxiety','Brain fog',
]

export default function AuthPage() {
  const [tab, setTab] = useState<'login' | 'register'>('login')
  const [showPw, setShowPw] = useState(false)
  const [loading, setLoading] = useState(false)
  const { login, register } = useAuthStore()
  const navigate = useNavigate()

  const [form, setForm] = useState({
    email: '', password: '', username: '', full_name: '', symptoms: [] as string[],
  })

  const toggleSymptom = (s: string) =>
    setForm(f => ({
      ...f,
      symptoms: f.symptoms.includes(s) ? f.symptoms.filter(x => x !== s) : [...f.symptoms, s],
    }))

  const set = (key: string) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm(f => ({ ...f, [key]: e.target.value }))

  const handleSubmit = async () => {
    if (!form.email || !form.password) return toast.error('Please fill in all fields')
    setLoading(true)
    try {
      if (tab === 'login') {
        await login(form.email, form.password)
        navigate('/')
      } else {
        if (!form.username || !form.full_name) return toast.error('Please fill in all fields')
        await register(form)
        navigate('/onboard')
      }
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-rose-light via-plum-light to-sage-light flex flex-col items-center justify-center px-6 py-12">
      {/* Logo */}
      <div className="text-center mb-8">
        <h1 className="font-serif text-5xl text-rose italic">NourisHer</h1>
        <p className="text-sm text-gray-500 mt-2 italic">Your PCOS wellness journey, beautifully guided 🌸</p>
      </div>

      {/* Card */}
      <div className="card w-full max-w-sm p-7">
        {/* Tabs */}
        <div className="flex bg-cream rounded-2xl p-1 mb-6">
          {(['login', 'register'] as const).map(t => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className={`flex-1 py-2 rounded-xl text-sm font-bold transition-all ${
                tab === t ? 'bg-white text-rose shadow-sm' : 'text-gray-400'
              }`}
            >
              {t === 'login' ? 'Sign In' : 'Create Account'}
            </button>
          ))}
        </div>

        <div className="space-y-4">
          {tab === 'register' && (
            <>
              <div>
                <label className="block text-xs font-bold text-gray-500 uppercase tracking-wide mb-1.5">Full Name</label>
                <input className="input-field" placeholder="Your name" onChange={set('full_name')} value={form.full_name} />
              </div>
              <div>
                <label className="block text-xs font-bold text-gray-500 uppercase tracking-wide mb-1.5">Username</label>
                <input className="input-field" placeholder="@username" onChange={set('username')} value={form.username} />
              </div>
            </>
          )}

          <div>
            <label className="block text-xs font-bold text-gray-500 uppercase tracking-wide mb-1.5">Email</label>
            <input className="input-field" type="email" placeholder="you@email.com" onChange={set('email')} value={form.email} />
          </div>

          <div>
            <label className="block text-xs font-bold text-gray-500 uppercase tracking-wide mb-1.5">Password</label>
            <div className="relative">
              <input
                className="input-field pr-10"
                type={showPw ? 'text' : 'password'}
                placeholder="••••••••"
                onChange={set('password')}
                value={form.password}
              />
              <button
                type="button"
                onClick={() => setShowPw(s => !s)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400"
              >
                {showPw ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
          </div>

          {tab === 'register' && (
            <div>
              <label className="block text-xs font-bold text-gray-500 uppercase tracking-wide mb-2">PCOS Symptoms (optional)</label>
              <div className="flex flex-wrap gap-2">
                {SYMPTOMS.map(s => (
                  <button
                    key={s}
                    type="button"
                    onClick={() => toggleSymptom(s)}
                    className={`chip ${form.symptoms.includes(s) ? 'chip-active' : ''}`}
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>
          )}

          <button className="btn-primary mt-2" onClick={handleSubmit} disabled={loading}>
            {loading ? '...' : tab === 'login' ? 'Sign In →' : 'Create Account →'}
          </button>

          {tab === 'login' && (
            <p className="text-center text-xs text-gray-400 mt-2">
              Forgot password?{' '}
              <span className="text-rose font-bold cursor-pointer">Reset</span>
            </p>
          )}
        </div>
      </div>

      <p className="text-xs text-gray-400 mt-6 text-center">🔒 Protected by end-to-end encryption</p>
    </div>
  )
}
