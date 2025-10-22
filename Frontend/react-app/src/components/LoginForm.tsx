import React, { useState } from 'react';
import { apiClient } from '../services/apiClient';
import { useAuth } from '../contexts/AuthContext';

const LoginForm: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const response = await apiClient.login({ email, password });

      if (response.success && response.user) {
        login(response.user);
        // No redirigir manualmente, App.tsx manejará la navegación
      } else {
        setError(response.detail || 'Error al iniciar sesión');
      }
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Error de conexión con el servidor');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-panel">
      <h2 className="login-title">Iniciar sesión</h2>
      {error && (
        <div className="alert alert-danger mt-3" role="alert">
          {error}
        </div>
      )}
      <form className="mt-4" onSubmit={handleSubmit}>
        <div className="mb-3">
          <input
            id="txtEmail"
            name="email"
            type="email"
            className="form-control form-control-lg"
            placeholder="Email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            disabled={loading}
          />
        </div>
        <div className="mb-3 position-relative">
          <input
            id="txtPassword"
            name="password"
            type="password"
            className="form-control form-control-lg"
            placeholder="Contraseña"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            disabled={loading}
          />
        </div>
        
        {/* TODO: Implementar recuperación de clave API en el futuro */}
        {/* Se agregará un enlace aquí para "¿Olvidaste tu clave de acceso?" */}
        {/* que permitirá al usuario recuperar su API key mediante email */}
        
        <div className="mb-3 text-start">
          <button
            className="btn btn-primary btn-lg px-4"
            type="submit"
            disabled={loading}
          >
            <i className="fa fa-sign-in-alt me-2"></i>
            {loading ? 'Ingresando...' : 'Ingresar'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default LoginForm;
