"use client";

import { motion } from "framer-motion";
import { Medal, FireFlame, Trophy } from "iconoir-react";
import { useTranslations } from "next-intl";

interface GamificationCardProps {
    profile: any;
    loading?: boolean;
}

export default function GamificationCard({ profile, loading }: GamificationCardProps) {
    const t = useTranslations("dashboard");

    if (loading) {
        return <div className="h-32 w-full animate-pulse rounded-2xl bg-slate-200"></div>;
    }

    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="col-span-1 md:col-span-2 rounded-2xl bg-slate-900 p-6 text-white shadow-lg"
        >
            <div className="flex flex-col md:flex-row md:items-center md:justify-between">
                <div className="flex items-center gap-4">
                    <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-slate-800 text-yellow-400">
                        <Trophy className="h-6 w-6" />
                    </div>
                    <div>
                        <h2 className="text-lg font-bold">{t('achievementsTitle')}</h2>
                        <p className="text-slate-400 text-sm">{t('momentumMessage')}</p>
                    </div>
                </div>

                <div className="mt-6 flex gap-6 md:mt-0">
                    <div className="flex items-end gap-3">
                        <div className="mb-1 text-emerald-400">
                            <Medal className="h-8 w-8" />
                        </div>
                        <div>
                            <p className="text-2xl font-bold">{profile?.total_points || 0}</p>
                            <p className="text-xs text-slate-400 uppercase tracking-wider">{t('totalPointsLabel')}</p>
                        </div>
                    </div>

                    <div className="h-10 w-px bg-slate-700 self-center hidden md:block"></div>

                    <div className="flex items-end gap-3">
                        <div className="mb-1 text-orange-400">
                            <FireFlame className="h-8 w-8" />
                        </div>
                        <div>
                            <p className="text-2xl font-bold">{profile?.current_streak || 0}</p>
                            <p className="text-xs text-slate-400 uppercase tracking-wider">{t('dayStreakLabel')}</p>
                        </div>
                    </div>
                </div>
            </div>
        </motion.div>
    );
}
