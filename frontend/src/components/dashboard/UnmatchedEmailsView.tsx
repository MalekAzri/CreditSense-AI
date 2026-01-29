"use client";

import React, { useState, useEffect } from "react";
import {
    Mail,
    Link as LinkIcon,
    UserPlus,
    Clock,
    AlertTriangle,
    CheckCircle2,
    ChevronDown,
    Search,
    Filter,
    Sparkles,
    Send
} from "lucide-react";
import { GlassCard } from "@/components/ui/GlassCard";
import { Button } from "@/components/ui/Button";
import { cn } from "@/lib/utils";
import { motion, AnimatePresence } from "framer-motion";
import EmailReplyModal from "./EmailReplyModal";

export function UnmatchedEmailsView() {
    const [emails, setEmails] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState("");
    const [selectedEmail, setSelectedEmail] = useState<any>(null);
    const [replyModal, setReplyModal] = useState<{
        isOpen: boolean;
        email: any;
        mode: 'auto' | 'manual';
    }>({
        isOpen: false,
        email: null,
        mode: 'manual'
    });

    useEffect(() => {
        fetchUnmatched();
    }, []);

    const fetchUnmatched = async () => {
        try {
            const res = await fetch("/api/emails/unmatched");
            if (res.ok) {
                const data = await res.json();
                setEmails(data);
            }
        } catch (err) {
            console.error("Error fetching unmatched emails:", err);
        } finally {
            setLoading(false);
        }
    };

    const filteredEmails = emails.filter(email =>
    (email.sender?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        email.subject?.toLowerCase().includes(searchTerm.toLowerCase()))
    );

    return (
        <div className="space-y-6">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h2 className="text-2xl font-bold text-white flex items-center gap-3">
                        <Mail className="w-6 h-6 text-indigo-400" />
                        Communications Orphelines
                    </h2>
                    <p className="text-slate-400 text-sm mt-1">
                        Emails reçus sans lien automatique avec un client existant
                    </p>
                </div>

                <div className="flex items-center gap-3">
                    <div className="relative group">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500 group-focus-within:text-indigo-400 transition-colors" />
                        <input
                            type="text"
                            placeholder="Rechercher un email..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="bg-slate-900/50 border border-slate-800 rounded-xl pl-10 pr-4 py-2 text-sm text-white focus:outline-none focus:border-indigo-500/50 transition-all w-64"
                        />
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Email List */}
                <div className="lg:col-span-1 space-y-4 max-h-[70vh] overflow-y-auto pr-2 custom-scrollbar">
                    {loading ? (
                        Array(3).fill(0).map((_, i) => (
                            <GlassCard key={i} className="p-4 animate-pulse">
                                <div className="h-4 bg-slate-800 rounded w-3/4 mb-3" />
                                <div className="h-3 bg-slate-800 rounded w-1/2" />
                            </GlassCard>
                        ))
                    ) : filteredEmails.length === 0 ? (
                        <div className="text-center py-20 bg-slate-900/20 rounded-3xl border border-slate-800/50">
                            <CheckCircle2 className="w-12 h-12 text-emerald-500/20 mx-auto mb-4" />
                            <p className="text-slate-500">Aucun email orphelin à traiter</p>
                        </div>
                    ) : (
                        filteredEmails.map((email) => (
                            <motion.div
                                key={email.id}
                                layoutId={`email-${email.id}`}
                                onClick={() => setSelectedEmail(email)}
                                className={cn(
                                    "cursor-pointer transition-all duration-300",
                                    selectedEmail?.id === email.id ? "scale-[1.02]" : "hover:scale-[1.01]"
                                )}
                            >
                                <GlassCard className={cn(
                                    "p-4 border-l-4 transition-colors",
                                    selectedEmail?.id === email.id ? "border-l-indigo-500 bg-indigo-500/5" : "border-l-slate-800 hover:border-l-slate-700"
                                )}>
                                    <div className="flex justify-between items-start mb-2">
                                        <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider truncate max-w-[150px]">
                                            {email.sender}
                                        </span>
                                        <span className="text-[10px] text-slate-500 whitespace-nowrap">
                                            {new Date(email.sentAt).toLocaleDateString()}
                                        </span>
                                    </div>
                                    <h4 className="text-sm font-semibold text-white mb-2 line-clamp-1">{email.subject}</h4>
                                    {email.intention && (
                                        <span className="bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 text-[9px] py-0 px-2 rounded-md font-bold uppercase">
                                            {email.intention}
                                        </span>
                                    )}
                                    {email.ton_urgence > 70 && (
                                        <span className="bg-red-500/10 text-red-400 border border-red-500/20 text-[9px] py-0 px-2 rounded-md font-bold uppercase">
                                            Urgent
                                        </span>
                                    )}
                                </GlassCard>
                            </motion.div>
                        ))
                    )}
                </div>

                {/* Email detail & Actions */}
                <div className="lg:col-span-2">
                    <AnimatePresence mode="wait">
                        {selectedEmail ? (
                            <motion.div
                                key={selectedEmail.id}
                                initial={{ opacity: 0, x: 20 }}
                                animate={{ opacity: 1, x: 0 }}
                                exit={{ opacity: 0, x: -20 }}
                            >
                                <GlassCard className="p-8 h-full flex flex-col">
                                    <div className="flex justify-between items-start mb-8">
                                        <div>
                                            <div className="flex items-center gap-2 text-slate-400 text-xs mb-1">
                                                <Clock className="w-3 h-3" />
                                                Reçu le {new Date(selectedEmail.sentAt).toLocaleString()}
                                            </div>
                                            <h3 className="text-xl font-bold text-white mb-1">{selectedEmail.subject}</h3>
                                            <p className="text-indigo-400 text-sm font-medium">{selectedEmail.sender}</p>
                                        </div>
                                        <div className="flex flex-col items-end gap-2">
                                            <div className="flex items-center gap-2 px-3 py-1 bg-amber-500/10 border border-amber-500/20 rounded-full">
                                                <AlertTriangle className="w-3.5 h-3.5 text-amber-500" />
                                                <span className="text-[10px] font-bold text-amber-500 uppercase">Non Associé</span>
                                            </div>
                                        </div>
                                    </div>

                                    <div className="flex-1 bg-slate-900/30 rounded-2xl p-6 mb-8 border border-slate-800/50">
                                        <p className="text-slate-300 leading-relaxed whitespace-pre-wrap text-sm">
                                            {selectedEmail.body}
                                        </p>
                                    </div>

                                    {selectedEmail.extractedData && (
                                        <div className="mb-8">
                                            <h4 className="text-[10px] text-slate-500 uppercase font-black tracking-widest mb-4">Analyse de l'IA</h4>
                                            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                                                {Object.entries(selectedEmail.extractedData).map(([key, value]: [string, any]) => (
                                                    value && value !== "None" && (
                                                        <div key={key} className="bg-white/5 p-3 rounded-xl border border-white/5">
                                                            <span className="text-[9px] text-slate-500 uppercase block mb-1">{key}</span>
                                                            <span className="text-xs font-medium text-indigo-300 truncate block">
                                                                {String(value)}
                                                            </span>
                                                        </div>
                                                    )
                                                ))}
                                            </div>
                                        </div>
                                    )}

                                    <div className="flex flex-wrap items-center gap-4 pt-6 border-t border-slate-800">
                                        <Button
                                            variant="primary"
                                            className="flex-1 min-w-[140px] bg-indigo-600 hover:bg-indigo-500 gap-2"
                                            onClick={() => setReplyModal({ isOpen: true, email: selectedEmail, mode: 'auto' })}
                                        >
                                            <Sparkles className="w-4 h-4" /> Réponse Auto
                                        </Button>
                                        <Button
                                            variant="secondary"
                                            className="flex-1 min-w-[140px] bg-slate-800 hover:bg-slate-700 border-slate-700 gap-2 text-white"
                                            onClick={() => setReplyModal({ isOpen: true, email: selectedEmail, mode: 'manual' })}
                                        >
                                            <Send className="w-4 h-4" /> Réponse Manuelle
                                        </Button>
                                        <Button
                                            variant="secondary"
                                            className="flex-1 min-w-[140px] bg-slate-800 hover:bg-slate-700 border-slate-700 gap-2 text-white"
                                            onClick={() => {/* TODO: Open Link Modal */ }}
                                        >
                                            <LinkIcon className="w-4 h-4" /> Lier au Client
                                        </Button>
                                    </div>
                                </GlassCard>
                            </motion.div>
                        ) : (
                            <div className="h-full flex flex-col items-center justify-center text-center p-20 bg-slate-900/10 rounded-3xl border border-dashed border-slate-800">
                                <div className="w-16 h-16 rounded-2xl bg-slate-900 border border-slate-800 flex items-center justify-center mb-6">
                                    <Mail className="w-8 h-8 text-slate-700" />
                                </div>
                                <h3 className="text-xl font-bold text-slate-400 mb-2">Sélectionnez un email</h3>
                                <p className="text-slate-500 max-w-xs mx-auto text-sm">
                                    Choisissez une communication orpheline dans la liste pour l'analyser et l'associer à un dossier client.
                                </p>
                            </div>
                        )}
                    </AnimatePresence>
                </div>
            </div>

            {replyModal.isOpen && (
                <EmailReplyModal
                    email={replyModal.email}
                    mode={replyModal.mode}
                    onClose={() => setReplyModal({ ...replyModal, isOpen: false })}
                />
            )}
        </div>
    );
}
