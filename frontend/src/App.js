import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import ChatsPage  from "./pages/ChatsPage";
import { Layout } from './components/Layout';



import React, { useEffect } from 'react';
import {BrowserRouter as Router, Routes, Route, useNavigate, useLocation} from 'react-router-dom';
import api from './api';
import {ChakraProvider} from "@chakra-ui/react";
import { Button, Flex, Box } from '@chakra-ui/react';
import {QueryClient, QueryClientProvider} from "react-query";


export const AuthWrapper = ({ children }) => {
    const navigate = useNavigate();
    const location = useLocation();

    useEffect(() => {
        const token = localStorage.getItem('access_token');
        const isAuthPage = ['/login', '/register'].includes(location.pathname);

        if (!token && !isAuthPage) {
            navigate('/login');
        } else if (token && isAuthPage) {
            navigate('/chats');
        }
    }, [navigate, location.pathname]);

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

                                        <Route path="/chats" element={<ChatsPage />} />


                                    <Route path="*" element={<LoginPage />} />
                                </Routes>
                        </AuthWrapper>
                    </Router>
            </ChakraProvider>
        </QueryClientProvider>
    );
}

export default App;
