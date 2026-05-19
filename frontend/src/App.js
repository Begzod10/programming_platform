import { Provider } from 'react-redux';
import { BrowserRouter } from 'react-router-dom';
import store from './store/store';
import { AuthProvider } from './context/AuthContext';
import AppRouter from './AppRouter';
import './App.css';

function App() {
    return (
        <Provider store={store}>
            <AuthProvider>
                <BrowserRouter>
                    <AppRouter />
                </BrowserRouter>
            </AuthProvider>
        </Provider>
    );
}

export default App;