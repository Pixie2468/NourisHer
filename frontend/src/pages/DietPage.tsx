import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '@/services/api'
import toast from 'react-hot-toast'
import { Sparkles, RefreshCw } from 'lucide-react'

const TABS = ['Today', 'PCOS Foods', 'Avoid']

const PCOS_FOODS = [
  { emoji:'🥦', name:'Cruciferous Veggies', bg:'#E8F4EC', gi:'Low GI', benefits:['Supports estrogen detox','Reduces inflammation','Aids weight management'] },
  { emoji:'🐟', name:'Wild-caught Salmon',  bg:'#FDE8EC', gi:'High Protein', benefits:['Reduces insulin resistance','Anti-inflammatory','Supports fertility'] },
  { emoji:'🫐', name:'Blueberries & Berries', bg:'#F0E8F2', gi:'Low Sugar', benefits:['Balances blood sugar','Reduces oxidative stress','Supports gut health'] },
  { emoji:'🥚', name:'Organic Eggs',        bg:'#FEF0E8', gi:'Complete Protein', benefits:['Hormone building blocks','Supports brain health','Rich in choline'] },
  { emoji:'🥑', name:'Avocado',             bg:'#E8F4EC', gi:'Healthy Fats', benefits:['Reduces androgens','Supports hormone synthesis','Anti-inflammatory'] },
  { emoji:'🫚', name:'Olive Oil (EVOO)',     bg:'#FEF0E8', gi:'Monounsaturated', benefits:['Improves insulin sensitivity','Heart health','Anti-inflammatory'] },
]

const AVOID_FOODS = [
  { emoji:'🍬', name:'Refined Sugar & Sweets',   reason:'Spikes insulin, worsens PCOS symptoms dramatically' },
  { emoji:'🥛', name:'Conventional Dairy',        reason:'May increase androgens and trigger inflammation' },
  { emoji:'🍞', name:'Refined Carbohydrates',     reason:'Causes blood sugar dysregulation and weight gain' },
  { emoji:'🥩', name:'Processed Meats',           reason:'High in inflammatory saturated fats' },
  { emoji:'☕', name:'Excess Caffeine (>2 cups)', reason:'Disrupts cortisol rhythm and hormone balance' },
  { emoji:'🍺', name:'Alcohol',                   reason:'Impairs liver detoxification of excess estrogen' },
]

const MEAL_COLORS: Record<string, string> = {
  breakfast: 'bg-rose-light', lunch: 'bg-sage-light', dinner: 'bg-plum-light', snack: 'bg-peach-light',
}

export default function DietPage() {
  const [tab, setTab] = useState('Today')
  const qc = useQueryClient()

  const { data: plan, isLoading } = useQuery({
    queryKey: ['diet-today'],
    queryFn: () => api.get('/diet/today').then(r => r.data),
    retry: false,
  })

  const generate = useMutation({
    mutationFn: () => api.post('/diet/generate'),
    onSuccess: (res) => {
      qc.setQueryData(['diet-today'], res.data)
      toast.success('New plan generated! 🥗')
    },
    onError: () => toast.error('Could not generate plan. Check your profile is complete.'),
  })

  return (
    <div className="pb-6">
      {/* Header */}
      <div className="bg-gradient-to-br from-sage to-green-700 text-white px-6 pt-14 pb-6">
        <h1 className="font-serif text-3xl italic mb-1">Your Diet Plan 🥗</h1>
        <p className="text-sm opacity-80">Personalized for PCOS hormone balance</p>
        <button
          onClick={() => generate.mutate()}
          disabled={generate.isPending}
          className="mt-4 flex items-center gap-2 bg-white/20 border border-white/30 rounded-full px-4 py-2 text-sm font-bold backdrop-blur-sm"
        >
          {generate.isPending
            ? <><RefreshCw size={14} className="animate-spin" /> Generating...</>
            : <><Sparkles size={14} /> Generate AI Plan</>
          }
        </button>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 px-5 py-4 overflow-x-auto">
        {TABS.map(t => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-4 py-2 rounded-full text-sm font-bold whitespace-nowrap border transition-all ${
              tab === t ? 'bg-sage text-white border-sage' : 'bg-white text-gray-500 border-plum/10'
            }`}
          >
            {t}
          </button>
        ))}
      </div>

      <div className="px-5 space-y-4">
        {/* TODAY TAB */}
        {tab === 'Today' && (
          <>
            {isLoading && <p className="text-center text-gray-400 py-10">Loading your plan...</p>}
            {!isLoading && !plan && (
              <div className="card p-6 text-center">
                <p className="text-3xl mb-3">🥗</p>
                <p className="font-bold text-gray-700 mb-1">No plan yet</p>
                <p className="text-sm text-gray-400 mb-4">Generate your personalized AI diet plan</p>
                <button onClick={() => generate.mutate()} className="btn-primary" disabled={generate.isPending}>
                  {generate.isPending ? 'Generating...' : 'Generate My Plan ✨'}
                </button>
              </div>
            )}
            {plan && (
              <>
                {/* Macros summary */}
                <div className="card p-4">
                  <p className="text-xs font-bold text-gray-400 uppercase tracking-wide mb-3">Daily Macros</p>
                  <div className="flex justify-between text-center">
                    {[
                      { label: 'Calories', value: plan.total_cal, unit: 'kcal', color: 'text-rose' },
                      { label: 'Protein',  value: plan.total_protein_g, unit: 'g', color: 'text-sage' },
                      { label: 'Carbs',    value: plan.total_carbs_g, unit: 'g', color: 'text-peach' },
                      { label: 'Fat',      value: plan.total_fat_g, unit: 'g', color: 'text-plum' },
                    ].map(m => (
                      <div key={m.label}>
                        <p className={`font-bold text-lg ${m.color}`}>{m.value}</p>
                        <p className="text-[10px] text-gray-400">{m.unit}</p>
                        <p className="text-[10px] text-gray-500 font-semibold">{m.label}</p>
                      </div>
                    ))}
                  </div>
                </div>

                {plan.meals?.map((meal: any) => (
                  <div key={meal.id} className={`card overflow-hidden`}>
                    <div className={`${MEAL_COLORS[meal.meal_type] || 'bg-cream'} px-4 py-3 flex items-center gap-3`}>
                      <span className="text-2xl">{meal.emoji}</span>
                      <div>
                        <p className="text-[10px] font-bold text-gray-500 uppercase capitalize">{meal.meal_type}</p>
                        <p className="font-bold text-gray-800 text-sm">{meal.name}</p>
                      </div>
                      <div className="ml-auto text-right">
                        <p className="font-bold text-rose text-sm">{meal.calories}</p>
                        <p className="text-[10px] text-gray-400">kcal</p>
                      </div>
                    </div>
                    <div className="px-4 py-3">
                      {meal.description && <p className="text-xs text-gray-500 mb-2">{meal.description}</p>}
                      <div className="flex gap-2">
                        {meal.gi_level && <span className="tag-sage">GI: {meal.gi_level}</span>}
                        {meal.tags?.slice(0,2).map((t: string) => (
                          <span key={t} className="tag-rose">{t}</span>
                        ))}
                      </div>
                    </div>
                  </div>
                ))}
              </>
            )}
          </>
        )}

        {/* PCOS FOODS TAB */}
        {tab === 'PCOS Foods' && PCOS_FOODS.map((food, i) => (
          <div key={i} className="card overflow-hidden">
            <div className="h-20 flex items-center justify-center text-4xl" style={{ background: food.bg }}>
              {food.emoji}
            </div>
            <div className="p-4">
              <div className="flex items-center justify-between mb-2">
                <p className="font-bold text-gray-800">{food.name}</p>
                <span className="tag-sage">{food.gi}</span>
              </div>
              <ul className="space-y-1">
                {food.benefits.map((b, j) => (
                  <li key={j} className="flex items-center gap-2 text-xs text-gray-500">
                    <span className="text-sage font-bold">✓</span> {b}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        ))}

        {/* AVOID TAB */}
        {tab === 'Avoid' && AVOID_FOODS.map((item, i) => (
          <div key={i} className="card flex items-center gap-4 px-4 py-4 border-l-4 border-rose">
            <span className="text-3xl">{item.emoji}</span>
            <div>
              <p className="font-bold text-sm text-gray-800">{item.name}</p>
              <p className="text-xs text-rose mt-0.5">⚠ {item.reason}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
