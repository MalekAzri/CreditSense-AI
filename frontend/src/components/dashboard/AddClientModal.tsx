"use client";

import { useState } from "react";
import { X, User, Building2, Upload, Plus, Loader2 } from "lucide-react";
import { GlassCard } from "../ui/GlassCard";
import { Button } from "../ui/Button";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "@/lib/utils";

interface AddClientModalProps {
    onClose: () => void;
    onSuccess: () => void;
}

export function AddClientModal({ onClose, onSuccess }: AddClientModalProps) {
    const [clientType, setClientType] = useState<"individu" | "pme">("individu");
    const [loading, setLoading] = useState(false);
    const [files, setFiles] = useState<{ [key: string]: File | null }>({});

    const [formData, setFormData] = useState({
        nom: "",
        prenom: "",
        montant_credit: "",
        duree_mois: "12",
        objectif_credit: "",
        emploi: "",
        age: "",
    });

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleFileChange = (type: string, e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            setFiles(prev => ({ ...prev, [type]: e.target.files![0] }));
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);

        try {
            const submitData = new FormData();
            submitData.append("typeClient", clientType);
            Object.entries(formData).forEach(([key, value]) => {
                submitData.append(key, value);
            });

            Object.entries(files).forEach(([type, file]) => {
                if (file) submitData.append(`doc_${type}`, file);
            });

            const res = await fetch("/api/clients", {
                method: "POST",
                body: submitData,
            });

            if (!res.ok) throw new Error("Erreur lors de la création");

            onSuccess();
            onClose();
        } catch (err) {
            console.error("Error creating client:", err);
            alert("Erreur lors de la création du client");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="fixed inset-0 z-[150] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
            <motion.div
                initial={{ opacity: 0, scale: 0.95, y: 20 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.95, y: 20 }}
                className="w-full max-w-4xl"
            >
                <GlassCard className="p-0 border-white/10 shadow-2xl overflow-hidden bg-[#0F1219]">
                    <div className="flex justify-between items-center p-6 border-b border-white/5 bg-white/5">
                        <div className="flex items-center gap-3">
                            <div className="p-2 bg-indigo-500/20 rounded-lg">
                                <Plus className="w-5 h-5 text-indigo-400" />
                            </div>
                            <h2 className="text-xl font-bold text-white">Nouveau Dossier Client</h2>
                        </div>
                        <button onClick={onClose} className="p-2 hover:bg-white/5 rounded-full transition-colors">
                            <X className="w-5 h-5 text-slate-500" />
                        </button>
                    </div>

                    <form onSubmit={handleSubmit} className="p-8 space-y-8">
                        {/* Client Type Selector */}
                        <div className="flex gap-4 p-1 bg-slate-900/50 border border-slate-800 rounded-xl w-fit">
                            <button
                                type="button"
                                onClick={() => setClientType("individu")}
                                className={cn(
                                    "flex items-center gap-2 px-6 py-2 rounded-lg text-sm font-medium transition-all",
                                    clientType === "individu" ? "bg-indigo-500/10 text-indigo-400 shadow-inner" : "text-slate-500 hover:text-slate-300"
                                )}
                            >
                                <User className="w-4 h-4" /> Individu
                            </button>
                            <button
                                type="button"
                                onClick={() => setClientType("pme")}
                                className={cn(
                                    "flex items-center gap-2 px-6 py-2 rounded-lg text-sm font-medium transition-all",
                                    clientType === "pme" ? "bg-indigo-500/10 text-indigo-400 shadow-inner" : "text-slate-500 hover:text-slate-300"
                                )}
                            >
                                <Building2 className="w-4 h-4" /> PME / Entreprise
                            </button>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                            {/* Left Column: Info */}
                            <div className="space-y-6">
                                <div className="space-y-4">
                                    <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest">Informations Générales</h3>
                                    <div className="grid grid-cols-2 gap-4">
                                        <div className="space-y-1.5">
                                            <label className="text-xs text-slate-400 ml-1">Nom / Raison Sociale</label>
                                            <input
                                                required
                                                name="nom"
                                                value={formData.nom}
                                                onChange={handleInputChange}
                                                className="w-full bg-slate-900 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white focus:border-indigo-500/50 outline-none transition-all"
                                                placeholder="Ex: Ben Ali"
                                            />
                                        </div>
                                        <div className="space-y-1.5">
                                            <label className="text-xs text-slate-400 ml-1">Prénom (si indiv.)</label>
                                            <input
                                                name="prenom"
                                                value={formData.prenom}
                                                onChange={handleInputChange}
                                                className="w-full bg-slate-900 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white focus:border-indigo-500/50 outline-none transition-all disabled:opacity-30"
                                                placeholder="Ex: Amine"
                                                disabled={clientType === "pme"}
                                            />
                                        </div>
                                    </div>
                                    <div className="grid grid-cols-2 gap-4">
                                        <div className="space-y-1.5">
                                            <label className="text-xs text-slate-400 ml-1">Montant Souhaité (TND)</label>
                                            <input
                                                required
                                                type="number"
                                                name="montant_credit"
                                                value={formData.montant_credit}
                                                onChange={handleInputChange}
                                                className="w-full bg-slate-900 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white focus:border-indigo-500/50 outline-none transition-all"
                                                placeholder="15000"
                                            />
                                        </div>
                                        <div className="space-y-1.5">
                                            <label className="text-xs text-slate-400 ml-1">Durée (mois)</label>
                                            <select
                                                name="duree_mois"
                                                value={formData.duree_mois}
                                                onChange={handleInputChange}
                                                className="w-full bg-slate-900 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white focus:border-indigo-500/50 outline-none transition-all"
                                            >
                                                <option value="6">6 mois</option>
                                                <option value="12">12 mois</option>
                                                <option value="24">24 mois</option>
                                                <option value="36">36 mois</option>
                                                <option value="48">48 mois</option>
                                            </select>
                                        </div>
                                    </div>
                                    <div className="space-y-1.5">
                                        <label className="text-xs text-slate-400 ml-1">Objectif du Crédit</label>
                                        <input
                                            name="objectif_credit"
                                            value={formData.objectif_credit}
                                            onChange={handleInputChange}
                                            className="w-full bg-slate-900 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white focus:border-indigo-500/50 outline-none transition-all"
                                            placeholder="Ex: Achat de matériel agricole"
                                        />
                                    </div>
                                    <div className="grid grid-cols-2 gap-4">
                                        <div className="space-y-1.5">
                                            <label className="text-xs text-slate-400 ml-1">Âge</label>
                                            <input
                                                type="number"
                                                name="age"
                                                value={formData.age}
                                                onChange={handleInputChange}
                                                className="w-full bg-slate-900 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white focus:border-indigo-500/50 outline-none transition-all"
                                                placeholder="35"
                                            />
                                        </div>
                                        <div className="space-y-1.5">
                                            <label className="text-xs text-slate-400 ml-1">Profession / Secteur</label>
                                            <input
                                                name="emploi"
                                                value={formData.emploi}
                                                onChange={handleInputChange}
                                                className="w-full bg-slate-900 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white focus:border-indigo-500/50 outline-none transition-all"
                                                placeholder="Ingénieur"
                                            />
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* Right Column: Uploads */}
                            <div className="space-y-6">
                                <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest">Documents de Vérification</h3>
                                <div className="space-y-4">
                                    <DocUploadField
                                        label="Pièce d'Identité (CIN/Passport)"
                                        type="ID"
                                        file={files["ID"]}
                                        onChange={(e) => handleFileChange("ID", e)}
                                    />
                                    <DocUploadField
                                        label="Demande de Crédit (Formulaire BTS)"
                                        type="BTS_APP"
                                        file={files["BTS_APP"]}
                                        onChange={(e) => handleFileChange("BTS_APP", e)}
                                    />
                                    <DocUploadField
                                        label="Justificatif Financier (Bilan/Fiche)"
                                        type="FIN"
                                        file={files["FIN"]}
                                        onChange={(e) => handleFileChange("FIN", e)}
                                    />
                                </div>

                                <div className="p-4 bg-amber-500/5 border border-amber-500/20 rounded-2xl">
                                    <p className="text-[10px] leading-relaxed text-amber-500/80">
                                        <span className="font-bold uppercase">Note:</span> L'IA lancera automatiquement la vérification OCR et CLIP sur ces documents dès la création du dossier.
                                    </p>
                                </div>
                            </div>
                        </div>

                        <div className="flex justify-end gap-3 pt-6 border-t border-white/5">
                            <Button type="button" variant="ghost" onClick={onClose} disabled={loading}>Annuler</Button>
                            <Button type="submit" variant="primary" className="bg-indigo-600 hover:bg-indigo-500 px-8" disabled={loading}>
                                {loading ? (
                                    <>
                                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                        Analyse AI en cours...
                                    </>
                                ) : (
                                    "Créer le Dossier Client"
                                )}
                            </Button>
                        </div>
                    </form>
                </GlassCard>
            </motion.div>
        </div>
    );
}

function DocUploadField({ label, type, file, onChange }: { label: string, type: string, file: File | null, onChange: (e: React.ChangeEvent<HTMLInputElement>) => void }) {
    return (
        <div className="space-y-2">
            <label className="text-[11px] font-bold text-slate-400 uppercase ml-1 tracking-tighter">{label}</label>
            <div className={cn(
                "relative group border-2 border-dashed rounded-2xl transition-all h-20 flex items-center px-4 gap-4",
                file ? "border-emerald-500/30 bg-emerald-500/5" : "border-slate-800 hover:border-indigo-500/30 bg-slate-900/40"
            )}>
                <div className={cn(
                    "p-2 rounded-lg shrink-0",
                    file ? "bg-emerald-500/20 text-emerald-400" : "bg-slate-800 text-slate-500"
                )}>
                    {file ? <CheckCircle2 className="w-5 h-5" /> : <Upload className="w-5 h-5" />}
                </div>
                <div className="flex-grow overflow-hidden">
                    <p className={cn("text-xs font-medium truncate", file ? "text-emerald-400" : "text-slate-500")}>
                        {file ? file.name : "Cliquez ou glissez un fichier"}
                    </p>
                    <p className="text-[10px] text-slate-600 uppercase font-black">PNG, JPG ou PDF</p>
                </div>
                <input
                    type="file"
                    className="absolute inset-0 opacity-0 cursor-pointer"
                    onChange={onChange}
                    accept="image/*,application/pdf"
                />
            </div>
        </div>
    );
}

function CheckCircle2(props: any) {
    return (
        <svg
            {...props}
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
        >
            <path d="M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10z" />
            <path d="m9 12 2 2 4-4" />
        </svg>
    );
}
