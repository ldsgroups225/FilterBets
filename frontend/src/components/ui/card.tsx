import * as React from "react"
import { motion } from 'motion/react'
import { cn } from "@/lib/utils"

function Card({
  className,
  size = "default",
  children,
  ...props
}: React.ComponentProps<"div"> & { size?: "default" | "sm" }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -4 }}
      transition={{
        duration: 0.4,
        ease: [0.23, 1, 0.32, 1]
      }}
      className="h-full"
    >
      <div
        data-slot="card"
        data-size={size}
        className={cn(
          "glass relative h-full flex flex-col overflow-hidden rounded-2xl p-6 transition-all duration-300",
          "hover:shadow-primary/5 hover:border-primary/20 hover:shadow-2xl",
          size === "sm" && "p-4 gap-3",
          className
        )}
        {...props}
      >
        {children}
        {/* Subtle inner glow */}
        <div className="absolute inset-0 bg-linear-to-br from-white/5 to-transparent pointer-events-none" />
      </div>
    </motion.div>
  )
}

function CardHeader({ className, ...props }: React.ComponentProps<"div">) {
  return (
    <div
      data-slot="card-header"
      className={cn(
        "flex flex-col gap-1.5 px-0 pb-4",
        className
      )}
      {...props}
    />
  )
}

function CardTitle({ className, ...props }: React.ComponentProps<"div">) {
  return (
    <div
      data-slot="card-title"
      className={cn("text-xl font-bold tracking-tight text-foreground", className)}
      {...props}
    />
  )
}

function CardDescription({ className, ...props }: React.ComponentProps<"div">) {
  return (
    <div
      data-slot="card-description"
      className={cn("text-muted-foreground text-sm font-medium", className)}
      {...props}
    />
  )
}

function CardAction({ className, ...props }: React.ComponentProps<"div">) {
  return (
    <div
      data-slot="card-action"
      className={cn(
        "ml-auto flex items-center gap-2",
        className
      )}
      {...props}
    />
  )
}

function CardContent({ className, ...props }: React.ComponentProps<"div">) {
  return (
    <div
      data-slot="card-content"
      className={cn("px-0 flex-1", className)}
      {...props}
    />
  )
}

function CardFooter({ className, ...props }: React.ComponentProps<"div">) {
  return (
    <div
      data-slot="card-footer"
      className={cn("flex items-center pt-4 border-t border-white/5", className)}
      {...props}
    />
  )
}

export {
  Card,
  CardHeader,
  CardFooter,
  CardTitle,
  CardAction,
  CardDescription,
  CardContent,
}
