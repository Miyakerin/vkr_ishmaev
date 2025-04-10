import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import endpointsConfig from '../config/endpointsConfig';
import axios from 'axios';
import {
    Box,
    Button,
    Input,
    Heading,
    Text,
    Link,
    FormControl,
    FormLabel,
    FormErrorMessage,
    InputGroup,
    InputRightElement,
    useToast,
} from '@chakra-ui/react';
import { ViewIcon, ViewOffIcon } from '@chakra-ui/icons';
import api from "../api";

const RegisterPage = () => {
    const navigate = useNavigate();
    const toast = useToast();

    // Состояния формы
    const [formData, setFormData] = useState({
        email: '',
        confirmEmail: '',
        password: '',
        confirmPassword: '',
        username: ''
    });

    const [errors, setErrors] = useState({
        email: '',
        confirmEmail: '',
        password: '',
        confirmPassword: '',
        username: ''
    });

    const [showPassword, setShowPassword] = useState(false);
    const [showConfirmPassword, setShowConfirmPassword] = useState(false);
    const [isSubmitting, setIsSubmitting] = useState(false);

    // Валидация email
    const validateEmail = (email) => {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    };

    // Обработчик изменений полей
    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));

        // Валидация в реальном времени
        if (name === 'email') {
            setErrors(prev => ({
                ...prev,
                email: validateEmail(value) ? '' : 'Некорректный email',
                confirmEmail: value === formData.confirmEmail ? '' : 'Email не совпадает'
            }));
        }

        if (name === 'confirmEmail') {
            setErrors(prev => ({
                ...prev,
                confirmEmail: value === formData.email ? '' : 'Email не совпадает'
            }));
        }

        if (name === 'password') {
            setErrors(prev => ({
                ...prev,
                password: value.length >= 6 ? '' : 'Пароль должен быть не менее 6 символов',
                confirmPassword: value === formData.confirmPassword ? '' : 'Пароли не совпадают'
            }));
        }

        if (name === 'confirmPassword') {
            setErrors(prev => ({
                ...prev,
                confirmPassword: value === formData.password ? '' : 'Пароли не совпадают'
            }));
        }
    };

    // Отправка формы
    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsSubmitting(true);

        // Проверка валидности перед отправкой
        const newErrors = {
            email: !formData.email ? 'Введите email' : !validateEmail(formData.email) ? 'Некорректный email' : '',
            confirmEmail: formData.email !== formData.confirmEmail ? 'Email не совпадает' : '',
            password: !formData.password ? 'Введите пароль' : formData.password.length < 6 ? 'Пароль должен быть не менее 6 символов' : '',
            confirmPassword: formData.password !== formData.confirmPassword ? 'Пароли не совпадают' : '',
            username: !formData.username ? 'Введите имя пользователя' : ''
        };

        setErrors(newErrors);

        // Если есть ошибки - не отправляем
        if (Object.values(newErrors).some(error => error)) {
            setIsSubmitting(false);
            return;
        }

        try {
            const response = await api.post(`${endpointsConfig.registerEndpoint}`, {
                email: formData.email,
                password: formData.password,
                username: formData.username
            });

            // Успешная регистрация
            toast({
                title: 'Регистрация успешна',
                description: 'Теперь вы можете войти в систему',
                status: 'success',
                duration: 5000,
                isClosable: true,
            });
            navigate('/login');

        } catch (error) {
            let errorMessage = 'Ошибка регистрации';

            if (error.response) {
                if (error.response.status === 409) {
                    errorMessage = 'Пользователь с таким email уже существует';
                } else {
                    errorMessage = error.response.data.message || errorMessage;
                }
            }

            toast({
                title: 'Ошибка',
                description: errorMessage,
                status: 'error',
                duration: 5000,
                isClosable: true,
            });
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <Box bg="gray.900" minH="100vh" display="flex" alignItems="center" justifyContent="center">
            <Box bg="gray.800" p={8} borderRadius="lg" width="96">
                <Heading size="lg" color="white" mb={6}>
                    Регистрация
                </Heading>

                <form onSubmit={handleSubmit}>
                    {/* Поле имени пользователя */}
                    <FormControl isInvalid={!!errors.username} mb={4}>
                        <FormLabel color="white">Имя пользователя</FormLabel>
                        <Input
                            name="username"
                            type="text"
                            placeholder="Ваше имя"
                            value={formData.username}
                            onChange={handleChange}
                            bg="gray.700"
                            color="white"
                            required
                        />
                        <FormErrorMessage>{errors.username}</FormErrorMessage>
                    </FormControl>

                    {/* Поле email */}
                    <FormControl isInvalid={!!errors.email} mb={4}>
                        <FormLabel color="white">Email</FormLabel>
                        <Input
                            name="email"
                            type="email"
                            placeholder="example@mail.com"
                            value={formData.email}
                            onChange={handleChange}
                            bg="gray.700"
                            color="white"
                            required
                        />
                        <FormErrorMessage>{errors.email}</FormErrorMessage>
                    </FormControl>

                    {/* Поле подтверждения email */}
                    <FormControl isInvalid={!!errors.confirmEmail} mb={4}>
                        <FormLabel color="white">Подтвердите Email</FormLabel>
                        <Input
                            name="confirmEmail"
                            type="email"
                            placeholder="Повторите email"
                            value={formData.confirmEmail}
                            onChange={handleChange}
                            bg="gray.700"
                            color="white"
                            required
                        />
                        <FormErrorMessage>{errors.confirmEmail}</FormErrorMessage>
                    </FormControl>

                    {/* Поле пароля */}
                    <FormControl isInvalid={!!errors.password} mb={4}>
                        <FormLabel color="white">Пароль</FormLabel>
                        <InputGroup>
                            <Input
                                name="password"
                                type={showPassword ? 'text' : 'password'}
                                placeholder="Не менее 6 символов"
                                value={formData.password}
                                onChange={handleChange}
                                bg="gray.700"
                                color="white"
                                required
                            />
                            <InputRightElement>
                                <Button
                                    variant="ghost"
                                    onClick={() => setShowPassword(!showPassword)}
                                    color="gray.400"
                                    _hover={{ bg: 'transparent' }}
                                >
                                    {showPassword ? <ViewOffIcon /> : <ViewIcon />}
                                </Button>
                            </InputRightElement>
                        </InputGroup>
                        <FormErrorMessage>{errors.password}</FormErrorMessage>
                    </FormControl>

                    {/* Поле подтверждения пароля */}
                    <FormControl isInvalid={!!errors.confirmPassword} mb={6}>
                        <FormLabel color="white">Подтвердите пароль</FormLabel>
                        <InputGroup>
                            <Input
                                name="confirmPassword"
                                type={showConfirmPassword ? 'text' : 'password'}
                                placeholder="Повторите пароль"
                                value={formData.confirmPassword}
                                onChange={handleChange}
                                bg="gray.700"
                                color="white"
                                required
                            />
                            <InputRightElement>
                                <Button
                                    variant="ghost"
                                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                                    color="gray.400"
                                    _hover={{ bg: 'transparent' }}
                                >
                                    {showConfirmPassword ? <ViewOffIcon /> : <ViewIcon />}
                                </Button>
                            </InputRightElement>
                        </InputGroup>
                        <FormErrorMessage>{errors.confirmPassword}</FormErrorMessage>
                    </FormControl>

                    <Button
                        type="submit"
                        colorScheme="blue"
                        width="full"
                        isLoading={isSubmitting}
                        loadingText="Регистрация..."
                    >
                        Зарегистрироваться
                    </Button>
                </form>

                <Text mt={4} color="gray.400">
                    Уже есть аккаунт?{' '}
                    <Link href="/login" color="blue.400">
                        Войти
                    </Link>
                </Text>
            </Box>
        </Box>
    );
};

export default RegisterPage;
