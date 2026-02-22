"use client";

import { useEffect, useRef } from "react";
import { useLocale } from "next-intl";
import { useRouter, usePathname } from "@/i18n/routing";
import { useAuth } from "@/lib/auth-provider";
import { supabase } from "@/lib/supabase";
import { routing } from "@/i18n/routing";

// Map legacy full-name values (from old signup form) to ISO codes
const LEGACY_LANGUAGE_MAP: Record<string, string> = {
    english: "en",
    hindi: "hi",
    french: "fr",
    german: "de",
    japanese: "ja",
    chinese: "zh",
    dutch: "nl",
    arabic: "ar",
    spanish: "en", // unsupported locale — fall back to en
    russian: "en",
    portuguese: "en",
    bengali: "en",
    telugu: "en",
    marathi: "en",
    tamil: "en",
    urdu: "en",
    gujarati: "en",
    kannada: "en",
    malayalam: "en",
    punjabi: "en",
    odia: "en",
    assamese: "en",
    maithili: "en",
    sanskrit: "en",
};

/**
 * On mount, fetches the user's saved language preference from `profiles.language`.
 * If it differs from the current URL locale, redirects to the preferred locale.
 * Handles legacy full-name values (e.g. "hindi" → "hi") and only redirects
 * to locales that are actually supported by the routing config.
 */
export function useLocaleRedirect() {
    const locale = useLocale();
    const router = useRouter();
    const pathname = usePathname();
    const { user } = useAuth();
    const hasChecked = useRef(false);

    useEffect(() => {
        if (!user || hasChecked.current) return;

        const sessionKey = `locale_redirect_checked_${user.id}`;
        if (sessionStorage.getItem(sessionKey)) {
            hasChecked.current = true;
            return;
        }

        async function checkPreference() {
            const { data } = await supabase
                .from("profiles")
                .select("language")
                .eq("id", user!.id)
                .single();

            sessionStorage.setItem(sessionKey, "true");
            hasChecked.current = true;

            if (!data?.language) return;

            // Normalize: if it's a legacy full name, map to ISO code
            let preferredLocale = data.language.toLowerCase();
            if (LEGACY_LANGUAGE_MAP[preferredLocale]) {
                preferredLocale = LEGACY_LANGUAGE_MAP[preferredLocale];

                // Also fix the DB value so this mapping only happens once
                supabase
                    .from("profiles")
                    .update({ language: preferredLocale })
                    .eq("id", user!.id)
                    .then(({ error }) => {
                        if (error) console.error("Failed to migrate language preference:", error);
                    });
            }

            // Only redirect if it's a supported locale and different from current
            const supportedLocales = routing.locales as readonly string[];
            if (supportedLocales.includes(preferredLocale) && preferredLocale !== locale) {
                router.replace(pathname, { locale: preferredLocale });
            }
        }

        checkPreference();
    }, [user, locale, router, pathname]);
}
