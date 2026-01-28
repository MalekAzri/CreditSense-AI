"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { ShieldCheck, ArrowRight, User, Mail, Lock, Loader2, Building2 } from "lucide-react";
import { Button } from "../ui/Button";
import { GlassCard } from "../ui/GlassCard";
import Link from "next/link";
import { useRouter } from "next/navigation";

export function RegisterView() {
    const [formData, setFormData] = useState({
        nom: "",
        prenom: "",
        email: "",
        password: "",
        bank: "",
    });
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);
    const router = useRouter();

    const banks = ["BIAT", "BNA", "STB", "Attijari Bank", "Amen Bank", "BH Bank"];

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!formData.bank) {
            setError("Veuillez choisir une banque.");
            return;
        }
        setError("");
        setLoading(true);

        try {
            const res = await fetch("/api/auth/register", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(formData),
            });

            const data = await res.json();

            if (!res.ok) {
                throw new Error(data.error || "Une erreur est survenue.");
            }

            // Succès -> Redirection vers login
            router.push("/login?registered=true");
        } catch (err: any) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="h-full w-full min-h-screen flex items-center justify-center relative overflow-hidden bg-[#05070a] py-12">
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
                        <h1 className="text-3xl font-bold text-white mb-2">Create Account</h1>
                        <p className="text-slate-400">Join CreditSense AI Analysts</p>
                    </div>

                    <form onSubmit={handleSubmit} className="space-y-4">
                        {error && (
                            <motion.div
                                initial={{ opacity: 0, y: -10 }}
                                animate={{ opacity: 1, y: 0 }}
                                className="p-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm text-center"
                            >
                                {error}
                            </motion.div>
                        )}

                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <label className="text-xs uppercase tracking-wider text-slate-500 font-semibold px-1">First Name</label>
                                <div className="relative">
                                    <User className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                                    <input
                                        type="text"
                                        required
                                        value={formData.prenom}
                                        onChange={(e) => setFormData({ ...formData, prenom: e.target.value })}
                                        className="w-full bg-slate-900/50 border border-slate-700/50 rounded-xl px-11 py-3 text-slate-200 outline-none focus:border-indigo-500/50 transition-all text-sm"
                                        placeholder="Jane"
                                    />
                                </div>
                            </div>
                            <div className="space-y-2">
                                <label className="text-xs uppercase tracking-wider text-slate-500 font-semibold px-1">Last Name</label>
                                <div className="relative">
                                    <User className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                                    <input
                                        type="text"
                                        required
                                        value={formData.nom}
                                        onChange={(e) => setFormData({ ...formData, nom: e.target.value })}
                                        className="w-full bg-slate-900/50 border border-slate-700/50 rounded-xl px-11 py-3 text-slate-200 outline-none focus:border-indigo-500/50 transition-all text-sm"
                                        placeholder="Doe"
                                    />
                                </div>
                            </div>
                        </div>

                        <div className="space-y-2">
                            <label className="text-xs uppercase tracking-wider text-slate-500 font-semibold px-1">Email</label>
                            <div className="relative">
                                <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                                <input
                                    type="email"
                                    required
                                    value={formData.email}
                                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                                    className="w-full bg-slate-900/50 border border-slate-700/50 rounded-xl px-12 py-3 text-slate-200 outline-none focus:border-indigo-500/50 transition-all"
                                    placeholder="jane.doe@creditsense.ai"
                                />
                            </div>
                        </div>

                        <div className="space-y-2">
                            <label className="text-xs uppercase tracking-wider text-slate-500 font-semibold px-1">Bank Institution</label>
                            <div className="relative text-slate-200">
                                <Building2 className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500 pointer-events-none" />
                                <select
                                    required
                                    value={formData.bank}
                                    onChange={(e) => setFormData({ ...formData, bank: e.target.value })}
                                    className="w-full bg-slate-900/50 border border-slate-800 rounded-xl px-12 py-3 text-sm outline-none focus:border-indigo-500/50 transition-all appearance-none cursor-pointer hover:bg-slate-900"
                                >
                                    <option value="" disabled className="bg-slate-950">Select Institution</option>
                                    {banks.map(bank => (
                                        <option key={bank} value={bank} className="bg-slate-950">{bank}</option>
                                    ))}
                                </select>
                                <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-slate-500">
                                    {/* Custom arrow if needed */}
                                </div>
                            </div>
                        </div>

                        <div className="space-y-2">
                            <label className="text-xs uppercase tracking-wider text-slate-500 font-semibold px-1">Password</label>
                            <div className="relative">
                                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                                <input
                                    type="password"
                                    required
                                    value={formData.password}
                                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                                    className="w-full bg-slate-900/50 border border-slate-700/50 rounded-xl px-12 py-3 text-slate-200 outline-none focus:border-indigo-500/50 transition-all"
                                    placeholder="••••••••••••"
                                />
                            </div>
                        </div>

                        <Button type="submit" disabled={loading} className="w-full gap-2 group h-12 mt-4" size="lg">
                            {loading ? (
                                <Loader2 className="w-5 h-5 animate-spin" />
                            ) : (
                                <>
                                    Create Account
                                    <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                                </>
                            )}
                        </Button>

                        <div className="text-center pt-4">
                            <p className="text-sm text-slate-500">
                                Already have an account?{" "}
                                <Link href="/login" className="text-indigo-400 hover:text-indigo-300 font-medium transition-colors">
                                    Sign in
                                </Link>
                            </p>
                        </div>
                    </form>
                </GlassCard>
            </motion.div>
        </div>
    );
}
