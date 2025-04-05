import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import ChatListPage from "./pages/ChatListPage";
import ChatPage from "./pages/ChatPage";



import React, { useEffect } from 'react';
import {BrowserRouter as Router, Routes, Route, useNavigate, useLocation} from 'react-router-dom';
import api from './api';
import {ChakraProvider} from "@chakra-ui/react";
import {QueryClient, QueryClientProvider} from "react-query";

const AuthWrapper = ({ children }) => {
    const navigate = useNavigate();
    const location = useLocation();

    useEffect(() => {
        const token = localStorage.getItem('access_token');
        if (!token && location.pathname !== '/register') {
            navigate('/login');
        } else {
            api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
            navigate('/chats')
        }
    }, [navigate]);

    return children;
};
const queryClient = new QueryClient();
function App() {
    return (
        <QueryClientProvider client={queryClient}>
            <ChakraProvider>
                    <Router>
                        <AuthWrapper>
                            <Routes>
                                <Route path="/login" element={<LoginPage />} />
                                <Route path="/register" element={<RegisterPage />} />
                                <Route path="/chats" element={<ChatListPage />} />
                                <Route path="/chats/:id" element={<ChatPage />} />
                                <Route path="*" element={<LoginPage />} /> {/* Дефолтный редирект */}
                            </Routes>
                        </AuthWrapper>
                    </Router>
            </ChakraProvider>
        </QueryClientProvider>
    );
}

export default App;
