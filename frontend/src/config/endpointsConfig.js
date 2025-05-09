const endpointsConfig = {
    apiBaseUrl: process.env.REACT_APP_API_HOSTNAME,
    loginEndpoint: '/api/auth/v1/user/login',
    registerEndpoint: '/api/auth/v1/user/register',
    verifyEndpoint: '/api/auth/v1/user/verify',
    verifyEmailEndpoint: '/api/auth/v1/user/verify_email',
    resendEmailEndpoint: '/api/auth/v1/user/email_code',
    forgotPasswordEndpoint: '/api/auth/v1/user/forget_password',
    restorePasswordEndpoint: '/api/auth/v1/user/restore_password',

    getUserChatsEndpoint: '/api/ai/v1/chat',
    createChatEndpoint: '/api/ai/v1/chat',
    getChatHistory: '/api/ai/v1/chat/:chat_id/history',

    sendMessageEndpoint: 'api/ai/v1/chat/:chat_id/message',

    modelsEndpoint: 'api/ai/v1/models',

    getTokensEndpoint: 'api/ai/v1/tokens',
    addTokensEndpoint: 'api/ai/v1/tokens'
};

export default endpointsConfig;