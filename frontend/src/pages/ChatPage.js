import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import api from '../api';
import { Box, Input, Button, Flex, Text } from '@chakra-ui/react';
import { useParams } from 'react-router-dom';

const ChatPage = () => {
    const { id: chatId } = useParams();
    const [message, setMessage] = useState('');
    const queryClient = useQueryClient();

    const { data: messages } = useQuery(['messages', chatId], () =>
        api.get(`/chats/${chatId}/messages`).then((res) => res.data)
    );

    const sendMessage = useMutation(
        (content) => api.post(`/chats/${chatId}/messages`, { content }),
        {
            onSuccess: () => {
                queryClient.invalidateQueries(['messages', chatId]);
                setMessage('');
            },
        }
    );

    const handleSubmit = (e) => {
        e.preventDefault();
        if (message.trim()) sendMessage.mutate(message);
    };

    return (
        <Box display="flex" height="100vh" bg="gray.900">
            <Box flex={1} display="flex" flexDirection="column">
                <Box flex={1} p={6} overflowY="auto">
                    {messages?.map((msg) => (
                        <Box key={msg.id} mb={4} p={4} bg="gray.800" borderRadius="lg">
                            <Text color="white">{msg.content}</Text>
                        </Box>
                    ))}
                </Box>
                <Box borderTop="1px" borderColor="gray.800" p={4}>
                    <Flex as="form" onSubmit={handleSubmit} gap={2}>
                        <Input
                            bg="gray.700"
                            color="white"
                            placeholder="Введите сообщение..."
                            value={message}
                            onChange={(e) => setMessage(e.target.value)}
                        />
                        <Button type="submit" colorScheme="blue" isLoading={sendMessage.isLoading}>
                            Отправить
                        </Button>
                    </Flex>
                </Box>
            </Box>
        </Box>
    );
};

export default ChatPage;
