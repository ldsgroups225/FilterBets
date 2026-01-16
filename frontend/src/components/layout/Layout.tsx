import { IconMenu2 } from '@tabler/icons-react'
import { motion } from 'motion/react'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { Sidebar } from './Sidebar'

interface LayoutProps {
  children: React.ReactNode
}

export function Layout({ children }: LayoutProps) {
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false)
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)

  return (
    <div className="min-h-screen bg-background selection:bg-primary/30 selection:text-primary">
      {/* Background Decor */}
      <div className="fixed inset-0 z-0 pointer-events-none overflow-hidden">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-primary/10 blur-[120px] rounded-full animate-pulse" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-secondary/10 blur-[120px] rounded-full animate-pulse [animation-delay:2s]" />
      </div>

      {/* Mobile Menu Toggle - Visible only on mobile */}
      <Button
        variant="ghost"
        size="icon"
        className="fixed top-4 left-4 z-40 md:hidden bg-background/50 backdrop-blur-md border border-white/10 shadow-lg rounded-xl"
        onClick={() => setIsMobileMenuOpen(true)}
      >
        <IconMenu2 className="h-6 w-6" />
      </Button>

      <div className="flex relative z-10">
        <Sidebar
          isCollapsed={isSidebarCollapsed}
          onToggle={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
          isMobileOpen={isMobileMenuOpen}
          onMobileClose={() => setIsMobileMenuOpen(false)}
        />
        <main
          className={cn(
            'flex-1 transition-all duration-500 ease-in-out min-h-screen',
            // Desktop: adjust for sidebar
            'md:ml-20',
            !isSidebarCollapsed && 'md:ml-64',
          )}
        >
          <div className="container px-4 py-8 md:px-8 max-w-7xl mx-auto pt-16 md:pt-8">
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, ease: 'easeOut' }}
            >
              {children}
            </motion.div>
          </div>
        </main>
      </div>
    </div>
  )
}
