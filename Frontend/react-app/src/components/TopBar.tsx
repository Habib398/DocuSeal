import React from 'react';
import { useAuth } from '../contexts/AuthContext';
const TopBar: React.FC = () => {
  const { user, logout } = useAuth();

  const handleLogout = () => {
    logout();
    // Redirigir al login (será manejado por App.tsx)
  };

  return (
    <nav className="navbar navbar-dark top-bar px-3">
      <div className="d-flex align-items-center gap-2 app-title">
        <i className="fas fa-certificate fs-4"></i>
        <span className="fw-semibold">DocuSeal - Administración de Certificados</span>
      </div>
      <div className="d-flex align-items-center gap-3">
        <span className="text-white" id="userName">
          {user ? `Hola, ${user.name}` : ''}
        </span>
        <button 
          className="btn btn-outline-light btn-sm" 
          onClick={handleLogout}
          title="Salir"
        >
          <i className="fas fa-sign-out-alt me-1"></i>Salir
        </button>
      </div>
    </nav>
  );
};

export default TopBar;
