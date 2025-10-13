import React from 'react';

interface ActionButtonsProps {
  hasSelection: boolean;
  showInactive: boolean;
  onAdd: () => void;
  onEdit: () => void;
  onDelete: () => void;
}

const ActionButtons: React.FC<ActionButtonsProps> = ({
  hasSelection,
  showInactive,
  onAdd,
  onEdit,
  onDelete,
}) => {
  const deleteButtonLabel = showInactive ? 'Reactivar seleccionado' : 'Desactivar seleccionado';
  const deleteButtonIcon = showInactive ? 'fa-check-circle' : 'fa-ban';

  return (
    <div className="col-lg-3 d-flex flex-column gap-2 actions-column">
      <button
        id="btnAgregar"
        className="btn btn-success btn-action"
        onClick={onAdd}
      >
        <i className="fas fa-plus me-1"></i>Agregar nuevo
      </button>
      <button
        id="btnEditar"
        className="btn btn-success btn-action"
        disabled={!hasSelection}
        onClick={onEdit}
      >
        <i className="fas fa-pen me-1"></i>Editar seleccionado
      </button>
      <button
        id="btnEliminar"
        className="btn btn-success btn-action"
        disabled={!hasSelection}
        onClick={onDelete}
      >
        <i className={`fas ${deleteButtonIcon} me-1`}></i>{deleteButtonLabel}
      </button>
    </div>
  );
};

export default ActionButtons;
