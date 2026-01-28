"use client";

import { useEffect, useState, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, Send } from "lucide-react";
import { Button } from "../ui/Button";
import { GlassCard } from "../ui/GlassCard";

interface Message {
    id: number;
    content: string;
    senderId: number;
    receiverId: number;
    createdAt: string;
}

export function ChatDialog({
    analyst,
    currentUserId,
    onClose
}: {
    analyst: any;
    currentUserId: number;
    onClose: () => void
}) {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState("");
    const [sending, setSending] = useState(false);
    const scrollRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const fetchMessages = async () => {
            try {
                const res = await fetch(`/api/messages?targetId=${analyst.id}`);
                const data = await res.json();
                if (Array.isArray(data)) {
                    setMessages(data);
                }
            } catch (err) {
                console.error("Error loading chat context:", err);
            }
        };

        fetchMessages();
        const interval = setInterval(fetchMessages, 3000); // Poll every 3s
        return () => clearInterval(interval);
    }, [analyst.id]);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages]);

    const handleSend = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim() || sending) return;

        setSending(true);
        try {
            const res = await fetch("/api/messages", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ targetId: analyst.id, content: input }),
            });

            if (res.ok) {
                const newMessage = await res.json();
                setMessages([...messages, newMessage]);
                setInput("");
            }
        } catch (err) {
            console.error("Error sending message:", err);
        } finally {
            setSending(false);
        }
    };

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
            <motion.div
                initial={{ opacity: 0, scale: 0.95, y: 20 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                className="w-full max-w-lg h-[600px] flex flex-col"
            >
                <GlassCard className="h-full flex flex-col p-0 border-white/10 overflow-hidden shadow-2xl bg-[#0F1219]">
                    {/* Header */}
                    <div className="p-4 border-b border-white/5 flex items-center justify-between bg-white/[0.02]">
                        <div className="flex items-center gap-3">
                            <div className="relative">
                                <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-indigo-500 to-purple-600 flex items-center justify-center text-xs font-bold text-white border border-white/10 uppercase">
                                    {analyst.prenom?.[0]}{analyst.nom?.[0]}
                                </div>
                                {analyst.isOnline && (
                                    <div className="absolute bottom-0 right-0 w-3 h-3 bg-emerald-500 border-2 border-[#0B0E14] rounded-full" />
                                )}
                            </div>
                            <div>
                                <h3 className="font-semibold text-white">{analyst.prenom} {analyst.nom}</h3>
                                <p className="text-[10px] text-slate-400 uppercase tracking-widest">{analyst.role}</p>
                            </div>
                        </div>
                        <Button variant="ghost" size="sm" onClick={onClose} className="hover:bg-red-500/10 hover:text-red-400">
                            <X className="w-5 h-5" />
                        </Button>
                    </div>

                    {/* Messages */}
                    <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-thin scrollbar-thumb-white/5">
                        {messages.length === 0 ? (
                            <div className="h-full flex flex-col items-center justify-center text-center opacity-40">
                                <p className="text-sm">End of record stream. No previous transmissions.</p>
                            </div>
                        ) : (
                            messages.map((msg) => {
                                // Logic: In a 1-to-1 chat, if the sender is NOT the target analyst, it must be ME.
                                const isMe = msg.senderId !== analyst.id;
                                return (
                                    <div key={msg.id} className={`flex ${isMe ? "justify-end" : "justify-start"}`}>
                                        <div className={`max-w-[80%] p-3 rounded-2xl text-sm ${isMe
                                            ? "bg-indigo-600 text-white rounded-br-none shadow-lg shadow-indigo-500/10"
                                            : "bg-white/5 text-slate-200 border border-white/5 rounded-bl-none"
                                            }`}>
                                            {msg.content}
                                            <div className={`text-[10px] mt-1 opacity-50 ${isMe ? "text-right font-medium" : "text-left"}`}>
                                                {new Date(msg.createdAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                            </div>
                                        </div>
                                    </div>
                                );
                            })
                        )}
                    </div>

                    {/* Footer */}
                    <form onSubmit={handleSend} className="p-4 border-t border-white/5 bg-white/[0.02] flex gap-3">
                        <input
                            type="text"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder="Broadcast internal communication..."
                            className="flex-1 bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-sm text-white outline-none focus:border-indigo-500/50 transition-all placeholder:text-slate-600"
                        />
                        <Button type="submit" size="sm" disabled={!input.trim() || sending} className="px-6 h-12 rounded-xl">
                            <Send className="w-4 h-4" />
                        </Button>
                    </form>
                </GlassCard>
            </motion.div>
        </div>
    );
}
