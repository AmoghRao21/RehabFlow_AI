"use client";

import { useEffect, useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
    Brain,
    Sparks,
    Clock,
    CheckCircle,
    FireFlame,
    Medal,
    WarningTriangle,
    Trophy,
} from "iconoir-react";
import Link from "next/link";
import { useTranslations } from "next-intl";

import { useAuth } from "@/lib/auth-provider";
import { supabase } from "@/lib/supabase";
import DayCard, { type Exercise } from "./DayCard";

/* ─── Types ───────────────────────────────────────────────────── */

interface DaySchedule {
    dayNumber: number;
    phase: string;
    phaseColor: "red" | "amber" | "emerald" | "blue";
    exercises: Exercise[];
    instructions: string[];
}

interface AnalysisData {
    id: string;
    injury_assessment_id: string;
    probable_condition: string;
    confidence_score: number;
    reasoning: string;
    model_version: string;
    created_at: string;
}

interface ProfileStats {
    total_points: number;
    current_streak: number;
    longest_streak: number;
}

/* ─── Parser ──────────────────────────────────────────────────── */

/**
 * Parses MedGemma's raw markdown output into a structured day-by-day schedule.
 * Each Phase maps to multiple days:
 *   Phase 1 (Acute, Days 1-7)       → days 1..7
 *   Phase 2 (Recovery, Weeks 2-4)   → days 8..28  (show as day 8, 9…)
 *   Phase 3 (Strengthening, 4-8wk)  → days 29..56
 * We create representative "day cards" repeated across the phase span.
 */
function parseToDaySchedule(reasoning: string): {
    days: DaySchedule[];
    clinicalReasoning: string;
    visualAssessment: string;
    precautions: string[];
} {
    if (!reasoning) return { days: [], clinicalReasoning: "", visualAssessment: "", precautions: [] };

    const lines = reasoning.split("\n");
    let clinicalReasoning = "";
    let visualAssessment = "";
    const precautions: string[] = [];

    type SectionType = "visual" | "reasoning" | "phase" | "precautions" | "home" | null;
    interface PhaseData {
        title: string;
        timeframe: string;
        goal: string;
        color: "red" | "amber" | "emerald" | "blue";
        exercises: Exercise[];
        instructions: string[];
        dayStart: number;
        dayEnd: number;
    }

    let currentSection: SectionType = null;
    let sectionLines: string[] = [];
    const phases: PhaseData[] = [];
    let currentPhase: Partial<PhaseData> | null = null;

    const phaseRanges: Array<{ dayStart: number; dayEnd: number; color: "red" | "amber" | "emerald" | "blue" }> = [
        { dayStart: 1, dayEnd: 7, color: "red" },
        { dayStart: 8, dayEnd: 28, color: "amber" },
        { dayStart: 29, dayEnd: 56, color: "emerald" },
        { dayStart: 57, dayEnd: 84, color: "blue" },
    ];

    const flushPhase = () => {
        if (!currentPhase?.title) return;
        const { exercises, instructions } = parseExercises(sectionLines);
        const phaseIdx = phases.length;
        const range = phaseRanges[Math.min(phaseIdx, phaseRanges.length - 1)];
        phases.push({
            title: currentPhase.title!,
            timeframe: currentPhase.timeframe || "",
            goal: currentPhase.goal || "",
            color: range.color,
            exercises,
            instructions,
            dayStart: range.dayStart,
            dayEnd: range.dayEnd,
        });
        sectionLines = [];
        currentPhase = null;
    };

    for (const line of lines) {
        const trimmed = line.trim();
        const lower = trimmed.toLowerCase();

        if (!trimmed) continue;

        // Visual Assessment
        if (lower.includes("visual assessment") && (trimmed.startsWith("#") || trimmed.startsWith("**"))) {
            if (currentSection === "phase") flushPhase();
            currentSection = "visual";
            sectionLines = [];
            continue;
        }

        // Clinical Reasoning
        if (lower.includes("clinical reasoning") && !lower.includes("phase")) {
            if (currentSection === "phase") flushPhase();
            currentSection = "reasoning";
            const inline = trimmed.replace(/^\*\*Clinical Reasoning:\*\*\s*/i, "").replace(/^#+\s*Clinical Reasoning:?\s*/i, "").trim();
            sectionLines = inline ? [inline] : [];
            continue;
        }

        // Phase header: "### Phase 1 — Title (Days 1-7)"
        const phaseMatch = trimmed.match(/^(?:#{1,3}\s*)?(?:\*\*)?Phase\s*(\d+)\s*[—–\-]\s*([^(#*\n]+?)(?:\(([^)]+)\))?(?:\*\*)?:?\s*$/i);
        if (phaseMatch) {
            // Flush previous section
            if (currentSection === "phase") flushPhase();
            else if (currentSection === "visual") {
                visualAssessment = sectionLines.map(l => l.replace(/^[-*]\s*/, "")).filter(Boolean).join("\n");
                sectionLines = [];
            } else if (currentSection === "reasoning") {
                clinicalReasoning = sectionLines.filter(Boolean).map(l => l.replace(/\*\*/g, "")).join("\n");
                sectionLines = [];
            }
            currentSection = "phase";
            currentPhase = {
                title: phaseMatch[2].trim(),
                timeframe: phaseMatch[3]?.trim() || "",
                goal: "",
            };
            sectionLines = [];
            continue;
        }

        // Precautions
        if ((lower.includes("precaution") || lower.includes("warning sign")) &&
            (trimmed.startsWith("#") || trimmed.startsWith("**"))) {
            if (currentSection === "phase") flushPhase();
            currentSection = "precautions";
            sectionLines = [];
            continue;
        }

        // Rehab Plan / Home Exercise (skip header only)
        if ((lower.includes("rehabilitation plan") || lower.includes("home exercise")) &&
            (trimmed.startsWith("#") || trimmed.startsWith("**"))) {
            if (currentSection === "phase") flushPhase();
            currentSection = null;
            sectionLines = [];
            continue;
        }

        // Skip standalone metadata lines
        if (lower.startsWith("**probable condition") || lower.startsWith("**confidence") ||
            lower.startsWith("**rehabilitation plan")) continue;

        // Goal line
        if (currentSection === "phase" && currentPhase && lower.startsWith("goal:")) {
            currentPhase.goal = trimmed.replace(/^Goal:\s*/i, "").trim();
            continue;
        }

        // Collect
        if (currentSection === "visual" || currentSection === "reasoning" ||
            currentSection === "phase" || currentSection === "precautions") {
            sectionLines.push(trimmed);
        } else if (!trimmed.startsWith("#") && trimmed.length > 5) {
            clinicalReasoning += (clinicalReasoning ? "\n" : "") + trimmed.replace(/\*\*/g, "");
        }
    }

    // Flush last section
    if (currentSection === "phase") flushPhase();
    else if (currentSection === "visual") {
        visualAssessment = sectionLines.map(l => l.replace(/^[-*]\s*/, "")).filter(Boolean).join("\n");
    } else if (currentSection === "reasoning") {
        clinicalReasoning = sectionLines.filter(Boolean).map(l => l.replace(/\*\*/g, "")).join("\n");
    } else if (currentSection === "precautions") {
        sectionLines.map(l => l.replace(/^[-*]\s*/, "").replace(/\*\*/g, "").trim()).filter(l => l.length > 3).forEach(l => precautions.push(l));
    }

    // Clean clinical reasoning
    clinicalReasoning = clinicalReasoning
        .replace(/^Image \d+:.*\n?/gm, "")
        .replace(/^- Image \d+:.*\n?/gm, "")
        .replace(/\*\*Probable Condition:\*\*.*\n?/gi, "")
        .replace(/\*\*Confidence:\*\*.*\n?/gi, "")
        .trim();

    // If no phases parsed, try a simpler fallback
    if (phases.length === 0 && reasoning.length > 100) {
        // Just create 1 day with the full text as instructions
        return {
            days: [{
                dayNumber: 1,
                phase: "General",
                phaseColor: "blue",
                exercises: [],
                instructions: reasoning
                    .split("\n")
                    .map(l => l.replace(/^[#*-]\s*/, "").replace(/\*\*/g, "").trim())
                    .filter(l => l.length > 10)
                    .slice(0, 15),
            }],
            clinicalReasoning,
            visualAssessment,
            precautions,
        };
    }

    // Build day-by-day schedule
    // For each phase, create a card for each day (max 7 days per phase for UI sanity)
    const days: DaySchedule[] = [];
    for (const phase of phases) {
        const daysInPhase = Math.min(phase.dayEnd - phase.dayStart + 1, 7);
        for (let d = 0; d < daysInPhase; d++) {
            const dayNum = phase.dayStart + d;
            // Distribute exercises across days — cycle through them
            const dayExercises = phase.exercises.length > 0
                ? [phase.exercises[d % phase.exercises.length], ...(d === 0 ? phase.exercises.slice(1, 3) : [])].filter(Boolean)
                : [];
            const dayInstructions = d === 0 ? phase.instructions : phase.instructions.slice(0, 2);

            days.push({
                dayNumber: dayNum,
                phase: phase.title,
                phaseColor: phase.color,
                exercises: dayExercises,
                instructions: dayInstructions,
            });
        }
    }

    return { days, clinicalReasoning, visualAssessment, precautions };
}

function parseExercises(lines: string[]): { exercises: Exercise[]; instructions: string[] } {
    const exercises: Exercise[] = [];
    const instructions: string[] = [];
    let current: Partial<Exercise> | null = null;

    for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed) continue;

        // Exercise name line: "* **Name**: description" or "- **Name:** desc"
        const exMatch = trimmed.match(/^[*\-]\s*\*\*([^*:]+)\*\*:?\s*(.*)/);
        if (exMatch) {
            if (current?.name) exercises.push(current as Exercise);
            current = { name: exMatch[1].trim().replace(/:$/, ""), description: exMatch[2].trim() };
            continue;
        }

        // Stats line: "- Sets: 3 | Reps: 10 | Hold: 20s | Frequency: 3x/day"
        if (/sets:/i.test(trimmed) && current) {
            current.sets = trimmed.match(/Sets:\s*([^|]+)/i)?.[1]?.trim();
            current.reps = trimmed.match(/Reps:\s*([^|]+)/i)?.[1]?.trim();
            current.hold = trimmed.match(/Hold:\s*([^|]+)/i)?.[1]?.trim();
            current.frequency = trimmed.match(/Frequency:\s*(.+)/i)?.[1]?.trim();
            continue;
        }

        // Bullet instruction
        const bulletMatch = trimmed.match(/^[*\-]\s+(.+)/);
        if (bulletMatch) {
            if (current?.name) {
                current.description = (current.description ? current.description + " " : "") + bulletMatch[1].replace(/\*\*/g, "");
            } else {
                instructions.push(bulletMatch[1].replace(/\*\*/g, "").trim());
            }
            continue;
        }

        // Plain text
        if (!trimmed.startsWith("#") && !trimmed.startsWith("Goal:")) {
            instructions.push(trimmed.replace(/\*\*/g, "").trim());
        }
    }

    if (current?.name) exercises.push(current as Exercise);
    return { exercises, instructions: instructions.filter(i => i.length > 3) };
}

/* ─── Main Component ──────────────────────────────────────────── */

export default function RehabPlanView() {
    const t = useTranslations("rehabPlan");
    const { user } = useAuth();

    const [analysis, setAnalysis] = useState<AnalysisData | null>(null);
    const [assessmentId, setAssessmentId] = useState<string | null>(null);
    const [completedDays, setCompletedDays] = useState<Set<number>>(new Set());
    const [profile, setProfile] = useState<ProfileStats>({ total_points: 0, current_streak: 0, longest_streak: 0 });
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [successMessage, setSuccessMessage] = useState<string | null>(null);

    // Get auth token helper
    const getToken = async () => {
        const { data } = await supabase.auth.getSession();
        return data.session?.access_token;
    };

    // Load analysis + completed days + profile
    useEffect(() => {
        if (!user) return;

        async function load() {
            try {
                // Latest assessment
                const { data: assessment } = await supabase
                    .from("injury_assessments")
                    .select("id")
                    .eq("user_id", user!.id)
                    .order("created_at", { ascending: false })
                    .limit(1)
                    .single();

                if (!assessment) { setError("noAssessment"); setLoading(false); return; }
                setAssessmentId(assessment.id);

                const token = await getToken();
                if (!token) throw new Error("No token");

                const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

                // Fetch analysis + completed days + profile in parallel
                const [analysisRes, completedRes, profileRes] = await Promise.all([
                    fetch(`${API_URL}/ai/analysis/${assessment.id}`, {
                        headers: { Authorization: `Bearer ${token}` },
                    }),
                    fetch(`${API_URL}/progress/completed-days/${assessment.id}`, {
                        headers: { Authorization: `Bearer ${token}` },
                    }),
                    supabase
                        .from("profiles")
                        .select("total_points, current_streak, longest_streak")
                        .eq("id", user!.id)
                        .single(),
                ]);

                if (!analysisRes.ok) {
                    setError(analysisRes.status === 404 ? "noAnalysis" : "fetchFailed");
                    setLoading(false);
                    return;
                }

                const analysisData: AnalysisData = await analysisRes.json();
                setAnalysis(analysisData);

                if (completedRes.ok) {
                    const { completed_days } = await completedRes.json();
                    setCompletedDays(new Set(completed_days as number[]));
                }

                if (profileRes.data) {
                    setProfile(profileRes.data as ProfileStats);
                }
            } catch (err) {
                console.error(err);
                setError("fetchFailed");
            } finally {
                setLoading(false);
            }
        }

        load();
    }, [user]);

    const handleCompleteDay = useCallback(async (dayNumber: number) => {
        if (!assessmentId) return;
        const token = await getToken();
        if (!token) return;

        const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
        try {
            const res = await fetch(`${API_URL}/progress/complete-day`, {
                method: "POST",
                headers: {
                    Authorization: `Bearer ${token}`,
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    injury_assessment_id: assessmentId,
                    day_number: dayNumber,
                }),
            });

            if (!res.ok) return;
            const data = await res.json();

            setCompletedDays((prev) => new Set([...prev, dayNumber]));
            setProfile({
                total_points: data.total_points,
                current_streak: data.current_streak,
                longest_streak: data.longest_streak,
            });

            if (!data.already_completed) {
                setSuccessMessage(`🎉 Day ${dayNumber} complete! +${data.points_earned} pts · ${data.current_streak} day streak 🔥`);
                setTimeout(() => setSuccessMessage(null), 4000);
            }
        } catch (err) {
            console.error("Complete day failed:", err);
        }
    }, [assessmentId]);

    /* ── Loading ── */
    if (loading) {
        return (
            <div className="flex min-h-[60vh] items-center justify-center">
                <div className="text-center space-y-3">
                    <div className="mx-auto h-12 w-12 animate-spin rounded-full border-4 border-slate-100 border-t-purple-600" />
                    <p className="text-sm text-slate-400">Loading your rehab plan…</p>
                </div>
            </div>
        );
    }

    /* ── Error ── */
    if (error || !analysis) {
        return (
            <div className="flex min-h-[60vh] items-center justify-center">
                <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }}
                    className="max-w-md text-center space-y-4">
                    <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-slate-100">
                        <Brain className="h-8 w-8 text-slate-400" />
                    </div>
                    <h2 className="text-xl font-bold text-slate-900">
                        {error === "noAssessment" ? t("noAssessmentTitle") :
                            error === "noAnalysis" ? t("noAnalysisTitle") : t("errorTitle")}
                    </h2>
                    <p className="text-sm text-slate-500">
                        {error === "noAssessment" ? t("noAssessmentDescription") :
                            error === "noAnalysis" ? t("noAnalysisDescription") : t("errorDescription")}
                    </p>
                    <Link href={error === "noAnalysis" ? "/dashboard" : "/assessment"}
                        className="mt-4 inline-flex items-center gap-2 rounded-xl bg-purple-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-purple-700 transition-colors">
                        {error === "noAnalysis" ? t("goToDashboard") : t("startAssessment")}
                    </Link>
                </motion.div>
            </div>
        );
    }

    const { days, clinicalReasoning, visualAssessment, precautions } = parseToDaySchedule(analysis.reasoning || "");
    const confidencePercent = Math.round((analysis.confidence_score || 0) * 100);
    const completedCount = days.filter(d => completedDays.has(d.dayNumber)).length;
    const progressPct = days.length > 0 ? Math.round((completedCount / days.length) * 100) : 0;

    // Today is the first incomplete day
    const firstIncompleteDay = days.find(d => !completedDays.has(d.dayNumber))?.dayNumber;

    return (
        <div className="space-y-5">
            {/* ── Success Toast ── */}
            <AnimatePresence>
                {successMessage && (
                    <motion.div
                        initial={{ opacity: 0, y: -20, scale: 0.95 }}
                        animate={{ opacity: 1, y: 0, scale: 1 }}
                        exit={{ opacity: 0, y: -20, scale: 0.95 }}
                        className="fixed top-4 left-1/2 z-50 -translate-x-1/2 rounded-2xl bg-slate-900 px-6 py-3 text-sm font-semibold text-white shadow-xl"
                    >
                        {successMessage}
                    </motion.div>
                )}
            </AnimatePresence>

            {/* ── Hero ── */}
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
                className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-purple-600 via-purple-700 to-indigo-800 p-7 text-white shadow-xl shadow-purple-300/30">
                <div className="pointer-events-none absolute -right-10 -top-10 h-44 w-44 rounded-full bg-white/5" />
                <div className="pointer-events-none absolute -bottom-6 -left-6 h-28 w-28 rounded-full bg-white/5" />

                <div className="relative z-10">
                    <div className="flex items-center gap-2 mb-3">
                        <Sparks className="h-4 w-4 text-purple-200" />
                        <span className="text-xs font-semibold uppercase tracking-wider text-purple-200">AI Analysis · MedGemma 4B</span>
                    </div>
                    <h1 className="text-2xl font-bold sm:text-3xl">{analysis.probable_condition || t("conditionFallback")}</h1>

                    <div className="mt-3 flex flex-wrap gap-2.5">
                        <div className="flex items-center gap-1.5 rounded-full bg-white/15 px-3.5 py-1.5 backdrop-blur-sm">
                            <CheckCircle className="h-3.5 w-3.5" />
                            <span className="text-xs font-semibold">{confidencePercent}% confidence</span>
                        </div>
                        {analysis.created_at && (
                            <div className="flex items-center gap-1.5 text-xs text-purple-200">
                                <Clock className="h-3.5 w-3.5" />
                                <span>{new Date(analysis.created_at).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })}</span>
                            </div>
                        )}
                    </div>

                    {/* Confidence bar */}
                    <div className="mt-4 h-1.5 w-full overflow-hidden rounded-full bg-white/20">
                        <motion.div initial={{ width: 0 }} animate={{ width: `${confidencePercent}%` }}
                            transition={{ duration: 1.2, ease: "easeOut", delay: 0.3 }}
                            className="h-full rounded-full bg-gradient-to-r from-emerald-400 to-emerald-300" />
                    </div>
                </div>
            </motion.div>

            {/* ── Stats Bar (Streak + Points + Progress) ── */}
            <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
                className="grid grid-cols-3 gap-3">
                <div className="flex flex-col items-center gap-1 rounded-2xl bg-white border border-slate-100 p-4 shadow-sm">
                    <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-orange-100">
                        <FireFlame className="h-5 w-5 text-orange-500" />
                    </div>
                    <span className="text-xl font-bold text-slate-900">{profile.current_streak}</span>
                    <span className="text-[10px] font-semibold uppercase tracking-wide text-slate-400">Day Streak</span>
                </div>
                <div className="flex flex-col items-center gap-1 rounded-2xl bg-white border border-slate-100 p-4 shadow-sm">
                    <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-yellow-100">
                        <Medal className="h-5 w-5 text-yellow-500" />
                    </div>
                    <span className="text-xl font-bold text-slate-900">{profile.total_points}</span>
                    <span className="text-[10px] font-semibold uppercase tracking-wide text-slate-400">Points</span>
                </div>
                <div className="flex flex-col items-center gap-1 rounded-2xl bg-white border border-slate-100 p-4 shadow-sm">
                    <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-purple-100">
                        <Trophy className="h-5 w-5 text-purple-500" />
                    </div>
                    <span className="text-xl font-bold text-slate-900">{progressPct}%</span>
                    <span className="text-[10px] font-semibold uppercase tracking-wide text-slate-400">Complete</span>
                </div>
            </motion.div>

            {/* ── Overall Progress Bar ── */}
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.15 }}
                className="rounded-2xl border border-slate-100 bg-white p-4 shadow-sm">
                <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-semibold text-slate-700">Overall Progress</span>
                    <span className="text-xs text-slate-400">{completedCount} of {days.length} days</span>
                </div>
                <div className="h-2.5 w-full overflow-hidden rounded-full bg-slate-100">
                    <motion.div initial={{ width: 0 }} animate={{ width: `${progressPct}%` }}
                        transition={{ duration: 1, ease: "easeOut", delay: 0.3 }}
                        className="h-full rounded-full bg-gradient-to-r from-purple-500 to-indigo-500" />
                </div>
            </motion.div>

            {/* ── Clinical Reasoning (collapsible) ── */}
            {clinicalReasoning && (
                <motion.details initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.2 }}
                    className="group rounded-2xl border border-slate-100 bg-white shadow-sm overflow-hidden">
                    <summary className="flex cursor-pointer items-center gap-2.5 p-4 select-none">
                        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-purple-100">
                            <Brain className="h-4 w-4 text-purple-600" />
                        </div>
                        <span className="text-sm font-semibold text-slate-800">{t("clinicalReasoning")}</span>
                        <span className="ml-auto text-xs text-slate-400 group-open:hidden">View</span>
                        <span className="ml-auto text-xs text-slate-400 hidden group-open:inline">Hide</span>
                    </summary>
                    <div className="px-4 pb-4">
                        <p className="text-sm leading-relaxed text-slate-500 whitespace-pre-line">{clinicalReasoning}</p>
                    </div>
                </motion.details>
            )}

            {/* ── Day-by-Day Cards ── */}
            {days.length > 0 && (
                <div>
                    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.25 }}
                        className="mb-4 flex items-baseline justify-between">
                        <h2 className="text-lg font-bold text-slate-900">Your Daily Plan</h2>
                        <span className="text-xs text-slate-400">{days.length} days total</span>
                    </motion.div>

                    <div className="space-y-3">
                        {days.map((day) => (
                            <DayCard
                                key={day.dayNumber}
                                dayNumber={day.dayNumber}
                                phase={day.phase}
                                phaseColor={day.phaseColor}
                                exercises={day.exercises}
                                instructions={day.instructions}
                                isCompleted={completedDays.has(day.dayNumber)}
                                isToday={day.dayNumber === firstIncompleteDay}
                                condition={analysis.probable_condition || ""}
                                painLocation={""}
                                onComplete={handleCompleteDay}
                            />
                        ))}
                    </div>
                </div>
            )}

            {/* ── Precautions ── */}
            {precautions.length > 0 && (
                <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.35 }}
                    className="rounded-2xl border border-orange-100 bg-orange-50 p-5">
                    <div className="flex items-center gap-2 mb-3">
                        <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-orange-100">
                            <WarningTriangle className="h-4 w-4 text-orange-500" />
                        </div>
                        <h3 className="text-sm font-bold text-orange-900">Precautions & Warning Signs</h3>
                    </div>
                    <ul className="space-y-1.5">
                        {precautions.map((p, i) => (
                            <li key={i} className="flex items-start gap-2 text-xs text-orange-800 leading-relaxed">
                                <span className="mt-1 h-1.5 w-1.5 flex-shrink-0 rounded-full bg-orange-400" />
                                {p}
                            </li>
                        ))}
                    </ul>
                </motion.div>
            )}

            {/* ── Disclaimer ── */}
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.4 }}
                className="rounded-xl bg-slate-50 border border-slate-200 p-4 text-center">
                <p className="text-xs text-slate-400">⚠️ {t("disclaimer")}</p>
            </motion.div>
        </div>
    );
}
