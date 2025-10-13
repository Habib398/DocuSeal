import { useState, useEffect, useCallback } from 'react';
import { Certificate, CertificateFormData, apiClient } from '../services/apiClient';

interface UseCertificatesOptions {
  initialShowInactive?: boolean;
  onSuccess?: (message: string) => void;
  onError?: (message: string) => void;
}

export const useCertificates = (options: UseCertificatesOptions = {}) => {
  const { initialShowInactive = false, onSuccess, onError } = options;

  const [certificates, setCertificates] = useState<Certificate[]>([]);
  const [allCertificates, setAllCertificates] = useState<Certificate[]>([]);
  const [showInactive, setShowInactive] = useState(initialShowInactive);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const loadCertificates = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = showInactive
        ? await apiClient.getCertificadosInactivos()
        : await apiClient.getAllCertificados();
      
      setCertificates(data);
      setAllCertificates(data);
      
      // No mostrar alerta en la primera carga para evitar spam
      // const tipo = showInactive ? 'inactivos' : 'activos';
      // onSuccess?.(`Se cargaron ${data.length} certificados ${tipo} correctamente.`);
      
      return data;
    } catch (err) {
      const error = err as Error;
      setError(error);
      onError?.(`Error al cargar certificados: ${error.message}`);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, [showInactive, onError]);

  // Auto-load certificates when showInactive changes
  useEffect(() => {
    loadCertificates();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [showInactive]);

  const createCertificate = useCallback(async (data: CertificateFormData) => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await apiClient.createCertificado(data);
      onSuccess?.('Certificado creado correctamente.');
      await loadCertificates();
      return result;
    } catch (err) {
      const error = err as Error;
      setError(error);
      onError?.(`Error al crear certificado: ${error.message}`);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, [loadCertificates, onSuccess, onError]);

  const updateCertificate = useCallback(async (id: number, data: CertificateFormData) => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await apiClient.updateCertificado(id, data);
      onSuccess?.('Certificado actualizado correctamente.');
      await loadCertificates();
      return result;
    } catch (err) {
      const error = err as Error;
      setError(error);
      onError?.(`Error al actualizar certificado: ${error.message}`);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, [loadCertificates, onSuccess, onError]);

  const deleteCertificate = useCallback(async (id: number) => {
    setIsLoading(true);
    setError(null);
    try {
      await apiClient.deleteCertificado(id);
      onSuccess?.('Certificado desactivado correctamente.');
      await loadCertificates();
    } catch (err) {
      const error = err as Error;
      setError(error);
      const msg = error.message.toLowerCase();
      if (msg.includes('not found') || msg.includes('no encontrado') || msg.includes('404')) {
        onError?.('El certificado no existe o ya está inactivo.');
      } else {
        onError?.(`Error al desactivar certificado: ${error.message}`);
      }
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, [loadCertificates, onSuccess, onError]);

  const reactivateCertificate = useCallback(async (id: number) => {
    setIsLoading(true);
    setError(null);
    try {
      await apiClient.reactivarCertificado(id);
      onSuccess?.('Certificado reactivado correctamente.');
      await loadCertificates();
    } catch (err) {
      const error = err as Error;
      setError(error);
      const msg = error.message.toLowerCase();
      if (msg.includes('not found') || msg.includes('no encontrado') || msg.includes('404')) {
        onError?.('El certificado no existe o ya está activo.');
      } else {
        onError?.(`Error al reactivar certificado: ${error.message}`);
      }
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, [loadCertificates, onSuccess, onError]);

  const filterCertificates = useCallback((query: string) => {
    const trimmedQuery = query.trim().toLowerCase();
    if (!trimmedQuery) {
      setCertificates(allCertificates);
      return allCertificates;
    }

    const filtered = allCertificates.filter(
      (cert) =>
        cert.usuarioPAC.toLowerCase().includes(trimmedQuery) ||
        cert.noCertificado.toLowerCase().includes(trimmedQuery)
    );
    setCertificates(filtered);
    return filtered;
  }, [allCertificates]);

  const toggleShowInactive = useCallback((show: boolean) => {
    setShowInactive(show);
  }, []);

  return {
    certificates,
    allCertificates,
    showInactive,
    isLoading,
    error,
    loadCertificates,
    createCertificate,
    updateCertificate,
    deleteCertificate,
    reactivateCertificate,
    filterCertificates,
    toggleShowInactive,
  };
};
