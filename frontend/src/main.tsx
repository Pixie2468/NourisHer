import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'react-hot-toast'
import '@/styles/globals.css'

import { useAuthStore } from '@/hooks/useAuthStore'
import AuthPage     from '@/pages/AuthPage'
import OnboardPage  from '@/pages/OnboardPage'
import AppLayout    from '@/components/layout/AppLayout'
import HomePage     from '@/pages/HomePage'
import DietPage     from '@/pages/DietPage'
import ChatPage     from '@/pages/ChatPage'
import CommunityPage from '@/pages/CommunityPage'
import LearnPage    from '@/pages/LearnPage'
import ProfilePage  from '@/pages/ProfilePage'

const qc = new QueryClient({ defaultOptions: { queries: { retry: 1, staleTime: 30_000 } } })

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore()
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={qc}>
      <BrowserRouter future={{ v7_relativeSplatPath: true }}>
        <Routes>
          <Route path="/login"    element={<AuthPage />} />
          <Route path="/onboard"  element={<PrivateRoute><OnboardPage /></PrivateRoute>} />
          <Route path="/" element={<PrivateRoute><AppLayout /></PrivateRoute>}>
            <Route index          element={<HomePage />} />
            <Route path="diet"    element={<DietPage />} />
            <Route path="chat"    element={<ChatPage />} />
            <Route path="community" element={<CommunityPage />} />
            <Route path="learn"   element={<LearnPage />} />
            <Route path="profile" element={<ProfilePage />} />
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
      <Toaster position="top-center" toastOptions={{ style: { borderRadius: '14px', fontFamily: 'Nunito, sans-serif' } }} />
    </QueryClientProvider>
  </React.StrictMode>
)
