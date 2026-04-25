import { create } from 'zustand'

type AppState = {
  activeSection: string
  setActiveSection: (section: string) => void
}

const useAppStore = create<AppState>((set) => ({
  activeSection: 'dashboard',
  setActiveSection: (section) => set({ activeSection: section })
}))

export default useAppStore
