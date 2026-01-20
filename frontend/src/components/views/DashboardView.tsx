"use client";

import { motion } from "framer-motion";
import { mockLoans } from "@/lib/mockData";
import { GlassCard } from "../ui/GlassCard";
import { Button } from "../ui/Button";
import { Search, Filter, ArrowUpRight, AlertTriangle, CheckCircle, Clock } from "lucide-react";
import { useRouter } from "next/navigation";
import { cn } from "@/lib/utils";

export function DashboardView() {
    const router = useRouter();

    const getRiskColor = (score: number) => {
        if (score < 30) return "text-emerald-400 bg-emerald-500/10 border-emerald-500/20";
        if (score < 70) return "text-amber-400 bg-amber-500/10 border-amber-500/20";
        return "text-red-400 bg-red-500/10 border-red-500/20";
    };

    const statusIcons: any = {
        "Approved": CheckCircle,
        "Needs Review": AlertTriangle,
        "Pending": Clock,
        "Rejected": AlertTriangle
    };

    return (
        <div className="space-y-8 pb-12">
            {/* Overview Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {[
                    { label: "Pending Requests", value: "12", trend: "+15%", color: "text-blue-400" },
                    { label: "High Risk Detected", value: "3", trend: "+2", color: "text-red-400" },
                    { label: "Processed Today", value: "28", trend: "+8%", color: "text-emerald-400" },
                ].map((stat, i) => (
                    <GlassCard key={i} className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-slate-500 uppercase tracking-wider font-medium">{stat.label}</p>
                            <h3 className="text-3xl font-bold mt-1 text-white">{stat.value}</h3>
                        </div>
                        <div className={cn("px-3 py-1 rounded-full text-xs font-semibold bg-white/5", stat.color)}>
                            {stat.trend}
                        </div>
                    </GlassCard>
                ))}
            </div>

            {/* Main Table */}
            <div className="space-y-4">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <h2 className="text-2xl font-bold text-white">Loan Requests</h2>
                    <div className="flex gap-2">
                        <div className="relative group">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500 group-focus-within:text-indigo-400" />
                            <input
                                type="text"
                                placeholder="Search applicants..."
                                className="bg-slate-900/50 border border-slate-700 rounded-lg pl-9 pr-4 py-2 text-sm text-slate-200 outline-none focus:border-indigo-500/50 transition-all w-64"
                            />
                        </div>
                        <Button variant="secondary" size="sm" className="gap-2">
                            <Filter className="w-4 h-4" /> Filter
                        </Button>
                    </div>
                </div>

                <GlassCard className="p-0 overflow-hidden">
                    <div className="overflow-x-auto">
                        <table className="w-full text-left text-sm text-slate-400">
                            <thead className="bg-white/5 uppercase text-xs font-semibold text-slate-300">
                                <tr>
                                    <th className="px-6 py-4">Request ID</th>
                                    <th className="px-6 py-4">Applicant</th>
                                    <th className="px-6 py-4">Source</th>
                                    <th className="px-6 py-4">Amount</th>
                                    <th className="px-6 py-4">Risk Score</th>
                                    <th className="px-6 py-4">Status</th>
                                    <th className="px-6 py-4 text-right">Action</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-white/5">
                                {mockLoans.map((loan, idx) => {
                                    const StatusIcon = statusIcons[loan.status] || Clock;
                                    return (
                                        <motion.tr
                                            key={loan.id}
                                            initial={{ opacity: 0, x: -20 }}
                                            animate={{ opacity: 1, x: 0 }}
                                            transition={{ delay: idx * 0.05 }}
                                            onClick={() => router.push(`/dashboard/${loan.id}`)}
                                            className="hover:bg-white/5 transition-colors cursor-pointer group"
                                        >
                                            <td className="px-6 py-4 font-mono text-xs">{loan.id}</td>
                                            <td className="px-6 py-4 font-medium text-white">{loan.applicant}</td>
                                            <td className="px-6 py-4">
                                                <span className="inline-flex items-center gap-1.5 px-2 py-1 rounded-md bg-white/5 text-xs">
                                                    {loan.source}
                                                </span>
                                            </td>
                                            <td className="px-6 py-4 text-white">
                                                {new Intl.NumberFormat('en-US', { style: 'currency', currency: 'TND' }).format(loan.amount)}
                                            </td>
                                            <td className="px-6 py-4">
                                                <span className={cn("px-2 py-1 rounded-full text-xs font-bold border", getRiskColor(loan.riskScore))}>
                                                    {loan.riskScore}/100
                                                </span>
                                            </td>
                                            <td className="px-6 py-4">
                                                <div className="flex items-center gap-2">
                                                    <StatusIcon className="w-4 h-4" />
                                                    <span>{loan.status}</span>
                                                </div>
                                            </td>
                                            <td className="px-6 py-4 text-right">
                                                <ArrowUpRight className="w-4 h-4 inline-block opacity-0 -translate-x-2 group-hover:opacity-100 group-hover:translate-x-0 transition-all text-indigo-400" />
                                            </td>
                                        </motion.tr>
                                    );
                                })}
                            </tbody>
                        </table>
                    </div>
                </GlassCard>
            </div>
        </div>
    );
}
