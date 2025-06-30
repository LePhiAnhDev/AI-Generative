import React from 'react';
import { motion } from 'framer-motion';
import { Video, Send, Download, Loader2, AlertCircle } from 'lucide-react';
import Card from '../common/Card';
import Button from '../common/Button';
import ModelToggleButton from './ModelToggleButton';

/**
 * Generative Video Section - Tạo video với AI
 */
const GenerativeVideoSection = ({
    generativeVideo,
    setGenerativeVideo,
    onGenerate,
    onDownloadVideo,
    onLoadModel,
    onUnloadModel,
    isLoadingModels
}) => {
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
        >
            <Card variant="glass" className="border-slate-700/50">
                <div className="space-y-6">
                    {/* Section Header */}
                    <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                            <div className="p-3 bg-violet-600/20 rounded-xl border border-violet-500/30">
                                <Video className="w-6 h-6 text-violet-400" />
                            </div>
                            <div>
                                <h2 className="text-2xl font-bold text-white">Generative Video</h2>
                                <p className="text-slate-300">Tạo video với AnimateDiff-Lightning + epiCRealism</p>
                            </div>
                        </div>
                        <ModelToggleButton
                            modelType="generative_video"
                            isLoaded={generativeVideo.isModelLoaded}
                            onLoad={onLoadModel}
                            onUnload={onUnloadModel}
                            isLoading={isLoadingModels}
                        />
                    </div>

                    {/* Result Display */}
                    <div className="bg-slate-800/50 rounded-xl p-4 min-h-[500px] flex items-center justify-center border border-slate-700/30">
                        {generativeVideo.isGenerating ? (
                            <div className="text-center">
                                <Loader2 className="w-12 h-12 animate-spin text-violet-400 mx-auto mb-4" />
                                <p className="text-violet-400 font-medium">Đang tạo video...</p>
                                <p className="text-slate-400 text-sm mt-2">Quá trình này có thể mất nhiều thời gian</p>
                            </div>
                        ) : generativeVideo.result ? (
                            <video
                                src={`http://localhost:8000${generativeVideo.result.video_url}`}
                                controls
                                className="max-w-full max-h-[450px] rounded-lg shadow-lg border border-slate-600/30"
                                autoPlay
                                loop
                                muted
                            />
                        ) : (
                            <div className="text-center text-slate-400">
                                <Video className="w-16 h-16 mx-auto mb-4 opacity-50" />
                                <p>Video được tạo sẽ hiển thị ở đây</p>
                            </div>
                        )}
                    </div>

                    {/* Result Actions - Moved outside display area */}
                    {generativeVideo.result && (
                        <div className="flex items-center justify-center space-x-4 pt-3 border-t border-slate-700/30">
                            <Button
                                onClick={() => onDownloadVideo(generativeVideo.result.video_url, 'generated-video.mp4')}
                                variant="primary"
                                size="sm"
                            >
                                <Download className="w-4 h-4 mr-2" />
                                Tải xuống
                            </Button>
                            <p className="text-sm text-slate-400">
                                Thời gian tạo: {generativeVideo.result.processing_time?.toFixed(2)}s
                            </p>
                            <p className="text-sm text-slate-400">
                                {generativeVideo.result.num_frames} frames @ {generativeVideo.result.fps} FPS
                            </p>
                        </div>
                    )}

                    {/* Input Area */}
                    <div className="space-y-4">
                        <div className="flex space-x-4 items-start">
                            <textarea
                                value={generativeVideo.prompt}
                                onChange={(e) => setGenerativeVideo(prev => ({ ...prev, prompt: e.target.value }))}
                                placeholder="Nhập prompt để tạo video..."
                                className="flex-1 px-4 py-3 bg-slate-900/50 border border-slate-600/50 rounded-xl focus:outline-none focus:ring-2 focus:ring-violet-500/50 focus:border-violet-500/50 text-white placeholder-slate-400 resize-none min-h-[48px] max-h-[120px]"
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
                                disabled={generativeVideo.isGenerating || !generativeVideo.isModelLoaded}
                                variant="primary"
                                className="min-h-[48px] px-6"
                            >
                                {generativeVideo.isGenerating ? (
                                    <Loader2 className="w-4 h-4 animate-spin mr-2" />
                                ) : (
                                    <Send className="w-4 h-4 mr-2" />
                                )}
                                Tạo video
                            </Button>
                        </div>
                        {!generativeVideo.isModelLoaded && (
                            <p className="text-amber-400 text-sm flex items-center">
                                <AlertCircle className="w-4 h-4 mr-2" />
                                Vui lòng tải model Generative Video để sử dụng tính năng này
                            </p>
                        )}
                    </div>
                </div>
            </Card>
        </motion.div>
    );
};

export default GenerativeVideoSection;