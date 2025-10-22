import React, { useState } from 'react';

interface ApiKeyModalProps {
  show: boolean;
  apiKey: string;
  onClose: () => void;
}

const ApiKeyModal: React.FC<ApiKeyModalProps> = ({ show, apiKey, onClose }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(apiKey);
      setCopied(true);
      setTimeout(() => setCopied(false), 3000);
    } catch (error) {
      console.error('Error al copiar:', error);
    }
  };

  const handleClose = () => {
    onClose();
  };

  if (!show) return null;

  return (
    <>
      <div className="modal fade show" style={{ display: 'block' }} tabIndex={-1}>
        <div className="modal-dialog modal-dialog-centered">
          <div className="modal-content">
            <div className="modal-header bg-warning">
              <h5 className="modal-title">
                <i className="fa fa-key me-2"></i>
                ¡Importante! Tu Clave de Acceso
              </h5>
            </div>
            <div className="modal-body">
              <div className="alert alert-warning mb-3" role="alert">
                <strong>⚠️ ATENCIÓN:</strong> Esta clave solo se mostrará una vez. Guárdala en un lugar seguro.
              </div>

              <p className="mb-3">
                Tu clave de acceso para obtener los datos de tus certificados es:
              </p>

              <div className="card bg-light mb-3">
                <div className="card-body">
                  <code className="d-block text-center fs-5 text-break" style={{ userSelect: 'all' }}>
                    {apiKey}
                  </code>
                </div>
              </div>

              <div className="d-grid gap-2">
                <button
                  className={`btn ${copied ? 'btn-success' : 'btn-primary'}`}
                  onClick={handleCopy}
                >
                  <i className={`fa ${copied ? 'fa-check' : 'fa-copy'} me-2`}></i>
                  {copied ? '¡Copiado!' : 'Copiar Clave'}
                </button>
              </div>

              <div className="mt-3">
                <h6 className="text-danger">Instrucciones de seguridad:</h6>
                <ul className="small text-muted">
                  <li>Copia y guarda esta clave en un lugar seguro (gestor de contraseñas, archivo encriptado, etc.)</li>
                  <li>Esta clave es necesaria para acceder a los datos de tus certificados desde el servicio backend</li>
                  <li>No compartas esta clave con nadie</li>
                  <li>Si pierdes esta clave, deberás contactar con soporte para recuperarla</li>
                  {/* TODO: Implementar flujo de recuperación de clave en el futuro */}
                </ul>
              </div>
            </div>
            <div className="modal-footer">
              <button type="button" className="btn btn-primary" onClick={handleClose}>
                Entendido, continuar al login
              </button>
            </div>
          </div>
        </div>
      </div>
      <div className="modal-backdrop fade show"></div>
    </>
  );
};

export default ApiKeyModal;
