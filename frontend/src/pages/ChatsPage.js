import React, { useState, useEffect, useCallback, useRef  } from 'react';
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
    Badge,
    Divider,
    Spinner,
    useToast,
    Stack,
    Tooltip,
    Textarea,
    FormControl,
    FormLabel,
    Modal,
    ModalOverlay,
    ModalContent,
    ModalHeader,
    ModalFooter,
    ModalBody,
    ModalCloseButton,
    NumberInput,
    NumberInputField,
    NumberInputStepper,
    NumberIncrementStepper,
    NumberDecrementStepper,
    useDisclosure
} from '@chakra-ui/react';
import {ArrowForwardIcon, AddIcon, SettingsIcon} from '@chakra-ui/icons';
import api from '../api';
import endpointsConfig from '../config/endpointsConfig';
import {Layout} from "../components/Layout";

const ChatsPage = () => {
    const [chats, setChats] = useState([]);
    const [models, setModels] = useState([]);
    const [selectedChat, setSelectedChat] = useState(null);
    const [chatHistory, setChatHistory] = useState(null);
    const [newMessage, setNewMessage] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [isSending, setIsSending] = useState(false);
    const [selectedModel, setSelectedModel] = useState(0);
    const [showModelSelector, setShowModelSelector] = useState(false);
    const [newChatLanguage, setNewChatLanguage] = useState('ru');
    const [systemMessage, setSystemMessage] = useState('Ты чат-бот помощник, который все силы прилагает, чтобы решить вопрос пользователя, ты отвечаешь кратко');
    const [showAdvancedSettings, setShowAdvancedSettings] = useState(false);
    const {
        isOpen: isTokenModalOpen,
        onOpen: onTokenModalOpen,
        onClose: onTokenModalClose
    } = useDisclosure();
    const topUpInputRef = useRef();
    const {
        isOpen: isTopUpModalOpen,
        onOpen: onTopUpModalOpen,
        onClose: onTopUpModalClose
    } = useDisclosure();
    const [topUpAmount, setTopUpAmount] = useState(10000);
    const [tokenBalance, setTokenBalance] = useState(0);
    const navigate = useNavigate();
    const toast = useToast();
    const [isProcessing, setIsProcessing] = useState(false);

    const handleTopUp = async (amount) => {
        if (topUpAmount <= 0) {
            toast({
                title: 'Ошибка',
                description: 'Введите положительное число',
                status: 'error',
                duration: 2000,
                isClosable: true,
            });
            return;
        }

        setIsProcessing(true);
        try {
            // Вызов API для пополнения баланса
            const response = await api.post(endpointsConfig.addTokensEndpoint, {
                amount: amount
            });

            // Обновляем баланс из ответа сервера
            setTokenBalance(response.data.balance);
            setTopUpAmount(amount);

            toast({
                title: 'Успешно',
                description: `Баланс пополнен на ${amount} токенов`,
                status: 'success',
                duration: 2000,
                isClosable: true,
            });

            onTopUpModalClose();
        } catch (error) {
            console.error('Ошибка при пополнении:', error);
            toast({
                title: 'Ошибка',
                description: error.response?.data?.message || 'Не удалось пополнить баланс',
                status: 'error',
                duration: 3000,
                isClosable: true,
            });
        } finally {
            setIsProcessing(false);
        }
    };

    useEffect( () => {
        fetchTokens();
    }, []);

    useEffect( () => {
        fetchModels();
    }, []);

    useEffect(() => {
        fetchChats();
    }, []);


    useEffect(() => {
        if (selectedChat) {
            fetchMessages(selectedChat);
        }
    }, [selectedChat]);

    const fetchTokens = async () => {
        setIsLoading(true);
        try {
            const response = await api.get(endpointsConfig.getTokensEndpoint);
            setTokenBalance(response.data.balance)
        } catch (error) {
            handleApiError(error, 'Failed to load balance');
        } finally {
            setIsLoading(false);
        }
    };

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
            width="300px"
            border="1px"
            borderColor="gray.200"
        >
            <Flex justify="space-between" align="center" mb="3">
                <Text fontWeight="bold">Настройки модели</Text>
                <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => setShowAdvancedSettings(!showAdvancedSettings)}
                >
                    {showAdvancedSettings ? 'Скрыть' : 'Дополнительно'}
                </Button>
            </Flex>

            <Stack spacing="3">
                <Box>
                    <Text fontSize="sm" fontWeight="medium" mb="1">Выберите модель</Text>
                    <Select
                        value={selectedModel}
                        onChange={(e) => setSelectedModel(e.target.value)}
                        size="sm"
                    >
                        {models.map(model => (
                            <option key={model.id} value={model.id}>{model.model_name}</option>
                        ))}
                    </Select>
                </Box>

                {showAdvancedSettings && (
                    <Box mt="2">
                        <FormControl>
                            <FormLabel fontSize="sm">System Message</FormLabel>
                            <Textarea
                                value={systemMessage}
                                onChange={(e) => setSystemMessage(e.target.value)}
                                placeholder="Задайте поведение модели..."
                                size="sm"
                                rows={3}
                            />
                            <Text fontSize="xs" color="gray.500" mt="1">
                                Это сообщение будет влиять на поведение модели
                            </Text>
                        </FormControl>
                    </Box>
                )}
            </Stack>

            <Button
                colorScheme="blue"
                size="sm"
                mt="3"
                w="full"
                onClick={() => {
                    console.log('Применены настройки:', {
                        model: selectedModel,
                        systemMessage: systemMessage
                    });
                    setShowModelSelector(false);
                    toast({
                        title: 'Настройки применены',
                        status: 'success',
                        duration: 2000,
                        isClosable: true,
                    });
                }}
            >
                Применить
            </Button>
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
                    <Tooltip label="Токены доступные для использования">
                        <Badge
                            colorScheme="purple"
                            mr="2"
                            cursor="pointer"
                            onClick={onTokenModalOpen}
                            _hover={{ bg: 'purple.600' }}
                            transition="background 0.2s"
                            px={3}
                            py={1}
                        >
                            {tokenBalance} токенов
                        </Badge>
                    </Tooltip>
                    <Tooltip label="Настройки модели">
                        <IconButton
                            icon={<SettingsIcon />}
                            aria-label="Model settings"
                            variant="ghost"
                            onClick={() => setShowModelSelector(!showModelSelector)}
                        />
                    </Tooltip>
                    <Badge colorScheme="purple" ml="2">
                        {models.find(({id}) => id === selectedModel)?.model_name || 'Model'}
                    </Badge>
                </Flex>
            </Flex>
            {showModelSelector && renderModelSelector()}
            <TokenModal/>
            <TopUpModal />
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

    const fetchModels = async () => {
      setIsLoading(true)
      try {
          const response = await api.get(endpointsConfig.modelsEndpoint);
          setModels(response.data.items);
          if (response.data.items.length > 0 && !selectedModel) {
              setSelectedModel(response.data.items[0].id);
          }
      }  catch (error) {
          handleApiError(error, 'Failed to load models')
      } finally {
          setIsLoading(false)
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

    const TokenModal = () => (
        <Modal isOpen={isTokenModalOpen} onClose={onTokenModalClose}>
            <ModalOverlay />
            <ModalContent>
                <ModalHeader>Управление токенами</ModalHeader>
                <ModalCloseButton />
                <ModalBody>
                    <Flex direction="column" align="center" py={4}>
                        <Text fontSize="2xl" fontWeight="bold">
                            {tokenBalance} токенов
                        </Text>
                        <Text color="gray.500" mt={2}>
                            Доступно для использования
                        </Text>
                    </Flex>
                </ModalBody>
                <ModalFooter>
                    <Button
                        colorScheme="blue"
                        mr={3}
                        onClick={() => {
                            onTokenModalClose();
                            onTopUpModalOpen();
                        }}
                    >
                        Пополнить баланс
                    </Button>
                    <Button variant="ghost" onClick={onTokenModalClose}>
                        Закрыть
                    </Button>
                </ModalFooter>
            </ModalContent>
        </Modal>
    );

    const TopUpModal = () => {
        const [inputValue, setInputValue] = useState(topUpAmount);

        const handleApply = () => {
            const currentValue = parseInt(inputValue) || 0;
            handleTopUp(currentValue);
        };

        return (
            <Modal isOpen={isTopUpModalOpen} onClose={onTopUpModalClose}>
                <ModalOverlay />
                <ModalContent>
                    <ModalHeader>Пополнение баланса</ModalHeader>
                    <ModalCloseButton />
                    <ModalBody>
                        <FormControl>
                            <FormLabel>Сумма пополнения</FormLabel>
                            <NumberInput
                                min={1}
                                defaultValue={topUpAmount}
                                onChange={(valueString) => setInputValue(valueString)}
                                ref={topUpInputRef}
                            >
                                <NumberInputField />
                                <NumberInputStepper>
                                    <NumberIncrementStepper />
                                    <NumberDecrementStepper />
                                </NumberInputStepper>
                            </NumberInput>
                        </FormControl>
                    </ModalBody>
                    <ModalFooter>
                        <Button
                            colorScheme="blue"
                            mr={3}
                            onClick={handleApply}
                            isLoading={isProcessing}
                            loadingText="Обработка..."
                        >
                            Пополнить
                        </Button>
                        <Button
                            variant="ghost"
                            onClick={onTopUpModalClose}
                            isDisabled={isProcessing}
                        >
                            Отмена
                        </Button>
                    </ModalFooter>
                </ModalContent>
            </Modal>
        );
    };

    const handleSendMessage = async () => {
        if (!newMessage.trim() || !selectedChat) return;
        const currentModel = models.find(model => model.id === selectedModel);
        setIsSending(true);

        try {
            // Отправляем сообщение
            await api.post(endpointsConfig.sendMessageEndpoint,
                {message_data: newMessage, system_message: systemMessage},
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
            await fetchTokens();

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
        const message = error.response?.data?.detail || defaultMessage;
        toast({
            title: 'Error',
            description: message,
            status: 'error',
            duration: 1000,
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
        <Layout>
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
        </Layout>
    );
};

export default ChatsPage;
