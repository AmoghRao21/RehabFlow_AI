"use client";

import { motion } from "framer-motion";

interface ProgressIndicatorProps {
    currentStep: number;
}

export default function ProgressIndicator({ currentStep }: ProgressIndicatorProps) {
    const steps = [
        { num: 1, label: "Lifestyle" },
        { num: 2, label: "Medical" },
        { num: 3, label: "Injury" },
        { num: 4, label: "Photos" },
        { num: 5, label: "Review" },
    ];

    return (
        <div className="mb-8 w-full">
            <div className="flex items-center justify-between px-2 sm:px-8">
                {steps.map((step, index) => {
                    const isActive = step.num === currentStep;
                    const isCompleted = step.num < currentStep;

                    return (
                        <div key={step.num} className="relative flex flex-col items-center flex-1">
                            {/* Connector Line */}
                            {index !== 0 && (
                                <div
                                    className={`absolute right-[50%] top-4 -z-10 h-0.5 w-[calc(100%-2rem)] -translate-y-1/2 ${isCompleted ? "bg-emerald-500" : "bg-slate-200"
                                        }`}
                                />
                            )}

                            <motion.div
                                initial={false}
                                animate={{
                                    scale: isActive ? 1.1 : 1,
                                    backgroundColor: isCompleted
                                        ? "#10B981" // emerald-500
                                        : isActive
                                            ? "#2563EB" // blue-600
                                            : "#F1F5F9", // slate-100
                                    color: isCompleted || isActive ? "#ffffff" : "#64748B", // slate-500
                                }}
                                className={`flex h-8 w-8 items-center justify-center rounded-full text-sm font-bold shadow-sm ring-2 z-10 ${isActive ? "ring-blue-100" : "ring-transparent"
                                    }`}
                            >
                                {isCompleted ? "✓" : step.num}
                            </motion.div>
                            <span
                                className={`mt-2 text-xs font-medium hidden sm:block ${isActive ? "text-blue-600" : "text-slate-500"
                                    }`}
                            >
                                {step.label}
                            </span>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
