"use client";

import { useLocale, useTranslations } from "next-intl";
import { usePathname, useRouter } from "@/i18n/routing";
import { useState, useTransition } from "react";
import { Globe, Check } from "iconoir-react";
import { motion, AnimatePresence } from "framer-motion";
import { supabase } from "@/lib/supabase";
import { useAuth } from "@/lib/auth-provider";

export default function LanguageSwitcher() {
    const locale = useLocale();
    const router = useRouter();
    const pathname = usePathname();
    const [isPending, startTransition] = useTransition();
    const [isOpen, setIsOpen] = useState(false);
    const { user } = useAuth();

    const languages = [
        { code: "en", name: "English" },
        { code: "hi", name: "हिन्दी" },
        { code: "fr", name: "Français" },
        { code: "ja", name: "日本語" },
        { code: "zh", name: "中文" },
        { code: "nl", name: "Nederlands" },
        { code: "de", name: "Deutsch" },
        { code: "ar", name: "العربية" },
    ];

    const currentLanguage = languages.find((l) => l.code === locale) || languages[0];

    const onSelectChange = (nextLocale: string) => {
        setIsOpen(false);

        // Persist preference to DB
        if (user) {
            supabase
                .from("profiles")
                .update({ language: nextLocale })
                .eq("id", user.id)
                .then(({ error }) => {
                    if (error) console.error("Failed to save language preference:", error);
                });
        }

        startTransition(() => {
            router.replace(pathname, { locale: nextLocale });
        });
    };

    return (
        <div className="relative">
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 hover:text-slate-900 transition-colors"
            >
                <Globe className="h-4 w-4" />
                <span className="hidden sm:inline">{currentLanguage.name}</span>
            </button>

            <AnimatePresence>
                {isOpen && (
                    <>
                        <div
                            className="fixed inset-0 z-10"
                            onClick={() => setIsOpen(false)}
                        />
                        <motion.div
                            initial={{ opacity: 0, y: 10, scale: 0.95 }}
                            animate={{ opacity: 1, y: 0, scale: 1 }}
                            exit={{ opacity: 0, y: 10, scale: 0.95 }}
                            transition={{ duration: 0.1 }}
                            className="absolute right-0 z-20 mt-2 w-40 origin-top-right rounded-xl border border-slate-100 bg-white p-1 shadow-lg ring-1 ring-black/5 focus:outline-none"
                        >
                            {languages.map((lang) => (
                                <button
                                    key={lang.code}
                                    onClick={() => onSelectChange(lang.code)}
                                    disabled={isPending}
                                    className={`flex w-full items-center justify-between rounded-lg px-3 py-2 text-sm transition-colors ${locale === lang.code
                                        ? "bg-blue-50 text-blue-600 font-medium"
                                        : "text-slate-700 hover:bg-slate-50"
                                        }`}
                                >
                                    {lang.name}
                                    {locale === lang.code && <Check className="h-3.5 w-3.5" />}
                                </button>
                            ))}
                        </motion.div>
                    </>
                )}
            </AnimatePresence>
        </div>
    );
}
