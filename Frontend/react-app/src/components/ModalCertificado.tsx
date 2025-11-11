import React, { useState, useEffect } from 'react';
import { Certificate, CertificateFormData } from '../services/apiClient';
import * as forge from 'node-forge';

interface CertificateModalProps {
  show: boolean;
  certificate: Certificate | null;
  onClose: () => void;
  onSave: (data: CertificateFormData) => Promise<void>;
}

// Función para generar UUID compatible con navegadores antiguos y HTTP
const generateUUID = (): string => {
  // Intentar usar crypto.randomUUID si está disponible (HTTPS)
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return crypto.randomUUID();
  }
  
  // Fallback para HTTP o navegadores antiguos
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
};

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
  const [validatingMessage, setValidatingMessage] = useState<string>('');
  const [cerFileName, setCerFileName] = useState<string>('');
  const [keyFileName, setKeyFileName] = useState<string>('');
  
  // Rastrear si se modificaron los archivos o contraseña del certificado
  const [filesModified, setFilesModified] = useState(false);
  const [originalCertData, setOriginalCertData] = useState<{
    CER: string;
    KEY: string;
    pwdCER: string;
  } | null>(null);

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
      
      // Guardar los datos originales del certificado para comparar
      setOriginalCertData({
        CER: certificate.CER || '',
        KEY: certificate.KEY || '',
        pwdCER: certificate.pwdCER || '',
      });
      
      // Reset del flag de modificación
      setFilesModified(false);
    } else {
      // Reset form para nuevo certificado
      setFormData(emptyFormData);
      setOriginalCertData(null);
      setFilesModified(false);
    }
    // Limpiar nombres de archivos al abrir/cerrar modal
    setCerFileName('');
    setKeyFileName('');
  }, [certificate, show]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const fieldId = e.target.id;
    const newValue = e.target.value;
    
    // Si se modifica la contraseña del certificado, marcar como modificado
    if (fieldId === 'pwdCER' && originalCertData && newValue !== originalCertData.pwdCER) {
      setFilesModified(true);
    }
    
    setFormData({
      ...formData,
      [fieldId]: newValue,
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
        
        // Marcar que los archivos fueron modificados
        setFilesModified(true);
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
        
        // Marcar que los archivos fueron modificados
        setFilesModified(true);
      } catch (error) {
        console.error('Error al convertir archivo KEY:', error);
        alert('Error al procesar el archivo KEY');
      }
    }
  };

  // Manejar subida de archivo Certificado
  // (Removed Certificado upload — CER already covers the required certificate file)

  // Función para validar certificados CSD - Validación básica y menos estricta
  const validateCertificate = async (
    cerBase64: string,
    keyBase64: string,
    password: string
  ): Promise<void> => {
    try {
      // 1. Validar que los archivos no estén vacíos
      if (!cerBase64 || !keyBase64) {
        throw new Error('Los archivos CER y KEY son obligatorios');
      }

      // 2. Convertir base64 a formato PEM para el certificado
      const cerPem = `-----BEGIN CERTIFICATE-----\n${cerBase64.match(/.{1,64}/g)?.join('\n')}\n-----END CERTIFICATE-----`;
      
      // 3. Parsear el certificado - validación básica
      let cert;
      try {
        cert = forge.pki.certificateFromPem(cerPem);
      } catch (error) {
        throw new Error('El archivo CER no es un certificado válido o está corrupto');
      }

      // 4. Validación simplificada - Solo verificar que NO sea FIEL
      const subject = cert.subject.attributes;
      
      // Buscar el campo OU (Organizational Unit) y O (Organization)
      const ouAttributes = subject.filter(
        (attr) => (attr.shortName === 'OU' || attr.name === 'organizationalUnitName') && attr.value !== undefined
      );
      const oAttributes = subject.filter(
        (attr) => (attr.shortName === 'O' || attr.name === 'organizationName') && attr.value !== undefined
      );
      
      // Convertir los valores a string para análisis
      const ouValues = ouAttributes.map(attr => String(attr.value).toUpperCase());
      const oValues = oAttributes.map(attr => String(attr.value).toUpperCase());
      const allValues = [...ouValues, ...oValues];
      
      // Solo verificar que NO sea FIEL (los FIEL no sirven para facturación)
      const isFIEL = allValues.some(value => 
        value.includes('FIRMA ELECTRONICA') || 
        value.includes('FIEL') ||
        value.includes('FIRMA ELECTRÓNICA')
      );
      
      if (isFIEL) {
        throw new Error(
          'El archivo CER es un certificado FIEL (Firma Electrónica), no un CSD. ' +
          'Para facturación electrónica necesitas un certificado de Sello Digital (CSD).'
        );
      }

      // 5. Verificar que el certificado no esté vencido
      const now = new Date();
      if (cert.validity.notBefore > now) {
        throw new Error('El certificado CSD aún no es válido (fecha de inicio futura)');
      }
      if (cert.validity.notAfter < now) {
        throw new Error('El certificado CSD ha expirado. Necesitas renovarlo ante el SAT.');
      }

      // 6. Intentar descifrar la KEY privada con la contraseña
      let privateKey;
      try {
        // Convertir base64 a bytes
        const keyDer = forge.util.decode64(keyBase64);
        
        // Intentar descifrar la clave privada
        // Primero intentamos con PKCS#8 encriptado
        try {
          const keyAsn1 = forge.asn1.fromDer(keyDer);
          privateKey = forge.pki.decryptRsaPrivateKey(forge.asn1.toDer(keyAsn1).data, password);
        } catch (e) {
          // Si falla, intentar con PKCS#5
          const p8Asn1 = forge.asn1.fromDer(keyDer);
          privateKey = forge.pki.decryptPrivateKeyInfo(p8Asn1, password);
        }

        if (!privateKey) {
          throw new Error('decrypt_failed');
        }
      } catch (error) {
        if (error instanceof Error && error.message === 'decrypt_failed') {
          throw new Error(
            'La contraseña ingresada no es correcta para descifrar el archivo KEY. ' +
            'Verifica que sea la contraseña correcta de tu certificado.'
          );
        }
        throw new Error(
          'No se pudo descifrar el archivo KEY. Verifica que la contraseña sea correcta ' +
          'y que el archivo KEY sea válido.'
        );
      }

      // 7. Verificar que la KEY privada corresponda al certificado CER
      // Comparar el módulo (n) de la clave pública del certificado con la clave privada
      const publicKeyFromCert = cert.publicKey as forge.pki.rsa.PublicKey;
      const privateKeyRsa = privateKey as forge.pki.rsa.PrivateKey;

      if (!publicKeyFromCert.n.equals(privateKeyRsa.n)) {
        throw new Error(
          'El archivo KEY no corresponde al certificado CER. ' +
          'Asegúrate de que ambos archivos pertenezcan al mismo certificado.'
        );
      }

      // 8. Validación exitosa
      // Certificado válido, continuar con el proceso de guardado
      
    } catch (error) {
      // Re-lanzar el error para que sea manejado por handleSubmit
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Error desconocido al validar el certificado');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validar que todos los campos obligatorios estén llenos
    const isEdit = !!certificate;
    const requiredFields = isEdit ? 
      ['usuarioPAC', 'contrasenaPAC', 'nombreEmpresa', 'correo', 'telefono', 'CER', 'KEY', 'pwdCER', 'noCertificado', 'vigencia', 'claveUsuario'] :
      ['usuarioPAC', 'contrasenaPAC', 'nombreEmpresa', 'correo', 'telefono', 'CER', 'KEY', 'pwdCER'];
    
    const missingFields = requiredFields.filter(field => {
      const value = formData[field as keyof CertificateFormData];
      return typeof value === 'string' && value.trim() === '';
    });
    
    if (missingFields.length > 0) {
      alert(`Todos los campos son obligatorios. Los siguientes campos están vacíos: ${missingFields.join(', ')}`);
      return;
    }
    
    setLoading(true);
    
    // Solo validar certificados si:
    // 1. Es un certificado nuevo (no hay certificate original), O
    // 2. Se modificaron los archivos CER/KEY o la contraseña
    const shouldValidate = !certificate || filesModified;
    
    if (shouldValidate) {
      setValidatingMessage('Validando certificados CSD...');
      try {
        // Validar que los archivos CER, KEY y contraseña sean válidos
        await validateCertificate(formData.CER, formData.KEY, formData.pwdCER);
        setValidatingMessage('Validación exitosa. Guardando...');
      } catch (error) {
        setLoading(false);
        setValidatingMessage('');
        if (error instanceof Error) {
          alert(`Error de validación:\n\n${error.message}`);
        } else {
          alert('Error desconocido al validar el certificado');
        }
        return;
      }
    } else {
      // Si no se validó, solo mostrar mensaje de guardado
      setValidatingMessage('Guardando cambios...');
    }
    
    try {
      // Asegurar que siempre haya una claveUsuario (generada automáticamente si no existía)
      const dataToSave = {
        ...formData,
        claveUsuario: formData.claveUsuario || generateUUID(),
        // Omitir noCertificado y vigencia si están vacíos para que el backend los extraiga del CER
        noCertificado: formData.noCertificado || undefined,
        vigencia: formData.vigencia || undefined,
      };
      
      // Eliminar campos undefined antes de enviar
      Object.keys(dataToSave).forEach(key => {
        if (dataToSave[key as keyof typeof dataToSave] === undefined) {
          delete dataToSave[key as keyof typeof dataToSave];
        }
      });
      
      await onSave(dataToSave);
      setValidatingMessage('');
      onClose();
    } catch (error) {
      console.error('Error saving certificate:', error);
      setValidatingMessage('');
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
                    <label htmlFor="nombreEmpresa" className="form-label required-asterisk">
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
                      required
                    />
                    <div className="field-help">Nombre asociado a estos certificados.</div>
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
                    <label htmlFor="correo" className="form-label required-asterisk">
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
                      required
                    />
                    <div className="field-help">Email de contacto.</div>
                  </div>
                  <div className="col-md-6">
                    <label htmlFor="telefono" className="form-label required-asterisk">
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
                      required
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
                <div className="d-flex align-items-center gap-3">
                  {validatingMessage && (
                    <div className="text-primary small d-flex align-items-center">
                      <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                      <span>{validatingMessage}</span>
                    </div>
                  )}
                  <div>
                    <button type="button" className="btn btn-secondary me-2" onClick={onClose} disabled={loading}>
                      Cancelar
                    </button>
                    <button type="submit" className="btn btn-success" disabled={loading}>
                      {loading ? 'Procesando...' : 'Guardar'}
                    </button>
                  </div>
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
