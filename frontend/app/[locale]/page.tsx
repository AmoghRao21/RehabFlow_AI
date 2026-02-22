"use client";

import { useTranslations } from 'next-intl';
import { Link } from '@/i18n/routing';
import { ArrowRight } from "iconoir-react";

export default function Home() {
  const t = useTranslations('dashboard');

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-slate-900 mb-4">{t('title')}</h1>
        <p className="mb-8 text-slate-600">Global Medical Rehabilitation Intelligence</p>
        <Link
          href="/dashboard"
          className="inline-flex items-center gap-2 rounded-full bg-blue-600 px-6 py-3 font-semibold text-white hover:bg-blue-700"
        >
          Go to Dashboard <ArrowRight className="h-4 w-4" />
        </Link>
      </div>
    </div>
  );
}
