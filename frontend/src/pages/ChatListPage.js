import React from 'react';
import { useQuery } from 'react-query';
import api from '../api';
import {
    Box,
    Button,
    Heading,
    List,
    ListItem,
    Text,
    Flex,
    Spinner,
    Badge,
    useColorModeValue
} from '@chakra-ui/react';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import { format } from 'date-fns';
import endpointsConfig from "../config/endpointsConfig";

const ChatListPage = () => {
    const navigate = useNavigate();
    const bgColor = useColorModeValue('gray.100', 'gray.700');
    const hoverBgColor = useColorModeValue('gray.200', 'gray.600');

    const { data, isLoading, error } = useQuery({
        queryKey: ['chats'],
        queryFn: () => api.get(endpointsConfig.getUserChatsEndpoint).then(res => res.data.items),
        refetchOnWindowFocus: false
    });
    if (isLoading) {
        return (
            <Flex justify="center" align="center" h="100vh">
                <Spinner size="xl" />
            </Flex>
        );
    }

    if (error) {
        return (
            <Box p={4}>
                <Text color="red.500">Ошибка загрузки чатов: {error.message}</Text>
            </Box>
        );
    }

    return (
        <Box display="flex" height="100vh" bg="gray.900">
            {/* Боковая панель со списком чатов */}
            <Box width="72" bg="gray.800" p={4} borderRight="1px" borderColor="gray.700">
                <Flex justify="space-between" align="center" mb={6}>
                    <Heading size="lg" color="white">
                        Мои чаты
                    </Heading>
                    <Button
                        colorScheme="blue"
                        size="sm"
                        onClick={() => navigate('/chats/new')}
                    >
                        +
                    </Button>
                </Flex>

                <List spacing={3}>
                    {data?.length > 0 ? (
                        data.map(chat => (
                            <ListItem key={chat.chat_id}>
                                <Box
                                    as={RouterLink}
                                    to={`/chats/${chat.chat_id}`}
                                    display="block"
                                    p={3}
                                    bg={bgColor}
                                    _hover={{ bg: hoverBgColor }}
                                    borderRadius="md"
                                    transition="background-color 0.2s"
                                >
                                    <Flex justify="space-between" mb={1}>
                                        <Text fontWeight="bold">Чат #{chat.chat_id}</Text>
                                        <Badge colorScheme="purple" fontSize="xs">
                                            {chat.language.toUpperCase()}
                                        </Badge>
                                    </Flex>
                                    <Text fontSize="sm" color="gray.500">
                                        {format(new Date(chat.create_timestamp), 'dd MMM yyyy, HH:mm', )}
                                    </Text>
                                </Box>
                            </ListItem>
                        ))
                    ) : (
                        <Text color="gray.400" textAlign="center" mt={4}>
                            У вас пока нет чатов
                        </Text>
                    )}
                </List>
            </Box>

            {/* Основное содержимое */}
            <Box flex={1} p={8} bg="gray.900" overflowY="auto">
                {data?.length > 0 ? (
                    <Box textAlign="center" color="gray.400" mt={48}>
                        Выберите чат или создайте новый
                    </Box>
                ) : (
                    <Box textAlign="center" mt={48}>
                        <Heading size="md" color="white" mb={4}>
                            Начните новый диалог
                        </Heading>
                        <Button
                            colorScheme="blue"
                            onClick={() => navigate('/chats/new')}
                        >
                            Создать чат
                        </Button>
                    </Box>
                )}
            </Box>
        </Box>
    );
};

export default ChatListPage;
