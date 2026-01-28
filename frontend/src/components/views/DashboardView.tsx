"use client";

import { motion, AnimatePresence } from "framer-motion";
import { GlassCard } from "../ui/GlassCard";
import { Button } from "../ui/Button";
import {
    Search,
    Filter,
    User,
    Building2,
    CheckCircle2,
    XCircle,
    AlertCircle,
    Paperclip,
    ArrowRight,
    TrendingUp
} from "lucide-react";
import { useRouter } from "next/navigation";
import { cn } from "@/lib/utils";
import { useState, useEffect } from "react";
import { AnalystColleagues } from "../chat/AnalystColleagues";
import { ChatDialog } from "../chat/ChatDialog";
import { useSession } from "next-auth/react";
import { AddClientModal } from "../dashboard/AddClientModal";
import { Plus } from "lucide-react";

export function DashboardView() {
    const router = useRouter();
    const [selectedAnalyst, setSelectedAnalyst] = useState<any>(null);
    const [clients, setClients] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const { data: session }: any = useSession();
    const currentUserId = session?.user?.id ? parseInt(session.user.id) : 0;
    const [showAddModal, setShowAddModal] = useState(false);

    const fetchClients = async () => {
        setLoading(true);
        try {
            const res = await fetch("/api/clients");
            const data = await res.json();
            if (Array.isArray(data)) {
                setClients(data);
            }
        } catch (err) {
            console.error("Error fetching dashboard data:", err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchClients();
    }, []);

    const getClassColor = (cls: string) => {
        switch (cls) {
            case "Bon": return "text-emerald-400 bg-emerald-500/10 border-emerald-500/20";
            case "Moyen": return "text-amber-400 bg-amber-500/10 border-amber-500/20";
            case "Mauvais": return "text-red-400 bg-red-500/10 border-red-500/20";
            default: return "text-slate-400";
        }
    };

    const getScoreColor = (score: number) => {
        if (score < 30) return "bg-emerald-500";
        if (score < 70) return "bg-amber-500";
        return "bg-red-500";
    };

    const getDocStatusColor = (status: string) => {
        switch (status) {
            case "Green": return "text-emerald-400";
            case "Yellow": return "text-amber-400";
            case "Red": return "text-red-400";
            default: return "text-slate-400";
        }
    };

    return (
        <div className="space-y-6 pb-12 w-full max-w-[1600px] mx-auto">
            {/* Header + Actions */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h1 className="text-3xl font-bold text-white tracking-tight">Vue Globale</h1>
                    <p className="text-slate-500">Gérez, triez et priorisez les demandes de crédit.</p>
                </div>
                <div className="flex gap-3">
                    <div className="relative group">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500 group-focus-within:text-indigo-400" />
                        <input
                            type="text"
                            placeholder="Rechercher un client..."
                            className="bg-slate-900/50 border border-slate-800 rounded-xl pl-9 pr-4 py-2.5 text-sm text-slate-200 outline-none focus:border-indigo-500/50 transition-all w-72"
                        />
                    </div>
                    <Button variant="secondary" className="gap-2 border-slate-800 bg-slate-900/50">
                        <Filter className="w-4 h-4" /> Filtres
                    </Button>
                    <Button
                        variant="primary"
                        className="gap-2 bg-indigo-600 hover:bg-indigo-500 shadow-lg shadow-indigo-500/20"
                        onClick={() => setShowAddModal(true)}
                    >
                        <Plus className="w-5 h-5" /> Nouveau Dossier
                    </Button>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
                {/* Main Table Area */}
                <div className="lg:col-span-3 space-y-6">
                    {/* Main Table */}
                    <GlassCard className="p-0 overflow-hidden border-slate-800/50">
                        <div className="overflow-x-auto scrollbar-none hover:scrollbar-thin scrollbar-thumb-slate-800/50 transition-all">
                            <table className="w-full text-left text-sm text-slate-400 border-collapse whitespace-nowrap">
                                <thead>
                                    <tr className="bg-slate-900/80 uppercase text-[11px] font-bold text-slate-500 tracking-wider">
                                        <th className="px-4 py-4 border-b border-slate-800">ID / Nom Client</th>
                                        <th className="px-4 py-4 border-b border-slate-800">Type</th>
                                        <th className="px-4 py-4 border-b border-slate-800">Classe</th>
                                        <th className="px-4 py-4 border-b border-slate-800">Risque IA</th>
                                        <th className="px-4 py-4 border-b border-slate-800">Rec. IA</th>
                                        <th className="px-4 py-4 border-b border-slate-800">Analyse</th>
                                        <th className="px-4 py-4 border-b border-slate-800 text-center">Diff.</th>
                                        <th className="px-4 py-4 border-b border-slate-800">Montant</th>
                                        <th className="px-4 py-4 border-b border-slate-800">Durée</th>
                                        <th className="px-4 py-4 border-b border-slate-800">Objectif</th>
                                        <th className="px-4 py-4 border-b border-slate-800">Remb. %</th>
                                        <th className="px-4 py-4 border-b border-slate-800">Âge/Emploi</th>
                                        <th className="px-4 py-4 border-b border-slate-800">Historique</th>
                                        <th className="px-4 py-4 border-b border-slate-800">Crédits</th>
                                        <th className="px-4 py-4 border-b border-slate-800">Logement</th>
                                        <th className="px-4 py-4 border-b border-slate-800">Documents</th>
                                        <th className="px-4 py-4 border-b border-slate-800 sticky right-0 bg-slate-900/95 shadow-[-10px_0_10px_-5px_rgba(0,0,0,0.3)]">Actions</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-slate-800/50">
                                    {clients.map((loan, idx) => {
                                        const isDiff = loan.iaRecommendation !== loan.analystDecision && loan.analystDecision !== "En attente";
                                        return (
                                            <motion.tr
                                                key={loan.id}
                                                initial={{ opacity: 0, y: 10 }}
                                                animate={{ opacity: 1, y: 0 }}
                                                transition={{ delay: idx * 0.03 }}
                                                className="hover:bg-indigo-500/5 transition-colors cursor-pointer group"
                                                onClick={() => router.push(`/dashboard/${loan.dbId}`)}
                                            >
                                                <td className="px-4 py-4">
                                                    <div className="flex flex-col">
                                                        <span className="text-white font-semibold">{loan.applicant}</span>
                                                        <span className="text-[10px] font-mono text-slate-500 tracking-tighter">{loan.id}</span>
                                                    </div>
                                                </td>
                                                <td className="px-4 py-4">
                                                    {loan.clientType === "Individu" ? (
                                                        <div className="flex items-center gap-1.5"><User className="w-3.5 h-3.5" /> <span className="text-xs">Indiv.</span></div>
                                                    ) : (
                                                        <div className="flex items-center gap-1.5"><Building2 className="w-3.5 h-3.5" /> <span className="text-xs">PME</span></div>
                                                    )}
                                                </td>
                                                <td className="px-4 py-4">
                                                    <span className={cn("px-2 py-0.5 rounded-md text-[10px] font-bold border", getClassColor(loan.class))}>
                                                        {loan.class}
                                                    </span>
                                                </td>
                                                <td className="px-4 py-4">
                                                    <div className="flex items-center gap-2">
                                                        <div className="w-12 h-1.5 bg-slate-800 rounded-full overflow-hidden">
                                                            <div className={cn("h-full rounded-full transition-all", getScoreColor(loan.iaScore))} style={{ width: `${loan.iaScore}%` }} />
                                                        </div>
                                                        <span className="text-[10px] font-bold text-white">{loan.iaScore}/100</span>
                                                    </div>
                                                </td>
                                                <td className="px-4 py-4">
                                                    {loan.iaRecommendation === "Oui" ? (
                                                        <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                                                    ) : (
                                                        <XCircle className="w-4 h-4 text-red-500" />
                                                    )}
                                                </td>
                                                <td className="px-4 py-4">
                                                    <div className="flex items-center gap-1.5">
                                                        {loan.analystDecision === "Oui" && <CheckCircle2 className="w-4 h-4 text-emerald-500" />}
                                                        {loan.analystDecision === "Non" && <XCircle className="w-4 h-4 text-red-500" />}
                                                        {loan.analystDecision === "En attente" && <AlertCircle className="w-4 h-4 text-amber-500" />}
                                                        <span className="text-xs">{loan.analystDecision}</span>
                                                    </div>
                                                </td>
                                                <td className="px-4 py-4 text-center">
                                                    {isDiff ? (
                                                        <div className="flex items-center justify-center">
                                                            <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse shadow-[0_0_8px_rgba(239,68,68,0.5)]" title="Écart IA vs Analyste" />
                                                        </div>
                                                    ) : (
                                                        <div className="flex items-center justify-center opacity-10">
                                                            <CheckCircle2 className="w-3.5 h-3.5 text-slate-400" />
                                                        </div>
                                                    )}
                                                </td>
                                                <td className="px-4 py-4 text-white font-medium">
                                                    {new Intl.NumberFormat('fr-TN', { style: 'currency', currency: 'TND', maximumFractionDigits: 0 }).format(loan.creditAmount)}
                                                </td>
                                                <td className="px-4 py-4 text-xs">{loan.duration} m</td>
                                                <td className="px-4 py-4">
                                                    <span className="text-xs truncate max-w-[100px] block" title={loan.creditObjective}>{loan.creditObjective}</span>
                                                </td>
                                                <td className="px-4 py-4">
                                                    <div className="flex items-center gap-1.5">
                                                        <TrendingUp className="w-3 h-3 text-slate-500" />
                                                        <span className="text-xs">{loan.repaymentRate}%</span>
                                                    </div>
                                                </td>
                                                <td className="px-4 py-4">
                                                    <div className="flex flex-col text-[10px]">
                                                        <span className="text-slate-300">{loan.age !== "-" ? `${loan.age} ans` : "-"}</span>
                                                        <span className="text-slate-500 truncate max-w-[80px]">{loan.employment}</span>
                                                    </div>
                                                </td>
                                                <td className="px-4 py-4">
                                                    <span className="text-xs text-slate-500 truncate max-w-[120px] block font-light italic" title={loan.creditHistory}>
                                                        {loan.creditHistory}
                                                    </span>
                                                </td>
                                                <td className="px-4 py-4 text-center">
                                                    <span className="text-xs bg-slate-800/50 px-2 py-0.5 rounded text-slate-300">{loan.bankCreditsCount}</span>
                                                </td>
                                                <td className="px-4 py-4 text-xs font-light tracking-wide">{loan.housing}</td>
                                                <td className="px-4 py-4">
                                                    <div className="flex items-center gap-2">
                                                        <div className="flex items-center gap-1 text-[10px] text-slate-300 font-mono">
                                                            <Paperclip className="w-3 h-3" />
                                                            {loan.documentsCount.uploaded}/{loan.documentsCount.total}
                                                        </div>
                                                        <div
                                                            className={cn("w-2 h-2 rounded-full shadow-[0_0_8px_currentColor]", getDocStatusColor(loan.documentStatus))}
                                                            style={{ backgroundColor: 'currentColor' }}
                                                        />
                                                    </div>
                                                </td>
                                                <td className="px-4 py-4 sticky right-0 bg-slate-900/95 shadow-[-10px_0_10px_-5px_rgba(0,0,0,0.3)] border-b border-slate-800 text-right">
                                                    <button className="p-2 hover:bg-white/5 rounded-lg transition-colors group-hover:text-indigo-400">
                                                        <ArrowRight className="w-4 h-4" />
                                                    </button>
                                                </td>
                                            </motion.tr>
                                        );
                                    })}
                                </tbody>
                            </table>
                        </div>
                    </GlassCard>
                </div>

                {/* Sidebar Widget Area */}
                <div className="lg:col-span-1 border-l border-white/5 pl-2">
                    <AnalystColleagues onOpenChat={setSelectedAnalyst} />
                </div>
            </div>

            {/* Chat Modal */}
            {selectedAnalyst && (
                <ChatDialog
                    analyst={selectedAnalyst}
                    currentUserId={currentUserId}
                    onClose={() => setSelectedAnalyst(null)}
                />
            )}
            {/* Client Add Modal */}
            <AnimatePresence>
                {showAddModal && (
                    <AddClientModal
                        onClose={() => setShowAddModal(false)}
                        onSuccess={() => fetchClients()}
                    />
                )}
            </AnimatePresence>
        </div>
    );
}
