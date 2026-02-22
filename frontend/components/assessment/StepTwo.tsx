"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Check } from "iconoir-react";
import { supabase } from "@/lib/supabase";
import { useTranslations } from "next-intl";

interface StepTwoProps {
    selectedConditions: string[];
    updateConditions: (ids: string[]) => void;
}

interface MedicalCondition {
    id: string;
    name: string;
    description: string;
}

export default function StepTwo({ selectedConditions, updateConditions }: StepTwoProps) {
    const t = useTranslations("assessment");
    const [conditions, setConditions] = useState<MedicalCondition[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function fetchConditions() {
            try {
                const { data, error } = await supabase
                    .from("medical_conditions")
                    .select("*")
                    .order("name");

                if (error) throw error;
                if (data) setConditions(data);
            } catch (err) {
                console.error("Failed to fetch medical conditions", err);
            } finally {
                setLoading(false);
            }
        }
        fetchConditions();
    }, []);

    const toggleCondition = (id: string) => {
        if (selectedConditions.includes(id)) {
            updateConditions(selectedConditions.filter(c => c !== id));
        } else {
            updateConditions([...selectedConditions, id]);
        }
    };

    if (loading) {
        return (
            <div className="grid gap-3 sm:grid-cols-2">
                {[1, 2, 3, 4, 5, 6].map((i) => (
                    <div key={i} className="h-16 animate-pulse rounded-xl bg-slate-100"></div>
                ))}
            </div>
        );
    }

    return (
        <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="space-y-6"
        >
            <div>
                <h3 className="text-lg font-semibold text-slate-900">{t('medicalHistoryTitle')}</h3>
                <p className="text-slate-500 text-sm">{t('medicalHistorySubtitle')}</p>
            </div>

            <div className="grid gap-3 sm:grid-cols-2">
                {conditions.map((condition) => {
                    const isSelected = selectedConditions.includes(condition.id);
                    return (
                        <button
                            key={condition.id}
                            onClick={() => toggleCondition(condition.id)}
                            className={`relative flex items-start gap-3 rounded-xl border p-4 text-left transition-all ${isSelected
                                ? "border-blue-600 bg-blue-50 ring-1 ring-blue-600"
                                : "border-slate-200 bg-white hover:border-slate-300 hover:bg-slate-50"
                                }`}
                        >
                            <div className={`mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded border ${isSelected ? "border-blue-600 bg-blue-600 text-white" : "border-slate-300 bg-white"
                                }`}>
                                {isSelected && <Check className="h-3.5 w-3.5" />}
                            </div>
                            <div>
                                <span className={`block text-sm font-semibold ${isSelected ? "text-blue-900" : "text-slate-900"}`}>
                                    {condition.name}
                                </span>
                                {condition.description && (
                                    <span className="mt-0.5 block text-xs text-slate-500 line-clamp-2">
                                        {condition.description}
                                    </span>
                                )}
                            </div>
                        </button>
                    );
                })}
            </div>

            {conditions.length === 0 && (
                <div className="text-center text-slate-500 py-8">
                    {t('noConditions')}
                </div>
            )}
        </motion.div>
    );
}
