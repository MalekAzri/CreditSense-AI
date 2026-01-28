"use client";

import { useEffect, useState } from "react";
import { GlassCard } from "../ui/GlassCard";
import { Users, MessageSquare } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

interface Analyst {
    id: number;
    nom: string;
    prenom: string;
    email: string;
    role: string;
    isOnline: boolean;
}

export function AnalystColleagues({ onOpenChat }: { onOpenChat: (analyst: Analyst) => void }) {
    const [analysts, setAnalysts] = useState<Analyst[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetch("/api/analysts")
            .then((res) => res.json())
            .then((data) => {
                if (Array.isArray(data)) {
                    setAnalysts(data);
                }
                setLoading(false);
            })
            .catch((err) => {
                console.error("Error fetching colleagues:", err);
                setLoading(false);
            });
    }, []);

    return (
        <GlassCard className="flex flex-col p-4 border-white/5 bg-slate-900/20">
            <div className="flex items-center gap-3 mb-6">
                <div className="p-2 rounded-lg bg-indigo-500/10">
                    <Users className="w-5 h-5 text-indigo-400" />
                </div>
                <h2 className="font-semibold text-slate-200">Colleagues</h2>
            </div>

            <div className="flex-1 overflow-y-auto space-y-3 pr-2 scrollbar-thin scrollbar-thumb-white/10">
                {loading ? (
                    <div className="space-y-3">
                        {[1, 2, 3].map((i) => (
                            <div key={i} className="h-14 bg-white/5 animate-pulse rounded-xl" />
                        ))}
                    </div>
                ) : (
                    <AnimatePresence>
                        {analysts.map((analyst) => (
                            <motion.div
                                key={analyst.id}
                                initial={{ opacity: 0, x: -10 }}
                                animate={{ opacity: 1, x: 0 }}
                                className="group flex items-center justify-between p-3 rounded-xl hover:bg-white/5 transition-all cursor-pointer border border-transparent hover:border-white/10"
                                onClick={() => onOpenChat(analyst)}
                            >
                                <div className="flex items-center gap-3">
                                    <div className="relative">
                                        <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-indigo-500/80 to-purple-600/80 flex items-center justify-center text-[10px] font-bold text-white uppercase border border-white/10">
                                            {analyst.prenom?.[0]}{analyst.nom?.[0]}
                                        </div>
                                        {analyst.isOnline && (
                                            <div className="absolute bottom-0 right-0 w-3 h-3 bg-emerald-500 border-2 border-[#161a22] rounded-full shadow-[0_0_8px_rgba(16,185,129,0.4)]" />
                                        )}
                                    </div>
                                    <div>
                                        <h3 className="text-sm font-medium text-slate-200 group-hover:text-white transition-colors">
                                            {analyst.prenom} {analyst.nom}
                                        </h3>
                                        <p className="text-[10px] text-slate-500 uppercase tracking-wider">{analyst.role}</p>
                                    </div>
                                </div>
                                <MessageSquare className="w-4 h-4 text-slate-600 group-hover:text-indigo-400 transition-colors opacity-0 group-hover:opacity-100" />
                            </motion.div>
                        ))}
                    </AnimatePresence>
                )}
                {!loading && analysts.length === 0 && (
                    <p className="text-xs text-center text-slate-500 mt-10">No other analysts found.</p>
                )}
            </div>
        </GlassCard>
    );
}
