import React, { useState } from 'react';
import TopBar from '../components/TopBar';
import SearchBar from '../components/BarraBusqueda';
import CertificatesTable from '../components/TablaCertificados';
import ActionButtons from '../components/AccionBtn';
import CertificateModal from '../components/ModalCertificado';
import ConfirmModal from '../components/ConfirmarModal';
import Alerts from '../components/Alertas';
import { Certificate, CertificateFormData } from '../services/apiClient';
import { useCertificates } from '../hooks/useCertificates';
import { useAlerts } from '../hooks/useAlerts';
import '../styles/certificates.css';

const CertificatesPage: React.FC = () => {
  // Hooks
  const { alerts, addAlert, dismissAlert } = useAlerts();
  const {
    certificates,
    showInactive,
    // isLoading, // Por ahora no se usa
    createCertificate,
    updateCertificate,
    deleteCertificate,
    reactivateCertificate,
    filterCertificates,
    toggleShowInactive,
  } = useCertificates({
    onSuccess: (message) => addAlert('success', message),
    onError: (message) => addAlert('danger', message),
  });

  // Local state
  const [selectedCertificate, setSelectedCertificate] = useState<Certificate | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  // Modals
  const [showCertModal, setShowCertModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [showReactivateModal, setShowReactivateModal] = useState(false);
  const [editingCertificate, setEditingCertificate] = useState<Certificate | null>(null);

  const handleSelectCertificate = (cert: Certificate) => {
    if (selectedCertificate?.id === cert.id) {
      setSelectedCertificate(null);
    } else {
      setSelectedCertificate(cert);
    }
  };

  const handleSearch = () => {
    filterCertificates(searchQuery);
    setSelectedCertificate(null);
  };

  const handleToggleInactive = (show: boolean) => {
    toggleShowInactive(show);
    setSelectedCertificate(null);
    setSearchQuery('');
  };

  const handleAddNew = () => {
    setEditingCertificate(null);
    setShowCertModal(true);
  };

  const handleEdit = () => {
    if (!selectedCertificate) return;
    setEditingCertificate(selectedCertificate);
    setShowCertModal(true);
  };

  const handleDelete = () => {
    if (!selectedCertificate) return;
    if (showInactive) {
      setShowReactivateModal(true);
    } else {
      setShowDeleteModal(true);
    }
  };

  const handleSaveCertificate = async (data: CertificateFormData) => {
    try {
      if (editingCertificate) {
        await updateCertificate(editingCertificate.id, data);
      } else {
        await createCertificate(data);
      }
      setShowCertModal(false);
      setEditingCertificate(null);
      setSelectedCertificate(null);
    } catch (error) {
      // Error already handled by hook
    }
  };

  const handleConfirmDelete = async () => {
    if (!selectedCertificate) return;
    try {
      await deleteCertificate(selectedCertificate.id);
      setShowDeleteModal(false);
      setSelectedCertificate(null);
    } catch (error) {
      // Error already handled by hook
    }
  };

  const handleConfirmReactivate = async () => {
    if (!selectedCertificate) return;
    try {
      await reactivateCertificate(selectedCertificate.id);
      setShowReactivateModal(false);
      setSelectedCertificate(null);
    } catch (error) {
      // Error already handled by hook
    }
  };

  return (
    <>
      <TopBar />
      <Alerts alerts={alerts} onDismiss={dismissAlert} />

      <div className="container-fluid py-4">
        {/* Encabezado y búsqueda */}
        <div className="row mb-3 align-items-center">
          <div className="col-lg-9 mb-2 mb-lg-0">
            <br />
            <h2 className="page-title">Certificados PAC</h2>
          </div>
          <div className="col-lg-9 order-2 order-lg-1">
            <SearchBar
              searchQuery={searchQuery}
              onSearchChange={setSearchQuery}
              onSearch={handleSearch}
              showInactive={showInactive}
              onToggleInactive={handleToggleInactive}
            />
          </div>
        </div>

        <div className="row g-4">
          {/* Tabla */}
          <div className="col-lg-9">
            <CertificatesTable
              certificates={certificates}
              selectedId={selectedCertificate?.id || null}
              onSelectCertificate={handleSelectCertificate}
            />
          </div>

          {/* Acciones */}
          <ActionButtons
            hasSelection={selectedCertificate !== null}
            showInactive={showInactive}
            onAdd={handleAddNew}
            onEdit={handleEdit}
            onDelete={handleDelete}
          />
        </div>
      </div>

      {/* Modals */}
      <CertificateModal
        show={showCertModal}
        certificate={editingCertificate}
        onClose={() => {
          setShowCertModal(false);
          setEditingCertificate(null);
        }}
        onSave={handleSaveCertificate}
      />

      <ConfirmModal
        show={showDeleteModal}
        title="Confirmar desactivación"
        message="¿Seguro que deseas desactivar el certificado seleccionado? El certificado quedará inactivo pero se conservará si se desea reactivar."
        confirmText="Desactivar"
        confirmVariant="warning"
        onConfirm={handleConfirmDelete}
        onCancel={() => setShowDeleteModal(false)}
      />

      <ConfirmModal
        show={showReactivateModal}
        title="Confirmar reactivación"
        message="¿Seguro que deseas reactivar el certificado seleccionado? El certificado volverá a estar disponible para su uso."
        confirmText="Reactivar"
        confirmVariant="success"
        onConfirm={handleConfirmReactivate}
        onCancel={() => setShowReactivateModal(false)}
      />
    </>
  );
};

export default CertificatesPage;