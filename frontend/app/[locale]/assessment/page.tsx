"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { ArrowRight, ArrowLeft } from "iconoir-react";
import { useTranslations } from "next-intl";

import ProtectedRoute from "@/components/protected-route";
import ProgressIndicator from "@/components/assessment/ProgressIndicator";
import StepOne from "@/components/assessment/StepOne";
import StepTwo from "@/components/assessment/StepTwo";
import StepThree from "@/components/assessment/StepThree";
import StepFourImageUpload from "@/components/assessment/StepFourImageUpload";
import StepFive from "@/components/assessment/StepFive";

import { useAuth } from "@/lib/auth-provider";
import { supabase } from "@/lib/supabase";

export default function AssessmentPage() {
    const router = useRouter();
    const { user } = useAuth();
    const t = useTranslations();

    const [currentStep, setCurrentStep] = useState(1);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Lifestyle Data
    const [formData, setFormData] = useState({
        // Baseline Profile Fields
        occupation_type: "",
        daily_sitting_hours: 0,
        physical_work_level: "sedentary",
        gym_frequency: "never",
        alcohol_usage: "never",
        smoking_usage: "never",
        drug_usage: "never",

        // Injury Assessment Fields
        pain_location: "",
        pain_level: 5,
        pain_cause: "",
        injury_date: new Date().toISOString().split("T")[0],
        is_swollen: false,
        mobility_restricted: false,
    });

    // Medical Conditions (Array of IDs)
    const [selectedConditions, setSelectedConditions] = useState<string[]>([]);

    // Images
    const [images, setImages] = useState<File[]>([]);

    const updateData = (updates: any) => {
        setFormData((prev) => ({ ...prev, ...updates }));
    };

    const updateConditions = (ids: string[]) => {
        setSelectedConditions(ids);
    };

    const updateImages = (files: File[]) => {
        setImages(files);
    };

    const handleNext = () => {
        setError(null);
        if (currentStep === 1) {
            if (!formData.occupation_type) return setError(t('assessment.errorOccupation'));
        }
        if (currentStep === 3) {
            if (!formData.pain_location) return setError(t('assessment.errorPainLocation'));
            if (!formData.pain_cause) return setError(t('assessment.errorPainCause'));
        }
        setCurrentStep((prev) => prev + 1);
    };

    const handleBack = () => {
        setError(null);
        setCurrentStep((prev) => prev - 1);
    };

    const handleSubmit = async () => {
        if (!user) return;
        setLoading(true);
        setError(null);

        try {
            // 1. Upsert Baseline Profile (Lifestyle)
            const { error: profileError } = await supabase
                .from("baseline_profiles")
                .upsert({
                    user_id: user.id,
                    occupation_type: formData.occupation_type,
                    daily_sitting_hours: formData.daily_sitting_hours,
                    physical_work_level: formData.physical_work_level,
                    gym_frequency: formData.gym_frequency,
                    alcohol_usage: formData.alcohol_usage,
                    smoking_usage: formData.smoking_usage,
                    drug_usage: formData.drug_usage,
                    updated_at: new Date().toISOString(),
                }, { onConflict: 'user_id' });

            if (profileError) throw new Error(`Profile Error: ${profileError.message}`);

            // 2. Sync Medical Conditions
            const { error: deleteError } = await supabase
                .from("user_medical_conditions")
                .delete()
                .eq("user_id", user.id);

            if (deleteError) throw new Error(`Condition Delete Error: ${deleteError.message}`);

            if (selectedConditions.length > 0) {
                const conditionRows = selectedConditions.map(id => ({
                    user_id: user.id,
                    condition_id: id
                }));

                const { error: insertCondError } = await supabase
                    .from("user_medical_conditions")
                    .insert(conditionRows);

                if (insertCondError) throw new Error(`Condition Insert Error: ${insertCondError.message}`);
            }

            // 3. Insert Injury Assessment
            const { data: assessmentData, error: injuryError } = await supabase
                .from("injury_assessments")
                .insert({
                    user_id: user.id,
                    pain_location: formData.pain_location,
                    pain_level: formData.pain_level,
                    pain_cause: formData.pain_cause,
                    pain_started_at: new Date(formData.injury_date).toISOString(),
                    visible_swelling: formData.is_swollen,
                    mobility_restriction: formData.mobility_restricted,
                    additional_notes: "Advanced assessment submission",
                })
                .select()
                .single();

            if (injuryError) throw new Error(`Injury Error: ${injuryError.message}`);

            const assessmentId = assessmentData.id;

            // 4. Upload Images & Insert Records
            if (images.length > 0 && assessmentId) {
                for (const file of images) {
                    const fileExt = file.name.split('.').pop();
                    const fileName = `${crypto.randomUUID()}.${fileExt}`;
                    const filePath = `${user.id}/${assessmentId}/${fileName}`;

                    // Upload to Storage
                    const { error: uploadError } = await supabase.storage
                        .from('injury-images')
                        .upload(filePath, file);

                    if (uploadError) throw new Error(`Image Upload Error: ${uploadError.message}`);

                    // Insert to DB
                    const { error: imgDbError } = await supabase
                        .from('injury_images')
                        .insert({
                            injury_assessment_id: assessmentId,
                            image_url: filePath,
                        });

                    if (imgDbError) throw new Error(`Image DB Error: ${imgDbError.message}`);
                }
            }

            // Success
            router.push("/dashboard");
        } catch (err: any) {
            console.error(err);
            setError(err.message || t('assessment.failedSubmit'));
            setLoading(false);
        }
    };

    return (
        <ProtectedRoute>
            <div className="min-h-screen bg-slate-50 py-12 px-4">
                <div className="mx-auto max-w-4xl">
                    <ProgressIndicator currentStep={currentStep} />

                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="rounded-2xl bg-white p-6 shadow-lg sm:p-10"
                    >
                        <div className="mb-8 border-b border-slate-100 pb-4">
                            <h1 className="text-2xl font-bold text-slate-900">
                                {currentStep === 1 && t('assessment.stepLifestyle')}
                                {currentStep === 2 && t('assessment.stepMedical')}
                                {currentStep === 3 && t('assessment.stepInjury')}
                                {currentStep === 4 && t('assessment.stepPhotos')}
                                {currentStep === 5 && t('assessment.stepReview')}
                            </h1>
                            <p className="text-slate-500">
                                {t('assessment.stepOfTotal', { current: currentStep, total: 5 })}
                            </p>
                        </div>

                        {error && (
                            <div className="mb-6 rounded-lg bg-red-50 p-3 text-sm text-red-600">
                                {error}
                            </div>
                        )}

                        <div className="min-h-[400px]">
                            <AnimatePresence mode="wait">
                                {currentStep === 1 && (
                                    <StepOne key="step1" data={formData} updateData={updateData} />
                                )}
                                {currentStep === 2 && (
                                    <StepTwo
                                        key="step2"
                                        selectedConditions={selectedConditions}
                                        updateConditions={updateConditions}
                                    />
                                )}
                                {currentStep === 3 && (
                                    <StepThree key="step3" data={formData} updateData={updateData} />
                                )}
                                {currentStep === 4 && (
                                    <StepFourImageUpload
                                        key="step4"
                                        images={images}
                                        updateImages={updateImages}
                                    />
                                )}
                                {currentStep === 5 && (
                                    <StepFive
                                        key="step5"
                                        formData={formData}
                                        conditions={selectedConditions}
                                        images={images}
                                    />
                                )}
                            </AnimatePresence>
                        </div>

                        <div className="mt-10 flex items-center justify-between border-t border-slate-100 pt-6">
                            <button
                                onClick={handleBack}
                                disabled={currentStep === 1 || loading}
                                className={`flex items-center gap-2 font-medium text-slate-500 transition-colors hover:text-slate-900 ${currentStep === 1 ? "invisible" : ""
                                    }`}
                            >
                                <ArrowLeft className="h-4 w-4" /> {t('assessment.back')}
                            </button>

                            {currentStep < 5 ? (
                                <button
                                    onClick={handleNext}
                                    className="flex items-center gap-2 rounded-lg bg-blue-600 px-6 py-2.5 font-semibold text-white transition-all hover:bg-blue-700 hover:shadow-lg hover:shadow-blue-600/20"
                                >
                                    {t('assessment.nextStep')} <ArrowRight className="h-4 w-4" />
                                </button>
                            ) : (
                                <button
                                    onClick={handleSubmit}
                                    disabled={loading}
                                    className="flex items-center gap-2 rounded-lg bg-emerald-600 px-8 py-2.5 font-semibold text-white transition-all hover:bg-emerald-700 hover:shadow-lg hover:shadow-emerald-600/20 disabled:opacity-70"
                                >
                                    {loading ? (
                                        <div className="h-5 w-5 animate-spin rounded-full border-2 border-white border-t-transparent" />
                                    ) : (
                                        <>{t('assessment.submit')} <ArrowRight className="h-4 w-4" /></>
                                    )}
                                </button>
                            )}
                        </div>
                    </motion.div>
                </div>
            </div>
        </ProtectedRoute>
    );
}
