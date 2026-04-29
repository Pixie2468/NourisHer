import { useState } from 'react'
import { useAuthStore } from '@/hooks/useAuthStore'
import { CheckCircle2, Circle, Flame, Droplets } from 'lucide-react'

const ROUTINE = [
  { time: '7:00 AM', task: 'Spearmint tea for hormone balance',  color: 'bg-sage',  cat: 'Nutrition'  },
  { time: '8:00 AM', task: 'Anti-inflammatory breakfast',         color: 'bg-rose',  cat: 'Nutrition'  },
  { time: '10:00 AM', task: '30 min low-impact yoga',             color: 'bg-peach', cat: 'Exercise'   },
  { time: '1:00 PM', task: 'Balanced lunch + sunlight walk',      color: 'bg-plum',  cat: 'Lifestyle'  },
  { time: '3:00 PM', task: 'Magnesium supplement + hydration',    color: 'bg-sage',  cat: 'Nutrition'  },
  { time: '9:00 PM', task: 'Evening wind-down meditation',        color: 'bg-plum',  cat: 'Mindfulness'},
]

const MEALS = [
  { emoji: '🍳', name: 'Veggie Scramble Bowl',        cal: 320, time: 'Breakfast', tag: 'tag-rose', tagLabel: 'Low-GI' },
  { emoji: '🥗', name: 'Mediterranean Quinoa Salad',  cal: 445, time: 'Lunch',     tag: 'tag-sage', tagLabel: 'Anti-inflammatory' },
  { emoji: '🐟', name: 'Grilled Salmon + Broccoli',   cal: 520, time: 'Dinner',    tag: 'tag-rose', tagLabel: 'Omega-3 Rich' },
  { emoji: '🫐', name: 'Berry & Nut Snack Box',        cal: 180, time: 'Snack',     tag: 'tag-plum', tagLabel: 'Antioxidant' },
]

export default function HomePage() {
  const { user } = useAuthStore()
  const [checks, setChecks] = useState<Record<number, boolean>>({})
  const done = Object.values(checks).filter(Boolean).length
  const firstName = user?.full_name?.split(' ')[0] ?? 'there'

  const greet = () => {
    const h = new Date().getHours()
    if (h < 12) return 'Good morning ☀️'
    if (h < 17) return 'Good afternoon 🌤'
    return 'Good evening 🌙'
  }

  return (
    <div className="pb-6">
      {/* Header */}
      <div className="bg-gradient-to-br from-rose to-plum text-white px-6 pt-14 pb-8">
        <p className="text-sm opacity-80 mb-1">{greet()}</p>
        <h1 className="font-serif text-3xl italic mb-5">Hey, {firstName}! 🌸</h1>

        {/* Cycle card */}
        <div className="bg-white/15 backdrop-blur-sm rounded-2xl p-4 border border-white/25">
          <div className="flex justify-between">
            {[
              { label: 'Cycle Day', value: 'Day 14 🌕' },
              { label: 'Phase',     value: 'Ovulatory' },
              { label: 'Streak',    value: '12 days 🔥' },
            ].map(({ label, value }) => (
              <div key={label}>
                <p className="text-xs opacity-70 uppercase tracking-wide">{label}</p>
                <p className="font-bold text-sm mt-0.5">{value}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Stats row */}
      <div className="flex gap-3 px-5 -mt-4">
        {[
          { label: 'Water', value: '1.2L', icon: <Droplets size={16} className="text-blue-400" /> },
          { label: 'Calories', value: '1,285', icon: <Flame size={16} className="text-peach" /> },
          { label: 'Steps', value: '4,820', icon: <span className="text-sm">👟</span> },
        ].map(s => (
          <div key={s.label} className="flex-1 card px-3 py-3 text-center">
            <div className="flex justify-center mb-1">{s.icon}</div>
            <div className="font-bold text-sm text-gray-800">{s.value}</div>
            <div className="text-[10px] text-gray-400">{s.label}</div>
          </div>
        ))}
      </div>

      {/* Daily Routine */}
      <section className="px-5 mt-6">
        <div className="flex items-center justify-between mb-3">
          <h2 className="font-bold text-base text-gray-800">Today's Routine</h2>
          <span className="text-xs font-bold text-sage">{done}/{ROUTINE.length} done</span>
        </div>
        {/* Progress bar */}
        <div className="h-1.5 bg-sage-light rounded-full mb-4">
          <div
            className="h-full bg-sage rounded-full transition-all duration-500"
            style={{ width: `${(done / ROUTINE.length) * 100}%` }}
          />
        </div>
        <div className="space-y-2.5">
          {ROUTINE.map((r, i) => (
            <div key={i} className="card flex items-center gap-3 px-4 py-3.5">
              <div className={`w-2.5 h-2.5 rounded-full ${r.color} flex-shrink-0`} />
              <div className="flex-1 min-w-0">
                <p className="text-[10px] text-gray-400 font-semibold">{r.time}</p>
                <p className="text-sm font-semibold text-gray-700 truncate">{r.task}</p>
              </div>
              <button
                onClick={() => setChecks(c => ({ ...c, [i]: !c[i] }))}
                className="flex-shrink-0"
              >
                {checks[i]
                  ? <CheckCircle2 size={22} className="text-sage" />
                  : <Circle size={22} className="text-gray-300" />
                }
              </button>
            </div>
          ))}
        </div>
      </section>

      {/* Today's Meals */}
      <section className="px-5 mt-6">
        <h2 className="font-bold text-base text-gray-800 mb-3">Today's Meals</h2>
        <div className="space-y-3">
          {MEALS.map((m, i) => (
            <div key={i} className="card flex items-center gap-4 px-4 py-3.5">
              <span className="text-3xl">{m.emoji}</span>
              <div className="flex-1">
                <p className="font-bold text-sm text-gray-800">{m.name}</p>
                <p className="text-xs text-gray-400">{m.time} · {m.cal} kcal</p>
                <span className={m.tag + ' mt-1 inline-block'}>{m.tagLabel}</span>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Wellness Tip */}
      <section className="px-5 mt-6">
        <div className="bg-gradient-to-r from-plum-light to-rose-light rounded-3xl p-5 border border-plum/10">
          <p className="text-xs font-bold text-plum mb-2 uppercase tracking-wide">💡 Today's Wellness Tip</p>
          <p className="text-sm text-gray-700 leading-relaxed">
            Spearmint tea consumed twice daily has been shown in studies to reduce androgen levels in women with PCOS — try it with your morning and evening routine!
          </p>
        </div>
      </section>
    </div>
  )
}
