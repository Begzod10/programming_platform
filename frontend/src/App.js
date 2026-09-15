import { Provider } from 'react-redux';
import { BrowserRouter } from 'react-router-dom';
import store from './store/store';
import { AuthProvider } from './context/AuthContext';
import { StoreProvider } from './context/StoreContext';
import AppRouter from './AppRouter';
import SSOHandler from './components/SSOHandler';
import UpdateBanner from './components/UpdateBanner/UpdateBanner';
import TerminalOverlay from './components/TerminalOverlay/TerminalOverlay';
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
                        {/* Needs useNavigate(), so it must live inside
                            BrowserRouter — self-gates on the equipped
                            "hacker terminal" theme's asset_ref.terminal
                            flag, so it renders nothing for anyone else. */}
                        <TerminalOverlay />
                    </BrowserRouter>
                    <UpdateBanner />
                </StoreProvider>
            </AuthProvider>
        </Provider>
    );
}

export default App;