import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '@/services/api'
import toast from 'react-hot-toast'

const ALLERGIES = ['Gluten','Dairy','Nuts','Soy','Eggs','Shellfish','Corn','Nightshades']
const GOALS     = ['Lose weight','Regulate hormones','Reduce inflammation','Improve fertility','Boost energy','Better mental health','Improve sleep','Clear skin']
const DIETS     = ['no_restriction','vegetarian','vegan','mediterranean','low_gi']
const DIET_LABELS: Record<string, string> = {
  no_restriction: 'No Restrictions', vegetarian: 'Vegetarian',
  vegan: 'Vegan', mediterranean: 'Mediterranean', low_gi: 'Low-GI',
}

const steps = [
  { emoji: '🌸', title: 'Tell us about yourself', sub: "We'll personalize your plan based on your unique profile." },
  { emoji: '🥦', title: 'Dietary needs & allergies', sub: 'Help us build a diet plan that works for your body.' },
  { emoji: '🎯', title: 'Your wellness goals', sub: 'What matters most to you on this journey?' },
]

export default function OnboardPage() {
  const [step, setStep] = useState(0)
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const [form, setForm] = useState({
    age: 28, weight_kg: '', height_cm: '',
    dietary_preference: 'no_restriction', activity_level: 'moderate',
    allergies: [] as string[], goals: [] as string[],
  })

  const toggle = (field: 'allergies' | 'goals', val: string) =>
    setForm(f => ({
      ...f,
      [field]: f[field].includes(val) ? f[field].filter(x => x !== val) : [...f[field], val],
    }))

  const handleFinish = async () => {
    setLoading(true)
    try {
      await api.post('/profile/', {
        ...form,
        weight_kg: form.weight_kg ? parseFloat(form.weight_kg as string) : null,
        height_cm: form.height_cm ? parseFloat(form.height_cm as string) : null,
        onboarding_complete: true,
      })
      navigate('/')
    } catch (err: any) {
      // Profile might already exist — update instead
      try {
        await api.put('/profile/', {
          ...form,
          weight_kg: form.weight_kg ? parseFloat(form.weight_kg as string) : null,
          height_cm: form.height_cm ? parseFloat(form.height_cm as string) : null,
          onboarding_complete: true,
        })
        navigate('/')
      } catch {
        toast.error('Could not save profile')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-cream flex flex-col max-w-md mx-auto px-6 py-10">
      {/* Step dots */}
      <div className="flex justify-center gap-2 mb-10">
        {steps.map((_, i) => (
          <div
            key={i}
            className={`h-2 rounded-full transition-all duration-300 ${
              i === step ? 'w-8 bg-rose' : 'w-2 bg-rose-mid'
            }`}
          />
        ))}
      </div>

      <div className="flex-1">
        <div className="text-5xl mb-4">{steps[step].emoji}</div>
        <h2 className="font-serif text-3xl text-gray-800 mb-2">{steps[step].title}</h2>
        <p className="text-sm text-gray-500 mb-8 leading-relaxed">{steps[step].sub}</p>

        {/* Step 0 — Basic info */}
        {step === 0 && (
          <div className="space-y-5">
            <div>
              <div className="flex justify-between text-sm mb-2">
                <span className="font-semibold text-gray-600">Age</span>
                <span className="font-bold text-rose">{form.age} yrs</span>
              </div>
              <input type="range" min={13} max={55} value={form.age} className="w-full accent-rose"
                onChange={e => setForm(f => ({ ...f, age: +e.target.value }))} />
            </div>
            <div>
              <label className="block text-xs font-bold text-gray-500 uppercase tracking-wide mb-1.5">Weight (kg)</label>
              <input className="input-field" type="number" placeholder="e.g. 65"
                value={form.weight_kg} onChange={e => setForm(f => ({ ...f, weight_kg: e.target.value }))} />
            </div>
            <div>
              <label className="block text-xs font-bold text-gray-500 uppercase tracking-wide mb-1.5">Height (cm)</label>
              <input className="input-field" type="number" placeholder="e.g. 165"
                value={form.height_cm} onChange={e => setForm(f => ({ ...f, height_cm: e.target.value }))} />
            </div>
            <div>
              <label className="block text-xs font-bold text-gray-500 uppercase tracking-wide mb-2">Activity Level</label>
              <div className="flex gap-2 flex-wrap">
                {['sedentary','light','moderate','active'].map(a => (
                  <button key={a} onClick={() => setForm(f => ({ ...f, activity_level: a }))}
                    className={`chip capitalize ${form.activity_level === a ? 'chip-active' : ''}`}>
                    {a}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Step 1 — Diet & allergies */}
        {step === 1 && (
          <div className="space-y-5">
            <div>
              <label className="block text-xs font-bold text-gray-500 uppercase tracking-wide mb-2">Dietary Preference</label>
              <div className="flex flex-wrap gap-2">
                {DIETS.map(d => (
                  <button key={d} onClick={() => setForm(f => ({ ...f, dietary_preference: d }))}
                    className={`chip ${form.dietary_preference === d ? 'chip-active' : ''}`}>
                    {DIET_LABELS[d]}
                  </button>
                ))}
              </div>
            </div>
            <div>
              <label className="block text-xs font-bold text-gray-500 uppercase tracking-wide mb-2">Food Allergies / Intolerances</label>
              <div className="flex flex-wrap gap-2">
                {ALLERGIES.map(a => (
                  <button key={a} onClick={() => toggle('allergies', a)}
                    className={`chip ${form.allergies.includes(a) ? 'chip-active' : ''}`}>
                    {a}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Step 2 — Goals */}
        {step === 2 && (
          <div>
            <label className="block text-xs font-bold text-gray-500 uppercase tracking-wide mb-2">Wellness Goals</label>
            <div className="flex flex-wrap gap-2">
              {GOALS.map(g => (
                <button key={g} onClick={() => toggle('goals', g)}
                  className={`chip ${form.goals.includes(g) ? 'chip-active' : ''}`}>
                  {g}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Navigation */}
      <div className="mt-10 space-y-3">
        <button
          className="btn-primary"
          onClick={() => { if (step < 2) setStep(s => s + 1); else handleFinish() }}
          disabled={loading}
        >
          {loading ? 'Saving...' : step < 2 ? 'Continue →' : 'Start My Journey 🌸'}
        </button>
        {step > 0 && (
          <button onClick={() => setStep(s => s - 1)} className="w-full text-center text-sm text-gray-400 font-semibold py-2">
            ← Back
          </button>
        )}
      </div>
    </div>
  )
}
