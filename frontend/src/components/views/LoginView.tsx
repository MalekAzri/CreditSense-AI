"use client";

import { motion } from "framer-motion";
import { ShieldCheck, ArrowRight, Lock } from "lucide-react";
import { Button } from "../ui/Button";
import { useAuth } from "../providers/AuthProvider";
import { GlassCard } from "../ui/GlassCard";

export function LoginView() {
    const { login } = useAuth();

    return (
        <div className="h-full w-full flex items-center justify-center relative overflow-hidden bg-[#05070a]">
            {/* Background Ambience */}
            <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-indigo-600/20 rounded-full blur-[120px]" />
            <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-purple-600/20 rounded-full blur-[120px]" />

            <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5 }}
                className="w-full max-w-md p-4 z-10"
            >
                <GlassCard className="border-t border-white/10 shadow-2xl shadow-indigo-500/10">
                    <div className="text-center mb-8">
                        <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-indigo-500/20 mb-6">
                            <ShieldCheck className="w-8 h-8 text-indigo-400" />
                        </div>
                        <h1 className="text-3xl font-bold text-white mb-2">CreditSense AI</h1>
                        <p className="text-slate-400">Secure Analyst Workspace</p>
                    </div>

                    <div className="space-y-4">
                        <div className="space-y-2">
                            <label className="text-xs uppercase tracking-wider text-slate-500 font-semibold">Workspace Access Key</label>
                            <div className="relative">
                                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                                <input
                                    type="password"
                                    className="w-full bg-slate-900/50 border border-slate-700/50 rounded-xl px-12 py-3 text-slate-200 outline-none focus:border-indigo-500/50 focus:ring-1 focus:ring-indigo-500/50 transition-all placeholder:text-slate-600"
                                    placeholder="••••••••••••"
                                />
                            </div>
                        </div>

                        <Button onClick={login} className="w-full gap-2 group" size="lg">
                            Authenticate
                            <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                        </Button>

                        <p className="text-center text-xs text-slate-600 mt-6">
                            Restricted access for authorized financial analysts only.
                            <br />Security protocols active.
                        </p>
                    </div>
                </GlassCard>
            </motion.div>
        </div>
    );
}
