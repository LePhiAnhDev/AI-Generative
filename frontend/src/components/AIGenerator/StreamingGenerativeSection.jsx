import React from 'react';
import { motion } from 'framer-motion';
import { Zap, Download, Loader2, AlertCircle, CheckCircle, Clock } from 'lucide-react';
import Card from '../common/Card';
import Button from '../common/Button';
import ModelToggleButton from './ModelToggleButton';

/**
 * Streaming Generative Section - Tạo hình ảnh streaming theo thời gian thực
 */
const StreamingGenerativeSection = ({
    streamingGenerative,
    setStreamingGenerative,
    onDownloadImage,
    onLoadModel,
    onUnloadModel,
    isLoadingModels
}) => {
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
        >
            <Card variant="glass" className="border-slate-700/50">
                <div className="space-y-6">
                    {/* Section Header */}
                    <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                            <div className="p-3 bg-emerald-600/20 rounded-xl border border-emerald-500/30">
                                <Zap className="w-6 h-6 text-emerald-400" />
                            </div>
                            <div>
                                <h2 className="text-2xl font-bold text-white">Streaming Generative Art</h2>
                                <p className="text-slate-300">Tạo hình ảnh theo thời gian thực với SDXL-Turbo</p>
                            </div>
                        </div>
                        <ModelToggleButton
                            modelType="streaming_generative"
                            isLoaded={streamingGenerative.isModelLoaded}
                            onLoad={onLoadModel}
                            onUnload={onUnloadModel}
                            isLoading={isLoadingModels}
                        />
                    </div>

                    {/* Result Display */}
                    <div className="bg-slate-800/50 rounded-xl p-4 min-h-[500px] flex items-center justify-center border border-slate-700/30">
                        {streamingGenerative.isGenerating ? (
                            <div className="text-center">
                                <Loader2 className="w-12 h-12 animate-spin text-emerald-400 mx-auto mb-4" />
                                <p className="text-emerald-400 font-medium">Đang tạo hình ảnh streaming...</p>
                                <p className="text-slate-400 text-sm mt-2">Tạo nhanh trong vài giây</p>
                            </div>
                        ) : streamingGenerative.result ? (
                            <img
                                src={`data:image/png;base64,${streamingGenerative.result.image_base64}`}
                                alt="Streaming Generated Art"
                                className="max-w-full max-h-[450px] rounded-lg shadow-lg border border-slate-600/30 object-contain"
                            />
                        ) : (
                            <div className="text-center text-slate-400">
                                <Zap className="w-16 h-16 mx-auto mb-4 opacity-50" />
                                <p>Hình ảnh streaming sẽ hiển thị ở đây</p>
                                <p className="text-sm mt-2">Tự động tạo sau 1.5s khi bạn ngừng gõ</p>
                            </div>
                        )}
                    </div>

                    {/* Result Actions - Moved outside display area */}
                    {streamingGenerative.result && (
                        <div className="flex items-center justify-center space-x-4 pt-3 border-t border-slate-700/30">
                            <Button
                                onClick={() => onDownloadImage(streamingGenerative.result.image_base64, 'streaming-art.png')}
                                variant="primary"
                                size="sm"
                            >
                                <Download className="w-4 h-4 mr-2" />
                                Tải xuống
                            </Button>
                            <p className="text-sm text-slate-400">
                                Thời gian tạo: {streamingGenerative.result.processing_time?.toFixed(2)}s
                            </p>
                        </div>
                    )}

                    {/* Input Area */}
                    <div className="space-y-4">
                        <div className="relative">
                            <textarea
                                value={streamingGenerative.prompt}
                                onChange={(e) => setStreamingGenerative(prev => ({ ...prev, prompt: e.target.value }))}
                                placeholder="Gõ prompt để tạo hình ảnh streaming theo thời gian thực..."
                                className="w-full px-4 py-3 bg-slate-900/50 border border-slate-600/50 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500/50 text-white placeholder-slate-400 pr-12 resize-none min-h-[48px] max-h-[120px]"
                                rows="1"
                                style={{
                                    height: 'auto',
                                    minHeight: '48px'
                                }}
                                onInput={(e) => {
                                    e.target.style.height = 'auto';
                                    e.target.style.height = Math.min(e.target.scrollHeight, 120) + 'px';
                                }}
                            />
                            <div className="absolute right-3 top-[13px]">
                                {streamingGenerative.isGenerating ? (
                                    <Loader2 className="w-5 h-5 animate-spin text-emerald-400" />
                                ) : streamingGenerative.isModelLoaded ? (
                                    <CheckCircle className="w-5 h-5 text-emerald-400" />
                                ) : (
                                    <Clock className="w-5 h-5 text-slate-500" />
                                )}
                            </div>
                        </div>
                        <div className="flex items-center justify-between text-sm">
                            {streamingGenerative.isModelLoaded ? (
                                <p className="text-emerald-400 flex items-center">
                                    <CheckCircle className="w-4 h-4 mr-2" />
                                    Streaming đang hoạt động - tự động tạo sau 1.5s
                                </p>
                            ) : (
                                <p className="text-amber-400 flex items-center">
                                    <AlertCircle className="w-4 h-4 mr-2" />
                                    Vui lòng tải model Streaming Generative để sử dụng tính năng này
                                </p>
                            )}
                        </div>
                    </div>
                </div>
            </Card>
        </motion.div>
    );
};

export default StreamingGenerativeSection;