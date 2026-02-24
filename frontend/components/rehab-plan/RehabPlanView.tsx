"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Brain, ArrowLeft, Sparks, Clock, CheckCircle } from "iconoir-react";
import Link from "next/link";
import { useTranslations } from "next-intl";

import { useAuth } from "@/lib/auth-provider";
import { supabase } from "@/lib/supabase";
import PhaseCard from "./PhaseCard";

interface ParsedPhase {
    phaseNumber: number;
    title: string;
    timeframe: string;
    goal: string;
    content: string[];
}

interface AnalysisData {
    id: string;
    probable_condition: string;
    confidence_score: number;
    reasoning: string;
    model_version: string;
    created_at: string;
}

/**
 * Parses the raw reasoning text to extract clinical reasoning
 * and structured rehab plan phases.
 */
function parseReasoningText(reasoning: string): {
    clinicalReasoning: string;
    phases: ParsedPhase[];
} {
    if (!reasoning) return { clinicalReasoning: "", phases: [] };

    // Split on "## Rehabilitation Plan" or "**Rehabilitation Plan:**"
    const rehabSplitRegex = /(?:##\s*Rehabilitation Plan|[\*]*Rehabilitation Plan[\*]*:?)/i;
    const parts = reasoning.split(rehabSplitRegex);

    let clinicalReasoning = parts[0]?.trim() || "";
    const rehabText = parts.length > 1 ? parts.slice(1).join("") : "";

    // Remove visual assessment header for cleaner display
    clinicalReasoning = clinicalReasoning
        .replace(/^##\s*Visual Assessment\n/m, "")
        .replace(/^##\s*Clinical Reasoning:?\n?/m, "")
        .replace(/^\*\*Clinical Reasoning:\*\*\s*/m, "")
        .replace(/^\*\*Probable Condition:\*\*.*\n?/m, "")
        .replace(/^\*\*Confidence:\*\*.*\n?/m, "")
        .trim();

    if (!rehabText) {
        return { clinicalReasoning, phases: [] };
    }

    // Parse phases: look for patterns like "1. **Phase 1 — Acute (Days 1-7):**"
    const phaseRegex = /\d+\.\s*\*\*Phase\s*(\d+)\s*[\u2013\u2014\-–—]\s*([^(]+)\(([^)]+)\)\s*:\*\*/gi;
    const phaseMatches = [...rehabText.matchAll(phaseRegex)];

    const phases: ParsedPhase[] = [];

    for (let i = 0; i < phaseMatches.length; i++) {
        const match = phaseMatches[i];
        const phaseNumber = parseInt(match[1], 10);
        const title = match[2].trim();
        const timeframe = match[3].trim();

        // Get text between this phase header and the next
        const startIdx = match.index! + match[0].length;
        const endIdx = i < phaseMatches.length - 1 ? phaseMatches[i + 1].index! : rehabText.length;
        const phaseBody = rehabText.slice(startIdx, endIdx).trim();

        // Extract goal
        let goal = "";
        const goalMatch = phaseBody.match(/\*\*Goal:\*\*\s*(.+)/i);
        if (goalMatch) {
            goal = goalMatch[1].trim();
        }

        // Extract bullet items
        const items: string[] = [];
        const bulletRegex = /\*\s+\*\*([^*]+)\*\*:?\s*([\s\S]*?)(?=\n\s*\*\s+\*\*|\n\s*\d+\.\s|\s*$)/g;
        const bulletMatches = [...phaseBody.matchAll(bulletRegex)];

        for (const bm of bulletMatches) {
            const label = bm[1].trim();
            if (label.toLowerCase() === "goal") continue;
            let detail = bm[2].trim().replace(/\n\s*/g, " ");
            items.push(`**${label}**: ${detail}`);
        }

        // Fallback: if no structured bullets found, split by lines
        if (items.length === 0) {
            const lines = phaseBody
                .split("\n")
                .map(l => l.replace(/^\s*[\*\-]\s*/, "").trim())
                .filter(l => l.length > 10);
            items.push(...lines);
        }

        phases.push({
            phaseNumber,
            title,
            timeframe,
            goal,
            content: items,
        });
    }

    // Fallback: if regex didn't match structured phases, try simple numbered list
    if (phases.length === 0) {
        const simplePhaseRegex = /(\d+)\.\s+\*\*([^*]+)\*\*[:\s]*([\s\S]*?)(?=\n\d+\.\s+\*\*|\s*$)/g;
        const simpleMatches = [...rehabText.matchAll(simplePhaseRegex)];

        for (const sm of simpleMatches) {
            const body = sm[3].trim();
            const lines = body
                .split("\n")
                .map(l => l.replace(/^\s*[\*\-]\s*/, "").trim())
                .filter(l => l.length > 5);

            phases.push({
                phaseNumber: parseInt(sm[1], 10),
                title: sm[2].trim(),
                timeframe: "",
                goal: "",
                content: lines,
            });
        }
    }

    return { clinicalReasoning, phases };
}

/**
 * Renders markdown-like bold text (**text**) as <strong> elements.
 */
function renderBoldText(text: string) {
    const parts = text.split(/\*\*([^*]+)\*\*/g);
    return parts.map((part, i) =>
        i % 2 === 1 ? (
            <strong key={i} className="font-semibold text-slate-900">
                {part}
            </strong>
        ) : (
            <span key={i}>{part}</span>
        )
    );
}

export default function RehabPlanView() {
    const t = useTranslations("rehabPlan");
    const { user } = useAuth();
    const [analysis, setAnalysis] = useState<AnalysisData | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        async function fetchAnalysis() {
            if (!user) return;

            try {
                // First fetch the latest assessment
                const { data: assessmentData } = await supabase
                    .from("injury_assessments")
                    .select("*")
                    .eq("user_id", user.id)
                    .order("created_at", { ascending: false })
                    .limit(1)
                    .single();

                if (!assessmentData) {
                    setError("noAssessment");
                    setLoading(false);
                    return;
                }

                // Fetch AI analysis via the backend API
                const { data: sessionData } = await supabase.auth.getSession();
                const token = sessionData.session?.access_token;

                if (!token) throw new Error("No access token");

                const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
                const res = await fetch(`${API_URL}/ai/analysis/${assessmentData.id}`, {
                    headers: { Authorization: `Bearer ${token}` },
                });

                if (!res.ok) {
                    if (res.status === 404) {
                        setError("noAnalysis");
                    } else {
                        setError("fetchFailed");
                    }
                    setLoading(false);
                    return;
                }

                const result: AnalysisData = await res.json();
                setAnalysis(result);
            } catch (err) {
                console.error("Failed to fetch analysis:", err);
                setError("fetchFailed");
            } finally {
                setLoading(false);
            }
        }

        fetchAnalysis();
    }, [user]);

    // Loading state
    if (loading) {
        return (
            <div className="flex min-h-[60vh] items-center justify-center">
                <div className="text-center space-y-4">
                    <div className="mx-auto h-12 w-12 animate-spin rounded-full border-4 border-slate-200 border-t-purple-600" />
                    <p className="text-sm font-medium text-slate-500">{t("loading")}</p>
                </div>
            </div>
        );
    }

    // Error states
    if (error || !analysis) {
        return (
            <div className="flex min-h-[60vh] items-center justify-center">
                <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="max-w-md text-center space-y-4"
                >
                    <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-slate-100">
                        <Brain className="h-8 w-8 text-slate-400" />
                    </div>
                    <h2 className="text-xl font-bold text-slate-900">
                        {error === "noAssessment" ? t("noAssessmentTitle") : error === "noAnalysis" ? t("noAnalysisTitle") : t("errorTitle")}
                    </h2>
                    <p className="text-sm text-slate-500">
                        {error === "noAssessment" ? t("noAssessmentDescription") : error === "noAnalysis" ? t("noAnalysisDescription") : t("errorDescription")}
                    </p>
                    <Link
                        href={error === "noAnalysis" ? "/dashboard" : "/assessment"}
                        className="mt-4 inline-flex items-center gap-2 rounded-lg bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-blue-700"
                    >
                        {error === "noAnalysis" ? t("goToDashboard") : t("startAssessment")}
                    </Link>
                </motion.div>
            </div>
        );
    }

    const { clinicalReasoning, phases } = parseReasoningText(analysis.reasoning || "");
    const confidencePercent = Math.round((analysis.confidence_score || 0) * 100);

    return (
        <div className="space-y-8">
            {/* Hero card */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-purple-600 via-purple-700 to-indigo-800 p-8 text-white shadow-xl shadow-purple-300/30"
            >
                {/* Background decorative elements */}
                <div className="pointer-events-none absolute -right-12 -top-12 h-48 w-48 rounded-full bg-white/5" />
                <div className="pointer-events-none absolute -bottom-8 -left-8 h-32 w-32 rounded-full bg-white/5" />

                <div className="relative z-10">
                    <div className="flex items-center gap-2 mb-4">
                        <Sparks className="h-5 w-5 text-purple-200" />
                        <span className="text-xs font-semibold uppercase tracking-wider text-purple-200">
                            {t("aiPoweredAnalysis")}
                        </span>
                    </div>

                    <h1 className="text-2xl font-bold sm:text-3xl">
                        {analysis.probable_condition || t("conditionFallback")}
                    </h1>

                    <div className="mt-4 flex flex-wrap items-center gap-4">
                        {/* Confidence */}
                        <div className="flex items-center gap-2 rounded-full bg-white/15 px-4 py-2 backdrop-blur-sm">
                            <CheckCircle className="h-4 w-4" />
                            <span className="text-sm font-semibold">{confidencePercent}% {t("confidence")}</span>
                        </div>

                        {/* Model version */}
                        <div className="flex items-center gap-2 rounded-full bg-white/10 px-3 py-1.5 text-xs text-purple-100">
                            <Brain className="h-3.5 w-3.5" />
                            <span>MedGemma 4B</span>
                        </div>

                        {/* Created date */}
                        {analysis.created_at && (
                            <div className="flex items-center gap-1.5 text-xs text-purple-200">
                                <Clock className="h-3.5 w-3.5" />
                                <span>
                                    {new Date(analysis.created_at).toLocaleDateString("en-US", {
                                        month: "short",
                                        day: "numeric",
                                        year: "numeric",
                                    })}
                                </span>
                            </div>
                        )}
                    </div>

                    {/* Confidence bar */}
                    <div className="mt-5">
                        <div className="h-2 w-full overflow-hidden rounded-full bg-white/20">
                            <motion.div
                                initial={{ width: 0 }}
                                animate={{ width: `${confidencePercent}%` }}
                                transition={{ duration: 1.2, ease: "easeOut", delay: 0.3 }}
                                className="h-full rounded-full bg-gradient-to-r from-emerald-400 to-emerald-300"
                            />
                        </div>
                    </div>
                </div>
            </motion.div>

            {/* Clinical Reasoning */}
            {clinicalReasoning && (
                <motion.div
                    initial={{ opacity: 0, y: 15 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.15 }}
                    className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm"
                >
                    <div className="flex items-center gap-2 mb-4">
                        <Brain className="h-5 w-5 text-purple-600" />
                        <h2 className="text-lg font-bold text-slate-900">{t("clinicalReasoning")}</h2>
                    </div>
                    <p className="text-sm leading-relaxed text-slate-600 whitespace-pre-line">
                        {clinicalReasoning}
                    </p>
                </motion.div>
            )}

            {/* Rehabilitation Plan — Phase Cards */}
            {phases.length > 0 && (
                <div>
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 0.3 }}
                        className="mb-5 flex items-center justify-between"
                    >
                        <h2 className="text-xl font-bold text-slate-900">{t("rehabilitationPlan")}</h2>
                        <span className="rounded-full bg-purple-100 px-3 py-1 text-xs font-bold text-purple-700">
                            {phases.length} {phases.length === 1 ? t("phase") : t("phases")}
                        </span>
                    </motion.div>

                    {/* Phase timeline */}
                    <div className="relative space-y-4">
                        {/* Vertical line connector */}
                        <div className="absolute left-[1.85rem] top-8 bottom-8 w-0.5 bg-gradient-to-b from-red-200 via-amber-200 to-emerald-200 hidden sm:block" />

                        {phases.map((phase) => (
                            <PhaseCard
                                key={phase.phaseNumber}
                                phaseNumber={phase.phaseNumber}
                                title={phase.title}
                                timeframe={phase.timeframe}
                                goal={phase.goal}
                                content={phase.content.map((item) =>
                                    // Strip markdown bold for display since PhaseCard uses renderBoldText
                                    item
                                )}
                                totalPhases={phases.length}
                            />
                        ))}
                    </div>
                </div>
            )}

            {/* Fallback: No structured phases, show raw rehab text */}
            {phases.length === 0 && analysis.reasoning && (
                <motion.div
                    initial={{ opacity: 0, y: 15 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.3 }}
                    className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm"
                >
                    <h2 className="mb-4 text-lg font-bold text-slate-900">{t("rehabilitationPlan")}</h2>
                    <div className="prose prose-sm max-w-none text-slate-600 whitespace-pre-line">
                        {analysis.reasoning}
                    </div>
                </motion.div>
            )}

            {/* Disclaimer */}
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.5 }}
                className="rounded-xl bg-amber-50 border border-amber-200 p-4 text-center"
            >
                <p className="text-xs text-amber-700">
                    ⚠️ {t("disclaimer")}
                </p>
            </motion.div>
        </div>
    );
}

export { renderBoldText, parseReasoningText };
