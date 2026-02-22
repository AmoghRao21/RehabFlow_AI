"use client";

import { motion } from "framer-motion";
import { Ruler, Weight, User, Heart } from "iconoir-react";
import { useTranslations } from "next-intl";

interface HealthMetricsCardProps {
    baseline: any;
    loading?: boolean;
}

export default function HealthMetricsCard({ baseline, loading }: HealthMetricsCardProps) {
    const t = useTranslations("dashboard");

    if (loading) {
        return <div className="h-64 w-full animate-pulse rounded-2xl bg-slate-200"></div>;
    }

    if (!baseline) {
        return (
            <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                className="flex h-full flex-col items-center justify-center rounded-2xl bg-white p-8 text-center shadow-sm ring-1 ring-slate-100"
            >
                <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-slate-100 text-slate-400">
                    <User className="h-8 w-8" />
                </div>
                <h3 className="text-lg font-semibold text-slate-900">{t('completeProfileTitle')}</h3>
                <p className="mt-1 text-sm text-slate-500">
                    {t('completeProfileDescription')}
                </p>
                <button className="mt-6 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-blue-700">
                    {t('updateProfileButton')}
                </button>
            </motion.div>
        );
    }

    const bmi =
        baseline.height_cm && baseline.weight_kg
            ? (baseline.weight_kg / ((baseline.height_cm / 100) ** 2)).toFixed(1)
            : "--";

    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-100"
        >
            <div className="mb-6 flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-50 text-emerald-600">
                    <Heart className="h-6 w-6" />
                </div>
                <h2 className="text-lg font-bold text-slate-900">{t('healthMetricsTitle')}</h2>
            </div>

            <div className="grid grid-cols-2 gap-4">
                <div className="rounded-xl bg-slate-50 p-4">
                    <div className="mb-2 flex items-center gap-2 text-sm font-medium text-slate-500">
                        <Ruler className="h-4 w-4" /> {t('heightLabel')}
                    </div>
                    <p className="text-2xl font-bold text-slate-900">{baseline.height_cm} cm</p>
                </div>

                <div className="rounded-xl bg-slate-50 p-4">
                    <div className="mb-2 flex items-center gap-2 text-sm font-medium text-slate-500">
                        <Weight className="h-4 w-4" /> {t('weightLabel')}
                    </div>
                    <p className="text-2xl font-bold text-slate-900">{baseline.weight_kg} kg</p>
                </div>

                <div className="rounded-xl bg-slate-50 p-4">
                    <div className="mb-2 flex items-center gap-2 text-sm font-medium text-slate-500">
                        <User className="h-4 w-4" /> {t('ageLabel')}
                    </div>
                    <p className="text-2xl font-bold text-slate-900">{baseline.age} yrs</p>
                </div>

                <div className="rounded-xl bg-slate-50 p-4">
                    <div className="mb-2 flex items-center gap-2 text-sm font-medium text-slate-500">
                        {t('bmiLabel')}
                    </div>
                    <p className="text-2xl font-bold text-slate-900">{bmi}</p>
                </div>
            </div>
        </motion.div>
    );
}
