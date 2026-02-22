"use client";

import { motion } from "framer-motion";
import { User } from "iconoir-react";
import { useTranslations, useLocale } from "next-intl";

interface WelcomeCardProps {
    fullName: string | null;
    loading?: boolean;
}

export default function WelcomeCard({ fullName, loading }: WelcomeCardProps) {
    const t = useTranslations("dashboard");
    const locale = useLocale();

    const date = new Date().toLocaleDateString(locale, {
        weekday: "long",
        month: "long",
        day: "numeric",
    });

    if (loading) {
        return (
            <div className="h-48 w-full animate-pulse rounded-2xl bg-slate-200"></div>
        );
    }

    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-blue-600 to-blue-500 p-8 text-white shadow-lg"
        >
            <div className="relative z-10">
                <p className="mb-2 text-blue-100 capitalize">{date}</p>
                <h1 className="text-3xl font-bold">
                    {t('welcomeTitle', { name: fullName || t('welcomeFallback') })}
                </h1>
                <p className="mt-2 max-w-lg text-blue-50">
                    {t('welcomeSubtitle')}
                </p>
            </div>

            <div className="absolute -right-4 -top-8 text-blue-400 opacity-20">
                <User className="h-64 w-64" />
            </div>
        </motion.div>
    );
}
