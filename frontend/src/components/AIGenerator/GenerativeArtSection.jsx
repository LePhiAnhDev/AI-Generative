import React from 'react';
import { motion } from 'framer-motion';
import { Image as ImageIcon, Send, Download, Loader2, AlertCircle } from 'lucide-react';
import Card from '../common/Card';
import Button from '../common/Button';
import ModelToggleButton from './ModelToggleButton';

/**
 * Generative Art Section - Tạo hình ảnh nghệ thuật với AI
 */
const GenerativeArtSection = ({
    generativeArt,
    setGenerativeArt,
    onGenerate,
    onDownloadImage,
    onLoadModel,
    onUnloadModel,
    isLoadingModels
}) => {
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
        >
            <Card variant="glass" className="border-slate-700/50">
                <div className="space-y-6">
                    {/* Section Header */}
                    <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                            <div className="p-3 bg-blue-600/20 rounded-xl border border-blue-500/30">
                                <ImageIcon className="w-6 h-6 text-blue-400" />
                            </div>
                            <div>
                                <h2 className="text-2xl font-bold text-white">Generative Art</h2>
                                <p className="text-slate-300">Tạo hình ảnh nghệ thuật với prompthero/openjourney</p>
                            </div>
                        </div>
                        <ModelToggleButton
                            modelType="generative_art"
                            isLoaded={generativeArt.isModelLoaded}
                            onLoad={onLoadModel}
                            onUnload={onUnloadModel}
                            isLoading={isLoadingModels}
                        />
                    </div>

                    {/* Result Display */}
                    <div className="bg-slate-800/50 rounded-xl p-4 min-h-[500px] flex items-center justify-center border border-slate-700/30">
                        {generativeArt.isGenerating ? (
                            <div className="text-center">
                                <Loader2 className="w-12 h-12 animate-spin text-blue-400 mx-auto mb-4" />
                                <p className="text-blue-400 font-medium">Đang tạo hình ảnh...</p>
                                <p className="text-slate-400 text-sm mt-2">Quá trình này có thể mất vài phút</p>
                            </div>
                        ) : generativeArt.result ? (
                            <img
                                src={`data:image/png;base64,${generativeArt.result.image_base64}`}
                                alt="Generated Art"
                                className="max-w-full max-h-[450px] rounded-lg shadow-lg border border-slate-600/30 object-contain"
                            />
                        ) : (
                            <div className="text-center text-slate-400">
                                <ImageIcon className="w-16 h-16 mx-auto mb-4 opacity-50" />
                                <p>Hình ảnh được tạo sẽ hiển thị ở đây</p>
                            </div>
                        )}
                    </div>

                    {/* Result Actions - Moved outside display area */}
                    {generativeArt.result && (
                        <div className="flex items-center justify-center space-x-4 pt-3 border-t border-slate-700/30">
                            <Button
                                onClick={() => onDownloadImage(generativeArt.result.image_base64, 'generated-art.png')}
                                variant="primary"
                                size="sm"
                            >
                                <Download className="w-4 h-4 mr-2" />
                                Tải xuống
                            </Button>
                            <p className="text-sm text-slate-400">
                                Thời gian tạo: {generativeArt.result.processing_time?.toFixed(2)}s
                            </p>
                        </div>
                    )}

                    {/* Input Area */}
                    <div className="space-y-4">
                        <div className="flex space-x-4 items-start">
                            <textarea
                                value={generativeArt.prompt}
                                onChange={(e) => setGenerativeArt(prev => ({ ...prev, prompt: e.target.value }))}
                                placeholder="Nhập prompt để tạo hình ảnh nghệ thuật..."
                                className="flex-1 px-4 py-3 bg-slate-900/50 border border-slate-600/50 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 text-white placeholder-slate-400 resize-none min-h-[48px] max-h-[120px]"
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
                            <Button
                                onClick={onGenerate}
                                disabled={generativeArt.isGenerating || !generativeArt.isModelLoaded}
                                variant="primary"
                                className="min-h-[48px] px-6"
                            >
                                {generativeArt.isGenerating ? (
                                    <Loader2 className="w-4 h-4 animate-spin mr-2" />
                                ) : (
                                    <Send className="w-4 h-4 mr-2" />
                                )}
                                Tạo hình ảnh
                            </Button>
                        </div>
                        {!generativeArt.isModelLoaded && (
                            <p className="text-amber-400 text-sm flex items-center">
                                <AlertCircle className="w-4 h-4 mr-2" />
                                Vui lòng tải model Generative Art để sử dụng tính năng này
                            </p>
                        )}
                    </div>
                </div>
            </Card>
        </motion.div>
    );
};

export default GenerativeArtSection;