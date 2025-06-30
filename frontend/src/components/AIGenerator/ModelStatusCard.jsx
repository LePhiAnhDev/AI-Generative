import React from 'react';
import { Loader2, Trash2 } from 'lucide-react';
import Card from '../common/Card';
import Button from '../common/Button';

/**
 * Model Status Card - Hiển thị trạng thái bộ nhớ GPU và các model đang hoạt động
 */
const ModelStatusCard = ({ modelStatus, isLoadingModels, onClearAllModels }) => {
    return (
        <Card variant="glass" className="border-slate-700/50">
            <div className="flex items-center justify-between">
                <div>
                    <h3 className="text-lg font-semibold text-white">Trạng thái Model AI</h3>
                    {modelStatus.memory_usage_mb ? (
                        <p className="text-slate-300">
                            Đang sử dụng: {Math.round(modelStatus.memory_usage_mb)} MB GPU
                        </p>
                    ) : (
                        <p className="text-slate-400">
                            Chưa có thông tin bộ nhớ
                        </p>
                    )}
                </div>
                <div className="flex items-center gap-4">
                    <div className="text-right">
                        <p className="text-sm text-slate-400">
                            Models đang hoạt động: {modelStatus.loaded_models?.length || 0}
                        </p>
                    </div>
                    <Button
                        onClick={onClearAllModels}
                        disabled={isLoadingModels}
                        variant="danger"
                        size="sm"
                    >
                        {isLoadingModels ? (
                            <Loader2 className="w-4 h-4 animate-spin mr-2" />
                        ) : (
                            <Trash2 className="w-4 h-4 mr-2" />
                        )}
                        Clear All
                    </Button>
                </div>
            </div>
        </Card>
    );
};

export default ModelStatusCard;