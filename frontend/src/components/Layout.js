// В файле Layout.js
import { Flex, Box, Button, Icon, useColorMode, useColorModeValue } from '@chakra-ui/react';
import { useNavigate, useLocation } from 'react-router-dom';
import { FiLogOut } from 'react-icons/fi';

export const Layout = ({ children }) => {
    const navigate = useNavigate();
    const location = useLocation();
    const { colorMode } = useColorMode();

    // Цвета
    const bgColor = useColorModeValue('white', 'gray.800');
    const buttonColor = useColorModeValue('gray.600', 'gray.300');
    const highlightColor = useColorModeValue('red.500', 'red.300');

    const isAuthPage = ['/login', '/register'].includes(location.pathname);

    const handleLogout = () => {
        localStorage.removeItem('access_token');
        navigate('/login');
    };

    return (
        <Box height="100vh" bg={useColorModeValue('gray.50', 'gray.900')}>
            {!isAuthPage && (
                <Flex
                    bg={bgColor}
                    px={4}
                    py={2}  // Уменьшил паддинги
                    h="48px" // Фиксированная высота
                    justifyContent="flex-end"
                    alignItems="center"
                    borderBottom={`2px solid ${highlightColor}`}  // Красная полоса
                    boxShadow="sm"
                >
                    <Button
                        variant="ghost"
                        onClick={handleLogout}
                        leftIcon={<Icon as={FiLogOut} boxSize={3.5} />}  // Уменьшил иконку
                        colorScheme="gray"
                        size="sm"  // Компактный размер
                        color={buttonColor}
                        _hover={{
                            color: highlightColor,
                        }}
                    >
                        Выход
                    </Button>
                </Flex>
            )}

            <Box
                p={{ base: 3, md: 4 }}
                height="calc(100% - 48px)"  // Учитываем новую высоту шапки
                overflow="auto"
            >
                {children}
            </Box>
        </Box>
    );
};
