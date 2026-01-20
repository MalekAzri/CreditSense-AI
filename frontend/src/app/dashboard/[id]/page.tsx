"use client";

import { useParams, useRouter } from "next/navigation";
import { mockLoans, mockAnalysis } from "@/lib/mockData";
import { GlassCard } from "@/components/ui/GlassCard";
import { Button } from "@/components/ui/Button";
import { ArrowLeft, ShieldAlert, FileCheck, Mic, Mail, AlertOctagon, CheckCircle2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { motion } from "framer-motion";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts";

export default function AnalysisPage() {
    const { id } = useParams();
    const router = useRouter();

    const loan = mockLoans.find(l => l.id === id);
    const analysis = mockAnalysis[id as string] || mockAnalysis["LN-2024-001"]; // Fallback for demo

    if (!loan) return <div className="p-8 text-center">Loan request not found.</div>;

    const riskData = [
        { name: "Risk", value: loan.riskScore },
        { name: "Safe", value: 100 - loan.riskScore },
    ];

    const riskColor = loan.riskScore > 70 ? "#EF4444" : loan.riskScore > 30 ? "#F59E0B" : "#10B981";

    return (
        <div className="space-y-6 pb-12">
            <div className="flex items-center gap-4">
                <Button variant="ghost" size="sm" onClick={() => router.back()} className="text-slate-400 hover:text-white">
                    <ArrowLeft className="w-4 h-4 mr-2" /> Back
                </Button>
                <div>
                    <h1 className="text-2xl font-bold text-white flex items-center gap-2">
                        Analysis Report: <span className="text-indigo-400 font-mono">{id}</span>
                    </h1>
                    <p className="text-slate-500 text-sm">Automated AI Assessment • {loan.date}</p>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

                {/* Module 1: Risk Score (Main) */}
                <GlassCard className="col-span-1 lg:col-span-1 flex flex-col items-center justify-center relative min-h-[300px]">
                    <h3 className="absolute top-6 left-6 font-semibold text-slate-300">Composite Risk Score</h3>
                    <div className="w-48 h-48 relative">
                        <ResponsiveContainer width="100%" height="100%">
                            <PieChart>
                                <Pie
                                    data={riskData}
                                    cx="50%"
                                    cy="50%"
                                    innerRadius={60}
                                    outerRadius={80}
                                    startAngle={180}
                                    endAngle={0}
                                    paddingAngle={5}
                                    dataKey="value"
                                    stroke="none"
                                >
                                    <Cell fill={riskColor} />
                                    <Cell fill="#1e293b" />
                                </Pie>
                                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#f8fafc' }} />
                            </PieChart>
                        </ResponsiveContainer>
                        <div className="absolute inset-0 flex flex-col items-center justify-center -mt-8">
                            <span className="text-4xl font-bold text-white">{loan.riskScore}</span>
                            <span className="text-xs uppercase text-slate-500 font-bold tracking-widest">{loan.riskScore > 50 ? "High Risk" : "Low Risk"}</span>
                        </div>
                    </div>

                    <div className="w-full mt-4 px-4">
                        <div className="flex justify-between text-sm text-slate-400 mb-2">
                            <span>Confidence</span>
                            <span className="text-white">98%</span>
                        </div>
                        <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                            <div className="h-full bg-indigo-500 w-[98%]" />
                        </div>
                    </div>
                </GlassCard>

                {/* AI Recommendation */}
                <GlassCard className="col-span-1 lg:col-span-2 flex flex-col justify-between">
                    <div>
                        <div className="flex items-center gap-3 mb-4">
                            <div className="p-2 bg-indigo-500/20 rounded-lg">
                                <ShieldAlert className="w-6 h-6 text-indigo-400" />
                            </div>
                            <h3 className="text-lg font-semibold text-white">AI Recommendation</h3>
                        </div>

                        <div className={cn("p-4 rounded-xl border mb-4",
                            analysis.recommendation.decision === "Approve" ? "bg-emerald-500/10 border-emerald-500/20" :
                                analysis.recommendation.decision === "Reject" ? "bg-red-500/10 border-red-500/20" : "bg-amber-500/10 border-amber-500/20"
                        )}>
                            <div className="flex items-start gap-4">
                                {analysis.recommendation.decision === "Approve" ? <CheckCircle2 className="w-6 h-6 text-emerald-400 shrink-0" /> : <AlertOctagon className="w-6 h-6 text-amber-400 shrink-0" />}
                                <div>
                                    <h4 className={cn("text-lg font-bold mb-1",
                                        analysis.recommendation.decision === "Approve" ? "text-emerald-400" :
                                            analysis.recommendation.decision === "Reject" ? "text-red-400" : "text-amber-400"
                                    )}>
                                        Recommendation: {analysis.recommendation.decision}
                                    </h4>
                                    <p className="text-slate-300 leading-relaxed">{analysis.recommendation.reason}</p>
                                </div>
                            </div>
                        </div>

                        <p className="text-slate-400 text-sm">{analysis.summary}</p>
                    </div>

                    <div className="flex gap-3 mt-6 justify-end">
                        <Button variant="secondary">Request More Info</Button>
                        <Button variant="primary" className={analysis.recommendation.decision === "Reject" ? "bg-red-600 hover:bg-red-500" : ""}>
                            {analysis.recommendation.decision === "Approve" ? "Approve Loan" : "Process Decision"}
                        </Button>
                    </div>
                </GlassCard>

                {/* Module 2: Document Validation */}
                <GlassCard className="col-span-1">
                    <div className="flex items-center gap-3 mb-6">
                        <div className="p-2 bg-blue-500/20 rounded-lg">
                            <FileCheck className="w-5 h-5 text-blue-400" />
                        </div>
                        <h3 className="font-semibold text-white">Document Validation</h3>
                    </div>
                    <div className="space-y-3">
                        {analysis.documents.map((doc, i) => (
                            <div key={i} className="flex items-center justify-between p-3 rounded-lg bg-white/5 border border-white/5">
                                <div className="flex items-center gap-3">
                                    <div className="w-8 h-8 rounded bg-slate-800 flex items-center justify-center text-xs font-bold text-slate-500">
                                        {doc.type}
                                    </div>
                                    <div>
                                        <p className="text-sm font-medium text-white">{doc.name}</p>
                                        <p className="text-xs text-slate-500">{doc.confidence}% Authenticity</p>
                                    </div>
                                </div>
                                <span className={cn("px-2 py-1 rounded text-xs font-semibold",
                                    doc.status === "Valid" ? "bg-emerald-500/10 text-emerald-400" : "bg-red-500/10 text-red-400"
                                )}>
                                    {doc.status}
                                </span>
                            </div>
                        ))}
                    </div>
                </GlassCard>

                {/* Module 3: Tone Analysis */}
                <GlassCard className="col-span-1 lg:col-span-2">
                    <div className="flex items-center gap-3 mb-6">
                        <div className="p-2 bg-purple-500/20 rounded-lg">
                            <Mic className="w-5 h-5 text-purple-400" />
                        </div>
                        <h3 className="font-semibold text-white">Tone & Sentiment Analysis</h3>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div className="space-y-4">
                            <div className="flex items-center justify-between">
                                <span className="text-sm text-slate-400">Source</span>
                                <span className="text-sm text-white font-mono bg-white/5 px-2 py-1 rounded">{analysis.toneAnalysis.source}</span>
                            </div>
                            <div className="flex items-center justify-between">
                                <span className="text-sm text-slate-400">Detected Emotion</span>
                                <span className={cn("text-sm font-bold",
                                    analysis.toneAnalysis.sentiment === "Stress" || analysis.toneAnalysis.sentiment === "Deception" ? "text-red-400" : "text-emerald-400"
                                )}>{analysis.toneAnalysis.sentiment}</span>
                            </div>
                            <div className="flex items-center justify-between">
                                <span className="text-sm text-slate-400">AI Confidence</span>
                                <span className="text-sm text-white">{analysis.toneAnalysis.confidence}%</span>
                            </div>
                        </div>

                        <div className="bg-slate-950/50 rounded-xl p-4 border border-white/5">
                            {/* Fake Waveform */}
                            <div className="flex items-end justify-between h-16 gap-1 mb-2">
                                {[40, 60, 30, 80, 50, 90, 30, 40, 70, 50, 30, 60, 40, 80, 50, 40, 30, 60, 90, 40].map((h, i) => (
                                    <motion.div
                                        key={i}
                                        initial={{ height: 10 }}
                                        animate={{ height: `${h}%` }}
                                        transition={{ repeat: Infinity, repeatType: "reverse", duration: 1, delay: i * 0.05 }}
                                        className={cn("w-1.5 rounded-full", analysis.toneAnalysis.sentiment === "Stress" ? "bg-red-500/50" : "bg-indigo-500/50")}
                                    />
                                ))}
                            </div>
                            <p className="text-xs text-slate-400 italic">"{analysis.toneAnalysis.details}"</p>
                        </div>
                    </div>
                </GlassCard>

            </div>
        </div>
    );
}
