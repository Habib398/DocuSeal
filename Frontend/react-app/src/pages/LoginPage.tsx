import React, { useState } from 'react';
import LoginForm from '../components/LoginForm';
import RegisterModal from '../components/RegistrarModal';
import '../styles/login.css';

const LoginPage: React.FC = () => {
  const [showRegisterModal, setShowRegisterModal] = useState(false);

  return (
    <>
      <nav className="navbar navbar-dark top-bar px-3">
        <div className="d-flex gap-2 app-title">
          <span className="fw-semibold">Bienvenido</span>
        </div>
      </nav>

      <main className="container-fluid login-page">
        <div className="row align-items-center min-vh-100 gx-0">
          {/* Formulario de inicio de sesión */}
          <div className="col-12 col-md-6 d-flex justify-content-center">
            <div>
              <LoginForm />
              <div className="text-center mt-3">
                <p className="text-muted">
                  ¿No tienes cuenta?{' '}
                  <a
                    href="#"
                    className="text-primary"
                    onClick={(e) => {
                      e.preventDefault();
                      setShowRegisterModal(true);
                    }}
                  >
                    Regístrate aquí
                  </a>
                </p>
              </div>
            </div>
          </div>

          {/* Imagen de inicio de sesión */}
          <div className="col-12 col-md-6 d-none d-md-flex justify-content-center">
            <div className="login-illustration-wrap">
              <img
                src="https://res.cloudinary.com/dt8ulsehy/image/upload/image-removebg-preview_qmxpfq"
                alt="Ilustración"
                className="img-fluid placeholder-img"
              />
            </div>
          </div>
        </div>
      </main>

      <RegisterModal show={showRegisterModal} onClose={() => setShowRegisterModal(false)} />
    </>
  );
};

export default LoginPage;
