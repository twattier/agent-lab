import { create } from 'zustand'

interface AppState {
  sidebarOpen: boolean
  currentLanguage: 'en' | 'fr'
  theme: 'light' | 'dark'
  toggleSidebar: () => void
  setLanguage: (lang: 'en' | 'fr') => void
  setTheme: (theme: 'light' | 'dark') => void
}

export const useAppStore = create<AppState>((set) => ({
  sidebarOpen: true,
  currentLanguage: 'en',
  theme: 'light',
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  setLanguage: (lang) => set({ currentLanguage: lang }),
  setTheme: (theme) => set({ theme }),
}))
