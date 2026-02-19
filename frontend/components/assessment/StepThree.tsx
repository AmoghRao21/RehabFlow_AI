"use client";

import { motion } from "framer-motion";
import { User, Ruler, Calendar, HelpCircle } from "iconoir-react";

interface StepThreeProps {
    data: any;
    updateData: (updates: any) => void;
}

const BODY_PARTS = [
    "Shoulder",
    "Elbow",
    "Wrist",
    "Neck",
    "Upper_Back",
    "Lower_Back",
    "Hip",
    "Knee",
    "Ankle",
    "Foot",
    "Other",
];

export default function StepThree({ data, updateData }: StepThreeProps) {
    const painLevelColor = (level: number) => {
        if (level <= 3) return "text-emerald-600";
        if (level <= 6) return "text-orange-500";
        return "text-red-600";
    };

    return (
        <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="space-y-8"
        >
            {/* Pain Location */}
            <div className="space-y-4">
                <label className="text-sm font-medium text-slate-700">
                    Where is the pain located?
                </label>
                <div className="flex flex-wrap gap-2">
                    {BODY_PARTS.map((part) => (
                        <button
                            key={part}
                            onClick={() => updateData({ pain_location: part.toLowerCase() })}
                            className={`rounded-full px-4 py-2 text-sm font-medium transition-all ${data.pain_location === part.toLowerCase()
                                ? "bg-blue-600 text-white shadow-md shadow-blue-600/20"
                                : "bg-white text-slate-600 ring-1 ring-slate-200 hover:bg-slate-50"
                                }`}
                        >
                            {part.replace("_", " ")}
                        </button>
                    ))}
                </div>
            </div>

            {/* Pain Level */}
            <div className="space-y-6 rounded-xl bg-slate-50 p-6">
                <div className="flex items-center justify-between">
                    <label className="text-sm font-medium text-slate-700">
                        Pain Intensity
                    </label>
                    <span
                        className={`text-2xl font-bold ${painLevelColor(data.pain_level)}`}
                    >
                        {data.pain_level} <span className="text-base text-slate-400">/ 10</span>
                    </span>
                </div>
                <input
                    type="range"
                    min="0"
                    max="10"
                    step="1"
                    value={data.pain_level}
                    onChange={(e) => updateData({ pain_level: parseInt(e.target.value) })}
                    className="h-2 w-full cursor-pointer appearance-none rounded-lg bg-slate-200 accent-blue-600"
                />
                <div className="flex justify-between text-xs text-slate-400 mt-1">
                    <span>No Pain</span>
                    <span>Unbearable</span>
                </div>
            </div>

            {/* Date & Cause */}
            <div className="grid gap-6 md:grid-cols-2">
                {/* Date Started */}
                <div className="space-y-2">
                    <label className="text-sm font-medium text-slate-700">Date Started</label>
                    <div className="relative">
                        <Calendar className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-400" />
                        <input
                            type="date"
                            value={data.injury_date || ""}
                            onChange={(e) => updateData({ injury_date: e.target.value })}
                            className="w-full rounded-lg border border-slate-200 py-2.5 pl-10 pr-4 text-slate-900 outline-none focus:border-blue-600 focus:ring-1 focus:ring-blue-600"
                        />
                    </div>
                </div>
                {/* Cause */}
                <div className="md:col-span-2 space-y-2">
                    <label className="text-sm font-medium text-slate-700">How did it happen?</label>
                    <div className="relative">
                        <HelpCircle className="absolute left-3 top-3 h-5 w-5 text-slate-400" />
                        <textarea
                            rows={2}
                            value={data.pain_cause}
                            onChange={(e) => updateData({ pain_cause: e.target.value })}
                            className="w-full rounded-lg border border-slate-200 py-2.5 pl-10 pr-4 text-slate-900 outline-none focus:border-blue-600 focus:ring-1 focus:ring-blue-600"
                            placeholder="Brief description..."
                        />
                    </div>
                </div>
            </div>

            {/* Toggles */}
            <div className="md:grid md:grid-cols-2 md:gap-4 space-y-4 md:space-y-0">
                <div className="flex items-center justify-between rounded-xl border border-slate-200 p-4">
                    <div>
                        <span className="block text-sm font-medium text-slate-900">
                            Visible Swelling
                        </span>
                    </div>
                    <label className="relative inline-flex cursor-pointer items-center">
                        <input
                            type="checkbox"
                            className="peer sr-only"
                            checked={data.is_swollen}
                            onChange={(e) => updateData({ is_swollen: e.target.checked })}
                        />
                        <div className="h-6 w-11 rounded-full bg-slate-200 after:absolute after:left-[2px] after:top-[2px] after:h-5 after:w-5 after:rounded-full after:border after:border-slate-300 after:bg-white after:transition-all after:content-[''] peer-checked:bg-blue-600 peer-checked:after:translate-x-full peer-checked:after:border-white peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-blue-300"></div>
                    </label>
                </div>

                <div className="flex items-center justify-between rounded-xl border border-slate-200 p-4">
                    <div>
                        <span className="block text-sm font-medium text-slate-900">
                            Mobility Issue
                        </span>
                    </div>
                    <label className="relative inline-flex cursor-pointer items-center">
                        <input
                            type="checkbox"
                            className="peer sr-only"
                            checked={data.mobility_restricted}
                            onChange={(e) => updateData({ mobility_restricted: e.target.checked })}
                        />
                        <div className="h-6 w-11 rounded-full bg-slate-200 after:absolute after:left-[2px] after:top-[2px] after:h-5 after:w-5 after:rounded-full after:border after:border-slate-300 after:bg-white after:transition-all after:content-[''] peer-checked:bg-blue-600 peer-checked:after:translate-x-full peer-checked:after:border-white peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-blue-300"></div>
                    </label>
                </div>
            </div>
        </motion.div>
    );
}
