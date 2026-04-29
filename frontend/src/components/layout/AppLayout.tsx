import { Outlet, NavLink } from 'react-router-dom'
import { Home, Salad, MessageCircle, Users, BookOpen } from 'lucide-react'

const navItems = [
  { to: '/',          icon: Home,          label: 'Home' },
  { to: '/diet',      icon: Salad,         label: 'Diet' },
  { to: '/chat',      icon: MessageCircle, label: 'Nour AI' },
  { to: '/community', icon: Users,         label: 'Community' },
  { to: '/learn',     icon: BookOpen,      label: 'Learn' },
]

export default function AppLayout() {
  return (
    <div className="flex flex-col min-h-screen bg-cream max-w-md mx-auto relative shadow-2xl">
      <main className="flex-1 overflow-y-auto pb-20">
        <Outlet />
      </main>

      {/* Bottom Navigation */}
      <nav className="fixed bottom-0 left-1/2 -translate-x-1/2 w-full max-w-md bg-white border-t border-plum/10 z-50">
        <div className="flex">
          {navItems.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className={({ isActive }) =>
                `flex-1 flex flex-col items-center py-2.5 gap-1 text-[10px] font-bold tracking-wide transition-colors
                 ${isActive ? 'text-rose' : 'text-gray-400'}`
              }
            >
              {({ isActive }) => (
                <>
                  <Icon size={20} strokeWidth={isActive ? 2.5 : 1.8} />
                  {label}
                </>
              )}
            </NavLink>
          ))}
        </div>
        {/* iPhone home indicator space */}
        <div className="h-safe-area-inset-bottom" />
      </nav>
    </div>
  )
}
