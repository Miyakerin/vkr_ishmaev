import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import endpointsConfig from '../config/endpointsConfig';
import axios from "axios";
import { Box, Button, Input, Heading, Text, Link, Modal,
    ModalOverlay,
    ModalContent,
    ModalHeader,
    ModalBody,
    ModalFooter,
    useToast,
    Stack,
    FormControl,
    FormLabel} from '@chakra-ui/react';
import api from "../api";

function LoginPage() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [isForgotPasswordModalOpen, setIsForgotPasswordModalOpen] = useState(false);
    const [verificationCode, setVerificationCode] = useState('');
    const [currentStep, setCurrentStep] = useState(1)
    const navigate = useNavigate();
    const toast = useToast();

    const handleForgotPassword = async () => {
        try {
            const response = await api.post(
                endpointsConfig.forgotPasswordEndpoint,
                {
                    username: username
                }
            );

            setCurrentStep(2);
            toast({
                title: 'Код отправлен',
                description: 'На вашу почту отправлен код подтверждения',
                status: 'success',
                duration: 5000,
                isClosable: true,
            });
        } catch (error) {
            toast({
                title: 'Ошибка сети',
                description: 'Не удалось подключиться к серверу',
                status: 'error',
                duration: 5000,
                isClosable: true,
            });
        }
    };

    const handleVerifyCode = async () => {
        try {
            const response = await api.post(
                endpointsConfig.restorePasswordEndpoint, {
                    username: username,
                    code: verificationCode
            });

            toast({
                title: 'Код подтвержден',
                description: 'Новый пароль отправлен на почту',
                status: 'success',
                duration: 5000,
                isClosable: true,
            });
            setCurrentStep(3);
        } catch (error) {
            toast({
                title: 'Ошибка сети',
                description: 'Не удалось подключиться к серверу',
                status: 'error',
                duration: 5000,
                isClosable: true,
            });
        }
    };

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
                    <Stack>
                    Нет аккаунта?{' '}
                    <Link href="/register" color="blue.400">
                        Зарегистрироваться
                    </Link>
                    <Link
                        color="blue.500"
                        onClick={() => {
                            setIsForgotPasswordModalOpen(true);
                        }}
                    >
                        Забыли пароль?
                    </Link>
                    </Stack>
                </Text>
            </Box>
            <Modal
                isOpen={isForgotPasswordModalOpen}
                onClose={() => {
                    setIsForgotPasswordModalOpen(false);
                    setCurrentStep(1);
                    setVerificationCode("");
                }}
            >
                <ModalOverlay />
                <ModalContent>
                    <ModalHeader>
                        {currentStep === 1 && 'Восстановление пароля'}
                        {currentStep === 2 && 'Введите код подтверждения'}
                    </ModalHeader>

                    <ModalBody>
                        {currentStep === 1 && (
                            <>
                                <Text mb={4}>
                                    Введите логин, на который зарегистрирован ваш аккаунт.
                                    Мы отправим код подтверждения.
                                </Text>
                                <Input
                                    placeholder="Ваш email"
                                    value={username}
                                    onChange={(e) => setUsername(e.target.value)}
                                    type="text"
                                />
                            </>
                        )}

                        {currentStep === 2 && (
                            <>
                                <Text mb={4}>
                                    Мы отправили 6-значный код на {username}. Введите его ниже:
                                </Text>
                                <Input
                                    placeholder="Код подтверждения"
                                    value={verificationCode}
                                    onChange={(e) => setVerificationCode(e.target.value)}
                                    maxLength={6}
                                />
                            </>
                        )}
                        {
                            currentStep === 3 && (
                                <>
                                    <Text mb={4}>
                                        Пароль отправлен на почту!
                                    </Text>
                                </>
                            )
                        }

                    </ModalBody>

                    <ModalFooter>
                        {currentStep === 1 && (
                            <Button
                                colorScheme="blue"
                                onClick={handleForgotPassword}
                                isDisabled={!username}
                            >
                                Отправить код
                            </Button>
                        )}

                        {currentStep === 2 && (
                            <Button
                                colorScheme="blue"
                                onClick={handleVerifyCode}
                                isDisabled={verificationCode.length !== 6}
                            >
                                Подтвердить
                            </Button>
                        )}
                    </ModalFooter>
                </ModalContent>
            </Modal>
        </Box>
    );
};

export default LoginPage;