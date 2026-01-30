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
    History,
    Sparkles,
    Send,
    Loader2,
    LayoutDashboard,
    Layout
} from "lucide-react";
import { cn } from "@/lib/utils";
import { motion, AnimatePresence } from "framer-motion";
import EmailReplyModal from "@/components/dashboard/EmailReplyModal";

// Mock data for static display
const MOCK_VOCALS = [
    {
        fileName: "Vocal_Demande_Initial.mp3",
        duration: "0:45",
        date: "Hier à 14:20",
        emotion: "Calme",
        transcript: "Bonjour, je souhaiterais savoir où en est mon dossier de crédit pour l'achat de mon nouveau véhicule. Merci."
    },
    {
        fileName: "Vocal_Pression_Identite.mp3",
        duration: "0:30",
        date: "Aujourd'hui à 11:45",
        emotion: "Deception",
        transcript: "Je vous jure que c'est mon frère sur la photo, il a juste un peu changé depuis 5 ans, c'est bien lui sur la CIN."
    },
    {
        fileName: "Vocal_Justificatif_Manquant.mp3",
        duration: "1:12",
        date: "Aujourd'hui à 09:15",
        emotion: "Stressé",
        transcript: "Je n'arrive pas à uploader ma fiche de paie sur le portail, est-ce que je peux vous l'envoyer par WhatsApp directement ?"
    }
];

export default function ClientDetailsPage() {
    const { id } = useParams();
    const router = useRouter();
    const loanId = id as string;
    const [loan, setLoan] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState<"documents" | "details" | "analysis" | "communications">("documents");
    const [reanalyzingDocs, setReanalyzingDocs] = useState<Set<number>>(new Set());
    const [mlAnalysis, setMlAnalysis] = useState<any>(null);
    const [loadingAnalysis, setLoadingAnalysis] = useState(false);
    const [updatingStatus, setUpdatingStatus] = useState(false);
    const [selectedEmail, setSelectedEmail] = useState<any>(null);
    const [selectedDocument, setSelectedDocument] = useState<any>(null);
    const [openedFromAnalysis, setOpenedFromAnalysis] = useState(false);
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

    const handleStatusChange = async (newStatus: string) => {
        setUpdatingStatus(true);
        try {
            const res = await fetch(`/api/clients/${loanId}`, {
                method: "PATCH",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ statut_dossier: newStatus })
            });
            if (res.ok) {
                setLoan({ ...loan, statut_dossier: newStatus });
            }
        } catch (error) {
            console.error("Error updating status:", error);
        } finally {
            setUpdatingStatus(false);
        }
    };

    const fetchMlAnalysis = async () => {
        if (!loan || mlAnalysis) return;
        setLoadingAnalysis(true);
        try {
            const res = await fetch(`http://localhost:8000/clients/analyze`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(loan)
            });
            if (res.ok) {
                const data = await res.json();
                setMlAnalysis(data);

                // Auto-persist Decision and Class to Database
                if (loan && (loan.classe !== (data.decision === "OUI" ? "bon client" : "mauvais client") || loan.decision_ia !== (data.decision === "OUI" ? "donner" : "refuser"))) {
                    await fetch(`/api/clients/${loan.id}`, {
                        method: "PATCH",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({
                            classe: data.decision === "OUI" ? "bon client" : "mauvais client",
                            decision_ia: data.decision === "OUI" ? "donner" : "refuser"
                        })
                    }).then(r => r.ok && setLoan((prev: any) => prev ? ({
                        ...prev,
                        classe: data.decision === "OUI" ? "bon client" : "mauvais client",
                        decision_ia: data.decision === "OUI" ? "donner" : "refuser"
                    }) : null));
                }
            }
        } catch (error) {
            console.error("Error fetching ML analysis:", error);
        } finally {
            setLoadingAnalysis(false);
        }
    };

    useEffect(() => {
        if (activeTab === "analysis") {
            fetchMlAnalysis();
        }
    }, [activeTab]);

    const analysis = mlAnalysis || {
        reliability_score: (loan?.decision_ia === "donner" ? 85 : 15),
        decision: (loan?.decision_ia === "donner" ? "OUI" : "NON"),
        risk_score: (loan?.decision_ia === "donner" ? 15 : 85),
        reasons: ["Chargement des données en cours..."]
    };

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
                    <Button
                        variant="primary"
                        disabled={updatingStatus}
                        onClick={() => {
                            const statuses = ["en attente", "accepté", "refusé"];
                            const currentIndex = statuses.indexOf(loan.statut_dossier || "en attente");
                            const nextIndex = (currentIndex + 1) % statuses.length;
                            handleStatusChange(statuses[nextIndex]);
                        }}
                        className={cn(
                            "mt-5 transition-all duration-300 shadow-lg font-bold min-w-[160px]",
                            (loan.statut_dossier === "en attente" || !loan.statut_dossier) && "bg-orange-500 hover:bg-orange-600 shadow-orange-500/20 text-white border-none",
                            loan.statut_dossier === "accepté" && "bg-emerald-500 hover:bg-emerald-600 shadow-emerald-500/20 text-white border-none",
                            loan.statut_dossier === "refusé" && "bg-rose-500 hover:bg-rose-600 shadow-rose-500/20 text-white border-none"
                        )}
                    >
                        {updatingStatus ? (
                            <Loader2 className="w-4 h-4 animate-spin" />
                        ) : (
                            <>
                                {loan.statut_dossier === "accepté" && "Dossier Accepté"}
                                {loan.statut_dossier === "refusé" && "Dossier Refusé"}
                                {(loan.statut_dossier === "en attente" || !loan.statut_dossier) && "En attente"}
                            </>
                        )}
                    </Button>
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
                    {activeTab === "communications" && (
                        <CommunicationsTab
                            loan={loan}
                            selectedEmail={selectedEmail}
                            setSelectedEmail={setSelectedEmail}
                            setOpenedFromAnalysis={setOpenedFromAnalysis}
                        />
                    )}
                    {activeTab === "analysis" && (
                        <AnalysisTab
                            analysis={analysis}
                            loan={loan}
                            loading={loadingAnalysis}
                            setSelectedEmail={(email: any) => {
                                setSelectedEmail(email);
                                setOpenedFromAnalysis(true);
                            }}
                            setSelectedDocument={(doc: any) => {
                                setSelectedDocument(doc);
                                setOpenedFromAnalysis(true);
                            }}
                        />
                    )}
                </motion.div>
            </AnimatePresence>

            {/* Shared Detail Modals */}
            <AnimatePresence>
                {/* Email Detail Modal */}
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
                                    <div className="min-w-0 flex-grow pr-4">
                                        <h3 className="text-2xl font-bold text-white mb-1 truncate">{selectedEmail.subject}</h3>
                                        <div className="flex items-center gap-3 text-sm text-slate-500">
                                            <span>{new Date(selectedEmail.sentAt).toLocaleString()}</span>
                                            <span className="w-1 h-1 rounded-full bg-slate-700" />
                                            <span className="text-indigo-400 font-medium">
                                                De: {selectedEmail.extractedData?.client_info?.name || "Client"}
                                            </span>
                                        </div>
                                    </div>
                                    <Button variant="ghost" size="sm" onClick={() => { setSelectedEmail(null); setOpenedFromAnalysis(false); }} className="hover:bg-white/5 rounded-full shrink-0">
                                        Fermer
                                    </Button>
                                </div>

                                <div className="bg-white/[0.03] rounded-2xl p-6 border border-white/5 min-h-[150px] max-h-[300px] overflow-y-auto mb-6 scrollbar-thin scrollbar-thumb-white/10">
                                    <p className="text-slate-300 leading-relaxed whitespace-pre-wrap text-sm">{selectedEmail.body}</p>
                                </div>

                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                                    <div>
                                        <h4 className="text-[10px] text-slate-500 uppercase font-black tracking-widest mb-3">Analyse IA</h4>
                                        <div className="bg-indigo-500/5 p-3 rounded-xl border border-indigo-500/10 flex justify-between items-center">
                                            <span className="text-[10px] text-slate-500 uppercase">Intention</span>
                                            <span className="text-xs font-bold text-white uppercase tracking-wider">{selectedEmail.intention}</span>
                                        </div>
                                    </div>
                                    <div>
                                        <h4 className="text-[10px] text-slate-500 uppercase font-black tracking-widest mb-3">Tonalité</h4>
                                        <div className="grid grid-cols-3 gap-2">
                                            <div className="bg-orange-500/5 p-2 rounded-xl border border-orange-500/10 text-center">
                                                <span className="text-[8px] text-slate-500 uppercase block">Urgence</span>
                                                <span className="text-[10px] font-black text-orange-400">{selectedEmail.ton_urgence || 0}</span>
                                            </div>
                                            <div className="bg-red-500/5 p-2 rounded-xl border border-red-500/10 text-center">
                                                <span className="text-[8px] text-slate-500 uppercase block">Stress</span>
                                                <span className="text-[10px] font-black text-red-400">{selectedEmail.ton_stress || 0}</span>
                                            </div>
                                            <div className="bg-blue-500/5 p-2 rounded-xl border border-blue-500/10 text-center">
                                                <span className="text-[8px] text-slate-500 uppercase block">Sérieux</span>
                                                <span className="text-[10px] font-black text-blue-400">{selectedEmail.ton_serieux || 0}</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <div className="flex flex-col gap-3 pt-6 border-t border-white/5">
                                    <div className="flex gap-4">
                                        <Button
                                            variant="primary"
                                            className="flex-1 bg-indigo-600 hover:bg-indigo-500 gap-2 font-bold"
                                            onClick={() => {
                                                setReplyModal({ isOpen: true, email: selectedEmail, mode: 'auto' });
                                                setSelectedEmail(null);
                                            }}
                                        >
                                            <Sparkles className="w-4 h-4" /> Réponse IA
                                        </Button>
                                        <Button
                                            variant="secondary"
                                            className="flex-1 bg-white/5 hover:bg-white/10 border-white/10 font-bold text-white gap-2"
                                            onClick={() => {
                                                setReplyModal({ isOpen: true, email: selectedEmail, mode: 'manual' });
                                                setSelectedEmail(null);
                                            }}
                                        >
                                            <Send className="w-4 h-4" /> Réponse Manuelle
                                        </Button>
                                    </div>
                                    {openedFromAnalysis && (
                                        <Button
                                            variant="ghost"
                                            className="w-full text-xs text-indigo-400 hover:text-indigo-300 gap-2"
                                            onClick={() => { setSelectedEmail(null); setOpenedFromAnalysis(false); setActiveTab("analysis"); }}
                                        >
                                            <LayoutDashboard className="w-4 h-4" /> Retour à l'analyse IA
                                        </Button>
                                    )}
                                </div>
                            </GlassCard>
                        </motion.div>
                    </div>
                )}

                {/* Document Detail Modal */}
                {selectedDocument && (
                    <div className="fixed inset-0 z-[110] flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
                        <motion.div
                            initial={{ opacity: 0, scale: 0.9, y: 20 }}
                            animate={{ opacity: 1, scale: 1, y: 0 }}
                            exit={{ opacity: 0, scale: 0.9, y: 20 }}
                            className="w-full max-w-4xl"
                        >
                            <GlassCard className="p-8 border-white/10 shadow-2xl bg-[#0F1219]">
                                <div className="flex justify-between items-start mb-6">
                                    <div>
                                        <h3 className="text-2xl font-bold text-white mb-1">{selectedDocument.type}</h3>
                                        <p className="text-sm text-slate-500 italic">ID Document: #{selectedDocument.id}</p>
                                    </div>
                                    <Button variant="ghost" size="sm" onClick={() => { setSelectedDocument(null); setOpenedFromAnalysis(false); }} className="hover:bg-white/5 rounded-full">
                                        Fermer
                                    </Button>
                                </div>

                                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                                    <div className="bg-slate-950 rounded-2xl overflow-hidden border border-slate-800 h-[400px] flex items-center justify-center relative group">
                                        {selectedDocument.url ? (
                                            <img
                                                src={`/api/documents/view?path=${encodeURIComponent(selectedDocument.url)}`}
                                                alt={selectedDocument.type}
                                                className="w-full h-full object-contain"
                                            />
                                        ) : (
                                            <FileText className="w-24 h-24 text-slate-800" />
                                        )}
                                        <div className="absolute top-4 right-4">
                                            <span className={cn("px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest shadow-xl",
                                                selectedDocument.statut === "valide" ? "bg-emerald-500 text-white" : "bg-amber-500 text-white"
                                            )}>
                                                {selectedDocument.statut}
                                            </span>
                                        </div>
                                    </div>

                                    <div className="space-y-6 flex flex-col justify-between">
                                        <div className="space-y-6">
                                            <div>
                                                <h4 className="text-[10px] text-slate-500 uppercase font-black tracking-widest mb-4">Scores de Validation</h4>
                                                <div className="grid grid-cols-2 gap-4">
                                                    <div className="bg-emerald-500/5 p-4 rounded-2xl border border-emerald-500/10">
                                                        <p className="text-[9px] text-slate-500 uppercase font-bold mb-1">OCR Match</p>
                                                        <p className="text-2xl font-black text-white">{Math.round(selectedDocument.ocrScore || 0)}%</p>
                                                    </div>
                                                    <div className="bg-indigo-500/5 p-4 rounded-2xl border border-indigo-500/10">
                                                        <p className="text-[9px] text-slate-500 uppercase font-bold mb-1">CLIP Semantic</p>
                                                        <p className="text-2xl font-black text-white">{Math.round(selectedDocument.clipScore || 0)}%</p>
                                                    </div>
                                                </div>
                                            </div>

                                            <div className="bg-white/5 p-6 rounded-2xl border border-white/5 space-y-3">
                                                <h4 className="text-[10px] text-slate-400 uppercase font-black tracking-widest">Commentaires de l'analyse</h4>
                                                <p className="text-sm text-slate-300 leading-relaxed italic">
                                                    "{selectedDocument.commentaire || "Aucune note complémentaire n'a été ajoutée pour ce document."}"
                                                </p>
                                            </div>
                                        </div>

                                        <div className="space-y-3">
                                            <Button
                                                variant="ghost"
                                                className="w-full bg-indigo-500/5 hover:bg-indigo-500/10 border border-indigo-500/10 text-indigo-400 font-bold gap-2 py-3"
                                                onClick={() => handleReanalyze(selectedDocument.id)}
                                                disabled={reanalyzingDocs.has(selectedDocument.id)}
                                            >
                                                {reanalyzingDocs.has(selectedDocument.id) ? (
                                                    <>
                                                        <Loader2 className="w-4 h-4 animate-spin" /> Analyse en cours...
                                                    </>
                                                ) : (
                                                    <>
                                                        <BrainCircuit className="w-4 h-4" /> Refaire l'analyse IA
                                                    </>
                                                )}
                                            </Button>
                                            <div className="flex gap-4">
                                                <Button variant="secondary" className="flex-1 bg-red-500/10 hover:bg-red-500/20 border-red-500/20 text-red-500 font-bold">Rejeter</Button>
                                                <Button variant="primary" className="flex-1 bg-emerald-600 hover:bg-emerald-500 font-bold">Valider</Button>
                                            </div>
                                            {openedFromAnalysis && (
                                                <Button
                                                    variant="ghost"
                                                    className="w-full text-xs text-indigo-400 hover:text-indigo-300 gap-2"
                                                    onClick={() => { setSelectedDocument(null); setOpenedFromAnalysis(false); setActiveTab("analysis"); }}
                                                >
                                                    <LayoutDashboard className="w-4 h-4" /> Retour à l'analyse IA
                                                </Button>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            </GlassCard>
                        </motion.div>
                    </div>
                )}
            </AnimatePresence>

            {replyModal.isOpen && (
                <EmailReplyModal
                    email={replyModal.email}
                    client={loan}
                    mode={replyModal.mode}
                    onClose={() => setReplyModal({ ...replyModal, isOpen: false })}
                />
            )}
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
        if (t.includes("domicile") || t.includes("facture") || t.includes("residence")) {
            // For PME, invoices are financial documents, not residence proof
            return (loan.typeClient === "pme" || loan.clientType === "PME") ? "Financier" : "Domicile";
        }
        if (t.includes("dirigeant") || t.includes("statuts")) return (loan.typeClient === "pme" || loan.clientType === "PME") ? "Entreprise" : "Identité";
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

function CommunicationsTab({
    loan,
    selectedEmail,
    setSelectedEmail,
    setOpenedFromAnalysis
}: {
    loan: any;
    selectedEmail: any;
    setSelectedEmail: (email: any) => void;
    setOpenedFromAnalysis: (val: boolean) => void;
}) {
    const emails = loan.emails || [];

    // Mock data for static display
    const MOCK_VOCALS = [
        {
            fileName: "Vocal_Demande_Initial.mp3",
            duration: "0:45",
            date: "Hier à 14:20",
            emotion: "Calme",
            transcript: "Bonjour, je souhaiterais savoir où en est mon dossier de crédit pour l'achat de mon nouveau véhicule. Merci."
        },
        {
            fileName: "Vocal_Justificatif_Manquant.mp3",
            duration: "1:12",
            date: "Aujourd'hui à 09:15",
            emotion: "Stressé",
            transcript: "Je n'arrive pas à uploader ma fiche de paie sur le portail, est-ce que je peux vous l'envoyer par WhatsApp directement ?"
        }
    ];

    const vocals = (loan.vocaux && loan.vocaux.length > 0) ? loan.vocaux : MOCK_VOCALS;
    const [replyModal, setReplyModal] = useState<{
        isOpen: boolean;
        email: any;
        mode: 'auto' | 'manual';
    }>({
        isOpen: false,
        email: null,
        mode: 'manual'
    });

    return (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 relative">
            <AnimatePresence>
                {replyModal.isOpen && (
                    <div className="fixed inset-0 z-[120] flex items-center justify-center p-4 bg-black/90 backdrop-blur-xl">
                        <EmailReplyModal
                            email={replyModal.email}
                            client={loan}
                            mode={replyModal.mode}
                            onClose={() => setReplyModal({ ...replyModal, isOpen: false })}
                        />
                    </div>
                )}
            </AnimatePresence>

            {replyModal.isOpen && (
                <EmailReplyModal
                    email={replyModal.email}
                    client={loan}
                    mode={replyModal.mode}
                    onClose={() => setReplyModal({ ...replyModal, isOpen: false })}
                />
            )}

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
                                            email.ton_urgence > 70 ? "text-red-400" :
                                                email.ton_stress > 70 ? "text-amber-400" : "text-emerald-400"
                                        )}>{email.intention || "N/A"}</span>
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
        </div >
    );
}

function DetailsTab({ loan }: { loan: any }) {
    const isIndiv = loan.clientType === "Individu" || loan.typeClient === "individu";

    const profileData = [
        { label: "Type de Client", value: isIndiv ? "Individu / Particulier" : "PME / Entreprise" },
        { label: "Email", value: loan.email || "-" },
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

function AnalysisTab({ analysis, loan, loading, setSelectedEmail, setSelectedDocument }: {
    analysis: any;
    loan: any;
    loading?: boolean;
    setSelectedEmail: (email: any) => void;
    setSelectedDocument: (doc: any) => void;
}) {
    const isError = (analysis.decision || loan.decision_ia) === "NON" || analysis.decision === "REFUSÉ" || loan.decision_ia === "refuser";

    // Logic for Fraud and Suspicious Content
    const fraudulentDocs = (loan.documents || []).filter((doc: any) =>
        (doc.ocrScore < 45 || doc.clipScore < 45) && doc.statut !== "valide"
    );

    const suspiciousEmails = (loan.emails || []).filter((email: any) =>
        email.ton_serieux < 20 || email.ton_stress > 80
    );

    const vocalsToFilter = (loan.vocaux && loan.vocaux.length > 0) ? loan.vocaux : MOCK_VOCALS;
    const suspiciousVocals = vocalsToFilter.filter((v: any) => v.emotion === "Deception");

    if (loading) {
        return (
            <div className="flex flex-col items-center justify-center p-20 gap-4">
                <div className="w-12 h-12 border-4 border-indigo-500/20 border-t-indigo-500 rounded-full animate-spin" />
                <p className="text-slate-400">Le modèle Random Forest analyse les variables...</p>
            </div>
        );
    }

    return (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* IA Conclusion Panel */}
            <div className="lg:col-span-1 space-y-6">
                <GlassCard className={cn("p-8 border-2 shadow-2xl overflow-hidden relative",
                    isError ? "border-rose-500/20 bg-rose-500/10" : "border-emerald-500/20 bg-emerald-500/10"
                )}>
                    <ShieldCheck className={cn("absolute -bottom-10 -right-10 w-48 h-48 opacity-5",
                        isError ? "text-rose-500" : "text-emerald-500"
                    )} />

                    <div className="relative z-10 space-y-6">
                        <div className="space-y-2">
                            <h3 className="text-sm font-bold text-slate-500 uppercase tracking-tighter">Décision IA Finale</h3>
                            <div className="flex items-center gap-4">
                                <div className={cn("text-6xl font-black", isError ? "text-rose-500" : "text-emerald-500")}>
                                    {isError ? "Non" : "Oui"}
                                </div>
                                <div className={cn("p-3 rounded-2xl", isError ? "bg-rose-500/10" : "bg-emerald-500/10")}>
                                    {isError ? <Ban className="w-12 h-12 text-rose-500" /> : <CheckCircle2 className="w-12 h-12 text-emerald-500" />}
                                </div>
                            </div>
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <div className="bg-slate-900/50 p-4 rounded-2xl border border-white/5">
                                <p className="text-[10px] text-slate-500 uppercase mb-1">Score Fiabilité</p>
                                <p className="text-2xl font-bold text-white">
                                    {Math.round(analysis.reliability_score || 0)}
                                    <span className="text-xs text-slate-600 ml-1">/100</span>
                                </p>
                            </div>
                            <div className="bg-slate-900/50 p-4 rounded-2xl border border-white/5">
                                <p className="text-[10px] text-slate-500 uppercase mb-1">Niveau Risque</p>
                                <p className={cn("text-lg font-bold", isError ? "text-rose-400" : "text-emerald-400")}>
                                    {analysis.risk_score > 70 ? "Critique" : analysis.risk_score > 40 ? "Modéré" : "Faible"}
                                </p>
                            </div>
                        </div>
                    </div>
                </GlassCard>

                <div className="bg-slate-900/50 p-6 rounded-2xl border border-white/5 space-y-4">
                    <h4 className="text-xs font-bold text-slate-400 uppercase tracking-widest">Détails Statistiques</h4>
                    <div className="space-y-3">
                        <div className="flex justify-between items-center">
                            <span className="text-sm text-slate-500">Probabilité Refus</span>
                            <span className="text-sm font-mono text-white">{(analysis.risk_score || 0).toFixed(1)}%</span>
                        </div>
                        <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                            <div
                                className={cn("h-full transition-all duration-1000", isError ? "bg-rose-500" : "bg-emerald-500")}
                                style={{ width: `${analysis.risk_score || 0}%` }}
                            />
                        </div>
                    </div>
                </div>
            </div>

            {/* Analysis Details & "Why" Reasoning */}
            <div className="lg:col-span-2 space-y-6">
                <GlassCard className="p-8 border-slate-800 h-full">
                    <div className="flex items-center gap-3 mb-8">
                        <div className="p-2 bg-indigo-500/10 rounded-lg">
                            <BrainCircuit className="w-6 h-6 text-indigo-400" />
                        </div>
                        <div>
                            <h3 className="text-xl font-bold text-white">Justification du Modèle</h3>
                            <p className="text-sm text-slate-500">Explication des variables impactant la décision</p>
                        </div>
                    </div>

                    <div className="space-y-6">
                        {analysis.reasons && analysis.reasons.length > 0 ? (
                            <div className="grid gap-4">
                                {analysis.reasons.map((reason: string, idx: number) => (
                                    <motion.div
                                        initial={{ opacity: 0, x: -10 }}
                                        animate={{ opacity: 1, x: 0 }}
                                        transition={{ delay: idx * 0.1 }}
                                        key={idx}
                                        className="flex gap-4 p-5 bg-white/5 rounded-2xl border border-white/5 items-start group hover:bg-white/10 transition-colors"
                                    >
                                        <div className={cn("w-2 h-2 rounded-full mt-2 shrink-0", isError ? "bg-rose-500" : "bg-emerald-500")} />
                                        <p className="text-slate-300 text-sm leading-relaxed">{reason}</p>
                                    </motion.div>
                                ))}
                            </div>
                        ) : (
                            <div className="text-center py-12 opacity-40">
                                <BarChart3 className="w-12 h-12 mx-auto mb-4" />
                                <p>Analyse des features en cours...</p>
                            </div>
                        )}

                        <div className="mt-8 pt-6 border-t border-white/5">
                            <div className="bg-indigo-500/5 p-6 rounded-2xl border border-indigo-500/10">
                                <h5 className="text-[10px] font-black text-indigo-400 uppercase tracking-widest mb-3">Note de Conformité</h5>
                                <p className="text-xs text-slate-400 leading-relaxed italic mb-4">
                                    "Cette analyse est générée par un algorithme de Random Forest agissant comme une assemblée de plusieurs centaines de 'juges' (arbres de décision).
                                    Le score de {isError ? 'risque' : 'fiabilité'} représente le pourcentage de ces juges ayant conclu {isError ? 'défavorablement' : 'favorablement'} au dossier après examen de toutes les variables.
                                    Le score de {isError ? 'fiabilité' : 'risque'} provient de la proportion inverse de juges."
                                </p>
                                <div className="grid grid-cols-2 gap-4 pt-4 border-t border-white/5">
                                    <div className="flex flex-col">
                                        <span className="text-[8px] text-slate-500 uppercase font-black">Confiance Modèle</span>
                                        <span className="text-xs font-bold text-indigo-400">78.4% (Précision globale)</span>
                                    </div>
                                    <div className="flex flex-col">
                                        <span className="text-[8px] text-slate-500 uppercase font-black">Fiabilité du Score</span>
                                        <span className="text-xs font-bold text-emerald-400">72.1% (Score F1)</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </GlassCard>
            </div>

            {/* Evidence Section - Refined Layout */}
            {
                (fraudulentDocs.length > 0 || suspiciousEmails.length > 0 || suspiciousVocals.length > 0) && (
                    <div className="lg:col-span-3 mt-8 space-y-8">
                        <div className="h-px bg-slate-800 w-full opacity-30" />

                        <div className="flex items-center gap-3">
                            <div className="p-2 bg-rose-500/20 rounded-lg">
                                <AlertTriangle className="w-6 h-6 text-rose-500" />
                            </div>
                            <div>
                                <h3 className="text-xl font-bold text-white uppercase tracking-tighter">Points de Vigilance Cruciaux</h3>
                                <p className="text-sm text-slate-500 tracking-tight">Veuillez examiner ces preuves avant toute validation finale</p>
                            </div>
                        </div>

                        <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
                            {/* Section 1: Documents Frauduleux */}
                            <div className="space-y-6">
                                <div className="flex items-center gap-3 px-2">
                                    <div className="w-1 h-8 bg-amber-500 rounded-full" />
                                    <h4 className="text-sm font-black text-amber-500 uppercase tracking-[0.2em]">Documents Frauduleux</h4>
                                </div>

                                <div className="grid grid-cols-1 gap-4">
                                    {fraudulentDocs.map((doc: any, i: number) => (
                                        <GlassCard key={i} className="p-5 border-amber-500/30 bg-amber-500/5 hover:border-amber-500/50 transition-all">
                                            <div className="flex flex-col h-full justify-between gap-4">
                                                <div className="space-y-3">
                                                    <div className="flex justify-between items-start">
                                                        <div className="p-2 bg-black/40 rounded-lg">
                                                            <FileText className="w-4 h-4 text-amber-400" />
                                                        </div>
                                                        <div className="text-right">
                                                            <p className="text-white font-bold text-sm tracking-tight">{doc.type}</p>
                                                            <p className="text-[9px] text-slate-500 uppercase font-black">{new Date(doc.createdAt).toLocaleDateString()}</p>
                                                        </div>
                                                    </div>
                                                    <div className="grid grid-cols-2 gap-2">
                                                        <div className="bg-black/40 p-2 rounded-lg border border-rose-500/10">
                                                            <p className="text-[8px] text-slate-500 uppercase font-black mb-1">OCR</p>
                                                            <p className="text-xs font-bold text-rose-400">{Math.round(doc.ocrScore || 0)}%</p>
                                                        </div>
                                                        <div className="bg-black/40 p-2 rounded-lg border border-rose-500/10">
                                                            <p className="text-[8px] text-slate-500 uppercase font-black mb-1">CLIP</p>
                                                            <p className="text-xs font-bold text-rose-400">{Math.round(doc.clipScore || 0)}%</p>
                                                        </div>
                                                    </div>
                                                </div>
                                                <Button
                                                    variant="ghost"
                                                    className="w-full py-2 h-auto text-[10px] font-black uppercase tracking-widest bg-white/5 hover:bg-white/10 text-slate-400 hover:text-white transition-all"
                                                    onClick={() => setSelectedDocument(doc)}
                                                >
                                                    Voir les détails
                                                </Button>
                                            </div>
                                        </GlassCard>
                                    ))}
                                    {fraudulentDocs.length === 0 && (
                                        <div className="p-8 border border-dashed border-slate-800 rounded-3xl flex items-center justify-center opacity-30 italic text-xs">
                                            Aucun document frauduleux détecté.
                                        </div>
                                    )}
                                </div>
                            </div>

                            {/* Section 2: Mails Suspects */}
                            <div className="space-y-6">
                                <div className="flex items-center gap-3 px-2">
                                    <div className="w-1 h-8 bg-rose-500 rounded-full" />
                                    <h4 className="text-sm font-black text-rose-500 uppercase tracking-[0.2em]">Emails Suspects</h4>
                                </div>

                                <div className="grid grid-cols-1 gap-4">
                                    {suspiciousEmails.map((email: any, i: number) => (
                                        <GlassCard key={i} className="p-5 border-rose-500/30 bg-rose-500/5 hover:border-rose-500/50 transition-all">
                                            <div className="flex flex-col gap-4">
                                                <div className="space-y-3">
                                                    <div className="flex items-start gap-4">
                                                        <div className="p-2 bg-black/40 rounded-lg shrink-0">
                                                            <Mail className="w-4 h-4 text-rose-400" />
                                                        </div>
                                                        <div className="min-w-0">
                                                            <p className="text-white font-bold text-sm truncate">{email.subject}</p>
                                                            <p className="text-[10px] text-slate-500 uppercase font-black">{new Date(email.sentAt).toLocaleString()}</p>
                                                        </div>
                                                    </div>
                                                    <div className="bg-black/40 p-3 rounded-xl line-clamp-2 text-xs text-slate-400 italic font-medium leading-relaxed font-mono">
                                                        "{email.body}"
                                                    </div>
                                                </div>
                                                <div className="space-y-2">
                                                    <div className="flex justify-between text-[9px] font-black text-slate-500 uppercase tracking-tighter">
                                                        <span>Stress Analysé</span>
                                                        <span className="text-rose-400">{Math.round(email.ton_stress || 0)}%</span>
                                                    </div>
                                                    <div className="h-1 bg-slate-900 rounded-full overflow-hidden">
                                                        <div className="h-full bg-rose-500" style={{ width: `${email.ton_stress}%` }} />
                                                    </div>
                                                    <Button
                                                        variant="ghost"
                                                        className="w-full py-2 h-auto text-[10px] font-black uppercase tracking-widest bg-white/5 hover:bg-white/10 text-slate-400 hover:text-white transition-all mt-2"
                                                        onClick={() => setSelectedEmail(email)}
                                                    >
                                                        Détails du mail
                                                    </Button>
                                                </div>
                                            </div>
                                        </GlassCard>
                                    ))}
                                    {suspiciousEmails.length === 0 && (
                                        <div className="p-8 border border-dashed border-slate-800 rounded-3xl flex items-center justify-center opacity-30 italic text-xs text-center">
                                            Aucun email suspect détecté.
                                        </div>
                                    )}
                                </div>
                            </div>

                            {/* Section 3: Vocaux Suspects */}
                            <div className="space-y-6">
                                <div className="flex items-center gap-3 px-2">
                                    <div className="w-1 h-8 bg-purple-500 rounded-full" />
                                    <h4 className="text-sm font-black text-purple-500 uppercase tracking-[0.2em]">Vocaux Suspects</h4>
                                </div>

                                <div className="grid grid-cols-1 gap-4">
                                    {suspiciousVocals.map((vocal: any, i: number) => (
                                        <GlassCard key={i} className="p-5 border-purple-500/30 bg-purple-500/5 hover:border-purple-500/50 transition-all">
                                            <div className="flex flex-col gap-4">
                                                <div className="space-y-3">
                                                    <div className="flex items-center gap-4">
                                                        <div className="p-2 bg-black/40 rounded-lg shrink-0">
                                                            <Mic className="w-4 h-4 text-purple-400" />
                                                        </div>
                                                        <div>
                                                            <p className="text-white font-bold text-sm uppercase tracking-tighter">{vocal.fileName}</p>
                                                            <p className="text-[10px] text-slate-500 uppercase font-black">{vocal.date}</p>
                                                        </div>
                                                    </div>
                                                    <div className="bg-black/40 p-3 rounded-xl line-clamp-2 text-xs text-slate-400 italic font-medium leading-relaxed border-l-2 border-purple-500/50">
                                                        "{vocal.transcript}"
                                                    </div>
                                                </div>
                                                <div className="space-y-3">
                                                    <div className="flex justify-between items-center bg-purple-500/10 p-2 rounded-lg border border-purple-500/20">
                                                        <span className="text-[9px] font-black text-slate-500 uppercase">Alerte Émotion</span>
                                                        <span className="text-[10px] font-bold text-purple-400">{vocal.emotion}</span>
                                                    </div>
                                                    {/* Fake Waveform miniature */}
                                                    <div className="flex items-end justify-between h-4 gap-0.5 px-2 opacity-50 text-purple-500">
                                                        {[20, 80, 40, 90, 30, 70, 50, 85, 45, 95].map((h, j) => (
                                                            <div key={j} className="w-1 bg-current rounded-full" style={{ height: `${h}%` }} />
                                                        ))}
                                                    </div>
                                                </div>
                                            </div>
                                        </GlassCard>
                                    ))}
                                    {suspiciousVocals.length === 0 && (
                                        <div className="p-8 border border-dashed border-slate-800 rounded-3xl flex items-center justify-center opacity-30 italic text-xs text-center">
                                            Aucune anomalie audio détectée.
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>
                    </div>
                )}
        </div>
    );
}
