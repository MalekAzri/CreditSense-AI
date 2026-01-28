"use client";

import { useState, useEffect } from "react";
import { signIn } from "next-auth/react";
import { motion } from "framer-motion";
import { ShieldCheck, ArrowRight, Lock, Mail, Loader2 } from "lucide-react";
import { Button } from "../ui/Button";
import { GlassCard } from "../ui/GlassCard";
import { useSearchParams, useRouter } from "next/navigation";
import Link from "next/link";

export function LoginView() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [statusMsg, setStatusMsg] = useState("");
    const [loading, setLoading] = useState(false);
    const searchParams = useSearchParams();
    const router = useRouter();

    useEffect(() => {
        if (searchParams.get("registered")) {
            setStatusMsg("Inscription réussie ! Vous pouvez maintenant vous connecter.");
        }
    }, [searchParams]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError("");
        setStatusMsg("");
        setLoading(true);

        try {
            const result = await signIn("credentials", {
                email,
                password,
                redirect: false,
            });

            if (result?.error) {
                setError("Email ou mot de passe incorrect.");
            } else {
                // Succès -> Redirection vers le dashboard
                router.push("/");
            }
        } catch (err) {
            setError("Une erreur est survenue lors de l'authentification.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="h-full w-full min-h-screen flex items-center justify-center relative overflow-hidden bg-[#05070a]">
            {/* Background Ambience */}
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
                        <h1 className="text-3xl font-bold text-white mb-2">CreditSense AI</h1>
                        <p className="text-slate-400">Secure Analyst Workspace</p>
                    </div>

                    <form onSubmit={handleSubmit} className="space-y-6">
                        {error && (
                            <motion.div
                                initial={{ opacity: 0, y: -10 }}
                                animate={{ opacity: 1, y: 0 }}
                                className="p-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm text-center"
                            >
                                {error}
                            </motion.div>
                        )}
                        {statusMsg && (
                            <motion.div
                                initial={{ opacity: 0, y: -10 }}
                                animate={{ opacity: 1, y: 0 }}
                                className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-sm text-center"
                            >
                                {statusMsg}
                            </motion.div>
                        )}

                        <div className="space-y-4">
                            <div className="space-y-2">
                                <label className="text-xs uppercase tracking-wider text-slate-500 font-semibold px-1">Email</label>
                                <div className="relative">
                                    <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                                    <input
                                        type="email"
                                        value={email}
                                        onChange={(e) => setEmail(e.target.value)}
                                        className="w-full bg-slate-900/50 border border-slate-700/50 rounded-xl px-12 py-3 text-slate-200 outline-none focus:border-indigo-500/50 focus:ring-1 focus:ring-indigo-500/50 transition-all placeholder:text-slate-600"
                                        placeholder="analyst@creditsense.ai"
                                        required
                                    />
                                </div>
                            </div>

                            <div className="space-y-2">
                                <label className="text-xs uppercase tracking-wider text-slate-500 font-semibold px-1">Password</label>
                                <div className="relative">
                                    <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                                    <input
                                        type="password"
                                        value={password}
                                        onChange={(e) => setPassword(e.target.value)}
                                        className="w-full bg-slate-900/50 border border-slate-700/50 rounded-xl px-12 py-3 text-slate-200 outline-none focus:border-indigo-500/50 focus:ring-1 focus:ring-indigo-500/50 transition-all placeholder:text-slate-600"
                                        placeholder="••••••••••••"
                                        required
                                    />
                                </div>
                            </div>
                        </div>

                        <Button type="submit" disabled={loading} className="w-full gap-2 group h-12" size="lg">
                            {loading ? (
                                <Loader2 className="w-5 h-5 animate-spin" />
                            ) : (
                                <>
                                    Authenticate
                                    <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                                </>
                            )}
                        </Button>

                        <div className="text-center pt-2">
                            <p className="text-sm text-slate-500">
                                Don't have an account?{" "}
                                <Link href="/register" className="text-indigo-400 hover:text-indigo-300 font-medium transition-colors">
                                    Create one
                                </Link>
                            </p>
                        </div>
                    </form>
                </GlassCard>
            </motion.div>
        </div>
    );
}
