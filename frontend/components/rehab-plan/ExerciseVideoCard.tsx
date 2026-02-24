"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { PlaySolid, Xmark, MultiplePages } from "iconoir-react";

interface ExerciseVideoCardProps {
    exerciseName: string;
    condition: string;
    painLocation: string;
    className?: string;
}

export default function ExerciseVideoCard({
    exerciseName,
    condition,
    painLocation,
    className = "",
}: ExerciseVideoCardProps) {
    const [embedUrl, setEmbedUrl] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);
    const [open, setOpen] = useState(false);
    const [failed, setFailed] = useState(false);

    const fetchVideo = async () => {
        if (embedUrl || loading) {
            setOpen(true);
            return;
        }
        setLoading(true);
        setFailed(false);

        try {
            const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
            // Build keyword list combining exercise name + condition + body part
            const keywords = [
                exerciseName,
                "physical therapy",
                painLocation,
                "exercise tutorial",
            ]
                .filter(Boolean)
                .slice(0, 4);

            const params = keywords.map((k) => `keywords=${encodeURIComponent(k)}`).join("&");
            const res = await fetch(`${API_URL}/youtube/video?${params}`);

            if (!res.ok) throw new Error("failed");
            const data = await res.json();
            setEmbedUrl(data.embed_url);
            setOpen(true);
        } catch {
            setFailed(true);
        } finally {
            setLoading(false);
        }
    };

    return (
        <>
            {/* Trigger button */}
            <button
                onClick={fetchVideo}
                disabled={loading}
                title={`Watch ${exerciseName} tutorial`}
                className={`inline-flex items-center gap-1.5 rounded-lg bg-red-50 px-2.5 py-1.5 text-xs font-semibold text-red-600 border border-red-100 transition-all hover:bg-red-100 hover:border-red-200 disabled:opacity-50 ${className}`}
            >
                {loading ? (
                    <span className="h-3 w-3 animate-spin rounded-full border-2 border-red-300 border-t-red-600" />
                ) : (
                    <PlaySolid className="h-3 w-3" />
                )}
                {failed ? "Retry" : loading ? "Loading..." : "Watch"}
            </button>

            {/* Video modal */}
            {open && embedUrl && (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4 backdrop-blur-sm"
                    onClick={() => setOpen(false)}
                >
                    <motion.div
                        initial={{ scale: 0.92, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        transition={{ duration: 0.2 }}
                        onClick={(e) => e.stopPropagation()}
                        className="relative w-full max-w-2xl rounded-2xl bg-slate-900 overflow-hidden shadow-2xl"
                    >
                        {/* Header */}
                        <div className="flex items-center justify-between px-4 py-3 bg-slate-800">
                            <div className="flex items-center gap-2">
                                <MultiplePages className="h-4 w-4 text-red-400" />
                                <span className="text-sm font-semibold text-white truncate max-w-xs">
                                    {exerciseName}
                                </span>
                            </div>
                            <button
                                onClick={() => setOpen(false)}
                                className="flex h-7 w-7 items-center justify-center rounded-lg text-slate-400 hover:bg-slate-700 hover:text-white transition-colors"
                            >
                                <Xmark className="h-4 w-4" />
                            </button>
                        </div>

                        {/* Embed */}
                        <div className="aspect-video w-full">
                            <iframe
                                src={`${embedUrl}?autoplay=1&rel=0&modestbranding=1`}
                                title={exerciseName}
                                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                                allowFullScreen
                                className="h-full w-full"
                            />
                        </div>
                    </motion.div>
                </motion.div>
            )}
        </>
    );
}
