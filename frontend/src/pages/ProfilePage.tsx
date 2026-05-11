import { useAuthStore } from '@/hooks/useAuthStore'
import { useQuery } from '@tanstack/react-query'
import api from '@/services/api'
import { useNavigate } from 'react-router-dom'
import { User, Settings, Bell, Shield, LogOut, ChevronRight, Edit3 } from 'lucide-react'

export default function ProfilePage() {
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()

  const { data: profile } = useQuery({
    queryKey: ['profile'],
    queryFn: () => api.get('/profile/').then(r => r.data).catch(() => null),
  })

  const handleLogout = () => { logout(); navigate('/login') }

  const SETTINGS = [
    { icon: Edit3,    label: 'Edit Profile',       color: 'bg-rose-light text-rose',   action: () => navigate('/onboard') },
    { icon: Bell,     label: 'Notifications',      color: 'bg-sage-light text-sage',   action: () => {} },
    { icon: Shield,   label: 'Privacy & Security', color: 'bg-plum-light text-plum',   action: () => {} },
    { icon: Settings, label: 'App Settings',       color: 'bg-peach-light text-peach', action: () => {} },
    { icon: LogOut,   label: 'Sign Out',            color: 'bg-red-50 text-red-500',    action: handleLogout },
  ]

  return (
    <div className="pb-8">
      <div className="bg-gradient-to-br from-rose to-plum text-white px-6 pt-14 pb-10 text-center">
        <div className="w-20 h-20 rounded-full bg-white/25 border-2 border-white mx-auto mb-3 flex items-center justify-center">
          <User size={32} />
        </div>
        <h2 className="font-bold text-xl">{user?.full_name ?? 'User'}</h2>
        <p className="text-sm opacity-75 mt-0.5">@{user?.username ?? 'user'}</p>
      </div>

      <div className="flex gap-3 px-5 -mt-5">
        {[{label:'Day Streak',value:'12'},{label:'Plans Done',value:'8'},{label:'Community',value:'3'}].map(s=>(
          <div key={s.label} className="flex-1 card px-3 py-3.5 text-center">
            <p className="font-bold text-lg text-rose">{s.value}</p>
            <p className="text-[10px] text-gray-400 mt-0.5">{s.label}</p>
          </div>
        ))}
      </div>

      {profile && (
        <div className="mx-5 mt-5 card p-4">
          <p className="text-xs font-bold text-gray-400 uppercase tracking-wide mb-3">Your PCOS Profile</p>
          <div className="grid grid-cols-2 gap-3">
            {[
              {label:'Age',    value: profile.age ? profile.age+' yrs' : '-'},
              {label:'Weight', value: profile.weight_kg ? profile.weight_kg+' kg' : '-'},
              {label:'BMI',    value: profile.bmi ?? '-'},
              {label:'Activity', value: profile.activity_level ?? '-'},
            ].map(({label,value})=>(
              <div key={label} className="bg-cream rounded-xl p-3">
                <p className="text-[10px] text-gray-400 uppercase">{label}</p>
                <p className="font-semibold text-sm text-gray-700 capitalize mt-0.5">{value}</p>
              </div>
            ))}
          </div>
          {profile.symptoms?.length > 0 && (
            <div className="mt-3">
              <p className="text-[10px] text-gray-400 uppercase mb-2">Tracked Symptoms</p>
              <div className="flex flex-wrap gap-1.5">
                {profile.symptoms.map((s: string)=>(
                  <span key={s} className="tag-rose">{s}</span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      <div className="mx-5 mt-5 card overflow-hidden">
        {SETTINGS.map(({icon:Icon,label,color,action},i)=>(
          <button key={label} onClick={action}
            className={"w-full flex items-center gap-3 px-4 py-4 text-left hover:bg-gray-50 " +
              (i<SETTINGS.length-1?'border-b border-plum/5':'')}>
            <div className={"w-9 h-9 rounded-xl flex items-center justify-center "+color}>
              <Icon size={16}/>
            </div>
            <span className="flex-1 text-sm font-semibold text-gray-700">{label}</span>
            <ChevronRight size={16} className="text-gray-300"/>
          </button>
        ))}
      </div>

      <p className="text-center text-xs text-gray-300 mt-6">NourisHer v1.0.0 - Made with love for PCOS warriors</p>
    </div>
  )
}
