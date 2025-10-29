import React from 'react';
import { Certificate } from '../services/apiClient';

interface CertificatesTableProps {
  certificates: Certificate[];
  selectedId: number | null;
  onSelectCertificate: (cert: Certificate) => void;
}

const CertificatesTable: React.FC<CertificatesTableProps> = ({
  certificates,
  selectedId,
  onSelectCertificate,
}) => {
  const getVigenciaBadgeClass = (vigencia: string): string => {
    const fechaVigencia = new Date(vigencia);
    const hoy = new Date();
    const diasRestantes = Math.ceil(
      (fechaVigencia.getTime() - hoy.getTime()) / (1000 * 60 * 60 * 24)
    );

    if (diasRestantes < 0) return 'bg-danger';
    if (diasRestantes < 30) return 'bg-warning';
    return 'bg-success';
  };

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES');
  };

  if (certificates.length === 0) {
    return (
      <div className="panel-box">
        <div className="table-responsive">
          <table className="table table-hover align-middle mb-0 table-blue">
            <thead>
              <tr>
                <th>ID</th>
                <th>Usuario PAC</th>
                <th>Empresa</th>
                <th>No. Certificado</th>
                <th>Vigencia</th>
                <th>Modo</th>
                <th>Correo</th>
                <th>Teléfono</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td colSpan={8} className="text-center text-muted py-4">
                  <i className="fas fa-inbox fa-2x mb-2 d-block"></i>
                  No hay certificados registrados
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    );
  }

  return (
    <div className="panel-box">
      <div className="table-responsive">
        <table className="table table-hover align-middle mb-0 table-blue" id="certificadosTable">
          <thead>
            <tr>
              <th>ID</th>
              <th>Usuario PAC</th>
              <th>Empresa</th>
              <th>No. Certificado</th>
              <th>Vigencia</th>
              <th>Modo</th>
              <th>Correo</th>
              <th>Teléfono</th>
            </tr>
          </thead>
          <tbody id="certificadosTableBody">
            {certificates.map((cert) => (
              <tr
                key={cert.id}
                data-id={cert.id}
                className={selectedId === cert.id ? 'selected-row' : ''}
                onClick={() => onSelectCertificate(cert)}
                style={{ cursor: 'pointer' }}
              >
                <td>{cert.id}</td>
                <td>{cert.usuarioPAC}</td>
                <td>{cert.nombreEmpresa || '-'}</td>
                <td>{cert.noCertificado}</td>
                <td>
                  <span className={`badge ${getVigenciaBadgeClass(cert.vigencia)}`}>
                    {formatDate(cert.vigencia)}
                  </span>
                </td>
                <td>
                  <span className={`badge ${cert.pruebas !== false ? 'bg-info' : 'bg-primary'}`}>
                    {cert.pruebas !== false ? 'Pruebas' : 'Producción'}
                  </span>
                </td>
                <td>{cert.correo || '-'}</td>
                <td>{cert.telefono || '-'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default CertificatesTable;
