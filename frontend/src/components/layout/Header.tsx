"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard, Settings, LogOut, Bell, ShieldCheck } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "../ui/Button";
import { useAuth } from "../providers/AuthProvider";

import { useState, useEffect } from "react";

// We will use a mock logout function passed from props or context later
export function Header({ isAuthenticated, onLogout }: { isAuthenticated: boolean; onLogout: () => void }) {
    const pathname = usePathname();
    const { user } = useAuth();
    const [unreadCount, setUnreadCount] = useState(0);

    useEffect(() => {
        if (isAuthenticated) {
            const fetchUnread = async () => {
                try {
                    const res = await fetch("/api/messages/unread");
                    const data = await res.json();
                    if (typeof data.count === 'number') setUnreadCount(data.count);
                } catch (e) {
                    console.error("Error fetching unread messages:", e);
                }
            };

            fetchUnread();
            // Poll every 10 seconds for real-time feel
            const interval = setInterval(fetchUnread, 10000);
            return () => clearInterval(interval);
        }
    }, [isAuthenticated]);

    if (!isAuthenticated) return null;

    const navItems = [
        { name: "Dashboard", href: "/", icon: LayoutDashboard },
        { name: "Settings & Integrations", href: "/settings", icon: Settings },
    ];

    return (
        <header className="fixed top-0 left-0 right-0 z-50 glass-panel border-b border-white/5 px-8 h-20 flex items-center justify-between">
            <Link href="/" className="flex items-center gap-3 hover:opacity-80 transition-opacity cursor-pointer">
                <div className="bg-indigo-600/20 p-2 rounded-lg">
                    <ShieldCheck className="w-6 h-6 text-indigo-400" />
                </div>
                <div>
                    <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400">
                        CreditSense AI
                    </h1>
                    <p className="text-xs text-slate-500">Intelligent Risk Tracking</p>
                </div>
            </Link>

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
                <Link href="/">
                    <Button variant="ghost" size="sm" className="relative">
                        <Bell className="w-5 h-5" />
                        {unreadCount > 0 && (
                            <span className="absolute -top-1 -right-1 bg-red-600 text-white text-[10px] font-bold px-1.5 py-0.5 rounded-full min-w-[18px] h-[18px] flex items-center justify-center animate-pulse shadow-lg shadow-red-500/20">
                                {unreadCount > 99 ? "99+" : unreadCount}
                            </span>
                        )}
                    </Button>
                </Link>
                <div className="h-8 w-[1px] bg-white/10" />
                <div className="flex items-center gap-3">
                    <div className="text-right hidden sm:block">
                        <p className="text-sm font-medium text-white">{user?.name || "Financial Analyst"}</p>
                        <p className="text-xs text-slate-500 capitalize">{user?.role || "Risk Analyst"}</p>
                    </div>
                    <div className="relative">
                        <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-indigo-500 to-purple-600 border-2 border-white/10 flex items-center justify-center text-[10px] font-bold text-white uppercase shadow-lg shadow-indigo-500/20">
                            {user?.name?.split(" ").map((n: string) => n[0]).join("") || "AI"}
                        </div>
                        <div className="absolute bottom-0 right-0 w-3 h-3 bg-emerald-500 border-2 border-[#0B0E14] rounded-full shadow-[0_0_8px_rgba(16,185,129,0.4)]" />
                    </div>
                </div>
                <Button variant="ghost" size="sm" onClick={onLogout} className="text-red-400 hover:bg-red-500/10">
                    <LogOut className="w-5 h-5" />
                </Button>
            </div>
        </header>
    );
}
