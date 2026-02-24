"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useState } from "react";
import { ArrowRight } from "iconoir-react";

interface PhaseCardProps {
    phaseNumber: number;
    title: string;
    timeframe: string;
    goal: string;
    content: string[];
    totalPhases: number;
}

const phaseColors = [
    {
        bg: "bg-red-50",
        border: "border-red-200",
        accent: "bg-red-600",
        text: "text-red-700",
        lightBg: "bg-red-100",
        badge: "bg-red-100 text-red-700",
        glow: "shadow-red-200/50",
    },
    {
        bg: "bg-amber-50",
        border: "border-amber-200",
        accent: "bg-amber-500",
        text: "text-amber-700",
        lightBg: "bg-amber-100",
        badge: "bg-amber-100 text-amber-700",
        glow: "shadow-amber-200/50",
    },
    {
        bg: "bg-emerald-50",
        border: "border-emerald-200",
        accent: "bg-emerald-600",
        text: "text-emerald-700",
        lightBg: "bg-emerald-100",
        badge: "bg-emerald-100 text-emerald-700",
        glow: "shadow-emerald-200/50",
    },
    {
        bg: "bg-blue-50",
        border: "border-blue-200",
        accent: "bg-blue-600",
        text: "text-blue-700",
        lightBg: "bg-blue-100",
        badge: "bg-blue-100 text-blue-700",
        glow: "shadow-blue-200/50",
    },
];

export default function PhaseCard({
    phaseNumber,
    title,
    timeframe,
    goal,
    content,
    totalPhases,
}: PhaseCardProps) {
    const [expanded, setExpanded] = useState(phaseNumber === 1);
    const colors = phaseColors[(phaseNumber - 1) % phaseColors.length];

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: phaseNumber * 0.12, duration: 0.4 }}
            className={`relative overflow-hidden rounded-2xl border ${colors.border} ${colors.bg} shadow-sm ${colors.glow} transition-shadow hover:shadow-md`}
        >
            {/* Phase progress bar at top */}
            <div className="h-1 w-full bg-slate-200/50">
                <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${(phaseNumber / totalPhases) * 100}%` }}
                    transition={{ duration: 0.8, delay: phaseNumber * 0.15 }}
                    className={`h-full ${colors.accent}`}
                />
            </div>

            {/* Header — always visible */}
            <button
                onClick={() => setExpanded(!expanded)}
                className="flex w-full items-center justify-between p-5 text-left"
            >
                <div className="flex items-center gap-4">
                    {/* Phase number badge */}
                    <div
                        className={`flex h-11 w-11 flex-shrink-0 items-center justify-center rounded-xl ${colors.accent} text-sm font-bold text-white shadow-lg`}
                    >
                        {phaseNumber}
                    </div>
                    <div>
                        <h3 className="text-lg font-bold text-slate-900">{title}</h3>
                        <span className={`mt-0.5 inline-block rounded-full px-2.5 py-0.5 text-xs font-semibold ${colors.badge}`}>
                            {timeframe}
                        </span>
                    </div>
                </div>

                <motion.div
                    animate={{ rotate: expanded ? 90 : 0 }}
                    transition={{ duration: 0.2 }}
                    className="flex-shrink-0 text-slate-400"
                >
                    <ArrowRight className="h-5 w-5" />
                </motion.div>
            </button>

            {/* Expandable content */}
            <AnimatePresence initial={false}>
                {expanded && (
                    <motion.div
                        key="content"
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: "auto", opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.3, ease: "easeInOut" }}
                        className="overflow-hidden"
                    >
                        <div className="space-y-4 px-5 pb-6">
                            {/* Goal */}
                            {goal && (
                                <div className={`rounded-xl ${colors.lightBg} p-4`}>
                                    <p className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-1">
                                        Goal
                                    </p>
                                    <p className={`text-sm font-medium ${colors.text}`}>{goal}</p>
                                </div>
                            )}

                            {/* Exercise / instruction items */}
                            <div className="space-y-2">
                                {content.map((item, idx) => (
                                    <motion.div
                                        key={idx}
                                        initial={{ opacity: 0, x: -10 }}
                                        animate={{ opacity: 1, x: 0 }}
                                        transition={{ delay: idx * 0.05 }}
                                        className="flex items-start gap-3 rounded-lg bg-white/70 p-3 text-sm text-slate-700 leading-relaxed"
                                    >
                                        <div className={`mt-1.5 h-2 w-2 flex-shrink-0 rounded-full ${colors.accent}`} />
                                        <span>{item}</span>
                                    </motion.div>
                                ))}
                            </div>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </motion.div>
    );
}
