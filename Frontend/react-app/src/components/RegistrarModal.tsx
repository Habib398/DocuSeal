import React, { useState } from 'react';
import { apiClient } from '../services/apiClient';

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
      const response = await apiClient.register({
        name,
        email,
        password,
        confirm_password: confirmPassword,
      });

      if (response.success) {
        setAlert({ message: 'Usuario registrado exitosamente. Por favor inicia sesión.', type: 'success' });
        setTimeout(() => {
          resetForm();
          onClose();
        }, 2000);
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
  };

  const handleClose = () => {
    resetForm();
    onClose();
  };

  return (
    <div className={`modal fade ${show ? 'show' : ''}`} style={{ display: show ? 'block' : 'none' }} tabIndex={-1}>
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
      {show && <div className="modal-backdrop fade show"></div>}
    </div>
  );
};

export default RegisterModal;
