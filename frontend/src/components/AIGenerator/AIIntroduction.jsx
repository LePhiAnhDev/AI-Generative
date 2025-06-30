import React from 'react';
import { motion } from 'framer-motion';
import { Lightbulb, AlertTriangle, CheckCircle, Sparkles, Cpu, Zap } from 'lucide-react';
import Card from '../common/Card';

/**
 * AI Introduction - Giới thiệu về AI, vấn đề và giải pháp
 */
const AIIntroduction = () => {
    return (
        <div className="space-y-6">
            {/* Giới thiệu */}
            <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.5 }}
            >
                <Card variant="glass" className="border-slate-700/50">
                    <div className="space-y-4">
                        <div className="flex items-center space-x-3">
                            <div className="p-2 bg-blue-600/20 rounded-lg border border-blue-500/30">
                                <Lightbulb className="w-5 h-5 text-blue-400" />
                            </div>
                            <h3 className="text-lg font-semibold text-white">Giới thiệu</h3>
                        </div>
                        <div className="text-sm text-slate-300 space-y-3">
                            <p>
                                AI tạo sinh (Generative AI) đang là xu hướng công nghệ hàng đầu thế giới,
                                mở ra những khả năng sáng tạo vô hạn trong việc tạo ra nội dung số.
                            </p>
                            <p>
                                Từ hình ảnh nghệ thuật đến video chuyên nghiệp, AI đã trở thành công cụ
                                không thể thiếu trong kỷ nguyên số hóa hiện tại.
                            </p>
                        </div>
                    </div>
                </Card>
            </motion.div>

            {/* Vấn đề */}
            <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.5, delay: 0.1 }}
            >
                <Card variant="glass" className="border-slate-700/50">
                    <div className="space-y-4">
                        <div className="flex items-center space-x-3">
                            <div className="p-2 bg-amber-600/20 rounded-lg border border-amber-500/30">
                                <AlertTriangle className="w-5 h-5 text-amber-400" />
                            </div>
                            <h3 className="text-lg font-semibold text-white">Vấn đề</h3>
                        </div>
                        <div className="text-sm text-slate-300 space-y-3">
                            <div className="flex items-start space-x-2">
                                <div className="w-1.5 h-1.5 bg-amber-400 rounded-full mt-2 flex-shrink-0"></div>
                                <p>AI đang phát triển nhanh chóng và trở thành xu hướng không thể bỏ qua</p>
                            </div>
                            <div className="flex items-start space-x-2">
                                <div className="w-1.5 h-1.5 bg-amber-400 rounded-full mt-2 flex-shrink-0"></div>
                                <p>Nổi bật nhất hiện nay là AI tạo sinh như Midjourney, Runway, Veo và DALL-E</p>
                            </div>
                            <div className="flex items-start space-x-2">
                                <div className="w-1.5 h-1.5 bg-amber-400 rounded-full mt-2 flex-shrink-0"></div>
                                <p>Sinh viên muốn tiếp cận nhưng gặp khó khăn về phần cứng, chi phí và kiến thức kỹ thuật</p>
                            </div>
                            <div className="flex items-start space-x-2">
                                <div className="w-1.5 h-1.5 bg-amber-400 rounded-full mt-2 flex-shrink-0"></div>
                                <p>Việc truy cập vào các công cụ AI tạo sinh chuyên nghiệp thường tốn kém và phức tạp</p>
                            </div>
                        </div>
                    </div>
                </Card>
            </motion.div>

            {/* Giải pháp */}
            <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.5, delay: 0.2 }}
            >
                <Card variant="glass" className="border-slate-700/50">
                    <div className="space-y-4">
                        <div className="flex items-center space-x-3">
                            <div className="p-2 bg-emerald-600/20 rounded-lg border border-emerald-500/30">
                                <CheckCircle className="w-5 h-5 text-emerald-400" />
                            </div>
                            <h3 className="text-lg font-semibold text-white">Giải pháp</h3>
                        </div>
                        <div className="text-sm text-slate-300 space-y-3">
                            <div className="flex items-start space-x-2">
                                <div className="w-1.5 h-1.5 bg-emerald-400 rounded-full mt-2 flex-shrink-0"></div>
                                <p>Cung cấp 3 chế độ AI tạo sinh khác nhau phù hợp với nhiều nhu cầu</p>
                            </div>
                            <div className="space-y-2 ml-4">
                                <div className="flex items-center space-x-2 text-xs">
                                    <Sparkles className="w-3 h-3 text-blue-400" />
                                    <span className="text-blue-300">Generative Art - Tạo hình ảnh nghệ thuật chất lượng cao</span>
                                </div>
                                <div className="flex items-center space-x-2 text-xs">
                                    <Cpu className="w-3 h-3 text-violet-400" />
                                    <span className="text-violet-300">Generative Video - Tạo video chuyên nghiệp từ text</span>
                                </div>
                                <div className="flex items-center space-x-2 text-xs">
                                    <Zap className="w-3 h-3 text-emerald-400" />
                                    <span className="text-emerald-300">Streaming Mode - Tạo hình ảnh thời gian thực</span>
                                </div>
                            </div>
                            <div className="flex items-start space-x-2">
                                <div className="w-1.5 h-1.5 bg-emerald-400 rounded-full mt-2 flex-shrink-0"></div>
                                <p>Giao diện thân thiện, dễ sử dụng cho người mới bắt đầu</p>
                            </div>
                            <div className="flex items-start space-x-2">
                                <div className="w-1.5 h-1.5 bg-emerald-400 rounded-full mt-2 flex-shrink-0"></div>
                                <p>Tích hợp sẵn các model AI mạnh mẽ và tối ưu hóa hiệu suất</p>
                            </div>
                        </div>
                    </div>
                </Card>
            </motion.div>
        </div>
    );
};

export default AIIntroduction;