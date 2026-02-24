"use client";

import ProtectedRoute from "@/components/protected-route";
import RehabPlanView from "@/components/rehab-plan/RehabPlanView";
import { ArrowLeft } from "iconoir-react";
import Link from "next/link";
import { useTranslations } from "next-intl";
import LanguageSwitcher from "@/components/LanguageSwitcher";

export default function RehabPlanPage() {
    const t = useTranslations("rehabPlan");

    return (
        <ProtectedRoute>
            <div className="min-h-screen bg-slate-50 pb-12">
                {/* Navigation */}
                <nav className="border-b border-slate-200 bg-white px-4 py-3 shadow-sm mb-6">
                    <div className="mx-auto flex max-w-4xl items-center justify-between">
                        <Link
                            href="/dashboard"
                            className="flex items-center gap-2 text-sm font-medium text-slate-600 transition-colors hover:text-slate-900"
                        >
                            <ArrowLeft className="h-4 w-4" />
                            {t("backToDashboard")}
                        </Link>
                        <div className="flex items-center gap-3">
                            <LanguageSwitcher />
                            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-purple-600 font-bold text-white text-sm">
                                R
                            </div>
                        </div>
                    </div>
                </nav>

                <main className="mx-auto max-w-4xl px-4">
                    <RehabPlanView />
                </main>
            </div>
        </ProtectedRoute>
    );
}
