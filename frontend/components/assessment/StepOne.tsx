"use client";

import { motion } from "framer-motion";
import { PcCheck, Clock, Gym, GlassEmpty, Smoking, Flask } from "iconoir-react";
import { useTranslations } from "next-intl";

interface StepOneProps {
    data: any;
    updateData: (updates: any) => void;
}

export default function StepOne({ data, updateData }: StepOneProps) {
    const t = useTranslations("assessment");

    return (
        <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="space-y-8"
        >
            <div className="grid gap-6 md:grid-cols-2">
                {/* Occupation Type */}
                <div className="space-y-2">
                    <label className="text-sm font-medium text-slate-700">{t('occupationType')}</label>
                    <div className="relative">
                        <PcCheck className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-400" />
                        <input
                            type="text"
                            value={data.occupation_type}
                            onChange={(e) => updateData({ occupation_type: e.target.value })}
                            className="w-full rounded-lg border border-slate-200 py-2.5 pl-10 pr-4 text-slate-900 outline-none focus:border-blue-600 focus:ring-1 focus:ring-blue-600"
                            placeholder={t('occupationPlaceholder')}
                        />
                    </div>
                </div>

                {/* Daily Sitting Hours */}
                <div className="space-y-2">
                    <label className="text-sm font-medium text-slate-700">{t('dailySittingHours')}</label>
                    <div className="relative">
                        <Clock className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-400" />
                        <input
                            type="number"
                            min="0"
                            max="24"
                            value={data.daily_sitting_hours}
                            onChange={(e) => updateData({ daily_sitting_hours: parseInt(e.target.value) || 0 })}
                            className="w-full rounded-lg border border-slate-200 py-2.5 pl-10 pr-4 text-slate-900 outline-none focus:border-blue-600 focus:ring-1 focus:ring-blue-600"
                            placeholder="8"
                        />
                    </div>
                </div>

                {/* Physical Work Level */}
                <div className="space-y-2">
                    <label className="text-sm font-medium text-slate-700">{t('physicalWorkLevel')}</label>
                    <select
                        value={data.physical_work_level}
                        onChange={(e) => updateData({ physical_work_level: e.target.value })}
                        className="w-full appearance-none rounded-lg border border-slate-200 bg-white px-4 py-2.5 text-slate-900 outline-none focus:border-blue-600 focus:ring-1 focus:ring-blue-600"
                    >
                        <option value="sedentary">{t('sedentary')}</option>
                        <option value="light">{t('light')}</option>
                        <option value="moderate">{t('moderate')}</option>
                        <option value="heavy">{t('heavy')}</option>
                    </select>
                </div>

                {/* Gym Frequency */}
                <div className="space-y-2">
                    <label className="text-sm font-medium text-slate-700">{t('gymFrequency')}</label>
                    <div className="relative">
                        <Gym className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-400" />
                        <select
                            value={data.gym_frequency}
                            onChange={(e) => updateData({ gym_frequency: e.target.value })}
                            className="w-full appearance-none rounded-lg border border-slate-200 bg-white py-2.5 pl-10 pr-4 text-slate-900 outline-none focus:border-blue-600 focus:ring-1 focus:ring-blue-600"
                        >
                            <option value="never">{t('gymNever')}</option>
                            <option value="1-2_times_week">{t('gym12')}</option>
                            <option value="3-4_times_week">{t('gym34')}</option>
                            <option value="5+_times_week">{t('gym5plus')}</option>
                        </select>
                    </div>
                </div>
            </div>

            <div className="space-y-4 rounded-xl bg-slate-50 p-6">
                <h3 className="font-semibold text-slate-900">{t('lifestyleHabits')}</h3>

                {/* Alcohol */}
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <GlassEmpty className="h-5 w-5 text-slate-500" />
                        <span className="text-sm font-medium text-slate-700">{t('alcohol')}</span>
                    </div>
                    <select
                        value={data.alcohol_usage}
                        onChange={(e) => updateData({ alcohol_usage: e.target.value })}
                        className="rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-sm outline-none focus:border-blue-600"
                    >
                        <option value="never">{t('freqNever')}</option>
                        <option value="occasional">{t('freqOccasional')}</option>
                        <option value="regular">{t('freqRegular')}</option>
                        <option value="heavy">{t('freqHeavy')}</option>
                    </select>
                </div>

                {/* Smoking */}
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <Smoking className="h-5 w-5 text-slate-500" />
                        <span className="text-sm font-medium text-slate-700">{t('smoking')}</span>
                    </div>
                    <select
                        value={data.smoking_usage}
                        onChange={(e) => updateData({ smoking_usage: e.target.value })}
                        className="rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-sm outline-none focus:border-blue-600"
                    >
                        <option value="never">{t('freqNever')}</option>
                        <option value="occasional">{t('freqOccasional')}</option>
                        <option value="regular">{t('freqRegular')}</option>
                        <option value="heavy">{t('freqHeavy')}</option>
                    </select>
                </div>

                {/* Drugs */}
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <Flask className="h-5 w-5 text-slate-500" />
                        <span className="text-sm font-medium text-slate-700">{t('recreationalDrugs')}</span>
                    </div>
                    <select
                        value={data.drug_usage}
                        onChange={(e) => updateData({ drug_usage: e.target.value })}
                        className="rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-sm outline-none focus:border-blue-600"
                    >
                        <option value="never">{t('freqNever')}</option>
                        <option value="occasional">{t('freqOccasional')}</option>
                        <option value="regular">{t('freqRegular')}</option>
                        <option value="heavy">{t('freqHeavy')}</option>
                    </select>
                </div>
            </div>
        </motion.div>
    );
}
