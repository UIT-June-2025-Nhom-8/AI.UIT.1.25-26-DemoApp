import { motion } from 'framer-motion'
import { Home, LogOut } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useAuthStore } from '@/store/authStore'
import { authAPI } from '@/lib/api'
import { useNavigate } from 'react-router-dom'

export function Header() {
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()

  const handleLogout = async () => {
    try {
      await authAPI.logout()
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      logout()
      navigate('/login')
    }
  }

  return (
    <motion.header
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      className="sticky top-0 z-50 w-full border-b bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/95 shadow-sm"
    >
      <div className="max-w-[1400px] mx-auto px-8 flex h-20 items-center justify-between">
        {/* Logo Section */}
        <div className="flex items-center gap-4">
          <div className="w-11 h-11 bg-gradient-to-br from-primary to-primary/80 rounded-xl flex items-center justify-center shadow-lg shadow-primary/25">
            <Home className="w-6 h-6 text-white stroke-[2.5]" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-foreground tracking-tight">
              House Price Predictor
            </h1>
            <p className="text-sm text-muted-foreground font-medium">
              Dự đoán giá nhà với AI
            </p>
          </div>
        </div>

        {/* User Section */}
        {user && (
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-3 px-4 py-2 bg-muted/50 rounded-xl border">
              <div className="w-8 h-8 bg-gradient-to-br from-primary/20 to-primary/10 rounded-full flex items-center justify-center">
                <span className="text-sm font-semibold text-primary">
                  {user.username.charAt(0).toUpperCase()}
                </span>
              </div>
              <span className="font-semibold text-foreground text-[15px]">
                {user.username}
              </span>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={handleLogout}
              className="rounded-xl border font-semibold hover:bg-muted/50"
            >
              <LogOut className="w-4 h-4 mr-2" />
              Đăng xuất
            </Button>
          </div>
        )}
      </div>
    </motion.header>
  )
}
