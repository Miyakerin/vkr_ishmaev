import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation, useQueryClient } from 'react-query';
import endpointsConfig from '../config/endpointsConfig';
import api from '../api';
import {
    Box,
    Button,
    Heading,
    FormControl,
    FormLabel,
    Select,
    Spinner,
    useToast,
    VStack
} from '@chakra-ui/react';

const NewChatPage = () => {
    const navigate = useNavigate();
    const queryClient = useQueryClient();
    const toast = useToast();
    const [language, setLanguage] = useState('ru'); // Язык по умолчанию

    // Мутация для создания нового чата
    const { mutate: createChat, isPending } = useMutation({
        mutationFn: () => api.post(endpointsConfig.createChatEndpoint, { language }),
        onSuccess: (data) => {
            // Инвалидируем кеш списка чатов
            queryClient.invalidateQueries(['chats']);

            // Перенаправляем в созданный чат
            navigate(`/chats/${data.data.chat_id}`);

            toast({
                title: 'Чат создан',
                status: 'success',
                duration: 3000,
                isClosable: true,
            });
        },
        onError: (error) => {
            toast({
                title: 'Ошибка при создании чата',
                description: error.response?.data?.message || error.message,
                status: 'error',
                duration: 5000,
                isClosable: true,
            });
        }
    });

    const handleSubmit = (e) => {
        e.preventDefault();
        createChat();
    };

    return (
        <Box
            display="flex"
            justifyContent="center"
            alignItems="center"
            minH="100vh"
            bg="gray.900"
        >
            <Box
                bg="gray.800"
                p={8}
                borderRadius="lg"
                width="md"
            >
                <Heading size="lg" color="white" mb={6} textAlign="center">
                    Создать новый чат
                </Heading>

                <form onSubmit={handleSubmit}>
                    <VStack spacing={6}>
                        <FormControl>
                            <FormLabel color="white">Язык чата</FormLabel>
                            <Select
                                bg="gray.700"
                                color="white"
                                value={language}
                                onChange={(e) => setLanguage(e.target.value)}
                            >
                                <option value="ru">Русский</option>
                                <option value="en">English</option>
                                <option value="es">Español</option>
                                <option value="fr">Français</option>
                                <option value="de">Deutsch</option>
                            </Select>
                        </FormControl>

                        <Button
                            type="submit"
                            colorScheme="blue"
                            width="full"
                            isLoading={isPending}
                            loadingText="Создание..."
                        >
                            Создать чат
                        </Button>
                    </VStack>
                </form>
            </Box>
        </Box>
        );
};

export default NewChatPage;
