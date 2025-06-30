import React from 'react';
import { Power, PowerOff, Loader2 } from 'lucide-react';
import Button from '../common/Button';

/**
 * Model Toggle Button - Nút để bật/tắt model
 */
const ModelToggleButton = ({ modelType, isLoaded, onLoad, onUnload, isLoading }) => (
    <Button
        onClick={isLoaded ? () => onUnload(modelType) : () => onLoad(modelType)}
        disabled={isLoading}
        variant={isLoaded ? "success" : "primary"}
        size="sm"
        className="min-w-[120px]"
    >
        {isLoading ? (
            <Loader2 className="w-4 h-4 animate-spin mr-2" />
        ) : isLoaded ? (
            <PowerOff className="w-4 h-4 mr-2" />
        ) : (
            <Power className="w-4 h-4 mr-2" />
        )}
        {isLoaded ? 'Tắt Model' : 'Tải Model'}
    </Button>
);

export default ModelToggleButton;