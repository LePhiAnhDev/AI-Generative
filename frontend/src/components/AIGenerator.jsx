import React, { useState, useEffect, useRef } from 'react';
import { Sparkles } from 'lucide-react';
import PageHeader from './common/PageHeader';
import aiGeneratorService from '../services/apiService';
import toast from 'react-hot-toast';

// Import từng component riêng biệt
import ModelStatusCard from './AIGenerator/ModelStatusCard';
import GenerativeArtSection from './AIGenerator/GenerativeArtSection';
import GenerativeVideoSection from './AIGenerator/GenerativeVideoSection';
import StreamingGenerativeSection from './AIGenerator/StreamingGenerativeSection';
import AIIntroduction from './AIGenerator/AIIntroduction';

/**
 * AI Generator - Main component for generative AI tools
 */
const AIGenerator = () => {
    // State for each section
    const [generativeArt, setGenerativeArt] = useState({
        prompt: '',
        result: null,
        isGenerating: false,
        isModelLoaded: false
    });

    const [generativeVideo, setGenerativeVideo] = useState({
        prompt: '',
        result: null,
        isGenerating: false,
        isModelLoaded: false
    });

    const [streamingGenerative, setStreamingGenerative] = useState({
        prompt: '',
        result: null,
        isGenerating: false,
        isModelLoaded: false
    });

    // Model status
    const [modelStatus, setModelStatus] = useState({});
    const [isLoadingModels, setIsLoadingModels] = useState(false);

    // Streaming debounce
    const streamingTimeoutRef = useRef(null);
    const STREAMING_DELAY = 1500; // 1.5 seconds

    // Load model status on component mount
    useEffect(() => {
        loadModelStatus();
    }, []);

    // Streaming effect for real-time generation
    useEffect(() => {
        if (streamingGenerative.prompt && streamingGenerative.isModelLoaded) {
            // Clear existing timeout
            if (streamingTimeoutRef.current) {
                clearTimeout(streamingTimeoutRef.current);
            }

            // Set new timeout for streaming generation
            streamingTimeoutRef.current = setTimeout(() => {
                handleStreamingGenerate();
            }, STREAMING_DELAY);
        }

        // Cleanup timeout on unmount
        return () => {
            if (streamingTimeoutRef.current) {
                clearTimeout(streamingTimeoutRef.current);
            }
        };
    }, [streamingGenerative.prompt, streamingGenerative.isModelLoaded]);

    const loadModelStatus = async () => {
        try {
            const response = await aiGeneratorService.getModelStatus();
            if (response.success) {
                setModelStatus(response.data);

                // Update individual model loaded states
                const models = response.data.models_status || {};
                setGenerativeArt(prev => ({
                    ...prev,
                    isModelLoaded: models.generative_art?.loaded || false
                }));
                setGenerativeVideo(prev => ({
                    ...prev,
                    isModelLoaded: models.generative_video?.loaded || false
                }));
                setStreamingGenerative(prev => ({
                    ...prev,
                    isModelLoaded: models.streaming_generative?.loaded || false
                }));
            }
        } catch (error) {
            console.error('Error loading model status:', error);
        }
    };

    const handleLoadModel = async (modelType) => {
        setIsLoadingModels(true);
        try {
            const response = await aiGeneratorService.loadModel(modelType);
            if (response.success) {
                // Update specific model status
                if (modelType === 'generative_art') {
                    setGenerativeArt(prev => ({ ...prev, isModelLoaded: true }));
                } else if (modelType === 'generative_video') {
                    setGenerativeVideo(prev => ({ ...prev, isModelLoaded: true }));
                } else if (modelType === 'streaming_generative') {
                    setStreamingGenerative(prev => ({ ...prev, isModelLoaded: true }));
                }

                // Reload model status
                await loadModelStatus();
                toast.success(`Model ${modelType} đã được tải thành công!`);
            }
        } catch (error) {
            console.error('Error loading model:', error);
            toast.error(`Không thể tải model ${modelType}`);
        } finally {
            setIsLoadingModels(false);
        }
    };

    const handleUnloadModel = async (modelType) => {
        setIsLoadingModels(true);
        try {
            const response = await aiGeneratorService.unloadModel(modelType);
            if (response.success) {
                // Update specific model status
                if (modelType === 'generative_art') {
                    setGenerativeArt(prev => ({ ...prev, isModelLoaded: false }));
                } else if (modelType === 'generative_video') {
                    setGenerativeVideo(prev => ({ ...prev, isModelLoaded: false }));
                } else if (modelType === 'streaming_generative') {
                    setStreamingGenerative(prev => ({ ...prev, isModelLoaded: false }));
                }

                // Reload model status
                await loadModelStatus();
                toast.success(`Model ${modelType} đã được tắt!`);
            }
        } catch (error) {
            console.error('Error unloading model:', error);
            toast.error(`Không thể tắt model ${modelType}`);
        } finally {
            setIsLoadingModels(false);
        }
    };

    const handleClearAllModels = async () => {
        setIsLoadingModels(true);
        try {
            const response = await aiGeneratorService.clearAllModels();
            if (response.success) {
                // Reset all model states
                setGenerativeArt(prev => ({ ...prev, isModelLoaded: false }));
                setGenerativeVideo(prev => ({ ...prev, isModelLoaded: false }));
                setStreamingGenerative(prev => ({ ...prev, isModelLoaded: false }));

                // Reload model status
                await loadModelStatus();
                toast.success('Đã xóa tất cả models!');
            }
        } catch (error) {
            console.error('Error clearing all models:', error);
            toast.error('Không thể xóa tất cả models');
        } finally {
            setIsLoadingModels(false);
        }
    };

    const handleGenerateArt = async () => {
        if (!generativeArt.prompt.trim()) {
            toast.error('Vui lòng nhập prompt để tạo hình ảnh');
            return;
        }

        if (!generativeArt.isModelLoaded) {
            toast.error('Vui lòng tải model Generative Art trước');
            return;
        }

        setGenerativeArt(prev => ({ ...prev, isGenerating: true }));

        try {
            const response = await aiGeneratorService.generateArt(generativeArt.prompt);
            if (response.success) {
                setGenerativeArt(prev => ({
                    ...prev,
                    result: response,
                    isGenerating: false
                }));
                toast.success('Hình ảnh đã được tạo thành công!');
            } else {
                throw new Error(response.message);
            }
        } catch (error) {
            console.error('Error generating art:', error);
            setGenerativeArt(prev => ({ ...prev, isGenerating: false }));
            toast.error('Không thể tạo hình ảnh');
        }
    };

    const handleGenerateVideo = async () => {
        if (!generativeVideo.prompt.trim()) {
            toast.error('Vui lòng nhập prompt để tạo video');
            return;
        }

        if (!generativeVideo.isModelLoaded) {
            toast.error('Vui lòng tải model Generative Video trước');
            return;
        }

        setGenerativeVideo(prev => ({ ...prev, isGenerating: true }));

        try {
            const response = await aiGeneratorService.generateVideo(generativeVideo.prompt);
            if (response.success) {
                setGenerativeVideo(prev => ({
                    ...prev,
                    result: response,
                    isGenerating: false
                }));
                toast.success('Video đã được tạo thành công!');
            } else {
                throw new Error(response.message);
            }
        } catch (error) {
            console.error('Error generating video:', error);
            setGenerativeVideo(prev => ({ ...prev, isGenerating: false }));
            toast.error('Không thể tạo video');
        }
    };

    const handleStreamingGenerate = async () => {
        if (!streamingGenerative.prompt.trim()) {
            return;
        }

        setStreamingGenerative(prev => ({ ...prev, isGenerating: true }));

        try {
            const response = await aiGeneratorService.generateStreaming(streamingGenerative.prompt);
            if (response.success) {
                setStreamingGenerative(prev => ({
                    ...prev,
                    result: response,
                    isGenerating: false
                }));
            } else {
                throw new Error(response.message);
            }
        } catch (error) {
            console.error('Error generating streaming image:', error);
            setStreamingGenerative(prev => ({ ...prev, isGenerating: false }));
        }
    };

    const downloadImage = (base64Data, filename) => {
        try {
            const link = document.createElement('a');
            link.href = `data:image/png;base64,${base64Data}`;
            link.download = filename;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            toast.success('Hình ảnh đã được tải xuống!');
        } catch (error) {
            console.error('Error downloading image:', error);
            toast.error('Không thể tải xuống hình ảnh');
        }
    };

    const downloadVideoFromUrl = async (videoUrl, filename) => {
        try {
            const response = await fetch(`http://localhost:8000${videoUrl}`);
            if (!response.ok) {
                throw new Error('Failed to fetch video');
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = filename;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            window.URL.revokeObjectURL(url);
            toast.success('Video đã được tải xuống!');
        } catch (error) {
            console.error('Error downloading video from URL:', error);
            toast.error('Không thể tải xuống video');
        }
    };

    return (
        <div className="space-y-6">
            {/* Header */}
            <PageHeader
                title="AI Generator"
                description="Bộ công cụ AI tạo sinh - Tạo hình ảnh, video và streaming với AI"
                icon={<Sparkles className="w-6 h-6" />}
            />

            {/* Model Status */}
            <ModelStatusCard
                modelStatus={modelStatus}
                isLoadingModels={isLoadingModels}
                onClearAllModels={handleClearAllModels}
            />

            {/* Main Layout */}
            <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
                {/* Main Content */}
                <div className="xl:col-span-2 order-1 xl:order-1 space-y-8">
                    {/* Generative Art Section */}
                    <GenerativeArtSection
                        generativeArt={generativeArt}
                        setGenerativeArt={setGenerativeArt}
                        onGenerate={handleGenerateArt}
                        onDownloadImage={downloadImage}
                        onLoadModel={handleLoadModel}
                        onUnloadModel={handleUnloadModel}
                        isLoadingModels={isLoadingModels}
                    />

                    {/* Generative Video Section */}
                    <GenerativeVideoSection
                        generativeVideo={generativeVideo}
                        setGenerativeVideo={setGenerativeVideo}
                        onGenerate={handleGenerateVideo}
                        onDownloadVideo={downloadVideoFromUrl}
                        onLoadModel={handleLoadModel}
                        onUnloadModel={handleUnloadModel}
                        isLoadingModels={isLoadingModels}
                    />

                    {/* Streaming Generative Section */}
                    <StreamingGenerativeSection
                        streamingGenerative={streamingGenerative}
                        setStreamingGenerative={setStreamingGenerative}
                        onDownloadImage={downloadImage}
                        onLoadModel={handleLoadModel}
                        onUnloadModel={handleUnloadModel}
                        isLoadingModels={isLoadingModels}
                    />
                </div>

                {/* Sidebar - AI Introduction */}
                <div className="xl:col-span-1 order-2 xl:order-2">
                    <AIIntroduction />
                </div>
            </div>
        </div>
    );
};

export default AIGenerator;