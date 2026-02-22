"use client";

import { motion } from "framer-motion";
import { CheckCircle, MediaImage } from "iconoir-react";
import { useTranslations } from "next-intl";

interface StepFiveProps {
    formData: any;
    conditions: string[];
    images: File[];
}

export default function StepFive({ formData, conditions, images }: StepFiveProps) {
    const t = useTranslations("assessment");

    return (
        <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="space-y-6"
        >
            <div className="flex flex-col items-center justify-center text-center">
                <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-emerald-50 text-emerald-600">
                    <CheckCircle className="h-8 w-8" />
                </div>
                <h2 className="text-xl font-bold text-slate-900">{t('readyToSubmit')}</h2>
                <p className="text-slate-500">{t('readySubtitle')}</p>
            </div>

            <div className="divide-y divide-slate-100 rounded-2xl border border-slate-200 bg-slate-50/50">
                {/* Lifestyle */}
                <div className="p-4">
                    <h4 className="mb-2 text-xs font-bold uppercase tracking-wider text-slate-500">{t('lifestyle')}</h4>
                    <dl className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                            <dt className="text-slate-500">{t('occupation')}</dt>
                            <dd className="font-semibold text-slate-900">{formData.occupation_type || t('na')}</dd>
                        </div>
                        <div>
                            <dt className="text-slate-500">{t('sitting')}</dt>
                            <dd className="font-semibold text-slate-900">{formData.daily_sitting_hours} {t('hrsPerDay')}</dd>
                        </div>
                        <div>
                            <dt className="text-slate-500">{t('gym')}</dt>
                            <dd className="font-semibold text-slate-900 capitalize">{formData.gym_frequency.replace(/_/g, " ")}</dd>
                        </div>
                    </dl>
                </div>

                {/* Medical */}
                <div className="p-4">
                    <h4 className="mb-2 text-xs font-bold uppercase tracking-wider text-slate-500">{t('medicalConditions')}</h4>
                    {conditions.length > 0 ? (
                        <div className="flex flex-wrap gap-2">
                            {conditions.map(id => (
                                <span key={id} className="rounded-full bg-blue-100 px-2.5 py-0.5 text-xs font-medium text-blue-700">
                                    Condition #{id.slice(0, 4)}...
                                </span>
                            ))}
                            <p className="text-xs text-slate-400 mt-1 w-full">{t('conditionSaved')}</p>
                        </div>
                    ) : (
                        <p className="text-sm font-semibold text-slate-900">{t('noneReported')}</p>
                    )}
                </div>

                {/* Injury */}
                <div className="p-4">
                    <h4 className="mb-2 text-xs font-bold uppercase tracking-wider text-slate-500">{t('injuryDetails')}</h4>
                    <dl className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                            <dt className="text-slate-500">{t('location')}</dt>
                            <dd className="font-semibold text-slate-900 capitalize">{formData.pain_location.replace(/_/g, " ")}</dd>
                        </div>
                        <div>
                            <dt className="text-slate-500">{t('intensity')}</dt>
                            <dd className="font-semibold text-slate-900">{formData.pain_level}/10</dd>
                        </div>
                        <div className="col-span-2">
                            <dt className="text-slate-500">{t('cause')}</dt>
                            <dd className="font-semibold text-slate-900">{formData.pain_cause}</dd>
                        </div>
                    </dl>
                </div>

                {/* Image Summary */}
                <div className="p-4">
                    <div className="mb-2 flex items-center justify-between">
                        <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500">{t('injuryImages')}</h4>
                        <span className="rounded-full bg-slate-200 px-2 py-0.5 text-[10px] font-bold text-slate-600">
                            {images.length}
                        </span>
                    </div>
                    {images.length > 0 ? (
                        <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
                            {images.map((file, i) => (
                                <div key={i} className="flex items-center gap-1.5 rounded border border-slate-200 bg-white p-1.5">
                                    <div className="h-6 w-6 flex-shrink-0 bg-slate-100 rounded flex items-center justify-center">
                                        <MediaImage className="h-3 w-3 text-slate-400" />
                                    </div>
                                    <span className="truncate text-xs text-slate-600">{file.name}</span>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <p className="text-sm italic text-slate-400">{t('noImagesAttached')}</p>
                    )}
                </div>
            </div>
        </motion.div>
    );
}
