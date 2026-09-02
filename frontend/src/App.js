import { Provider } from 'react-redux';
import { BrowserRouter } from 'react-router-dom';
import store from './store/store';
import { AuthProvider } from './context/AuthContext';
import { StoreProvider } from './context/StoreContext';
import AppRouter from './AppRouter';
import SSOHandler from './components/SSOHandler';
import './App.css';

function App() {
    return (
        <Provider store={store}>
            <AuthProvider>
                <StoreProvider>
                    <BrowserRouter>
                        <SSOHandler>
                            <AppRouter />
                        </SSOHandler>
                    </BrowserRouter>
                </StoreProvider>
            </AuthProvider>
        </Provider>
    );
}

export default App;