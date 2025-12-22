import { ReactNode } from 'react'
import { Header } from './Header'

interface LayoutProps {
  children: ReactNode
}

export function Layout({ children }: LayoutProps) {
  return (
    <div className="min-h-screen flex flex-col bg-[#f8f9fc]">
      <Header />
      <main className="flex-1 max-w-[1400px] mx-auto w-full px-8 py-12">
        {children}
      </main>
    </div>
  )
}
