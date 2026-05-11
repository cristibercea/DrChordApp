import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './store/authStore';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import Dashboard from './pages/Dashboard';
import TabsViewerPage from './pages/TabsViewerPage';
import ProtectedRoute from './components/ProtectedRoute';
import Navbar from './components/Navbar';
import ProfileSettings from './pages/ProfileSettings'
import VerifyCode from "./pages/VerifyCode";

export default function App() {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  return (
    <BrowserRouter>
      {isAuthenticated && <Navbar />}
      <main className="min-h-screen bg-gray-50">
        <Routes>
          {/* Rute Publice */}
          <Route path="/login" element={isAuthenticated ? <Navigate to="/" /> : <LoginPage />} />
          <Route path="/register" element={isAuthenticated ? <Navigate to="/" /> : <RegisterPage />} />
          <Route path="/verify-code" element={<VerifyCode />} />

          {/* Rute Protejate (necesită login) */}
          <Route element={<ProtectedRoute />}>
            <Route path="/" element={<Dashboard />} /> {/* Pagina principală cu lista de piese */}
            <Route path="/tabs/:id" element={<TabsViewerPage />} /> {/* Pagina de vizualizare tab */}
            <Route path="/profile" element={<ProfileSettings />} />
          </Route>

          {/* Fallback pentru rute inexistente */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </BrowserRouter>
  );
}