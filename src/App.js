import { useState } from 'react';
import { Provider } from 'react-redux';
import store from './store/store';
import StudentLayout from './layouts/StudentLayout';
import TeacherLayout from './layouts/TeacherLayout';
import Login from './views/auth/login/Login';
import Register from './views/auth/register/Register';
import './App.css';

function AppContent() {
    const savedUser = localStorage.getItem('user');
    const [user, setUser] = useState(savedUser ? JSON.parse(savedUser) : null);

    const savedTab = localStorage.getItem('activeTab') || 'profile';
    const [activeTab, setActiveTab] = useState(savedTab);

    const [isRegister, setIsRegister] = useState(false);

    const handleLogin = (res) => {
        const userData = res.user || res;
        setUser(userData);
        localStorage.setItem('user', JSON.stringify(userData));
    };

    const handleTabChange = (tab) => {
        setActiveTab(tab);
        localStorage.setItem('activeTab', tab);
    };

    const handleLogout = () => {
        setUser(null);
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        localStorage.removeItem('activeTab');
        setActiveTab('profile');
    };

    if (!user) {
        return (
            <div className="app">
                {isRegister
                    ? <Register
                        onLogin={handleLogin}
                        onGoLogin={() => setIsRegister(false)}
                      />
                    : <Login
                        onLogin={handleLogin}
                        onGoRegister={() => setIsRegister(true)}
                      />
                }
            </div>
        );
    }

    return user.role === 'teacher' ? (
        <TeacherLayout
            user={user}
            activeTab={activeTab}
            setActiveTab={handleTabChange}
            onLogout={handleLogout}
        />
    ) : (
        <StudentLayout
            user={user}
            activeTab={activeTab}
            setActiveTab={handleTabChange}
            onLogout={handleLogout}
        />
    );
}

function App() {
    return (
        <Provider store={store}>
            <AppContent />
        </Provider>
    );
}

export default App;