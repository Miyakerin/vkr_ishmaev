const endpointsConfig = {
    apiBaseUrl: process.env.REACT_APP_API_HOSTNAME,
    loginEndpoint: '/api/auth/v1/user/login',
    registerEndpoint: '/api/auth/v1/user/register',
    verifyEndpoint: '/api/auth/v1/user/verify',

    getUserChatsEndpoint: '/api/ai/v1/chat',
    createChatEndpoint: '/api/ai/v1/chat',
    getChatHistory: '/api/ai/v1/chat/:chat_id/history',

    sendMessageEndpoint: 'api/ai/v1/chat/:chat_id/message',

    modelsEndpoint: 'api/ai/v1/models'
};

export default endpointsConfig;