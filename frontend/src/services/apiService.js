import axios from 'axios';

const API_URL = 'http://localhost:8000';

const apiService = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// AI Collections endpoints
const aiGeneratorService = {
    // Model management
    getModelStatus: async () => {
        try {
            const response = await apiService.get('/models/status');
            return response.data;
        } catch (error) {
            console.error('Error getting model status:', error);
            throw error;
        }
    },

    loadModel: async (modelType) => {
        try {
            const response = await apiService.post('/models/load', {
                model_type: modelType,
                force_reload: false,
            });
            return response.data;
        } catch (error) {
            console.error(`Error loading model ${modelType}:`, error);
            throw error;
        }
    },

    unloadModel: async (modelType) => {
        try {
            const response = await apiService.post('/models/unload', {
                model_type: modelType,
            });
            return response.data;
        } catch (error) {
            console.error(`Error unloading model ${modelType}:`, error);
            throw error;
        }
    },

    clearAllModels: async () => {
        try {
            const response = await apiService.post('/models/clear-all');
            return response.data;
        } catch (error) {
            console.error('Error clearing all models:', error);
            throw error;
        }
    },

    // Generation endpoints
    generateArt: async (prompt) => {
        try {
            const response = await apiService.post('/generate-art', {
                prompt,
                num_inference_steps: 70,
                guidance_scale: 5.0,
                width: 512,
                height: 512,
            });
            return response.data;
        } catch (error) {
            console.error('Error generating art:', error);
            throw error;
        }
    },

    generateVideo: async (prompt) => {
        try {
            const response = await apiService.post('/generate-video', {
                prompt,
                num_frames: 32,
                guidance_scale: 1.0,
                num_inference_steps: 4,
                width: 512,
                height: 512,
            });
            return response.data;
        } catch (error) {
            console.error('Error generating video:', error);
            throw error;
        }
    },

    generateStreaming: async (prompt) => {
        try {
            const response = await apiService.post('/generate-streaming', {
                prompt,
                num_inference_steps: 2,
                guidance_scale: 0.0,
                width: 512,
                height: 512,
            });
            return response.data;
        } catch (error) {
            console.error('Error generating streaming image:', error);
            throw error;
        }
    },
};

export default aiGeneratorService;