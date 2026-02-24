"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useState } from "react";
import { ArrowRight } from "iconoir-react";

/* ─── Types ───────────────────────────────────────────────────── */

interface Exercise {
    name: string;
    description: string;
    sets?: string;
    reps?: string;
    hold?: string;
    frequency?: string;
}

interface PhaseCardProps {
    phaseNumber: number;
    title: string;
    timeframe: string;
    goal: string;
    exercises: Exercise[];
    instructions: string[];
    totalPhases: number;
}

/* ─── Colors ──────────────────────────────────────────────────── */

const phaseColors = [
    {
        bg: "bg-red-50",
        border: "border-red-200",
        accent: "bg-red-600",
        text: "text-red-700",
        lightBg: "bg-red-100",
        badge: "bg-red-100 text-red-700",
        glow: "shadow-red-200/50",
        statBg: "bg-red-50 border-red-100",
        statText: "text-red-600",
        exerciseBg: "bg-white border-red-100",
    },
    {
        bg: "bg-amber-50",
        border: "border-amber-200",
        accent: "bg-amber-500",
        text: "text-amber-700",
        lightBg: "bg-amber-100",
        badge: "bg-amber-100 text-amber-700",
        glow: "shadow-amber-200/50",
        statBg: "bg-amber-50 border-amber-100",
        statText: "text-amber-600",
        exerciseBg: "bg-white border-amber-100",
    },
    {
        bg: "bg-emerald-50",
        border: "border-emerald-200",
        accent: "bg-emerald-600",
        text: "text-emerald-700",
        lightBg: "bg-emerald-100",
        badge: "bg-emerald-100 text-emerald-700",
        glow: "shadow-emerald-200/50",
        statBg: "bg-emerald-50 border-emerald-100",
        statText: "text-emerald-600",
        exerciseBg: "bg-white border-emerald-100",
    },
    {
        bg: "bg-blue-50",
        border: "border-blue-200",
        accent: "bg-blue-600",
        text: "text-blue-700",
        lightBg: "bg-blue-100",
        badge: "bg-blue-100 text-blue-700",
        glow: "shadow-blue-200/50",
        statBg: "bg-blue-50 border-blue-100",
        statText: "text-blue-600",
        exerciseBg: "bg-white border-blue-100",
    },
];

/* ─── Stat Pill ───────────────────────────────────────────────── */

function StatPill({
    label,
    value,
    colorClasses,
}: {
    label: string;
    value: string;
    colorClasses: { statBg: string; statText: string };
}) {
    if (!value || value.toLowerCase() === "n/a") return null;
    return (
        <div className={`flex flex-col items-center rounded-xl border px-3 py-2 ${colorClasses.statBg}`}>
            <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">
                {label}
            </span>
            <span className={`text-sm font-bold ${colorClasses.statText}`}>{value}</span>
        </div>
    );
}

/* ─── Exercise Card ───────────────────────────────────────────── */

function ExerciseCard({
    exercise,
    index,
    colors,
}: {
    exercise: Exercise;
    index: number;
    colors: (typeof phaseColors)[0];
}) {
    const hasStats = exercise.sets || exercise.reps || exercise.hold || exercise.frequency;

    return (
        <motion.div
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.06 }}
            className={`rounded-xl border ${colors.exerciseBg} p-4 transition-shadow hover:shadow-sm`}
        >
            <div className="flex items-start gap-3">
                {/* Exercise number badge */}
                <div
                    className={`flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-lg ${colors.lightBg} text-xs font-bold ${colors.text}`}
                >
                    {index + 1}
                </div>
                <div className="flex-1 min-w-0">
                    <h4 className="text-sm font-semibold text-slate-900">
                        {exercise.name.replace(/:/g, "")}
                    </h4>
                    {exercise.description && (
                        <p className="mt-1 text-xs leading-relaxed text-slate-500">
                            {exercise.description}
                        </p>
                    )}

                    {/* Stats row */}
                    {hasStats && (
                        <div className="mt-3 flex flex-wrap gap-2">
                            <StatPill label="Sets" value={exercise.sets || ""} colorClasses={colors} />
                            <StatPill label="Reps" value={exercise.reps || ""} colorClasses={colors} />
                            <StatPill label="Hold" value={exercise.hold || ""} colorClasses={colors} />
                            <StatPill
                                label="Freq"
                                value={exercise.frequency || ""}
                                colorClasses={colors}
                            />
                        </div>
                    )}
                </div>
            </div>
        </motion.div>
    );
}

/* ─── Phase Card ──────────────────────────────────────────────── */

export default function PhaseCard({
    phaseNumber,
    title,
    timeframe,
    goal,
    exercises,
    instructions,
    totalPhases,
}: PhaseCardProps) {
    const [expanded, setExpanded] = useState(phaseNumber === 1);
    const colors = phaseColors[(phaseNumber - 1) % phaseColors.length];
    const totalItems = exercises.length + instructions.length;

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: phaseNumber * 0.12, duration: 0.4 }}
            className={`relative overflow-hidden rounded-2xl border ${colors.border} ${colors.bg} shadow-sm ${colors.glow} transition-shadow hover:shadow-md`}
        >
            {/* Progress bar at top */}
            <div className="h-1 w-full bg-slate-200/50">
                <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${(phaseNumber / totalPhases) * 100}%` }}
                    transition={{ duration: 0.8, delay: phaseNumber * 0.15 }}
                    className={`h-full ${colors.accent}`}
                />
            </div>

            {/* Header */}
            <button
                onClick={() => setExpanded(!expanded)}
                className="flex w-full items-center justify-between p-5 text-left"
            >
                <div className="flex items-center gap-4">
                    <div
                        className={`flex h-11 w-11 flex-shrink-0 items-center justify-center rounded-xl ${colors.accent} text-sm font-bold text-white shadow-lg`}
                    >
                        {phaseNumber}
                    </div>
                    <div>
                        <h3 className="text-lg font-bold text-slate-900">{title}</h3>
                        <div className="flex items-center gap-2 mt-1">
                            {timeframe && (
                                <span
                                    className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-semibold ${colors.badge}`}
                                >
                                    {timeframe}
                                </span>
                            )}
                            {totalItems > 0 && (
                                <span className="text-xs text-slate-400">
                                    {exercises.length > 0
                                        ? `${exercises.length} exercise${exercises.length !== 1 ? "s" : ""}`
                                        : `${instructions.length} item${instructions.length !== 1 ? "s" : ""}`}
                                </span>
                            )}
                        </div>
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

                            {/* Instructions (non-exercise items) */}
                            {instructions.length > 0 && exercises.length > 0 && (
                                <div className="space-y-1.5">
                                    {instructions.map((item, idx) => (
                                        <div
                                            key={`instr-${idx}`}
                                            className="flex items-start gap-3 rounded-lg bg-white/60 p-3 text-sm text-slate-600 leading-relaxed"
                                        >
                                            <div
                                                className={`mt-1.5 h-2 w-2 flex-shrink-0 rounded-full ${colors.accent}`}
                                            />
                                            <span>{item.replace(/\*\*/g, "")}</span>
                                        </div>
                                    ))}
                                </div>
                            )}

                            {/* Exercise cards */}
                            {exercises.length > 0 && (
                                <div className="space-y-3">
                                    <p className="text-xs font-bold uppercase tracking-wider text-slate-400 pl-1">
                                        Exercises
                                    </p>
                                    {exercises.map((exercise, idx) => (
                                        <ExerciseCard
                                            key={idx}
                                            exercise={exercise}
                                            index={idx}
                                            colors={colors}
                                        />
                                    ))}
                                </div>
                            )}

                            {/* Fallback: only instructions, no exercises */}
                            {exercises.length === 0 && instructions.length > 0 && (
                                <div className="space-y-2">
                                    {instructions.map((item, idx) => (
                                        <motion.div
                                            key={idx}
                                            initial={{ opacity: 0, x: -10 }}
                                            animate={{ opacity: 1, x: 0 }}
                                            transition={{ delay: idx * 0.05 }}
                                            className="flex items-start gap-3 rounded-lg bg-white/70 p-3 text-sm text-slate-700 leading-relaxed"
                                        >
                                            <div
                                                className={`mt-1.5 h-2 w-2 flex-shrink-0 rounded-full ${colors.accent}`}
                                            />
                                            <span>{item.replace(/\*\*/g, "")}</span>
                                        </motion.div>
                                    ))}
                                </div>
                            )}
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </motion.div>
    );
}
