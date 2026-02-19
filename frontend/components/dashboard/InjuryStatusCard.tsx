"use client";

import { motion } from "framer-motion";
import { ReportColumns, CheckCircle, ArrowRight } from "iconoir-react";
import Link from "next/link";

interface InjuryStatusCardProps {
    assessment: any; // Using any for simplicity in this context, ideally proper type
    loading?: boolean;
}

export default function InjuryStatusCard({ assessment, loading }: InjuryStatusCardProps) {
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
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-emerald-100 text-emerald-600">
                    <CheckCircle className="h-5 w-5" />
                </div>
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

            <div className="mt-6">
                <div className="mb-2 flex justify-between text-sm">
                    <span className="font-medium text-slate-700">Rehab Progress</span>
                    <span className="text-slate-500">12%</span>
                </div>
                <div className="h-2 w-full overflow-hidden rounded-full bg-slate-100">
                    <div className="h-full w-[12%] rounded-full bg-blue-600"></div>
                </div>
            </div>
        </motion.div>
    );
}
