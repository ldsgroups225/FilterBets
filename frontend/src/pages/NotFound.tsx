import { IconActivity, IconHome } from '@tabler/icons-react'
import { motion } from 'motion/react'
import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'

export function NotFound() {
  return (
    <div className="flex min-h-[calc(100vh-8rem)] flex-col items-center justify-center text-center p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.5 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5, ease: 'easeOut' }}
        className="relative mb-8"
      >
        <div className="absolute inset-0 bg-primary/20 blur-[100px] rounded-full scale-150" />
        <h1 className="text-[12rem] font-black leading-none text-white/5 select-none font-mono">
          404
        </h1>
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2">
          <IconActivity className="h-20 w-20 text-primary opacity-50 animate-pulse" />
        </div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="relative z-10 space-y-4"
      >
        <h2 className="text-4xl font-black tracking-tight text-glow">SIGNAL LOST</h2>
        <p className="text-muted-foreground max-w-md mx-auto font-medium">
          The terminal you are looking for has been decommissioned or moved to a different sector.
        </p>
        <div className="pt-6">
          <Link to="/">
            <Button className="rounded-xl h-12 px-8 font-black uppercase tracking-widest shadow-lg shadow-primary/20 hover:shadow-primary/40 transition-all">
              <IconHome className="mr-2 h-5 w-5" />
              Return to Base
            </Button>
          </Link>
        </div>
      </motion.div>
    </div>
  )
}
