"use client";

import { useEffect, useState } from "react";
import ProtectedRoute from "@/components/protected-route";
import { useAuth } from "@/lib/auth-provider";
import { supabase } from "@/lib/supabase";
import { LogOut } from "iconoir-react";

import WelcomeCard from "@/components/dashboard/WelcomeCard";
import HealthMetricsCard from "@/components/dashboard/HealthMetricsCard";
import InjuryStatusCard from "@/components/dashboard/InjuryStatusCard";
import GamificationCard from "@/components/dashboard/GamificationCard";

export default function DashboardPage() {
    const { user, signOut } = useAuth();
    const [profile, setProfile] = useState<any>(null);
    const [baseline, setBaseline] = useState<any>(null);
    const [assessment, setAssessment] = useState<any>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function fetchData() {
            if (!user) return;

            try {
                // Fetch public profile
                const { data: profileData } = await supabase
                    .from("profiles")
                    .select("*")
                    .eq("id", user.id)
                    .single();

                // Fetch baseline metrics (latest)
                const { data: baselineData } = await supabase
                    .from("baseline_profiles")
                    .select("*")
                    .eq("user_id", user.id)
                    .order("created_at", { ascending: false })
                    .limit(1)
                    .single();

                // Fetch latest injury assessment
                const { data: assessmentData } = await supabase
                    .from("injury_assessments")
                    .select("*, ai_clinical_analysis(*)")
                    .eq("user_id", user.id)
                    .order("created_at", { ascending: false })
                    .limit(1)
                    .single();

                setProfile(profileData);
                setBaseline(baselineData);
                setAssessment(assessmentData);
            } catch (error) {
                console.error("Error fetching dashboard data:", error);
            } finally {
                setLoading(false);
            }
        }

        fetchData();
    }, [user]);

    const handleRunAnalysis = async () => {
        if (!assessment || !user) return;

        try {
            // Get session for JWT
            const { data: sessionData } = await supabase.auth.getSession();
            const token = sessionData.session?.access_token;

            if (!token) throw new Error("No access token found");

            const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
            const response = await fetch(`${API_URL}/ai/analyze/${assessment.id}`, {
                method: "POST",
                headers: {
                    "Authorization": `Bearer ${token}`,
                    "Content-Type": "application/json",
                },
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || "Analysis failed");
            }

            const analysisResult = await response.json();

            // Optimistically update state
            setAssessment((prev: any) => ({
                ...prev,
                ai_clinical_analysis: [analysisResult]
            }));

        } catch (err) {
            console.error("AI Analysis failed:", err);
            alert("Failed to run AI analysis. Please try again.");
        }
    };

    return (
        <ProtectedRoute>
            <div className="min-h-screen bg-slate-50 pb-12">
                {/* Helper Nav */}
                <nav className="border-b border-slate-200 bg-white px-4 py-3 shadow-sm mb-6">
                    <div className="mx-auto flex max-w-5xl items-center justify-between">
                        <div className="flex items-center gap-2">
                            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-600 font-bold text-white">
                                R
                            </div>
                            <span className="text-lg font-bold text-slate-900">RehabFlow AI</span>
                        </div>

                        <button
                            onClick={signOut}
                            className="flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium text-slate-600 hover:bg-slate-50 hover:text-slate-900"
                        >
                            <LogOut className="h-4 w-4" />
                            <span className="hidden sm:inline">Sign Out</span>
                        </button>
                    </div>
                </nav>

                <main className="mx-auto max-w-5xl px-4 space-y-6">
                    <WelcomeCard
                        fullName={profile?.full_name}
                        loading={loading}
                    />

                    <div className="grid gap-6 md:grid-cols-2">
                        <HealthMetricsCard
                            baseline={baseline}
                            loading={loading}
                        />
                        <InjuryStatusCard
                            assessment={assessment}
                            loading={loading}
                            onRunAnalysis={handleRunAnalysis}
                        />

                        {/* Creates a full-width row on desktop */}
                        <GamificationCard
                            profile={profile}
                            loading={loading}
                        />
                    </div>
                </main>
            </div>
        </ProtectedRoute>
    );
}
