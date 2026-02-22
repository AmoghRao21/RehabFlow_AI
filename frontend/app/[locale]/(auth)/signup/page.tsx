"use client";

import { useState } from "react";
import { supabase } from "@/lib/supabase";
import { useRouter, Link } from "@/i18n/routing";
import { Mail, Lock, User, Ruler, Weight, InfoCircle, ArrowRight } from "iconoir-react";
import { motion } from "framer-motion";

export default function SignupPage() {
    const router = useRouter();
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const [formData, setFormData] = useState({
        email: "",
        password: "",
        fullName: "",
        age: "",
        gender: "male",
        height: "",
        weight: "",
        language: "en",
    });

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
        setFormData((prev) => ({ ...prev, [e.target.name]: e.target.value }));
    };

    const validatePassword = (pass: string) => {
        const minLength = 8;
        const hasUpper = /[A-Z]/.test(pass);
        const hasLower = /[a-z]/.test(pass);
        const hasNumber = /[0-9]/.test(pass);
        const hasSpecial = /[!@#$%^&*(),.?":{}|<>]/.test(pass);
        return pass.length >= minLength && hasUpper && hasLower && hasNumber && hasSpecial;
    };

    const handleSignup = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);

        // Validation
        if (!validatePassword(formData.password)) {
            setError("Password must have 8+ chars, uppercase, lowercase, number, and special char.");
            return;
        }

        setLoading(true);

        try {
            // 1. Sign Up
            const { data: authData, error: authError } = await supabase.auth.signUp({
                email: formData.email,
                password: formData.password,
                options: {
                    data: {
                        full_name: formData.fullName,
                        language: formData.language,
                    },
                },
            });

            if (authError) throw authError;
            if (!authData.user) throw new Error("No user created");

            // 2. Explicitly update Profile table to ensure language is saved
            const { error: profileUpdateError } = await supabase
                .from("profiles")
                .update({
                    full_name: formData.fullName,
                    language: formData.language,
                })
                .eq("id", authData.user.id);

            if (profileUpdateError) {
                console.warn("Profile update failed, attempting upsert", profileUpdateError);
                await supabase.from("profiles").upsert({
                    id: authData.user.id,
                    full_name: formData.fullName,
                    language: formData.language,
                });
            }

            // 2. Insert Baseline Profile Data
            // Note: We use the authenticated user's ID. RLS must allow insert.
            const { error: profileError } = await supabase.from("baseline_profiles").insert({
                user_id: authData.user.id,
                age: parseInt(formData.age),
                gender: formData.gender,
                height_cm: parseInt(formData.height),
                weight_kg: parseInt(formData.weight),
                gym_frequency: "never", // Default
                alcohol_usage: "never", // Default
                smoking_usage: "never", // Default
                drug_usage: "never", // Default
            });

            // Even if profile insert fails (e.g. RLS issue), we still redirect to dashboard
            // Log the error silently or handle it. Ideally, we want to block if critical.
            if (profileError) {
                console.error("Profile creation failed:", profileError);
                // We continue to dashboard anyway, user exists.
            }

            router.refresh();
            router.push("/dashboard");
        } catch (err: any) {
            setError(err.message || "An error occurred during signup");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex min-h-screen items-center justify-center bg-slate-50 px-4 py-8">
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="w-full max-w-2xl overflow-hidden rounded-2xl bg-white shadow-xl ring-1 ring-slate-100"
            >
                <div className="bg-emerald-600 p-8 text-center">
                    <h1 className="text-3xl font-bold text-white">Create Account</h1>
                    <p className="mt-2 text-emerald-100">Begin your personalized rehabilitation plan</p>
                </div>

                <div className="p-8">
                    <form onSubmit={handleSignup} className="space-y-6">
                        {error && (
                            <div className="flex items-center gap-2 rounded-lg bg-red-50 p-3 text-sm text-red-600">
                                <InfoCircle className="h-5 w-5 flex-shrink-0" />
                                <p>{error}</p>
                            </div>
                        )}

                        {/* Personal Info Grid */}
                        <div className="grid gap-6 md:grid-cols-2">
                            <div className="space-y-2">
                                <label className="text-sm font-medium text-slate-700">Full Name</label>
                                <div className="relative">
                                    <User className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-400" />
                                    <input
                                        name="fullName"
                                        required
                                        value={formData.fullName}
                                        onChange={handleChange}
                                        className="w-full rounded-lg border border-slate-200 py-2.5 pl-10 pr-4 text-slate-900 outline-none focus:border-emerald-600 focus:ring-1 focus:ring-emerald-600"
                                        placeholder="John Doe"
                                    />
                                </div>
                            </div>

                            <div className="space-y-2">
                                <label className="text-sm font-medium text-slate-700">Email Address</label>
                                <div className="relative">
                                    <Mail className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-400" />
                                    <input
                                        name="email"
                                        type="email"
                                        required
                                        value={formData.email}
                                        onChange={handleChange}
                                        className="w-full rounded-lg border border-slate-200 py-2.5 pl-10 pr-4 text-slate-900 outline-none focus:border-emerald-600 focus:ring-1 focus:ring-emerald-600"
                                        placeholder="you@example.com"
                                    />
                                </div>
                            </div>

                            <div className="space-y-2">
                                <label className="text-sm font-medium text-slate-700">Password</label>
                                <div className="relative">
                                    <Lock className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-400" />
                                    <input
                                        name="password"
                                        type="password"
                                        required
                                        value={formData.password}
                                        onChange={handleChange}
                                        className="w-full rounded-lg border border-slate-200 py-2.5 pl-10 pr-4 text-slate-900 outline-none focus:border-emerald-600 focus:ring-1 focus:ring-emerald-600"
                                        placeholder="Strong password"
                                    />
                                </div>
                                <p className="text-xs text-slate-500">Min 8 chars, uppercase, lowercase, number, special</p>
                            </div>

                            <div className="space-y-2">
                                <label className="text-sm font-medium text-slate-700">Age</label>
                                <input
                                    name="age"
                                    type="number"
                                    required
                                    min="1"
                                    max="120"
                                    value={formData.age}
                                    onChange={handleChange}
                                    className="w-full rounded-lg border border-slate-200 px-4 py-2.5 text-slate-900 outline-none focus:border-emerald-600 focus:ring-1 focus:ring-emerald-600"
                                    placeholder="30"
                                />
                            </div>

                            <div className="space-y-2">
                                <label className="text-sm font-medium text-slate-700">Gender</label>
                                <select
                                    name="gender"
                                    value={formData.gender}
                                    onChange={handleChange}
                                    className="w-full appearance-none rounded-lg border border-slate-200 bg-white px-4 py-2.5 text-slate-900 outline-none focus:border-emerald-600 focus:ring-1 focus:ring-emerald-600"
                                >
                                    <option value="male">Male</option>
                                    <option value="female">Female</option>
                                    <option value="other">Other</option>
                                </select>
                            </div>

                            <div className="space-y-2">
                                <label className="text-sm font-medium text-slate-700">Language</label>
                                <select
                                    name="language"
                                    value={formData.language}
                                    onChange={handleChange}
                                    className="w-full appearance-none rounded-lg border border-slate-200 bg-white px-4 py-2.5 text-slate-900 outline-none focus:border-emerald-600 focus:ring-1 focus:ring-emerald-600"
                                >
                                    <option value="en">English</option>
                                    <option value="hi">हिन्दी (Hindi)</option>
                                    <option value="fr">Français (French)</option>
                                    <option value="de">Deutsch (German)</option>
                                    <option value="ja">日本語 (Japanese)</option>
                                    <option value="zh">中文 (Chinese)</option>
                                    <option value="nl">Nederlands (Dutch)</option>
                                    <option value="ar">العربية (Arabic)</option>
                                </select>
                            </div>

                            <div className="space-y-2">
                                <label className="text-sm font-medium text-slate-700">Height (cm)</label>
                                <div className="relative">
                                    <Ruler className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-400" />
                                    <input
                                        name="height"
                                        type="number"
                                        required
                                        min="50"
                                        max="300"
                                        value={formData.height}
                                        onChange={handleChange}
                                        className="w-full rounded-lg border border-slate-200 py-2.5 pl-10 pr-4 text-slate-900 outline-none focus:border-emerald-600 focus:ring-1 focus:ring-emerald-600"
                                        placeholder="175"
                                    />
                                </div>
                            </div>

                            <div className="space-y-2">
                                <label className="text-sm font-medium text-slate-700">Weight (kg)</label>
                                <div className="relative">
                                    <Weight className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-400" />
                                    <input
                                        name="weight"
                                        type="number"
                                        required
                                        min="20"
                                        max="500"
                                        value={formData.weight}
                                        onChange={handleChange}
                                        className="w-full rounded-lg border border-slate-200 py-2.5 pl-10 pr-4 text-slate-900 outline-none focus:border-emerald-600 focus:ring-1 focus:ring-emerald-600"
                                        placeholder="70"
                                    />
                                </div>
                            </div>
                        </div>

                        <button
                            type="submit"
                            disabled={loading}
                            className="group flex w-full items-center justify-center gap-2 rounded-lg bg-emerald-600 py-3 font-semibold text-white transition-all hover:bg-emerald-700 hover:shadow-lg hover:shadow-emerald-600/20 disabled:opacity-70"
                        >
                            {loading ? (
                                <div className="h-5 w-5 animate-spin rounded-full border-2 border-white border-t-transparent" />
                            ) : (
                                <>
                                    Complete Registration <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
                                </>
                            )}
                        </button>
                    </form>

                    <p className="mt-8 text-center text-sm text-slate-600">
                        Already have an account?{" "}
                        <Link href="/login" className="font-semibold text-emerald-600 hover:text-emerald-700 hover:underline">
                            Log In
                        </Link>
                    </p>
                </div>
            </motion.div>
        </div>
    );
}
