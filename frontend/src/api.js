import axios from 'axios';
import endpointsConfig from "./config/endpointsConfig";

const api = axios.create({
    baseURL: `${endpointsConfig.apiBaseUrl}`,
});

// Добавляем interceptor для автоматической вставки токена
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    console.log("1")
    if (!config.url) {
        return config;
    }
    console.log(2)
    const currentUrl = new URL(config.url, config.baseURL);
    Object.entries(config.urlParams || {}).forEach(([
        k,
        v
    ]) => {
        currentUrl.pathname = currentUrl.pathname.replace(`:${k}`, encodeURIComponent(v));
    });
    console.log(currentUrl.pathname, config.urlParams)

    return {
        ...config,
        baseUrl: config.baseURL,
        url: currentUrl.pathname,
    };
});

export default api;
