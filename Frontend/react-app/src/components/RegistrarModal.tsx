import React, { useState } from 'react';
import { apiClient } from '../services/apiClient';
import ApiKeyModal from './ApiKeyModal';

interface RegisterModalProps {
  show: boolean;
  onClose: () => void;
}

const RegisterModal: React.FC<RegisterModalProps> = ({ show, onClose }) => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [alert, setAlert] = useState<{ message: string; type: 'success' | 'danger' } | null>(null);
  const [loading, setLoading] = useState(false);
  const [showApiKeyModal, setShowApiKeyModal] = useState(false);
  const [generatedApiKey, setGeneratedApiKey] = useState('');

  // Función para generar UUID v4 usando crypto API del navegador
  const generateApiKey = (): string => {
    return crypto.randomUUID();
  };

  const handleRegister = async () => {
    setAlert(null);

    // Validar contraseñas coinciden
    if (password !== confirmPassword) {
      setAlert({ message: 'Las contraseñas no coinciden', type: 'danger' });
      return;
    }

    // Validar longitud mínima
    if (password.length < 8) {
      setAlert({ message: 'La contraseña debe tener al menos 8 caracteres', type: 'danger' });
      return;
    }

    setLoading(true);

    try {
      // Generar la clave API única
      const apiKey = generateApiKey();

      const response = await apiClient.register({
        name,
        email,
        password,
        confirm_password: confirmPassword,
        api_key: apiKey,
      });

      if (response.success) {
        // Guardar la clave generada y mostrar el modal de API Key
        setGeneratedApiKey(apiKey);
        setShowApiKeyModal(true);
      } else {
        setAlert({ message: response.detail || 'Error al registrar usuario', type: 'danger' });
      }
    } catch (error) {
      setAlert({
        message: error instanceof Error ? error.message : 'Error de conexión con el servidor',
        type: 'danger',
      });
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setName('');
    setEmail('');
    setPassword('');
    setConfirmPassword('');
    setAlert(null);
    setGeneratedApiKey('');
  };

  const handleClose = () => {
    resetForm();
    onClose();
  };

  const handleApiKeyModalClose = () => {
    setShowApiKeyModal(false);
    resetForm();
    onClose();
  };

  const handleBackdropClick = (e: React.MouseEvent<HTMLDivElement>) => {
    // Solo cerrar si el clic es directamente en el backdrop (no en el contenido del modal)
    if (e.target === e.currentTarget) {
      handleClose();
    }
  };

  if (!show) return null;

  return (
    <>
      <div 
        className="modal fade show" 
        style={{ display: 'block' }} 
        tabIndex={-1}
        onClick={handleBackdropClick}
      >
        <div className="modal-dialog modal-dialog-centered">
          <div className="modal-content">
            <div className="modal-header">
              <h5 className="modal-title">Registrar nuevo usuario</h5>
              <button type="button" className="btn-close" onClick={handleClose} aria-label="Close"></button>
            </div>
            <div className="modal-body">
              <form>
                <div className="mb-3">
                  <label htmlFor="registerName" className="form-label">
                    Nombre completo
                  </label>
                  <input
                    type="text"
                    className="form-control"
                    id="registerName"
                    required
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    disabled={loading}
                  />
                </div>
                <div className="mb-3">
                  <label htmlFor="registerEmail" className="form-label">
                    Email
                  </label>
                  <input
                    type="email"
                    className="form-control"
                    id="registerEmail"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    disabled={loading}
                  />
                </div>
                <div className="mb-3">
                  <label htmlFor="registerPassword" className="form-label">
                    Contraseña (mínimo 8 caracteres)
                  </label>
                  <input
                    type="password"
                    className="form-control"
                    id="registerPassword"
                    required
                    minLength={8}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    disabled={loading}
                  />
                </div>
                <div className="mb-3">
                  <label htmlFor="registerConfirmPassword" className="form-label">
                    Confirmar contraseña
                  </label>
                  <input
                    type="password"
                    className="form-control"
                    id="registerConfirmPassword"
                    required
                    minLength={8}
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    disabled={loading}
                  />
                </div>
                {alert && (
                  <div className={`alert alert-${alert.type}`} role="alert">
                    {alert.message}
                  </div>
                )}
              </form>
            </div>
            <div className="modal-footer">
              <button type="button" className="btn btn-secondary" onClick={handleClose} disabled={loading}>
                Cancelar
              </button>
              <button type="button" className="btn btn-primary" onClick={handleRegister} disabled={loading}>
                {loading ? 'Registrando...' : 'Registrar'}
              </button>
            </div>
          </div>
        </div>
      </div>
      <div className="modal-backdrop fade show"></div>

      {/* Modal para mostrar la clave API generada */}
      <ApiKeyModal 
        show={showApiKeyModal} 
        apiKey={generatedApiKey} 
        onClose={handleApiKeyModalClose}
      />
    </>
  );
};

export default RegisterModal;
