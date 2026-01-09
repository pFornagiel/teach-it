import * as React from "react"
import { cn } from "@/lib/utils"

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "default" | "outline" | "ghost" | "link" | "secondary" | "accent"
  size?: "default" | "sm" | "lg" | "icon"
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "default", size = "default", ...props }, ref) => {
    return (
      <button
        ref={ref}
        className={cn(
          "inline-flex items-center justify-center whitespace-nowrap rounded-lg text-sm font-bold ring-offset-background transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border-2 border-black active:shadow-none active:translate-x-[2px] active:translate-y-[2px]",
          {
            "bg-primary text-primary-foreground shadow-neo hover:bg-primary/90":
              variant === "default",
            "bg-white text-black shadow-neo hover:bg-accent":
              variant === "outline",
            "bg-secondary text-secondary-foreground shadow-neo hover:bg-secondary/80":
              variant === "secondary",
             "bg-accent text-accent-foreground shadow-neo hover:bg-accent/80":
              variant === "accent",
            "hover:bg-accent hover:text-accent-foreground border-transparent shadow-none hover:border-black hover:shadow-neo": variant === "ghost",
            "text-primary underline-offset-4 hover:underline border-none shadow-none active:translate-x-0 active:translate-y-0": variant === "link",
            "h-10 px-4 py-2": size === "default",
            "h-9 rounded-md px-3": size === "sm",
            "h-11 rounded-md px-8": size === "lg",
            "h-10 w-10": size === "icon",
          },
          className
        )}
        {...props}
      />
    )
  }
)
Button.displayName = "Button"

export { Button }
