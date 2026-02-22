"use client";

import { motion } from "framer-motion";
import { Upload, Xmark, MediaImage } from "iconoir-react";
import Image from "next/image";
import { useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { useTranslations } from "next-intl";

interface StepFourImageUploadProps {
    images: File[];
    updateImages: (files: File[]) => void;
}

export default function StepFourImageUpload({ images, updateImages }: StepFourImageUploadProps) {
    const t = useTranslations("assessment");

    const onDrop = useCallback((acceptedFiles: File[]) => {
        const validFiles = acceptedFiles.filter(file => file.size <= 5 * 1024 * 1024);
        updateImages([...images, ...validFiles]);
    }, [images, updateImages]);

    const { getRootProps, getInputProps, isDragActive, fileRejections } = useDropzone({
        onDrop,
        accept: {
            'image/jpeg': [],
            'image/png': [],
            'image/webp': []
        },
        maxSize: 5 * 1024 * 1024,
        multiple: true
    });

    const removeImage = (index: number) => {
        const newImages = [...images];
        newImages.splice(index, 1);
        updateImages(newImages);
    };

    return (
        <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="space-y-8"
        >
            <div className="space-y-4">
                <h3 className="text-lg font-semibold text-slate-900">{t('uploadTitle')}</h3>
                <p className="text-sm text-slate-500">
                    {t('uploadSubtitle')}
                </p>

                {/* Dropzone */}
                <div
                    {...getRootProps()}
                    className={`cursor-pointer rounded-2xl border-2 border-dashed p-8 text-center transition-all duration-200 ease-in-out
                        ${isDragActive
                            ? "border-blue-500 bg-blue-50/50"
                            : "border-slate-200 bg-slate-50 hover:border-blue-400 hover:bg-slate-100"
                        }`}
                >
                    <input {...getInputProps()} />
                    <div className="flex flex-col items-center justify-center gap-4">
                        <div className={`rounded-full p-4 ${isDragActive ? "bg-blue-100 text-blue-600" : "bg-white text-slate-400 shadow-sm"}`}>
                            <Upload className="h-8 w-8" />
                        </div>
                        <div className="space-y-1">
                            <p className="font-medium text-slate-900">
                                {isDragActive ? t('dropHere') : t('clickOrDrag')}
                            </p>
                            <p className="text-xs text-slate-500">
                                {t('supportedFormats')}
                            </p>
                        </div>
                    </div>
                </div>

                {/* Error Messages */}
                {fileRejections.length > 0 && (
                    <div className="rounded-lg bg-red-50 p-3 text-sm text-red-600">
                        {fileRejections.map(({ file, errors }) => (
                            <div key={file.name}>
                                <span className="font-medium">{file.name}:</span> {errors.map(e => e.message).join(", ")}
                            </div>
                        ))}
                    </div>
                )}

                {/* Image Grid */}
                {images.length > 0 && (
                    <div className="grid grid-cols-2 gap-4 sm:grid-cols-3">
                        {images.map((file, index) => (
                            <div key={`${file.name}-${index}`} className="group relative aspect-square overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
                                <Image
                                    src={URL.createObjectURL(file)}
                                    alt="Preview"
                                    fill
                                    className="object-cover"
                                    onLoad={(e) => {
                                        URL.revokeObjectURL((e.target as HTMLImageElement).src);
                                    }}
                                />
                                <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/60 to-transparent p-2 opacity-0 transition-opacity group-hover:opacity-100">
                                    <p className="truncate text-xs text-white">{file.name}</p>
                                </div>
                                <button
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        removeImage(index);
                                    }}
                                    className="absolute right-2 top-2 rounded-full bg-white/90 p-1.5 text-slate-600 shadow-sm transition-colors hover:bg-red-50 hover:text-red-500"
                                >
                                    <Xmark className="h-4 w-4" />
                                </button>
                            </div>
                        ))}
                    </div>
                )}

                {images.length === 0 && (
                    <div className="flex flex-col items-center justify-center rounded-xl border border-slate-100 bg-white py-12 text-slate-400">
                        <MediaImage className="mb-2 h-10 w-10 opacity-20" />
                        <p className="text-sm">{t('noImagesSelected')}</p>
                    </div>
                )}
            </div>
        </motion.div>
    );
}
