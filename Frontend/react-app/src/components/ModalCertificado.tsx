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
  Certificado: '',
  pwdCER: '',
  pruebas: true, // Por defecto, los certificados nuevos son para pruebas
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
      const certificateData = {
        ...emptyFormData,
        ...certificate,
      };
      
      // Si el certificado existente no tiene claveUsuario, generarla automáticamente
      if (!certificateData.claveUsuario) {
        certificateData.claveUsuario = crypto.randomUUID();
      }
      
      setFormData(certificateData);
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

  // Función para extraer el certificado del archivo .cer
  const extractCertificateFromCer = async (file: File): Promise<string> => {
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
        // Extraer también el certificado para el campo Certificado del XML
        const certificado = await extractCertificateFromCer(file);
        
        setFormData({
          ...formData,
          CER: base64,
          Certificado: certificado, // Agregar el certificado extraído
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
      // Asegurar que siempre haya una claveUsuario (generada automáticamente si no existía)
      const dataToSave = {
        ...formData,
        claveUsuario: formData.claveUsuario || crypto.randomUUID(),
      };
      
      await onSave(dataToSave);
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
                  
                  {/* Mostrar noCertificado y vigencia solo en modo edición (valores automáticos del CER) */}
                  {certificate && (
                    <>
                      <div className="col-md-6">
                        <label htmlFor="noCertificado" className="form-label">
                          No. Certificado
                        </label>
                        <input
                          type="text"
                          className="form-control"
                          id="noCertificado"
                          value={formData.noCertificado}
                          readOnly
                          disabled
                        />
                        <div className="field-help">Valor extraído automáticamente del certificado CER.</div>
                      </div>
                      <div className="col-md-6">
                        <label htmlFor="vigencia" className="form-label">
                          Vigencia
                        </label>
                        <input
                          type="date"
                          className="form-control"
                          id="vigencia"
                          value={formData.vigencia}
                          readOnly
                          disabled
                        />
                        <div className="field-help">Valor extraído automáticamente del certificado CER.</div>
                      </div>
                    </>
                  )}
                  
                  {/* Mostrar clave de usuario solo cuando se está editando un certificado existente */}
                  {certificate && formData.claveUsuario && (
                    <div className="col-md-6">
                      <label htmlFor="claveUsuario" className="form-label">
                        Clave de Usuario
                      </label>
                      <div className="input-group">
                        <input
                          type="text"
                          className="form-control"
                          id="claveUsuario"
                          value={formData.claveUsuario}
                          readOnly
                          disabled
                        />
                        <button
                          className="btn btn-outline-secondary"
                          type="button"
                          onClick={() => {
                            navigator.clipboard.writeText(formData.claveUsuario || '');
                            // Opcional: mostrar feedback visual
                          }}
                          title="Copiar clave"
                        >
                          <i className="fas fa-copy"></i>
                        </button>
                      </div>
                      <div className="field-help">Clave única para acceder a este certificado desde el servicio.</div>
                    </div>
                  )}
                  
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
                  
                  {/* Checkbox para indicar si el certificado es para pruebas */}
                  <div className="col-12">
                    <div className="form-check">
                      <input
                        className="form-check-input"
                        type="checkbox"
                        id="pruebas"
                        checked={formData.pruebas ?? true}
                        onChange={(e) => setFormData({
                          ...formData,
                          pruebas: e.target.checked
                        })}
                        disabled={loading}
                      />
                      <label className="form-check-label" htmlFor="pruebas">
                        <strong>Usar certificado para pruebas</strong>
                      </label>
                    </div>
                    <div className="field-help ms-4">
                      Si está marcado, este certificado se usará en el ambiente de pruebas del PAC. 
                      Desmarcar para usar en producción.
                    </div>
                  </div>
                  
                  <div className="col-12">
                    <div className="divider"></div>
                    <div className="section-title">Archivos</div>
                  </div>
                  <div className="col-12">
                    <label htmlFor="pwdCER" className="form-label required-asterisk">
                      Contraseña del Certificado
                    </label>
                    <input
                      type="password"
                      className="form-control"
                      id="pwdCER"
                      placeholder="Contraseña de los archivos CER/KEY"
                      value={formData.pwdCER || ''}
                      onChange={handleChange}
                      disabled={loading}
                      required
                    />
                    <div className="field-help">Contraseña para descifrar los archivos CER y KEY (dejar vacío solo si no tienen contraseña).</div>
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
