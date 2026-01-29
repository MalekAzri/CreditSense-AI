'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Send, Sparkles, Loader2 } from 'lucide-react';

interface EmailReplyModalProps {
    email: {
        id: number;
        subject: string;
        sender: string;
        body: string;
    };
    client?: any;
    mode: 'auto' | 'manual';
    onClose: () => void;
}

export default function EmailReplyModal({ email, client, mode, onClose }: EmailReplyModalProps) {
    const [body, setBody] = useState('');
    const [subject, setSubject] = useState(`Re: ${email.subject}`);
    const [loading, setLoading] = useState(false);
    const [sending, setSending] = useState(false);

    useEffect(() => {
        if (mode === 'auto') {
            fetchSuggestion();
        }
    }, [mode]);

    const fetchSuggestion = async () => {
        setLoading(true);
        try {
            const response = await fetch('http://localhost:8000/messages/generate-reply', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    email_text: email.body,
                    client_data: client || null
                })
            });
            const data = await response.json();
            setBody(data.suggestion);
        } catch (error) {
            console.error('Error fetching suggestion:', error);
            setBody("Bonjour, nous avons bien reçu votre email...");
        } finally {
            setLoading(false);
        }
    };

    const handleSend = async () => {
        setSending(true);
        try {
            const destEmail = email.sender.match(/<([^>]+)>/)?.[1] || email.sender;

            const response = await fetch('http://localhost:8000/messages/send-reply', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    to_email: destEmail,
                    subject: subject,
                    body: body
                })
            });

            if (response.ok) {
                alert('Email envoyé avec succès !');
                onClose();
            } else {
                alert("Erreur lors de l'envoi de l'email.");
            }
        } catch (error) {
            console.error('Error sending reply:', error);
            alert("Erreur réseau lors de l'envoi.");
        } finally {
            setSending(false);
        }
    };

    return (
        <AnimatePresence>
            <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
                <motion.div
                    initial={{ opacity: 0, scale: 0.95, y: 20 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.95, y: 20 }}
                    className="bg-[#0f172a] border border-slate-800 rounded-2xl w-full max-w-2xl overflow-hidden shadow-2xl"
                >
                    {/* Header */}
                    <div className="p-6 border-b border-slate-800 flex items-center justify-between bg-slate-900/50">
                        <div className="flex items-center gap-3">
                            <div className={`p-2 rounded-lg ${mode === 'auto' ? 'bg-indigo-500/10 text-indigo-400' : 'bg-slate-700/10 text-slate-400'}`}>
                                {mode === 'auto' ? <Sparkles size={20} /> : <Send size={20} />}
                            </div>
                            <div>
                                <h2 className="text-xl font-semibold text-white">
                                    {mode === 'auto' ? 'Réponse Automatisée (AI)' : 'Réponse Manuelle'}
                                </h2>
                                <p className="text-sm text-slate-400">À : {email.sender}</p>
                            </div>
                        </div>
                        <button onClick={onClose} className="p-2 hover:bg-slate-800 rounded-full transition-colors text-slate-400">
                            <X size={20} />
                        </button>
                    </div>

                    {/* Content */}
                    <div className="p-6 space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-slate-400 mb-1.5 ml-1">Sujet</label>
                            <input
                                type="text"
                                value={subject}
                                onChange={(e) => setSubject(e.target.value)}
                                className="w-full bg-slate-900/50 border border-slate-700 rounded-xl px-4 py-2.5 text-white placeholder:text-slate-600 focus:outline-none focus:ring-2 focus:ring-indigo-500/40 transition-all"
                            />
                        </div>

                        <div className="relative">
                            <label className="block text-sm font-medium text-slate-400 mb-1.5 ml-1">Message</label>
                            {loading ? (
                                <div className="h-64 flex flex-col items-center justify-center bg-slate-900/50 border border-slate-700 rounded-xl gap-3">
                                    <Loader2 className="animate-spin text-indigo-400" size={32} />
                                    <p className="text-slate-400 animate-pulse">L'IA génère votre réponse...</p>
                                </div>
                            ) : (
                                <textarea
                                    value={body}
                                    onChange={(e) => setBody(e.target.value)}
                                    className="w-full h-64 bg-slate-900/50 border border-slate-700 rounded-xl px-4 py-3 text-white placeholder:text-slate-600 focus:outline-none focus:ring-2 focus:ring-indigo-500/40 transition-all resize-none"
                                    placeholder="Épuisez votre réponse ici..."
                                />
                            )}
                        </div>
                    </div>

                    {/* Footer */}
                    <div className="p-6 bg-slate-900/50 border-t border-slate-800 flex items-center justify-end gap-3">
                        <button
                            onClick={onClose}
                            className="px-5 py-2.5 rounded-xl text-slate-400 hover:bg-slate-800 transition-colors font-medium"
                        >
                            Annuler
                        </button>
                        <button
                            onClick={handleSend}
                            disabled={sending || loading || !body.trim()}
                            className="flex items-center gap-2 px-6 py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all rounded-xl text-white font-semibold shadow-lg shadow-indigo-500/20"
                        >
                            {sending ? (
                                <Loader2 className="animate-spin" size={18} />
                            ) : (
                                <Send size={18} />
                            )}
                            {sending ? 'Envoi...' : 'Envoyer'}
                        </button>
                    </div>
                </motion.div>
            </div>
        </AnimatePresence>
    );
}
