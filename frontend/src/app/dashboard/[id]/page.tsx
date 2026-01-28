"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { mockLoans, mockAnalysis } from "@/lib/mockData";
import { GlassCard } from "@/components/ui/GlassCard";
import { Button } from "@/components/ui/Button";
import {
    ArrowLeft,
    FileText,
    User,
    Fingerprint,
    ShieldCheck,
    AlertTriangle,
    CheckCircle2,
    XCircle,
    Calendar,
    MessageSquare,
    ExternalLink,
    Search,
    BrainCircuit,
    BarChart3,
    Ban,
    FileSearch,
    ScanLine,
    Mail,
    Mic,
    Play,
    Pause,
    History
} from "lucide-react";
import { cn } from "@/lib/utils";
import { motion, AnimatePresence } from "framer-motion";

export default function ClientDetailsPage() {
    const { id } = useParams();
    const router = useRouter();
    const loanId = id as string;
    const [loan, setLoan] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState<"documents" | "details" | "analysis" | "communications">("documents");
    const [reanalyzingDocs, setReanalyzingDocs] = useState<Set<number>>(new Set());

    useEffect(() => {
        const fetchLoanDetails = async () => {
            try {
                const res = await fetch(`/api/clients/${loanId}`);
                if (!res.ok) throw new Error("Dossier non trouvé");
                const data = await res.json();
                setLoan(data);
            } catch (err) {
                console.error("Error fetching client details:", err);
                setLoan(null);
            } finally {
                setLoading(false);
            }
        };

        fetchLoanDetails();
    }, [loanId]);

    const handleReanalyze = async (documentId: number) => {
        setReanalyzingDocs(prev => new Set(prev).add(documentId));
        try {
            const res = await fetch(`/api/documents/${documentId}/reanalyze`, {
                method: "POST"
            });
            const data = await res.json();

            if (data.success) {
                // Refresh loan details to get updated scores
                const refreshRes = await fetch(`/api/clients/${loanId}`);
                const refreshedData = await refreshRes.json();
                setLoan(refreshedData);
            } else {
                alert(data.error || "Échec de la re-analyse");
            }
        } catch (error) {
            console.error("Error reanalyzing document:", error);
            alert("Erreur lors de la re-analyse du document");
        } finally {
            setReanalyzingDocs(prev => {
                const newSet = new Set(prev);
                newSet.delete(documentId);
                return newSet;
            });
        }
    };

    const analysis = mockAnalysis[loanId] || mockAnalysis[loan?.id] || mockAnalysis["LN-2024-001"];

    if (loading) return (
        <div className="flex flex-col items-center justify-center h-[60vh] gap-4">
            <div className="w-12 h-12 border-4 border-indigo-500/20 border-t-indigo-500 rounded-full animate-spin" />
            <p className="text-slate-500 animate-pulse">Chargement du dossier sécurisé...</p>
        </div>
    );

    if (!loan) return <div className="p-8 text-center text-slate-400">Dossier non trouvé.</div>;

    const tabs = [
        { id: "documents", label: "Documents", icon: FileText },
        { id: "details", label: "Détails Client", icon: User },
        { id: "communications", label: "Communications", icon: History },
        { id: "analysis", label: "Analyse & Résultat IA", icon: BrainCircuit },
    ];

    return (
        <div className="space-y-6 pb-20 max-w-7xl mx-auto">
            {/* Header Area */}
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
                <div className="space-y-4">
                    <Button variant="ghost" size="sm" onClick={() => router.back()} className="text-slate-400 hover:text-white -ml-2">
                        <ArrowLeft className="w-4 h-4 mr-2" /> Retour au Dashboard
                    </Button>
                    <div className="flex items-center gap-4">
                        <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-indigo-500/20 to-purple-500/20 border border-indigo-500/20 flex items-center justify-center">
                            {(loan.clientType === "Individu" || loan.typeClient === "individu") ? <User className="w-8 h-8 text-indigo-400" /> : <Fingerprint className="w-8 h-8 text-indigo-400" />}
                        </div>
                        <div>
                            <h1 className="text-3xl font-bold text-white leading-tight">
                                {loan.applicant || (loan.prenom && loan.nom ? `${loan.prenom} ${loan.nom}` : loan.nom || "Dossier sans nom")}
                            </h1>
                            <div className="flex items-center gap-3 mt-1">
                                <span className="text-slate-500 font-mono text-sm">{loanId}</span>
                                <span className="w-1 h-1 rounded-full bg-slate-700" />
                                <span className={cn("text-xs font-bold px-2 py-0.5 rounded border",
                                    loan.classe === "bon client" || loan.class === "Bon" ? "text-emerald-400 border-emerald-500/30" :
                                        loan.classe === "mauvais client" || loan.class === "Mauvais" ? "text-red-400 border-red-500/30" : "text-amber-400 border-amber-500/30"
                                )}>
                                    Classe {loan.classe || loan.class || "N/A"}
                                </span>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="flex items-center gap-3">
                    <Button variant="secondary" className="bg-slate-900 border-slate-800">Assigner à...</Button>
                    <Button variant="primary" className="bg-indigo-600 hover:bg-indigo-500 shadow-lg shadow-indigo-500/20">Valider Dossier</Button>
                </div>
            </div>

            {/* Custom Tabs Navigation */}
            <div className="flex gap-1 p-1 bg-slate-900/50 border border-slate-800/50 rounded-xl w-fit">
                {tabs.map((tab) => {
                    const Icon = tab.icon;
                    return (
                        <button
                            key={tab.id}
                            onClick={() => setActiveTab(tab.id as any)}
                            className={cn(
                                "flex items-center gap-2 px-6 py-2.5 rounded-lg text-sm font-medium transition-all",
                                activeTab === tab.id
                                    ? "bg-indigo-500/10 text-indigo-400 shadow-inner"
                                    : "text-slate-500 hover:text-slate-300 hover:bg-white/5"
                            )}
                        >
                            <Icon className="w-4 h-4" />
                            {tab.label}
                        </button>
                    );
                })}
            </div>

            {/* Content Area with AnimatePresence */}
            <AnimatePresence mode="wait">
                <motion.div
                    key={activeTab}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    transition={{ duration: 0.2 }}
                >
                    {activeTab === "documents" && <DocumentsTab loan={loan} reanalyzingDocs={reanalyzingDocs} handleReanalyze={handleReanalyze} />}
                    {activeTab === "details" && <DetailsTab loan={loan} />}
                    {activeTab === "communications" && <CommunicationsTab analysis={analysis} loan={loan} />}
                    {activeTab === "analysis" && <AnalysisTab analysis={analysis} loan={loan} />}
                </motion.div>
            </AnimatePresence>
        </div>
    );
}

function DocumentsTab({ loan, reanalyzingDocs, handleReanalyze }: { loan: any; reanalyzingDocs: Set<number>; handleReanalyze: (docId: number) => void }) {
    const categories = loan.typeClient === "individu" || loan.clientType === "Individu"
        ? ["Identité", "Demande", "Financier", "Domicile"]
        : ["Entreprise", "Financier", "Demande", "Dirigeant"];

    const dbDocuments = loan.documents || [];

    // Map doc type to UI category
    const getCategoryForType = (type: string) => {
        const t = type.toLowerCase();
        if (t.includes("cin") || t.includes("identite") || t.includes("passeport")) return "Identité";
        if (t.includes("bts") || t.includes("formulaire") || t.includes("demande")) return "Demande";
        if (t.includes("paie") || t.includes("salaire") || t.includes("financier") || t.includes("bilan")) return "Financier";
        if (t.includes("domicile") || t.includes("facture") || t.includes("residence")) return "Domicile";
        if (t.includes("dirigeant") || t.includes("statuts")) return loan.clientType === "PME" ? "Entreprise" : "Identité";
        return "Demande"; // Default
    };

    return (
        <div className="grid grid-cols-1 gap-12">
            {categories.map((category) => {
                const docs = dbDocuments.filter((d: any) => getCategoryForType(d.type) === category);
                return (
                    <div key={category} className="space-y-6">
                        <div className="flex items-center gap-2 text-slate-400 px-2">
                            <h3 className="font-bold text-xl text-white">{category}</h3>
                            <div className="h-px bg-slate-800 flex-grow ml-4 opacity-30" />
                        </div>

                        <div className="grid grid-cols-1 gap-6">
                            {docs.length > 0 ? docs.map((doc: any, i: number) => {
                                const isSensitive = doc.type.toLowerCase().includes("cin") ||
                                    doc.type.toLowerCase().includes("passport") ||
                                    doc.type.toLowerCase().includes("passeport");

                                return (
                                    <GlassCard key={i} className="p-0 overflow-hidden flex flex-col md:flex-row h-auto border-slate-800 hover:border-indigo-500/30 transition-all group min-h-[220px]">
                                        <div className="w-full md:w-80 bg-slate-950 relative overflow-hidden flex items-center justify-center border-b md:border-b-0 md:border-r border-slate-800 group-hover:bg-slate-900 transition-colors shrink-0">
                                            {/* Document Preview */}
                                            {doc.url ? (
                                                <img
                                                    src={`/api/documents/view?path=${encodeURIComponent(doc.url)}`}
                                                    alt={doc.type}
                                                    className={cn(
                                                        "w-full h-full object-cover transition-all duration-500 group-hover:scale-105",
                                                        isSensitive && "blur-xl"
                                                    )}
                                                />
                                            ) : (
                                                <FileText className="w-16 h-16 text-slate-800 group-hover:text-indigo-500/30 transition-colors" />
                                            )}

                                            <div className="absolute top-3 left-3 z-20">
                                                <span className={cn("px-2 py-0.5 rounded text-[10px] font-bold shadow-lg uppercase",
                                                    doc.statut === "valide" || doc.statut === "Valide" ? "bg-emerald-500/90 text-white" :
                                                        doc.statut === "rejete" || doc.statut === "Rejeté" ? "bg-red-500/90 text-white" : "bg-amber-500/90 text-white"
                                                )}>
                                                    {doc.statut || "En attente"}
                                                </span>
                                            </div>

                                            {isSensitive && (
                                                <div className="absolute inset-0 z-10 flex flex-col items-center justify-center bg-black/40 backdrop-blur-sm opacity-100 group-hover:opacity-0 transition-opacity">
                                                    <ShieldCheck className="w-8 h-8 text-white/50 mb-2" />
                                                    <span className="text-[10px] font-black uppercase tracking-tighter text-white/60">Contenu Sensible</span>
                                                </div>
                                            )}

                                            <div className="absolute inset-0 bg-gradient-to-r from-slate-950/20 to-transparent opacity-40 z-10" />

                                            <button className="absolute inset-0 bg-indigo-500/0 hover:bg-indigo-500/5 transition-colors flex items-center justify-center group/btn z-20">
                                                <span className="bg-white/10 backdrop-blur-md border border-white/20 px-4 py-2 rounded-full text-xs font-medium text-white opacity-0 group-hover:opacity-100 transition-all translate-y-2 group-hover:translate-y-0">
                                                    Agrandir l'aperçu
                                                </span>
                                            </button>
                                        </div>

                                        <div className="p-6 flex-grow flex flex-col justify-between gap-6">
                                            <div className="flex flex-col md:flex-row justify-between items-start gap-4">
                                                <div className="space-y-1">
                                                    <h4 className="font-bold text-white text-lg">{doc.type}</h4>
                                                    <div className="flex items-center gap-2 text-xs text-slate-500">
                                                        <Calendar className="w-3 h-3" />
                                                        {new Date(doc.createdAt).toLocaleDateString()}
                                                    </div>
                                                </div>

                                                <div className="grid grid-cols-2 gap-3 w-full md:w-auto">
                                                    <div className="bg-slate-900/50 p-3 rounded-xl border border-white/5 flex flex-col justify-center min-w-[120px]">
                                                        <div className="flex items-center gap-1.5 text-[10px] text-slate-500 uppercase font-bold mb-1">
                                                            <FileSearch className="w-3 h-3 text-emerald-400" /> OCR Score
                                                        </div>
                                                        <div className="flex items-end gap-1">
                                                            <span className="text-xl font-bold text-white">{Math.round(doc.ocrScore || 0)}%</span>
                                                            <div className="w-full h-1 bg-slate-800 rounded-full mb-1.5 ml-2">
                                                                <div className="h-full bg-emerald-500 rounded-full" style={{ width: `${doc.ocrScore || 0}%` }} />
                                                            </div>
                                                        </div>
                                                    </div>
                                                    <div className="bg-slate-900/50 p-3 rounded-xl border border-white/5 flex flex-col justify-center min-w-[120px]">
                                                        <div className="flex items-center gap-1.5 text-[10px] text-slate-500 uppercase font-black tracking-tighter mb-1">
                                                            <ScanLine className="w-3 h-3 text-indigo-400" /> CLIP Match
                                                        </div>
                                                        <div className="flex items-end gap-1">
                                                            <span className="text-xl font-bold text-white">{Math.round(doc.clipScore || 0)}%</span>
                                                            <div className="w-full h-1 bg-slate-800 rounded-full mb-1.5 ml-2">
                                                                <div className="h-full bg-indigo-500 rounded-full" style={{ width: `${doc.clipScore || 0}%` }} />
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>

                                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                                <div className="flex items-start gap-3 p-4 bg-indigo-500/5 rounded-2xl border border-indigo-500/10">
                                                    <BrainCircuit className="w-5 h-5 text-indigo-400 shrink-0 mt-0.5" />
                                                    <div className="text-xs leading-relaxed text-slate-300">
                                                        <span className="text-indigo-400 font-bold block mb-1 uppercase tracking-wider text-[10px]">Analyse IA</span>
                                                        {doc.statut === "valide" ? "Cohérence documentaire confirmée par les modèles CLIP/OCR." : "Incohérence détectée ou en attente d'analyse profonde."}
                                                    </div>
                                                </div>

                                                {doc.commentaire ? (
                                                    <div className="flex items-start gap-3 p-4 bg-white/5 rounded-2xl border border-white/5">
                                                        <MessageSquare className="w-5 h-5 text-slate-500 shrink-0 mt-0.5" />
                                                        <div className="text-xs leading-relaxed text-slate-400 italic">
                                                            <span className="text-slate-300 font-bold not-italic block mb-1 uppercase tracking-wider text-[10px]">Note Analyste</span>
                                                            "{doc.commentaire}"
                                                        </div>
                                                    </div>
                                                ) : (
                                                    <div className="flex items-center justify-center p-4 border border-dashed border-slate-800 rounded-2xl opacity-40">
                                                        <span className="text-[10px] uppercase font-bold text-slate-600">Aucun commentaire</span>
                                                    </div>
                                                )}
                                            </div>

                                            <div className="flex gap-3 pt-2 justify-between">
                                                <Button
                                                    variant="secondary"
                                                    className="px-4 py-2 h-auto text-xs bg-indigo-500/10 hover:bg-indigo-500/20 border-indigo-500/30 hover:border-indigo-500/50 transition-all flex items-center gap-2"
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        handleReanalyze(doc.id);
                                                    }}
                                                    disabled={reanalyzingDocs.has(doc.id)}
                                                >
                                                    {reanalyzingDocs.has(doc.id) ? (
                                                        <>
                                                            <div className="w-3 h-3 border-2 border-indigo-400/30 border-t-indigo-400 rounded-full animate-spin" />
                                                            Analyse en cours...
                                                        </>
                                                    ) : (
                                                        <>
                                                            <BrainCircuit className="w-3 h-3" />
                                                            Refaire l'analyse
                                                        </>
                                                    )}
                                                </Button>
                                                <div className="flex gap-3">
                                                    <Button variant="secondary" className="px-6 py-2 h-auto text-xs bg-transparent hover:bg-red-500/10 hover:text-red-400 hover:border-red-500/20 transition-all">Rejeter</Button>
                                                    <Button variant="primary" className="px-8 py-2 h-auto text-xs bg-emerald-600 hover:bg-emerald-500 border-none shadow-lg shadow-emerald-500/10">Valider</Button>
                                                </div>
                                            </div>
                                        </div>
                                    </GlassCard>
                                );
                            }) : (
                                <div className="p-12 rounded-2xl border border-dashed border-slate-800 flex flex-col items-center justify-center text-slate-600 gap-2">
                                    <Search className="w-10 h-10 opacity-20" />
                                    <p className="text-sm font-medium">Aucun document téléchargé dans cette catégorie</p>
                                </div>
                            )}
                        </div>
                    </div>
                );
            })}
        </div>
    );
}

function CommunicationsTab({ analysis, loan }: { analysis: any; loan: any }) {
    const emails = loan.emails || [];
    const vocals = loan.vocaux || [];
    const [selectedEmail, setSelectedEmail] = useState<any>(null);

    return (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 relative">
            {/* Modal pour lire le mail complet */}
            <AnimatePresence>
                {selectedEmail && (
                    <div className="fixed inset-0 z-[110] flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
                        <motion.div
                            initial={{ opacity: 0, scale: 0.9, y: 20 }}
                            animate={{ opacity: 1, scale: 1, y: 0 }}
                            exit={{ opacity: 0, scale: 0.9, y: 20 }}
                            className="w-full max-w-2xl"
                        >
                            <GlassCard className="p-8 border-white/10 shadow-2xl bg-[#0F1219]">
                                <div className="flex justify-between items-start mb-6">
                                    <div>
                                        <h3 className="text-2xl font-bold text-white mb-1">{selectedEmail.subject}</h3>
                                        <div className="flex items-center gap-3 text-sm text-slate-500">
                                            <span>{new Date(selectedEmail.sentAt).toLocaleString()}</span>
                                            <span className="w-1 h-1 rounded-full bg-slate-700" />
                                            <span className="text-indigo-400 font-medium">De: Client</span>
                                        </div>
                                    </div>
                                    <Button variant="ghost" size="sm" onClick={() => setSelectedEmail(null)} className="hover:bg-white/5 rounded-full">
                                        Fermer
                                    </Button>
                                </div>

                                <div className="bg-white/[0.03] rounded-2xl p-6 border border-white/5 min-h-[200px] mb-8">
                                    <p className="text-slate-300 leading-relaxed whitespace-pre-wrap">{selectedEmail.body}</p>
                                </div>

                                <div className="grid grid-cols-3 gap-4 p-4 bg-indigo-500/5 rounded-2xl border border-indigo-500/10">
                                    <div className="flex flex-col">
                                        <span className="text-[10px] text-slate-500 uppercase font-black mb-1">Intention</span>
                                        <span className="text-xs font-bold text-white">{selectedEmail.intention || "N/A"}</span>
                                    </div>
                                    <div className="flex flex-col">
                                        <span className="text-[10px] text-slate-500 uppercase font-black mb-1">Ton Estimé</span>
                                        <span className="text-xs font-bold text-indigo-300">{selectedEmail.ton_estime || "N/A"}</span>
                                    </div>
                                    <div className="flex flex-col">
                                        <span className="text-[10px] text-slate-500 uppercase font-black mb-1">Fiabilité IA</span>
                                        <span className="text-xs font-bold text-emerald-400">{Math.round(selectedEmail.confiance || 0)}%</span>
                                    </div>
                                </div>
                            </GlassCard>
                        </motion.div>
                    </div>
                )}
            </AnimatePresence>

            {/* Emails Section */}
            <div className="space-y-6">
                <div className="flex items-center gap-3 px-2">
                    <div className="p-2 bg-blue-500/20 rounded-lg">
                        <Mail className="w-5 h-5 text-blue-400" />
                    </div>
                    <h3 className="font-bold text-xl text-white">Mails du Client</h3>
                </div>

                <div className="space-y-4">
                    {emails.length > 0 ? emails.map((email: any, i: number) => (
                        <GlassCard key={i} className="p-6 border-slate-800 hover:border-blue-500/30 transition-all group cursor-pointer" onClick={() => setSelectedEmail(email)}>
                            <div className="flex justify-between items-start mb-3">
                                <h4 className="font-bold text-white group-hover:text-blue-400 transition-colors">{email.subject}</h4>
                                <span className="text-[10px] text-slate-500 bg-white/5 px-2 py-0.5 rounded-md font-mono">
                                    {new Date(email.sentAt).toLocaleDateString()}
                                </span>
                            </div>
                            <p className="text-sm text-slate-400 line-clamp-2 mb-4 italic">"{email.body}"</p>

                            <div className="flex items-center justify-between pt-4 border-t border-white/5">
                                <div className="flex items-center gap-6">
                                    <div className="flex flex-col">
                                        <span className="text-[9px] text-slate-500 uppercase font-black tracking-tighter">Intention</span>
                                        <span className={cn("text-xs font-bold",
                                            email.intention === "Confiance" ? "text-emerald-400" :
                                                email.intention === "Stress" ? "text-amber-400" :
                                                    email.intention === "Doute" ? "text-red-400" : "text-slate-300"
                                        )}>{email.intention || "N/A"}</span>
                                    </div>
                                    <div className="flex flex-col">
                                        <span className="text-[9px] text-slate-500 uppercase font-black tracking-tighter">Ton Estimé</span>
                                        <span className="text-xs text-indigo-300 font-bold">{email.ton_estime || "Analysé"}</span>
                                    </div>
                                    <div className="flex flex-col">
                                        <span className="text-[9px] text-slate-500 uppercase font-black tracking-tighter">Confiance IA</span>
                                        <span className="text-xs text-white font-bold">{Math.round(email.confiance || 0)}%</span>
                                    </div>
                                </div>
                                <Button variant="ghost" size="sm" className="text-xs py-1 h-auto opacity-0 group-hover:opacity-100 transition-opacity" onClick={(e) => {
                                    e.stopPropagation();
                                    setSelectedEmail(email);
                                }}>Détails</Button>
                            </div>
                        </GlassCard>
                    )) : (
                        <div className="p-12 text-center border border-dashed border-slate-800 rounded-2xl opacity-40">
                            <p className="text-sm">Aucun email synchronisé</p>
                        </div>
                    )}
                </div>
            </div>

            {/* Audio Section */}
            <div className="space-y-6">
                <div className="flex items-center gap-3 px-2">
                    <div className="p-2 bg-purple-500/20 rounded-lg">
                        <Mic className="w-5 h-5 text-purple-400" />
                    </div>
                    <h3 className="font-bold text-xl text-white">Audio & Vocaux (WhatsApp)</h3>
                </div>

                <div className="space-y-4">
                    {vocals.length > 0 ? vocals.map((vocal: any, i: number) => (
                        <GlassCard key={i} className="p-6 border-slate-800 hover:border-purple-500/30 transition-all">
                            <div className="flex items-center justify-between mb-6">
                                <div className="flex items-center gap-4">
                                    <button className="w-12 h-12 rounded-full bg-purple-500/20 flex items-center justify-center hover:bg-purple-500/30 transition-colors">
                                        <Play className="w-5 h-5 text-purple-400 fill-purple-400" />
                                    </button>
                                    <div>
                                        <h4 className="font-bold text-white text-sm">{vocal.fileName}</h4>
                                        <span className="text-[10px] text-slate-500">{vocal.duration} • {vocal.date}</span>
                                    </div>
                                </div>
                                <div className="text-right">
                                    <span className={cn("px-2 py-0.5 rounded text-[10px] font-bold uppercase",
                                        vocal.emotion === "Calme" ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20" :
                                            vocal.emotion === "Deception" ? "bg-red-500/10 text-red-400 border border-red-500/20" : "bg-amber-500/10 text-amber-400 border border-red-500/20"
                                    )}>{vocal.emotion}</span>
                                </div>
                            </div>

                            <div className="bg-slate-950/50 p-4 rounded-xl border border-white/5 mb-4 relative overflow-hidden group">
                                <p className="text-xs text-slate-400 italic line-clamp-2">"{vocal.transcript}"</p>
                                <div className="absolute inset-0 bg-gradient-to-t from-slate-950/80 to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                                    <Button variant="ghost" size="sm" className="text-[10px] h-auto py-1">Voir transcription</Button>
                                </div>
                            </div>

                            {/* Fake Waveform */}
                            <div className="flex items-end justify-between h-8 gap-1">
                                {[30, 70, 45, 90, 20, 50, 80, 40, 60, 30, 75, 40, 20, 85, 50, 30, 65, 40, 20, 95, 40, 30, 60, 80, 40, 50, 20, 70, 35, 90].map((h, j) => (
                                    <div
                                        key={j}
                                        className={cn("w-1 rounded-full bg-slate-800 transition-all group-hover:bg-purple-500/30")}
                                        style={{ height: `${h}%` }}
                                    />
                                ))}
                            </div>
                        </GlassCard>
                    )) : (
                        <div className="p-12 text-center border border-dashed border-slate-800 rounded-2xl opacity-40">
                            <p className="text-sm">Aucun vocal reçu</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

function DetailsTab({ loan }: { loan: any }) {
    const isIndiv = loan.clientType === "Individu" || loan.typeClient === "individu";

    const profileData = [
        { label: "Type de Client", value: isIndiv ? "Individu / Particulier" : "PME / Entreprise" },
        { label: "Compte courant", value: loan.compte_courant || "-" },
        { label: "Montant crédit", value: `${(loan.montant_credit || 0).toLocaleString()} TND` },
        { label: "Durée crédit", value: `${loan.duree_mois || 0} mois` },
        { label: "Historique crédit", value: loan.historique_credit || "-", fullWidth: true },
        { label: "Épargne", value: loan.epargne ? `${loan.epargne.toLocaleString()} TND` : "-" },
        { label: "Emploi / Secteur", value: loan.emploi || "-" },
        { label: "Ancienneté emploi", value: loan.emploi_depuis ? `${loan.emploi_depuis} ans` : "-" },
        { label: "Taux remboursement", value: `${loan.taux_remboursement || 0}%` },
        { label: "Statut personnel", value: loan.statut_personnel || "-" },
        { label: "Âge", value: loan.age ? `${loan.age} ans` : "-" },
        { label: "Résidence depuis", value: loan.residence_depuis ? `${loan.residence_depuis} ans` : "-" },
        { label: "Patrimoine", value: loan.patrimoine ? `${loan.patrimoine.toLocaleString()} TND` : "-" },
        { label: "Logement", value: loan.logement || "-" },
        { label: "Autres crédits", value: loan.autres_credits || "-" },
        { label: "Crédits en banque", value: loan.nb_credits_banque || 0 },
        { label: "Personnes à charge", value: loan.personnes_a_charge || 0 },
        { label: "Téléphone", value: loan.telephone || "-" },
        { label: "Travailleur étranger", value: loan.travailleur_etranger !== null ? (loan.travailleur_etranger ? "Oui" : "Non") : "-" },
    ];

    return (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2 space-y-8">
                <GlassCard className="p-8 border-slate-800">
                    <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                        <User className="w-5 h-5 text-indigo-400" /> Profil Complet {isIndiv ? "Individu" : "Entreprise"}
                    </h3>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-y-8 gap-x-12">
                        {profileData.map((item: any, i: number) => (
                            <div key={i} className={cn("space-y-1.5", item.fullWidth ? "md:col-span-2 bg-indigo-500/5 p-4 rounded-xl border border-indigo-500/10" : "")}>
                                <p className="text-xs font-bold text-slate-500 uppercase tracking-widest">{item.label}</p>
                                <p className="text-lg text-white font-medium">{item.value}</p>
                                {item.subValue && <p className="text-sm text-indigo-400/70">{item.subValue}</p>}
                            </div>
                        ))}
                    </div>
                </GlassCard>
            </div>

            <div className="space-y-6">
                <GlassCard className="p-6 border-slate-800 bg-gradient-to-br from-slate-900 to-slate-950">
                    <h4 className="font-bold text-slate-400 text-xs uppercase tracking-widest mb-4">Objectif du Crédit</h4>
                    <p className="text-white text-xl font-medium leading-relaxed">
                        {loan.objectif_credit || loan.creditObjective || "Non spécifié"}
                    </p>
                    <div className="mt-6 flex items-center justify-between p-4 bg-white/5 rounded-xl">
                        <div>
                            <p className="text-[10px] text-slate-500 uppercase">Durée Souhaitée</p>
                            <p className="text-lg font-bold text-white">{loan.duree_mois || loan.duration || 0} mois</p>
                        </div>
                        <Calendar className="w-6 h-6 text-indigo-500/50" />
                    </div>
                </GlassCard>

                <GlassCard className="p-6 border-slate-800">
                    <h4 className="font-bold text-slate-400 text-xs uppercase tracking-widest mb-4">Quick Actions</h4>
                    <div className="space-y-3">
                        <Button variant="secondary" className="w-full justify-start gap-3 bg-white/5 border-white/5"><ExternalLink className="w-4 h-4" /> Voir relevés bancaires</Button>
                        <Button variant="secondary" className="w-full justify-start gap-3 bg-white/5 border-white/5"><Fingerprint className="w-4 h-4" /> Vérifier Identité</Button>
                    </div>
                </GlassCard>
            </div>
        </div>
    );
}

function AnalysisTab({ analysis, loan }: { analysis: any; loan: any }) {
    const isError = (analysis.finalDecision || loan.decision_ia) === "Non" || loan.decision_ia === "refuser";

    return (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* IA Conclusion Panel */}
            <div className="lg:col-span-1 space-y-6">
                <GlassCard className={cn("p-8 border-2 shadow-2xl overflow-hidden relative",
                    isError ? "border-red-500/20 bg-red-500/5" : "border-emerald-500/20 bg-emerald-500/5"
                )}>
                    <ShieldCheck className={cn("absolute -bottom-10 -right-10 w-48 h-48 opacity-5",
                        isError ? "text-red-500" : "text-emerald-500"
                    )} />

                    <div className="relative z-10 space-y-6">
                        <div className="space-y-2">
                            <h3 className="text-sm font-bold text-slate-500 uppercase tracking-tighter">Décision IA Finale</h3>
                            <div className="flex items-center gap-4">
                                <div className={cn("text-6xl font-black", isError ? "text-red-500" : "text-emerald-500")}>
                                    {isError ? "Non" : "Oui"}
                                </div>
                                <div className={cn("p-3 rounded-2xl", isError ? "bg-red-500/10" : "bg-emerald-500/10")}>
                                    {isError ? <XCircle className="w-10 h-10 text-red-500" /> : <CheckCircle2 className="w-10 h-10 text-emerald-500" />}
                                </div>
                            </div>
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <div className="bg-slate-900/50 p-4 rounded-2xl border border-white/5">
                                <p className="text-[10px] text-slate-500 uppercase mb-1">Score IA</p>
                                <p className="text-2xl font-bold text-white">{analysis.score || (isError ? 85 : 15)}<span className="text-xs text-slate-600 ml-1">/100</span></p>
                            </div>
                            <div className="bg-slate-900/50 p-4 rounded-2xl border border-white/5">
                                <p className="text-[10px] text-slate-500 uppercase mb-1">Risque</p>
                                <p className={cn("text-lg font-bold", isError ? "text-red-400" : "text-emerald-400")}>{isError ? "Élevé" : "Faible"}</p>
                            </div>
                        </div>
                    </div>
                </GlassCard>
            </div>

            {/* Analysis Details Placeholder */}
            <div className="lg:col-span-2">
                <GlassCard className="p-8 border-slate-800 text-center opacity-40 h-full flex flex-col items-center justify-center">
                    <BarChart3 className="w-12 h-12 mb-4" />
                    <p>Les rapports d'analyse détaillés seront bientôt synchronisés ici.</p>
                </GlassCard>
            </div>
        </div>
    );
}
