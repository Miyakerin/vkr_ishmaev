import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    Flex,
    Box,
    Button,
    Select,
    Heading,
    Text,
    Input,
    InputGroup,
    InputRightElement,
    IconButton,
    Avatar,
    Divider,
    Spinner,
    useToast,
    Stack,
    Tooltip,
    Badge
} from '@chakra-ui/react';
import {ArrowForwardIcon, AddIcon, SettingsIcon} from '@chakra-ui/icons';
import api from '../api';
import endpointsConfig from '../config/endpointsConfig';

const ChatsPage = () => {
    const [chats, setChats] = useState([]);
    const [selectedChat, setSelectedChat] = useState(null);
    const [chatHistory, setChatHistory] = useState(null);
    const [newMessage, setNewMessage] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [isSending, setIsSending] = useState(false);
    const [selectedModel, setSelectedModel] = useState(1);
    const [showModelSelector, setShowModelSelector] = useState(false);
    const [newChatLanguage, setNewChatLanguage] = useState('ru');
    const navigate = useNavigate();
    const toast = useToast();

    const availableModels = [
        {
            "id": 1,
            "company_name": "gigachat",
            "model_name": "gigachat"
        }
    ]

    useEffect(() => {
        fetchChats();
    }, []);

    useEffect(() => {
        if (selectedChat) {
            fetchMessages(selectedChat);
        }
    }, [selectedChat]);

    const renderModelSelector = () => (
        <Box
            position="absolute"
            right="4"
            top="16"
            bg="white"
            p="4"
            borderRadius="md"
            boxShadow="lg"
            zIndex="dropdown"
            width="250px"
            border="1px"
            borderColor="gray.200"
        >
            <Text fontWeight="bold" mb="2">Выберите модель</Text>
            <Stack spacing="3">
                {availableModels.map(model => (
                    <Box
                        key={model.id}
                        p="2"
                        borderRadius="md"
                        bg={selectedModel === model.id ? 'blue.50' : 'transparent'}
                        border="1px"
                        borderColor={selectedModel === model.id ? 'blue.200' : 'transparent'}
                        cursor="pointer"
                        onClick={() => {
                            setSelectedModel(model.id);
                            toast({
                                title: `Модель изменена на ${model.model_name}`,
                                status: 'info',
                                duration: 2000,
                                isClosable: true,
                            });
                            setShowModelSelector(false);
                        }}
                    >
                        <Text fontWeight="medium">{model.model_name}</Text>
                    </Box>
                ))}
            </Stack>
        </Box>
    );

    const renderChatHeader = () => (
        <Box p={4} borderBottom="1px" borderColor="gray.200" bg="white" position="relative">
            <Flex align="center" justify="space-between">
                <Heading size="md">
                    Chat #{selectedChat}
                    {chatHistory && (
                        <Badge ml={2} colorScheme="blue">
                            {chatHistory.chat_data.language}
                        </Badge>
                    )}
                </Heading>
                <Flex align="center">
                    {chatHistory?.messages?.length > 0 && (
                        <Badge colorScheme="green" mr="2">
                            Tokens: {chatHistory.messages.reduce((acc, msg) => {
                            return acc + (msg.total_tokens || 0);
                        }, 0)}
                        </Badge>
                    )}
                    <Tooltip label="Настройки модели">
                        <IconButton
                            icon={<SettingsIcon />}
                            aria-label="Model settings"
                            variant="ghost"
                            onClick={() => setShowModelSelector(!showModelSelector)}
                        />
                    </Tooltip>
                    <Badge colorScheme="purple" ml="2">
                        {availableModels.find(m => m.id === selectedModel)?.name || 'Model'}
                    </Badge>
                </Flex>
            </Flex>
            {showModelSelector && renderModelSelector()}
        </Box>
    );

    const renderMessageInput = () => (
        <Box p={4} borderTop="1px" borderColor="gray.200" bg="white">
            <InputGroup>
                <Input
                    placeholder="Type your message..."
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                />
                <InputRightElement>
                    <IconButton
                        icon={<ArrowForwardIcon />}
                        onClick={handleSendMessage}
                        aria-label="Send message"
                        colorScheme="blue"
                        isLoading={isSending}
                        isDisabled={!newMessage.trim()}
                    />
                </InputRightElement>
            </InputGroup>
        </Box>
    );

    const fetchChats = async () => {
        setIsLoading(true);
        try {
            const response = await api.get(endpointsConfig.getUserChatsEndpoint);
            setChats(response.data.items);
            if (response.data.items.length > 0 && !selectedChat) {
                setSelectedChat(response.data.items[0].chat_id);
            }
        } catch (error) {
            handleApiError(error, 'Failed to load chats');
        } finally {
            setIsLoading(false);
        }
    };

    const fetchMessages = async (chatId) => {
        setIsLoading(true);
        try {
            const response = await api.get(
                endpointsConfig.getChatHistory,
                {urlParams: {chat_id: chatId}}
            );
            setChatHistory(response.data);
        } catch (error) {
            handleApiError(error, 'Failed to load messages');
        } finally {
            setIsLoading(false);
        }
    };

    const createNewChat = async () => {
        setIsLoading(true);
        try {
            const response = await api.post(endpointsConfig.createChatEndpoint, { language: newChatLanguage });
            setChats([...chats, response.data]);
            setSelectedChat(response.data.chat_id);
            toast({
                title: 'New chat created',
                status: 'success',
                duration: 3000,
                isClosable: true,
            });
        } catch (error) {
            handleApiError(error, 'Failed to create chat');
        } finally {
            setIsLoading(false);
        }
    };

    const handleSendMessage = async () => {
        if (!newMessage.trim() || !selectedChat) return;
        const currentModel = availableModels.find(model => model.id === selectedModel);
        setIsSending(true);

        try {
            // Отправляем сообщение
            await api.post(endpointsConfig.sendMessageEndpoint,
                {message_data: newMessage},
                {
                    urlParams: {
                        'chat_id': selectedChat
                    },
                    params: {
                        'model_name': currentModel.model_name,
                        'company_name': currentModel.company_name
                    }
                });

            // Обновляем историю сообщений
            await fetchMessages(selectedChat);

            setNewMessage('');
            toast({
                title: 'Message sent',
                status: 'success',
                duration: 2000,
                isClosable: true,
            });
        } catch (error) {
            handleApiError(error, 'Failed to send message');
        } finally {
            setIsSending(false);
        }
    };

    const handleApiError = (error, defaultMessage) => {
        console.error(error);
        const message = error.response?.data?.message || defaultMessage;
        toast({
            title: 'Error',
            description: message,
            status: 'error',
            duration: 5000,
            isClosable: true,
        });

        if (error.response?.status === 401) {
            localStorage.removeItem('access_token');
            navigate('/login');
        }
    };

    const formatDate = (dateString) => {
        const date = new Date(dateString);
        return date.toLocaleString();
    };

    return (
        <Flex h="100vh" bg="gray.50">
            {/* Sidebar */}
            <Box w="300px" borderRight="1px" borderColor="gray.200" bg="white">
                <Box p={4} borderBottom="1px" borderColor="gray.200">
                    <Flex align="center" justify="space-between" mb={4}>
                        <Heading size="md">Chats</Heading>
                        <IconButton
                            icon={<AddIcon />}
                            onClick={createNewChat}
                            aria-label="New chat"
                            colorScheme="blue"
                            size="sm"
                            isLoading={isLoading}
                        />
                    </Flex>
                    <Select
                        value={newChatLanguage}
                        onChange={(e) => setNewChatLanguage(e.target.value)}
                        size="sm"
                        mb={2}
                    >
                        <option value="ru">Russian</option>
                        <option value="en">English</option>
                    </Select>
                </Box>

                <Box overflowY="auto" h="calc(100vh - 120px)">
                    {chats.map(chat => (
                        <Box
                            key={chat.chat_id}
                            p={4}
                            borderBottom="1px"
                            borderColor="gray.100"
                            bg={selectedChat === chat.chat_id ? 'blue.50' : 'white'}
                            _hover={{ bg: 'gray.50' }}
                            cursor="pointer"
                            onClick={() => setSelectedChat(chat.chat_id)}
                        >
                            <Flex justify="space-between" align="center">
                                <Text fontWeight="bold">Chat #{chat.chat_id}</Text>
                                <Badge colorScheme="blue">{chat.language}</Badge>
                            </Flex>
                            <Text fontSize="sm" color="gray.500">
                                {formatDate(chat.create_timestamp)}
                            </Text>
                        </Box>
                    ))}
                </Box>
            </Box>

            {/* Chat area */}

            <Box flex={1} display="flex" flexDirection="column">
                {selectedChat ? (
                    <>
                        {renderChatHeader()}

                        <Box flex={1} p={4} overflowY="auto" bg="gray.50">
                            {isLoading ? (
                                <Flex justify="center" align="center" h="100%">
                                    <Spinner size="xl" />
                                </Flex>
                            ) : (
                                chatHistory?.messages.map((message) => (
                                    <Box
                                        key={message.message_id}
                                        mb={4}
                                        alignSelf={message.sender === 'user' ? 'flex-end' : 'flex-start'}
                                        maxW="80%"
                                    >
                                        <Box
                                            p={3}
                                            borderRadius="lg"
                                            bg={message.sender === 'user' ? 'blue.500' : 'gray.200'}
                                            color={message.sender === 'user' ? 'white' : 'gray.800'}
                                        >
                                            <Text fontSize="sm" fontWeight="bold" mb={1}>
                                                {message.company_name || 'You'}
                                            </Text>
                                            {message.message_data.map(data => (
                                                <Text key={data.message_data_id}>{data.text}</Text>
                                            ))}
                                            <Text fontSize="xs" opacity={0.7} mt={1}>
                                                {formatDate(message.create_timestamp)}
                                            </Text>
                                        </Box>
                                    </Box>
                                ))
                            )}
                        </Box>

                        {renderMessageInput()}
                    </>
                ) : (
                    <Flex justify="center" align="center" h="100%">
                        <Box textAlign="center">
                            <Heading size="lg" mb={4}>No chats available</Heading>
                            <Button
                                colorScheme="blue"
                                leftIcon={<AddIcon />}
                                onClick={createNewChat}
                                isLoading={isLoading}
                            >
                                Create New Chat
                            </Button>
                        </Box>
                    </Flex>
                )}
            </Box>
        </Flex>
    );
};

export default ChatsPage;
