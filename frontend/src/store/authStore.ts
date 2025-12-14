import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { User } from '@/types'

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  login: (user: User) => void
  logout: () => void
  setToken: (token: string) => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,

      login: (user: User) => {
        localStorage.setItem('auth_token', user.token)
        set({ user, isAuthenticated: true })
      },

      logout: () => {
        localStorage.removeItem('auth_token')
        set({ user: null, isAuthenticated: false })
      },

      setToken: (token: string) => {
        localStorage.setItem('auth_token', token)
        set((state) => ({
          user: state.user ? { ...state.user, token } : null,
        }))
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)
