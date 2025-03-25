const config = {
    apiBaseUrl: process.env.REACT_APP_API_HOSTNAME,
    loginEndpoint: '/api/v1/user/login',
    registerEndpoint: '/api/v1/user/register',
    verifyEndpoint: '/api/v1/user/verify'
};

export default config;