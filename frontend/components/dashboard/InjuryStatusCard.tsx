"use client";

import { motion } from "framer-motion";
import { ReportColumns, CheckCircle, ArrowRight, Sparks, Brain } from "iconoir-react";
import Link from "next/link";
import { useState } from "react";

interface InjuryStatusCardProps {
    assessment: any;
    loading?: boolean;
    onRunAnalysis?: () => Promise<void>;
}

export default function InjuryStatusCard({ assessment, loading, onRunAnalysis }: InjuryStatusCardProps) {
    const [analyzing, setAnalyzing] = useState(false);

    if (loading) {
        return <div className="h-64 w-full animate-pulse rounded-2xl bg-slate-200"></div>;
    }

    if (!assessment) {
        return (
            <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="flex h-full flex-col items-center justify-center rounded-2xl bg-white p-8 text-center shadow-sm ring-1 ring-slate-100"
            >
                <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-blue-50 text-blue-600">
                    <ReportColumns className="h-8 w-8" />
                </div>
                <h3 className="text-lg font-semibold text-slate-900">No Active Assessment</h3>
                <p className="mt-1 text-sm text-slate-500">
                    Assess your injury to generate a personalized rehab plan.
                </p>
                <Link
                    href="/assessment"
                    className="mt-6 flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-blue-700"
                >
                    Start Assessment <ArrowRight className="h-4 w-4" />
                </Link>
            </motion.div>
        );
    }

    const painLevelColor =
        assessment.pain_level <= 3
            ? "text-emerald-600 bg-emerald-50"
            : assessment.pain_level <= 6
                ? "text-orange-600 bg-orange-50"
                : "text-red-600 bg-red-50";

    const aiResult = assessment.ai_clinical_analysis?.[0];

    const handleAnalyzeClick = async () => {
        if (!onRunAnalysis) return;
        setAnalyzing(true);
        await onRunAnalysis();
        setAnalyzing(false);
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="relative overflow-hidden rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-100"
        >
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-50 text-blue-600">
                        <ReportColumns className="h-6 w-6" />
                    </div>
                    <div>
                        <h2 className="text-lg font-bold text-slate-900">Current Injury</h2>
                        <p className="text-sm text-slate-500 capitalize">{assessment.pain_cause || "Assessment"}</p>
                    </div>
                </div>
                {aiResult ? (
                    <div className="flex items-center gap-1 rounded-full bg-purple-100 px-2 py-1 text-xs font-bold text-purple-700">
                        <Sparks className="h-3.5 w-3.5" /> AI Analyzed
                    </div>
                ) : (
                    <div className="flex h-8 w-8 items-center justify-center rounded-full bg-emerald-100 text-emerald-600">
                        <CheckCircle className="h-5 w-5" />
                    </div>
                )}
            </div>

            <div className="mt-6 grid grid-cols-2 gap-4">
                <div className="rounded-xl border border-slate-100 p-4">
                    <p className="text-xs font-medium uppercase text-slate-500">Location</p>
                    <p className="mt-1 text-lg font-semibold text-slate-900 capitalize">
                        {assessment.pain_location.replace("_", " ")}
                    </p>
                </div>
                <div className={`rounded-xl border border-slate-100 p-4`}>
                    <p className="text-xs font-medium uppercase text-slate-500">Pain Level</p>
                    <div className="mt-1 flex items-center gap-2">
                        <span className={`rounded-full px-2 py-0.5 text-xs font-bold ${painLevelColor}`}>
                            {assessment.pain_level}/10
                        </span>
                    </div>
                </div>
            </div>

            {/* AI Analysis Section */}
            <div className="mt-6 border-t border-slate-100 pt-6">
                {aiResult ? (
                    <div className="space-y-4">
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2 text-purple-700">
                                <Brain className="h-5 w-5" />
                                <h3 className="font-semibold">Clinical Analysis</h3>
                            </div>
                            <button
                                onClick={handleAnalyzeClick}
                                disabled={analyzing}
                                className="text-xs font-medium text-slate-400 hover:text-purple-600 disabled:opacity-50"
                            >
                                {analyzing ? "Updating..." : "Re-analyze"}
                            </button>
                        </div>

                        <div className="rounded-xl bg-purple-50 p-5 ring-1 ring-purple-100">
                            <h4 className="text-lg font-bold text-purple-900">
                                {aiResult.probable_condition || "Condition Identified"}
                            </h4>

                            {/* Confidence Bar */}
                            <div className="mt-3 mb-4">
                                <div className="mb-1 flex justify-between text-xs font-medium">
                                    <span className="text-purple-700/80">Confidence Score</span>
                                    <span className="text-purple-900">{Math.round((aiResult.confidence_score || 0) * 100)}%</span>
                                </div>
                                <div className="h-2 w-full overflow-hidden rounded-full bg-purple-200/50">
                                    <motion.div
                                        initial={{ width: 0 }}
                                        animate={{ width: `${(aiResult.confidence_score || 0) * 100}%` }}
                                        transition={{ duration: 1, ease: "easeOut" }}
                                        className="h-full rounded-full bg-purple-600"
                                    />
                                </div>
                            </div>

                            <p className="text-sm leading-relaxed text-slate-700">
                                {aiResult.reasoning}
                            </p>
                        </div>
                    </div>
                ) : (
                    <div className="rounded-xl bg-slate-50 p-6 text-center shadow-inner">
                        <p className="mb-4 text-sm text-slate-500">
                            Unlock personalized insights with our AI clinical model.
                        </p>
                        <button
                            onClick={handleAnalyzeClick}
                            disabled={analyzing}
                            className="inline-flex w-full items-center justify-center gap-2 rounded-xl bg-slate-900 px-4 py-3 text-sm font-semibold text-white transition-all hover:bg-slate-800 disabled:opacity-70 shadow-lg shadow-slate-200"
                        >
                            {analyzing ? (
                                <>
                                    <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                                    Analyzing Injury...
                                </>
                            ) : (
                                <>
                                    <Sparks className="h-4 w-4 text-purple-300" /> Analyze Injury
                                </>
                            )}
                        </button>
                    </div>
                )}
            </div>
        </motion.div>
    );
}
