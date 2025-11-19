/**
 * SelectPAC.tsx - Componente para seleccionar tipo de PAC
 * 
 * ESTADO: Preparado para implementación futura (Multi-PAC)
 * 
 * Este componente está listo para usar cuando se active el soporte multi-PAC.
 * Para activarlo:
 * 1. Descomentar el código en este archivo
 * 2. Descomentar el endpoint /v1/pacs/tipos en backend/app/api_admin/main.py
 * 3. Importar y usar este componente en ModalCertificado.tsx
 * 4. Agregar campo tipoPAC al formulario de certificados
 */

/*
import React, { useState, useEffect } from 'react';

interface PACInfo {
  id: string;
  nombre: string;
  descripcion: string;
  soporta_timbrado: boolean;
  soporta_cancelacion: boolean;
  requiere_configuracion_especial: boolean;
  activo: boolean;
}

interface SelectPACProps {
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
}

const SelectPAC: React.FC<SelectPACProps> = ({ value, onChange, disabled = false }) => {
  const [pacs, setPacs] = useState<PACInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchPACTypes();
  }, []);

  const fetchPACTypes = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch('/api/admin/v1/pacs/tipos', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          // Agregar token de autenticación si es necesario
          // 'Authorization': `Bearer ${token}`
        },
      });

      if (!response.ok) {
        throw new Error('Error al cargar tipos de PAC');
      }

      const data = await response.json();
      
      // Filtrar solo PACs activos
      const pacsActivos = data.pacs.filter((pac: PACInfo) => pac.activo);
      setPacs(pacsActivos);

      // Si no hay valor seleccionado, usar el default
      if (!value && data.default) {
        onChange(data.default);
      }

    } catch (err) {
      console.error('Error al cargar tipos de PAC:', err);
      setError('No se pudieron cargar los tipos de PAC');
      
      // Fallback: usar solo Comercio Digital
      setPacs([{
        id: 'comerciodigital',
        nombre: 'Comercio Digital',
        descripcion: 'PAC por defecto',
        soporta_timbrado: true,
        soporta_cancelacion: true,
        requiere_configuracion_especial: false,
        activo: true
      }]);
      
      if (!value) {
        onChange('comerciodigital');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    onChange(e.target.value);
  };

  const selectedPAC = pacs.find(pac => pac.id === value);

  if (loading) {
    return (
      <div className="form-group">
        <label htmlFor="tipoPAC">
          Tipo de PAC <span className="text-danger">*</span>
        </label>
        <select className="form-control" disabled>
          <option>Cargando...</option>
        </select>
      </div>
    );
  }

  return (
    <div className="form-group">
      <label htmlFor="tipoPAC">
        Tipo de PAC <span className="text-danger">*</span>
      </label>
      
      <select
        id="tipoPAC"
        className="form-control"
        value={value}
        onChange={handleChange}
        disabled={disabled}
        required
      >
        <option value="">-- Seleccione un PAC --</option>
        {pacs.map((pac) => (
          <option key={pac.id} value={pac.id}>
            {pac.nombre}
          </option>
        ))}
      </select>

      {selectedPAC && (
        <small className="form-text text-muted">
          {selectedPAC.descripcion}
          {selectedPAC.requiere_configuracion_especial && (
            <span className="text-warning">
              {' '}⚠️ Requiere configuración especial
            </span>
          )}
        </small>
      )}

      {error && (
        <small className="form-text text-danger">
          {error}
        </small>
      )}

      <small className="form-text text-muted mt-2">
        <strong>Capacidades:</strong>
        {selectedPAC && (
          <span>
            {' '}
            {selectedPAC.soporta_timbrado && '✓ Timbrado '}
            {selectedPAC.soporta_cancelacion && '✓ Cancelación'}
          </span>
        )}
      </small>
    </div>
  );
};

export default SelectPAC;
*/

/**
 * PLACEHOLDER TEMPORAL
 * Este export evita errores de compilación mientras el componente está comentado
 */
export default null;
