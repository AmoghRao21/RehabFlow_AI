"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useState } from "react";
import { Check, NavArrowDown, FireFlame, Medal, Clock } from "iconoir-react";
import ExerciseVideoCard from "./ExerciseVideoCard";

/* ─── Types ───────────────────────────────────────────────────── */

export interface Exercise {
    name: string;
    description: string;
    sets?: string;
    reps?: string;
    hold?: string;
    frequency?: string;
}

export interface DayCardProps {
    dayNumber: number;
    phase: string;        // e.g. "Acute Relief"
    phaseColor: "red" | "amber" | "emerald" | "blue";
    exercises: Exercise[];
    instructions: string[];
    isCompleted: boolean;
    isToday: boolean;
    condition: string;    // for YouTube search context
    painLocation: string; // for YouTube search context
    onComplete: (dayNumber: number) => Promise<void>;
}

/* ─── Color maps ──────────────────────────────────────────────── */

const colors = {
    red: {
        ring: "ring-red-200",
        badge: "bg-red-100 text-red-700",
        dot: "bg-red-500",
        progress: "bg-red-500",
        completedBg: "bg-red-50",
        completedBorder: "border-red-200",
        header: "from-red-500 to-rose-600",
    },
    amber: {
        ring: "ring-amber-200",
        badge: "bg-amber-100 text-amber-700",
        dot: "bg-amber-500",
        progress: "bg-amber-500",
        completedBg: "bg-amber-50",
        completedBorder: "border-amber-200",
        header: "from-amber-500 to-orange-500",
    },
    emerald: {
        ring: "ring-emerald-200",
        badge: "bg-emerald-100 text-emerald-700",
        dot: "bg-emerald-500",
        progress: "bg-emerald-500",
        completedBg: "bg-emerald-50",
        completedBorder: "border-emerald-200",
        header: "from-emerald-500 to-teal-600",
    },
    blue: {
        ring: "ring-blue-200",
        badge: "bg-blue-100 text-blue-700",
        dot: "bg-blue-400",
        progress: "bg-blue-400",
        completedBg: "bg-blue-50",
        completedBorder: "border-blue-200",
        header: "from-blue-500 to-indigo-600",
    },
};

/* ─── Component ───────────────────────────────────────────────── */

export default function DayCard({
    dayNumber,
    phase,
    phaseColor,
    exercises,
    instructions,
    isCompleted,
    isToday,
    condition,
    painLocation,
    onComplete,
}: DayCardProps) {
    const [expanded, setExpanded] = useState(isToday || dayNumber === 1);
    const [completing, setCompleting] = useState(false);
    const c = colors[phaseColor];

    const handleComplete = async (e: React.MouseEvent) => {
        e.stopPropagation();
        if (isCompleted || completing) return;
        setCompleting(true);
        try {
            await onComplete(dayNumber);
        } finally {
            setCompleting(false);
        }
    };

    const totalItems = exercises.length + instructions.length;

    return (
        <motion.div
            layout
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: Math.min(dayNumber * 0.04, 0.5), duration: 0.35 }}
            className={`overflow-hidden rounded-2xl border transition-shadow ${isCompleted
                    ? `${c.completedBorder} ${c.completedBg}`
                    : isToday
                        ? "border-purple-200 bg-white shadow-md ring-2 ring-purple-100"
                        : "border-slate-200 bg-white"
                }`}
        >
            {/* Card header (always visible) */}
            <button
                onClick={() => setExpanded((v) => !v)}
                className="flex w-full items-center gap-4 px-5 py-4 text-left"
            >
                {/* Day badge */}
                <div
                    className={`relative flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-xl bg-gradient-to-br ${c.header} text-white shadow-md`}
                >
                    {isCompleted ? (
                        <motion.div
                            initial={{ scale: 0 }}
                            animate={{ scale: 1 }}
                            transition={{ type: "spring", stiffness: 400, damping: 15 }}
                        >
                            <Check className="h-6 w-6" />
                        </motion.div>
                    ) : (
                        <span className="text-sm font-bold">{dayNumber}</span>
                    )}
                    {isToday && !isCompleted && (
                        <span className="absolute -right-1 -top-1 h-3 w-3 rounded-full bg-purple-500 ring-2 ring-white" />
                    )}
                </div>

                {/* Title area */}
                <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                        <span className="text-sm font-bold text-slate-900">Day {dayNumber}</span>
                        {isToday && !isCompleted && (
                            <span className="rounded-full bg-purple-100 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wide text-purple-700">
                                Today
                            </span>
                        )}
                        {isCompleted && (
                            <span className="rounded-full bg-emerald-100 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wide text-emerald-700">
                                ✓ Done
                            </span>
                        )}
                        <span className={`rounded-full px-2 py-0.5 text-[10px] font-semibold ${c.badge}`}>
                            {phase}
                        </span>
                    </div>
                    <p className="mt-0.5 text-xs text-slate-400">
                        {totalItems} {totalItems === 1 ? "exercise" : "exercises"}
                    </p>
                </div>

                {/* Complete button (right side) */}
                {!isCompleted && (
                    <button
                        onClick={handleComplete}
                        disabled={completing}
                        className="ml-2 flex-shrink-0 flex items-center gap-1.5 rounded-xl bg-slate-900 px-3 py-2 text-xs font-semibold text-white shadow-sm transition-all hover:bg-purple-700 hover:shadow-md disabled:opacity-60"
                    >
                        {completing ? (
                            <span className="h-3 w-3 animate-spin rounded-full border-2 border-white/40 border-t-white" />
                        ) : (
                            <Check className="h-3 w-3" />
                        )}
                        Complete
                    </button>
                )}

                {isCompleted && (
                    <div className="ml-2 flex items-center gap-1 text-emerald-500 flex-shrink-0">
                        <Medal className="h-4 w-4" />
                        <span className="text-xs font-bold">+50 pts</span>
                    </div>
                )}

                {/* Chevron */}
                <motion.div
                    animate={{ rotate: expanded ? 180 : 0 }}
                    transition={{ duration: 0.2 }}
                    className="ml-1 flex-shrink-0 text-slate-300"
                >
                    <NavArrowDown className="h-4 w-4" />
                </motion.div>
            </button>

            {/* Expandable body */}
            <AnimatePresence initial={false}>
                {expanded && (
                    <motion.div
                        key="body"
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: "auto", opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.28, ease: "easeInOut" }}
                        className="overflow-hidden"
                    >
                        <div className="space-y-3 px-5 pb-5">
                            {/* General instructions */}
                            {instructions.length > 0 && (
                                <div className="space-y-1.5">
                                    {instructions.map((instr, i) => (
                                        <div
                                            key={`instr-${i}`}
                                            className="flex items-start gap-2.5 rounded-xl bg-slate-50 px-3 py-2.5"
                                        >
                                            <div className={`mt-1.5 h-1.5 w-1.5 flex-shrink-0 rounded-full ${c.dot}`} />
                                            <p className="text-xs leading-relaxed text-slate-600">
                                                {instr.replace(/\*\*/g, "")}
                                            </p>
                                        </div>
                                    ))}
                                </div>
                            )}

                            {/* Exercise cards */}
                            {exercises.length > 0 && (
                                <div className="space-y-2.5">
                                    {exercises.map((ex, i) => (
                                        <motion.div
                                            key={i}
                                            initial={{ opacity: 0, x: -8 }}
                                            animate={{ opacity: 1, x: 0 }}
                                            transition={{ delay: i * 0.05 }}
                                            className="rounded-xl border border-slate-100 bg-white p-4 shadow-sm"
                                        >
                                            {/* Exercise name + video button */}
                                            <div className="flex items-start justify-between gap-3">
                                                <div className="flex items-start gap-2.5 flex-1 min-w-0">
                                                    <div
                                                        className={`mt-0.5 flex h-5 w-5 flex-shrink-0 items-center justify-center rounded-md bg-gradient-to-br ${c.header} text-[10px] font-bold text-white`}
                                                    >
                                                        {i + 1}
                                                    </div>
                                                    <div className="flex-1 min-w-0">
                                                        <p className="text-sm font-semibold text-slate-900 leading-tight">
                                                            {ex.name}
                                                        </p>
                                                        {ex.description && (
                                                            <p className="mt-0.5 text-xs leading-relaxed text-slate-500">
                                                                {ex.description}
                                                            </p>
                                                        )}
                                                    </div>
                                                </div>

                                                <ExerciseVideoCard
                                                    exerciseName={ex.name}
                                                    condition={condition}
                                                    painLocation={painLocation}
                                                />
                                            </div>

                                            {/* Stat pills */}
                                            {(ex.sets || ex.reps || ex.hold || ex.frequency) && (
                                                <div className="mt-3 flex flex-wrap gap-2">
                                                    {ex.sets && ex.sets.toLowerCase() !== "n/a" && (
                                                        <StatPill label="Sets" value={ex.sets} color={phaseColor} />
                                                    )}
                                                    {ex.reps && ex.reps.toLowerCase() !== "n/a" && (
                                                        <StatPill label="Reps" value={ex.reps} color={phaseColor} />
                                                    )}
                                                    {ex.hold && ex.hold.toLowerCase() !== "n/a" && (
                                                        <StatPill label="Hold" value={ex.hold} color={phaseColor} />
                                                    )}
                                                    {ex.frequency && ex.frequency.toLowerCase() !== "n/a" && (
                                                        <StatPill label="Freq" value={ex.frequency} color={phaseColor} />
                                                    )}
                                                </div>
                                            )}
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

/* ─── Stat Pill ───────────────────────────────────────────────── */

function StatPill({ label, value, color }: { label: string; value: string; color: string }) {
    const bgMap: Record<string, string> = {
        red: "bg-red-50 text-red-700 border-red-100",
        amber: "bg-amber-50 text-amber-700 border-amber-100",
        emerald: "bg-emerald-50 text-emerald-700 border-emerald-100",
        blue: "bg-blue-50 text-blue-700 border-blue-100",
    };
    return (
        <div className={`flex items-center gap-1.5 rounded-lg border px-2.5 py-1.5 ${bgMap[color] || bgMap.blue}`}>
            <Clock className="h-3 w-3 opacity-60" />
            <span className="text-[10px] font-semibold uppercase tracking-wide opacity-60">{label}</span>
            <span className="text-xs font-bold">{value}</span>
        </div>
    );
}
