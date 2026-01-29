"use client";

import React, { useState, useEffect } from "react";
import { Search, User, Check, X, Loader2 } from "lucide-react";
import { GlassCard } from "@/components/ui/GlassCard";
import { Button } from "@/components/ui/Button";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "@/lib/utils";

interface LinkClientModalProps {
    email: any;
    onClose: () => void;
    onSuccess: () => void;
}

export default function LinkClientModal({ email, onClose, onSuccess }: LinkClientModalProps) {
    const [searchTerm, setSearchTerm] = useState("");
    const [clients, setClients] = useState<any[]>([]);
    const [loading, setLoading] = useState(false);
    const [linking, setLinking] = useState(false);
    const [selectedClientId, setSelectedClientId] = useState<any>(null);

    useEffect(() => {
        const delayDebounceFn = setTimeout(() => {
            if (searchTerm.length >= 2) {
                searchClients();
            } else {
                setClients([]);
            }
        }, 300);

        return () => clearTimeout(delayDebounceFn);
    }, [searchTerm]);

    const searchClients = async () => {
        setLoading(true);
        try {
            const res = await fetch(`/api/clients?search=${searchTerm}`);
            if (res.ok) {
                const data = await res.json();
                setClients(data);
            }
        } catch (err) {
            console.error("Error searching clients:", err);
        } finally {
            setLoading(false);
        }
    };

    const handleLink = async () => {
        if (!selectedClientId) return;
        setLinking(true);
        try {
            const res = await fetch(`/api/emails/${email.id}/link`, {
                method: "PATCH",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ clientId: selectedClientId })
            });
            if (res.ok) {
                onSuccess();
                onClose();
            }
        } catch (err) {
            console.error("Error linking email:", err);
        } finally {
            setLinking(false);
        }
    };

    return (
        <div className="fixed inset-0 z-[130] flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
            <motion.div
                initial={{ opacity: 0, scale: 0.9, y: 20 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.9, y: 20 }}
                className="w-full max-w-md"
            >
                <GlassCard className="p-6 border-white/10 shadow-2xl bg-[#0F1219]">
                    <div className="flex justify-between items-center mb-6">
                        <h3 className="text-xl font-bold text-white flex items-center gap-2">
                            <User className="w-5 h-5 text-indigo-400" />
                            Lier au Client
                        </h3>
                        <Button variant="ghost" size="sm" onClick={onClose} className="hover:bg-white/5 rounded-full p-1 h-auto">
                            <X className="w-5 h-5" />
                        </Button>
                    </div>

                    <div className="relative mb-6">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                        <input
                            type="text"
                            placeholder="Rechercher par nom ou ID..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="w-full bg-slate-900/50 border border-slate-800 rounded-xl pl-10 pr-4 py-3 text-sm text-white focus:outline-none focus:border-indigo-500/50 transition-all font-medium"
                            autoFocus
                        />
                    </div>

                    <div className="space-y-2 max-h-[300px] overflow-y-auto mb-6 custom-scrollbar px-1">
                        {loading ? (
                            <div className="flex flex-col items-center justify-center py-8 text-slate-500">
                                <Loader2 className="w-6 h-6 animate-spin mb-2" />
                                <span className="text-xs">Recherche en cours...</span>
                            </div>
                        ) : clients.length > 0 ? (
                            clients.map((client) => (
                                <div
                                    key={client.id}
                                    onClick={() => setSelectedClientId(client.dbId)}
                                    className={cn(
                                        "p-3 rounded-xl border transition-all cursor-pointer flex items-center justify-between group",
                                        selectedClientId === client.dbId
                                            ? "bg-indigo-500/10 border-indigo-500/30"
                                            : "bg-white/5 border-white/5 hover:border-white/10"
                                    )}
                                >
                                    <div className="flex flex-col">
                                        <span className="text-sm font-bold text-white group-hover:text-indigo-400 transition-colors">
                                            {client.nom} {client.prenom}
                                        </span>
                                        <span className="text-[10px] text-slate-500 font-mono">{client.id}</span>
                                    </div>
                                    {selectedClientId === client.dbId && (
                                        <div className="bg-indigo-500 rounded-full p-1">
                                            <Check className="w-3 h-3 text-white" />
                                        </div>
                                    )}
                                </div>
                            ))
                        ) : searchTerm.length >= 2 ? (
                            <div className="text-center py-8 text-slate-500 text-xs">
                                Aucun client trouvé pour "{searchTerm}"
                            </div>
                        ) : (
                            <div className="text-center py-8 text-slate-500 text-xs">
                                Entrez au moins 2 caractères pour rechercher
                            </div>
                        )}
                    </div>

                    <div className="flex gap-3">
                        <Button
                            variant="secondary"
                            className="flex-1 bg-white/5 hover:bg-white/10 border-white/10 text-white font-bold"
                            onClick={onClose}
                        >
                            Annuler
                        </Button>
                        <Button
                            variant="primary"
                            className="flex-1 bg-indigo-600 hover:bg-indigo-500 font-bold gap-2"
                            disabled={!selectedClientId || linking}
                            onClick={handleLink}
                        >
                            {linking ? <Loader2 className="w-4 h-4 animate-spin" /> : <Check className="w-4 h-4" />}
                            Confirmer
                        </Button>
                    </div>
                </GlassCard>
            </motion.div>
        </div>
    );
}
