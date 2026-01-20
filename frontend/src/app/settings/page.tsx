"use client";

import { useState } from "react";
import { GlassCard } from "@/components/ui/GlassCard";
import { Button } from "@/components/ui/Button";
import { defaultIntegrations, Integration } from "@/lib/mockData";
import { Plus, Check, Link as LinkIcon, Mail, Database, MessageSquare, Terminal, Save, Trash2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { motion, AnimatePresence } from "framer-motion";

export default function SettingsPage() {
    const [activeTab, setActiveTab] = useState<"integrations" | "automation">("integrations");

    // Integrations State
    const [integrations, setIntegrations] = useState<Integration[]>(defaultIntegrations);
    const [showAddModal, setShowAddModal] = useState(false);
    const [newApiName, setNewApiName] = useState("");
    const [newApiEndpoint, setNewApiEndpoint] = useState("");

    // Automation State
    const [emailTemplate, setEmailTemplate] = useState("Dear {ClientName},\n\nThank you for your loan inquiry. To proceed, please fill out the attached application form.\n\nBest regards,\nCreditSense Team");

    const toggleIntegration = (id: string) => {
        setIntegrations(prev => prev.map(int =>
            int.id === id ? { ...int, connected: !int.connected } : int
        ));
    };

    const handleAddIntegration = () => {
        if (!newApiName || !newApiEndpoint) return;
        const newInt: Integration = {
            id: `custom_${Date.now()}`,
            name: newApiName,
            type: "Custom",
            connected: true,
            endpoint: newApiEndpoint,
            lastSync: "Just now"
        };
        setIntegrations([...integrations, newInt]);
        setShowAddModal(false);
        setNewApiName("");
        setNewApiEndpoint("");
    };

    return (
        <div className="space-y-8 pb-12">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-white">System Configuration</h1>
                    <p className="text-slate-500 text-sm">Manage data sources and automated responses</p>
                </div>

                <div className="flex p-1 bg-slate-900/50 rounded-xl border border-white/5">
                    <button
                        onClick={() => setActiveTab("integrations")}
                        className={cn("px-4 py-2 rounded-lg text-sm font-medium transition-all", activeTab === "integrations" ? "bg-indigo-600 text-white shadow-lg" : "text-slate-400 hover:text-white")}
                    >
                        Data Sources
                    </button>
                    <button
                        onClick={() => setActiveTab("automation")}
                        className={cn("px-4 py-2 rounded-lg text-sm font-medium transition-all", activeTab === "automation" ? "bg-indigo-600 text-white shadow-lg" : "text-slate-400 hover:text-white")}
                    >
                        Automation
                    </button>
                </div>
            </div>

            <AnimatePresence mode="wait">
                {activeTab === "integrations" ? (
                    <motion.div
                        key="integrations"
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        className="space-y-6"
                    >
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                            {/* Add New Card */}
                            <button onClick={() => setShowAddModal(true)} className="group h-full min-h-[160px] border border-dashed border-slate-700 hover:border-indigo-500 rounded-2xl flex flex-col items-center justify-center gap-3 transition-colors bg-white/5 hover:bg-white/10">
                                <div className="w-12 h-12 rounded-full bg-indigo-500/10 group-hover:bg-indigo-500/20 flex items-center justify-center transition-colors">
                                    <Plus className="w-6 h-6 text-indigo-400" />
                                </div>
                                <span className="text-slate-300 font-medium group-hover:text-white">Add Custom API</span>
                            </button>

                            {/* Existing Integrations */}
                            {integrations.map((int) => (
                                <GlassCard key={int.id} className="relative overflow-hidden group">
                                    <div className="flex items-start justify-between mb-4">
                                        <div className={cn("p-3 rounded-xl",
                                            int.type === "CRM" ? "bg-blue-500/20 text-blue-400" :
                                                int.type === "Email" ? "bg-amber-500/20 text-amber-400" :
                                                    int.type === "Chat" ? "bg-emerald-500/20 text-emerald-400" :
                                                        "bg-purple-500/20 text-purple-400"
                                        )}>
                                            {int.type === "CRM" ? <Database className="w-6 h-6" /> :
                                                int.type === "Email" ? <Mail className="w-6 h-6" /> :
                                                    int.type === "Chat" ? <MessageSquare className="w-6 h-6" /> :
                                                        <Terminal className="w-6 h-6" />}
                                        </div>
                                        <div className={cn("w-3 h-3 rounded-full", int.connected ? "bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.5)]" : "bg-slate-700")} />
                                    </div>

                                    <h3 className="text-lg font-bold text-white mb-1">{int.name}</h3>
                                    <p className="text-xs text-slate-500 mb-6">Type: {int.type} • {int.lastSync ? `Synced ${int.lastSync}` : "Not synced"}</p>

                                    <div className="flex items-center gap-3">
                                        <Button
                                            variant="secondary"
                                            size="sm"
                                            onClick={() => toggleIntegration(int.id)}
                                            className={cn("w-full transition-colors", int.connected ? "bg-red-500/10 text-red-400 hover:bg-red-500/20 border-red-500/20" : "")}
                                        >
                                            {int.connected ? "Disconnect" : "Connect"}
                                        </Button>
                                        {int.type === "Custom" && (
                                            <Button variant="ghost" size="sm" className="text-slate-500 hover:text-red-400">
                                                <Trash2 className="w-4 h-4" />
                                            </Button>
                                        )}
                                    </div>
                                </GlassCard>
                            ))}
                        </div>

                        {/* Add Modal (Simple Overlay) */}
                        {showAddModal && (
                            <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
                                <GlassCard className="w-full max-w-md border border-indigo-500/30 shadow-2xl">
                                    <h2 className="text-xl font-bold text-white mb-4">Add Custom Data Source</h2>
                                    <div className="space-y-4">
                                        <div>
                                            <label className="text-xs text-slate-400 uppercase font-semibold mb-1 block">API Name</label>
                                            <input
                                                type="text"
                                                value={newApiName}
                                                onChange={(e) => setNewApiName(e.target.value)}
                                                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-4 py-2 text-white focus:border-indigo-500 outline-none"
                                                placeholder="e.g. External Credit Scoring"
                                            />
                                        </div>
                                        <div>
                                            <label className="text-xs text-slate-400 uppercase font-semibold mb-1 block">Endpoint URL</label>
                                            <input
                                                type="text"
                                                value={newApiEndpoint}
                                                onChange={(e) => setNewApiEndpoint(e.target.value)}
                                                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-4 py-2 text-white focus:border-indigo-500 outline-none"
                                                placeholder="https://api.partner.com/v1/data"
                                            />
                                        </div>
                                        <div className="flex gap-3 pt-2">
                                            <Button variant="secondary" className="flex-1" onClick={() => setShowAddModal(false)}>Cancel</Button>
                                            <Button variant="primary" className="flex-1" onClick={handleAddIntegration}>Add Source</Button>
                                        </div>
                                    </div>
                                </GlassCard>
                            </div>
                        )}
                    </motion.div>
                ) : (
                    <motion.div
                        key="automation"
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        className="max-w-3xl mx-auto"
                    >
                        <GlassCard>
                            <div className="flex items-start gap-4 mb-6">
                                <div className="p-3 rounded-xl bg-indigo-500/20">
                                    <Mail className="w-6 h-6 text-indigo-400" />
                                </div>
                                <div>
                                    <h3 className="text-lg font-bold text-white">Email Automation</h3>
                                    <p className="text-sm text-slate-400">Configure auto-replies for new or incomplete loan requests.</p>
                                </div>
                            </div>

                            <div className="space-y-6">
                                <div>
                                    <label className="text-sm font-medium text-slate-300 block mb-2">Trigger Event</label>
                                    <select className="w-full bg-slate-950 border border-slate-800 rounded-lg px-4 py-3 text-slate-300 outline-none focus:border-indigo-500">
                                        <option>New Request (Unknown Source)</option>
                                        <option>Incomplete Documents</option>
                                        <option>Loan Approved</option>
                                        <option>Loan Rejected</option>
                                    </select>
                                </div>

                                <div>
                                    <label className="text-sm font-medium text-slate-300 block mb-2">Subject Line</label>
                                    <input
                                        type="text"
                                        defaultValue="Action Required: Complete your Loan Application"
                                        className="w-full bg-slate-950 border border-slate-800 rounded-lg px-4 py-3 text-slate-300 outline-none focus:border-indigo-500"
                                    />
                                </div>

                                <div>
                                    <label className="text-sm font-medium text-slate-300 block mb-2">Email Body Template</label>
                                    <textarea
                                        rows={6}
                                        value={emailTemplate}
                                        onChange={(e) => setEmailTemplate(e.target.value)}
                                        className="w-full bg-slate-950 border border-slate-800 rounded-lg px-4 py-3 text-slate-300 outline-none focus:border-indigo-500 font-mono text-sm"
                                    />
                                    <p className="text-xs text-slate-500 mt-2">Available variables: {"{ClientName}, {LoanID}, {Link}"}</p>
                                </div>

                                <div className="pt-4 flex justify-end">
                                    <Button className="gap-2">
                                        <Save className="w-4 h-4" /> Save Configuration
                                    </Button>
                                </div>
                            </div>
                        </GlassCard>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}
