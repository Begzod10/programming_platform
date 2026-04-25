import { useState } from 'react';
import { Provider } from 'react-redux';
import store from './store/store';
import StudentLayout from './layouts/StudentLayout';
import TeacherLayout from './layouts/TeacherLayout';
import Login from './views/auth/login/Login';
import Register from './views/auth/register/Register';
import './App.css';

function AppContent() {
    const [isRegister, setIsRegister] = useState(false);
    const [activeTab,  setActiveTab]  = useState('profile');

    const savedUser = localStorage.getItem('user');
    const [user, setUser] = useState(savedUser ? JSON.parse(savedUser) : null);

    const handleLogin = (res) => {
        const userData = res.user || res;
        setUser(userData);
        localStorage.setItem('user', JSON.stringify(userData));
    };

    const handleLogout = () => {
        setUser(null);
        localStorage.removeItem('token');
        localStorage.removeItem('user');
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
            setActiveTab={setActiveTab}
            onLogout={handleLogout}
        />
    ) : (
        <StudentLayout
            user={user}
            activeTab={activeTab}
            setActiveTab={setActiveTab}
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


// import { useState } from 'react';
// import { Provider } from 'react-redux';
// import store from './store/store';
// import StudentLayout from './layouts/StudentLayout';
// import TeacherLayout from './layouts/TeacherLayout';
// import Login from './views/auth/login/Login';
// import Register from './views/auth/register/Register';
// import './App.css';
//
// // ТЕСТОВЫЙ УЧИТЕЛЬ (пока бекенд спит)
// const TEST_TEACHER = {
//     id: 1,
//     name: 'Иван Иванов',
//     email: 'teacher@test.com',
//     role: 'teacher',
//     avatar: '👨‍🏫',
//     level: 'Expert'
// };
//
// function AppContent() {
//     const [isRegister, setIsRegister] = useState(false);
//     const [activeTab,  setActiveTab]  = useState('profile');
//
//     // АВТОЛОГИН КАК УЧИТЕЛЬ
//     const [user, setUser] = useState(TEST_TEACHER);
//
//     // Сохраняем в localStorage
//     if (!localStorage.getItem('user')) {
//         localStorage.setItem('user', JSON.stringify(TEST_TEACHER));
//         localStorage.setItem('token', 'test-teacher-token-123');
//     }
//
//     const handleLogin = (res) => {
//         const userData = res.user || res;
//         setUser(userData);
//         localStorage.setItem('user', JSON.stringify(userData));
//     };
//
//     const handleLogout = () => {
//         setUser(TEST_TEACHER); // Возвращаемся к тестовому
//         localStorage.setItem('user', JSON.stringify(TEST_TEACHER));
//         setActiveTab('profile');
//     };
//
//     return user.role === 'teacher' ? (
//         <TeacherLayout
//             user={user}
//             activeTab={activeTab}
//             setActiveTab={setActiveTab}
//             onLogout={handleLogout}
//         />
//     ) : (
//         <StudentLayout
//             user={user}
//             activeTab={activeTab}
//             setActiveTab={setActiveTab}
//             onLogout={handleLogout}
//         />
//     );
// }
//
// function App() {
//     return (
//         <Provider store={store}>
//             <AppContent />
//         </Provider>
//     );
// }
//
// export default App;