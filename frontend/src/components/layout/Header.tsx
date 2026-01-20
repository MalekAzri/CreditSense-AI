"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard, Settings, LogOut, Bell, ShieldCheck } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "../ui/Button";

// We will use a mock logout function passed from props or context later
export function Header({ isAuthenticated, onLogout }: { isAuthenticated: boolean; onLogout: () => void }) {
    const pathname = usePathname();

    if (!isAuthenticated) return null;

    const navItems = [
        { name: "Dashboard", href: "/", icon: LayoutDashboard },
        // Merged Integrations into Settings as requested, or keep separate?
        // User asked "via the header... access section to integrate apis" and "configure email".
        // "Settings" usually implies both. The user accepted merging them.
        { name: "Settings & Integrations", href: "/settings", icon: Settings },
    ];

    return (
        <header className="fixed top-0 left-0 right-0 z-50 glass-panel border-b border-white/5 px-8 h-20 flex items-center justify-between">
            <div className="flex items-center gap-3">
                <div className="bg-indigo-600/20 p-2 rounded-lg">
                    <ShieldCheck className="w-6 h-6 text-indigo-400" />
                </div>
                <div>
                    <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400">
                        CreditSense AI
                    </h1>
                    <p className="text-xs text-slate-500">Intelligent Risk Tracking</p>
                </div>
            </div>

            <nav className="hidden md:flex items-center gap-1">
                {navItems.map((item) => {
                    const isActive = pathname === item.href;
                    return (
                        <Link key={item.href} href={item.href}>
                            <Button
                                variant="ghost"
                                className={cn(
                                    "gap-2 text-slate-400 hover:text-white",
                                    isActive && "bg-white/5 text-indigo-400"
                                )}
                            >
                                <item.icon className="w-4 h-4" />
                                {item.name}
                            </Button>
                        </Link>
                    );
                })}
            </nav>

            <div className="flex items-center gap-4">
                <Button variant="ghost" size="sm" className="relative">
                    <Bell className="w-5 h-5" />
                    <span className="absolute top-2 right-2 w-2 h-2 bg-red-500 rounded-full animate-pulse" />
                </Button>
                <div className="h-8 w-[1px] bg-white/10" />
                <div className="flex items-center gap-3">
                    <div className="text-right hidden sm:block">
                        <p className="text-sm font-medium text-white">Sarah Connor</p>
                        <p className="text-xs text-slate-500">Senior Risk Analyst</p>
                    </div>
                    <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-indigo-500 to-purple-600 border-2 border-white/10" />
                </div>
                <Button variant="ghost" size="sm" onClick={onLogout} className="text-red-400 hover:bg-red-500/10">
                    <LogOut className="w-5 h-5" />
                </Button>
            </div>
        </header>
    );
}
