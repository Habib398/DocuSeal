import React, { useState, useEffect } from 'react';
import { Certificate, CertificateFormData } from '../services/apiClient';

interface CertificateModalProps {
  show: boolean;
  certificate: Certificate | null;
  onClose: () => void;
  onSave: (data: CertificateFormData) => Promise<void>;
}

// Estado inicial del formulario
const emptyFormData: CertificateFormData = {
  usuarioPAC: '',
  contrasenaPAC: '',
  nombreEmpresa: '',
  noCertificado: '',
  vigencia: '',
  correo: '',
  telefono: '',
  CER: '',
  KEY: '',
};

const CertificateModal: React.FC<CertificateModalProps> = ({
  show,
  certificate,
  onClose,
  onSave,
}) => {
  const [formData, setFormData] = useState<CertificateFormData>(emptyFormData);
  const [loading, setLoading] = useState(false);
  const [cerFileName, setCerFileName] = useState<string>('');
  const [keyFileName, setKeyFileName] = useState<string>('');

  useEffect(() => {
    if (certificate) {
      // Popula el formulario con los datos del certificado existente
      setFormData({
        ...emptyFormData,
        ...certificate,
      });
    } else {
      // Reset form para nuevo certificado
      setFormData(emptyFormData);
    }
    // Limpiar nombres de archivos al abrir/cerrar modal
    setCerFileName('');
    setKeyFileName('');
  }, [certificate, show]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData({
      ...formData,
      [e.target.id]: e.target.value,
    });
  };

  // Función para convertir archivo a Base64
  const fileToBase64 = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => {
        const result = reader.result as string;
        // Remover el prefijo "data:*/*;base64," para obtener solo el Base64
        const base64 = result.split(',')[1];
        resolve(base64);
      };
      reader.onerror = (error) => reject(error);
    });
  };

  // Manejar subida de archivo CER
  const handleCerFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setCerFileName(file.name);
      try {
        const base64 = await fileToBase64(file);
        setFormData({
          ...formData,
          CER: base64,
        });
      } catch (error) {
        console.error('Error al convertir archivo CER:', error);
        alert('Error al procesar el archivo CER');
      }
    }
  };

  // Manejar subida de archivo KEY
  const handleKeyFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setKeyFileName(file.name);
      try {
        const base64 = await fileToBase64(file);
        setFormData({
          ...formData,
          KEY: base64,
        });
      } catch (error) {
        console.error('Error al convertir archivo KEY:', error);
        alert('Error al procesar el archivo KEY');
      }
    }
  };

  // Manejar subida de archivo Certificado
  // (Removed Certificado upload — CER already covers the required certificate file)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await onSave(formData);
      onClose();
    } catch (error) {
      console.error('Error saving certificate:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!show) return null;

  const modalTitle = certificate ? 'Editar Certificado' : 'Agregar Certificado';

  return (
    <>
      <div className="modal fade show" style={{ display: 'block' }} tabIndex={-1}>
        <div className="modal-dialog modal-lg modal-dialog-centered">
          <div className="modal-content modal-enhanced">
            <div className="modal-header">
              <h5 className="modal-title d-flex align-items-center">
                <span className="icon-badge">
                  <i className="fas fa-file-signature"></i>
                </span>
                <span id="modalTitleText">{modalTitle}</span>
              </h5>
              <button type="button" className="btn-close" onClick={onClose} aria-label="Cerrar"></button>
            </div>
            <form onSubmit={handleSubmit} noValidate>
              <div className="modal-body">
                <div className="row g-3">
                  <div className="col-12">
                    <div className="section-title">Datos básicos</div>
                  </div>
                  <div className="col-md-6">
                    <label htmlFor="usuarioPAC" className="form-label required-asterisk">
                      Usuario PAC
                    </label>
                    <input
                      type="text"
                      className="form-control"
                      id="usuarioPAC"
                      required
                      value={formData.usuarioPAC}
                      onChange={handleChange}
                      disabled={loading}
                    />
                    <div className="field-help">Identificador asignado por el PAC.</div>
                  </div>
                  <div className="col-md-6">
                    <label htmlFor="contrasenaPAC" className="form-label required-asterisk">
                      Contraseña PAC
                    </label>
                    <input
                      type="password"
                      className="form-control"
                      id="contrasenaPAC"
                      required
                      value={formData.contrasenaPAC}
                      onChange={handleChange}
                      disabled={loading}
                    />
                    <div className="field-help">Nunca compartas esta información.</div>
                  </div>
                  <div className="col-md-6">
                    <label htmlFor="nombreEmpresa" className="form-label">
                      Nombre de la empresa
                    </label>
                    <input
                      type="text"
                      className="form-control"
                      id="nombreEmpresa"
                      placeholder="Nombre de la empresa"
                      value={formData.nombreEmpresa}
                      onChange={handleChange}
                      disabled={loading}
                    />
                    <div className="field-help">Opcional: Nombre asociado a estos certificados.</div>
                  </div>
                  <div className="col-md-6">
                    <label htmlFor="noCertificado" className="form-label required-asterisk">
                      No. Certificado
                    </label>
                    <input
                      type="text"
                      className="form-control"
                      id="noCertificado"
                      required
                      value={formData.noCertificado}
                      onChange={handleChange}
                      disabled={loading}
                    />
                  </div>
                  <div className="col-md-6">
                    <label htmlFor="vigencia" className="form-label required-asterisk">
                      Vigencia
                    </label>
                    <input
                      type="date"
                      className="form-control"
                      id="vigencia"
                      required
                      value={formData.vigencia}
                      onChange={handleChange}
                      disabled={loading}
                    />
                  </div>
                  <div className="col-md-6">
                    <label htmlFor="correo" className="form-label">
                      Correo electrónico
                    </label>
                    <input
                      type="email"
                      className="form-control"
                      id="correo"
                      placeholder="ejemplo@correo.com"
                      value={formData.correo}
                      onChange={handleChange}
                      disabled={loading}
                    />
                    <div className="field-help">Email de contacto.</div>
                  </div>
                  <div className="col-md-6">
                    <label htmlFor="telefono" className="form-label">
                      Teléfono
                    </label>
                    <input
                      type="tel"
                      className="form-control"
                      id="telefono"
                      placeholder="+52 123 456 7890"
                      value={formData.telefono}
                      onChange={handleChange}
                      disabled={loading}
                    />
                    <div className="field-help">Número de contacto.</div>
                  </div>
                  <div className="col-12">
                    <div className="divider"></div>
                    <div className="section-title">Archivos</div>
                  </div>
                  <div className="col-12">
                    <label htmlFor="CER" className="form-label required-asterisk">
                      Archivo CER (Base64)
                    </label>
                    <div className="mb-2">
                      <input
                        type="file"
                        className="d-none"
                        id="cerFileInput"
                        accept=".cer"
                        onChange={handleCerFileChange}
                        disabled={loading}
                      />
                      <button
                        type="button"
                        className="btn btn-outline-primary btn-sm"
                        onClick={() => document.getElementById('cerFileInput')?.click()}
                        disabled={loading}
                      >
                        <i className="fas fa-upload me-2"></i>
                        Subir archivo .cer
                      </button>
                      {cerFileName && (
                        <span className="ms-2 text-success">
                          <i className="fas fa-check-circle me-1"></i>
                          {cerFileName}
                        </span>
                      )}
                    </div>
                    <div className="form-text text-muted">El contenido se cargará automáticamente al subir el archivo .cer</div>
                  </div>
                  <div className="col-12">
                    <label htmlFor="KEY" className="form-label required-asterisk">
                      Archivo KEY (Base64)
                    </label>
                    <div className="mb-2">
                      <input
                        type="file"
                        className="d-none"
                        id="keyFileInput"
                        accept=".key"
                        onChange={handleKeyFileChange}
                        disabled={loading}
                      />
                      <button
                        type="button"
                        className="btn btn-outline-primary btn-sm"
                        onClick={() => document.getElementById('keyFileInput')?.click()}
                        disabled={loading}
                      >
                        <i className="fas fa-upload me-2"></i>
                        Subir archivo .key
                      </button>
                      {keyFileName && (
                        <span className="ms-2 text-success">
                          <i className="fas fa-check-circle me-1"></i>
                          {keyFileName}
                        </span>
                      )}
                    </div>
                    <div className="form-text text-muted">El contenido se cargará automáticamente al subir el archivo .key</div>
                  </div>
                </div>
              </div>
              <div className="modal-footer d-flex justify-content-between">
                <div className="text-muted small">
                  <span className="text-danger">*</span> Campos obligatorios
                </div>
                <div>
                  <button type="button" className="btn btn-outline-light" onClick={onClose} disabled={loading}>
                    Cancelar
                  </button>
                  <button type="submit" className="btn btn-success" disabled={loading}>
                    {loading ? 'Guardando...' : 'Guardar'}
                  </button>
                </div>
              </div>
            </form>
          </div>
        </div>
      </div>
      <div className="modal-backdrop fade show"></div>
    </>
  );
};

export default CertificateModal;
