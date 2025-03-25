import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import config from '../config/authConfig';

function LoginPage() {
    const [email, setEmail] = useState('');
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const navigate = useNavigate();

    useEffect(() => {
        const checkAutoLogin = async () => {
            const accessToken = localStorage.getItem('access_token');
            if (accessToken) {
                try {
                    const response = await fetch(`${config.apiBaseUrl}${config.verifyEndpoint}`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${accessToken}`
                        }
                    });

                    if (response.ok) {
                        navigate('/dashboard'); // Перенаправляем на главную страницу если токен валиден
                    } else {
                        // Если токен невалиден - очищаем его
                        localStorage.removeItem('access_token');
                    }
                } catch (error) {
                    console.error('Ошибка проверки токена:', error);
                    localStorage.removeItem('access_token');
                }
            }
        };

        checkAutoLogin();
    }, [navigate]);

    const handleLogin = async (e) => {
        e.preventDefault();
        try {
            const response = await fetch(`${config.apiBaseUrl}${config.loginEndpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({password, username })
            });

            if (response.ok) {
                const data = await response.json();
                localStorage.setItem('access_token', data.access_token);
                navigate('/dashboard');
            } else {
                alert('Ошибка входа');
            }
        } catch (error) {
            console.error('Ошибка:', error);
            alert('Не удалось выполнить вход');
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-100">
            <div className="bg-white p-8 rounded shadow-md w-96">
                <h2 className="text-2xl mb-4 text-center">Вход</h2>
                <form onSubmit={handleLogin}>
                    <div className="mb-4">
                        <label className="block mb-2">Username</label>
                        <input
                            type="username"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            className="w-full px-3 py-2 border rounded"
                            required
                        />
                    </div>
                    <div className="mb-4">
                        <label className="block mb-2">Пароль</label>
                        <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            className="w-full px-3 py-2 border rounded"
                            required
                        />
                    </div>
                    <button
                        type="submit"
                        className="w-full bg-blue-500 text-white py-2 rounded hover:bg-blue-600"
                    >
                        Войти
                    </button>
                </form>
                <p className="mt-4 text-center">
                    Нет аккаунта?
                    <button
                        onClick={() => navigate('/register')}
                        className="text-blue-500 ml-1"
                    >
                        Зарегистрироваться
                    </button>
                </p>
            </div>
        </div>
    );
}

export default LoginPage;