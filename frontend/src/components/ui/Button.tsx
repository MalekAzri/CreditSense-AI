import { ButtonHTMLAttributes, forwardRef } from "react";
import { cn } from "@/lib/utils";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: "primary" | "secondary" | "ghost" | "danger";
    size?: "sm" | "md" | "lg";
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
    ({ className, variant = "primary", size = "md", ...props }, ref) => {
        return (
            <button
                ref={ref}
                className={cn(
                    "inline-flex items-center justify-center rounded-xl font-medium transition-all duration-200 disabled:opacity-50 disabled:pointer-events-none active:scale-95",
                    {
                        "bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-500/20": variant === "primary",
                        "bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700": variant === "secondary",
                        "bg-transparent hover:bg-white/5 text-slate-300": variant === "ghost",
                        "bg-red-500/10 hover:bg-red-500/20 text-red-400 border border-red-500/20": variant === "danger",
                        "h-9 px-4 text-sm": size === "sm",
                        "h-11 px-6 text-base": size === "md",
                        "h-14 px-8 text-lg": size === "lg",
                    },
                    className
                )}
                {...props}
            />
        );
    }
);
Button.displayName = "Button";

export { Button };
