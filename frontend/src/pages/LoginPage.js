import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import endpointsConfig from '../config/endpointsConfig';
import axios from "axios";
import { Box, Button, Input, Heading, Text, Link } from '@chakra-ui/react';
import api from "../api";

function LoginPage() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const response = await api.post(
                `${endpointsConfig.loginEndpoint}`,
                {password, username}
            );
            localStorage.setItem('access_token', response.data.access_token);
            axios.defaults.headers.common["Authorization"] = `Bearer ${response.data.access_token}`;
            navigate('/chats');
        } catch (error) {
            alert('Ошибка входа');
        }
    }

    return (
        <Box bg="gray.900" minH="100vh" display="flex" alignItems="center" justifyContent="center">
            <Box bg="gray.800" p={8} borderRadius="lg" width="96">
                <Heading size="lg" color="white" mb={6}>
                    Вход
                </Heading>
                <form onSubmit={handleSubmit}>
                    <Input
                        type="username"
                        placeholder="Username"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        mb={4}
                        bg="gray.700"
                        color="white"
                        required
                    />
                    <Input
                        type="password"
                        placeholder="Пароль"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        mb={6}
                        bg="gray.700"
                        color="white"
                        required
                    />
                    <Button type="submit" colorScheme="blue" width="full">
                        Войти
                    </Button>
                </form>
                <Text mt={4} color="gray.400">
                    Нет аккаунта?{' '}
                    <Link href="/register" color="blue.400">
                        Зарегистрироваться
                    </Link>
                </Text>
            </Box>
        </Box>
    );
};

export default LoginPage;