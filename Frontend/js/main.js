// Variables globales
let certificados = [];
let currentCertificadoId = null; // usado para editar
let deleteId = null; // usado para eliminar
let selectedRow = null; // referencia visual
let selectedCert = null; // objeto certificado seleccionado

// Inicialización cuando se carga la página
document.addEventListener('DOMContentLoaded', function() {
    loadCertificados();
    checkApiConnection();
});

// Verificar conexión con la API
async function checkApiConnection() {
    const isHealthy = await apiClient.healthCheck();
    if (!isHealthy) {
        showAlert('warning', 'No se pudo conectar con el servidor backend. Verifique que esté ejecutándose en http://localhost:8000');
    }
}

// Cargar todos los certificados
async function loadCertificados() {
    try {
        showLoading(true);
        certificados = await apiClient.getAllCertificados();
        renderCertificados();
        showAlert('success', `Se cargaron ${certificados.length} certificados correctamente.`, 3000);
    } catch (error) {
        showAlert('danger', `Error al cargar certificados: ${error.message}`);
        console.error('Error loading certificados:', error);
    } finally {
        showLoading(false);
    }
}

// Renderizar la tabla de certificados
function renderCertificados() {
    const tbody = document.getElementById('certificadosTableBody');
    tbody.innerHTML = '';

    if (certificados.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="4" class="text-center text-muted py-4">
                    <i class="fas fa-inbox fa-2x mb-2 d-block"></i>
                    No hay certificados registrados
                </td>
            </tr>
        `;
        return;
    }

    certificados.forEach(cert => {
        const row = document.createElement('tr');
        row.setAttribute('data-id', cert.id);
        row.innerHTML = `
            <td>${cert.id}</td>
            <td>${cert.usuarioPAC}</td>
            <td>${cert.noCertificado}</td>
            <td><span class="badge ${getVigenciaBadgeClass(cert.vigencia)}">${formatDate(cert.vigencia)}</span></td>
        `;

        row.addEventListener('click', () => selectRow(row, cert));
        tbody.appendChild(row);
    });
}

function selectRow(row, cert) {
    // quitar selección previa
    if (selectedRow) selectedRow.classList.remove('selected-row');
    row.classList.add('selected-row');
    selectedRow = row;
    selectedCert = cert;
    // habilitar botones
    toggleActionButtons(true);
}

function toggleActionButtons(enabled) {
    ['btnEditar','btnEliminar','btnVer'].forEach(id => {
        const btn = document.getElementById(id);
        if (btn) btn.disabled = !enabled;
    });
}

// Obtener clase CSS para el badge de vigencia
function getVigenciaBadgeClass(vigencia) {
    const fechaVigencia = new Date(vigencia);
    const hoy = new Date();
    const diasRestantes = Math.ceil((fechaVigencia - hoy) / (1000 * 60 * 60 * 24));
    
    if (diasRestantes < 0) return 'bg-danger';
    if (diasRestantes < 30) return 'bg-warning';
    return 'bg-success';
}

// Formatear fecha
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES');
}

// Mostrar modal para agregar certificado
function openAddModal() {
    currentCertificadoId = null;
    document.getElementById('modalTitle').textContent = 'Agregar Certificado';
    document.getElementById('certificadoForm').reset();
    document.getElementById('certificadoId').value = '';
}

// Editar certificado
function editSelected() {
    if (!selectedCert) return;
    const cert = selectedCert;
    currentCertificadoId = cert.id;
    document.getElementById('modalTitleText').textContent = 'Editar Certificado';
    document.getElementById('certificadoId').value = cert.id;
    document.getElementById('usuarioPAC').value = cert.usuarioPAC;
    document.getElementById('contrasenaPAC').value = cert.contrasenaPAC;
    document.getElementById('nombreEmpresa').value = cert.nombreEmpresa || '';
    document.getElementById('noCertificado').value = cert.noCertificado;
    document.getElementById('vigencia').value = cert.vigencia;
    document.getElementById('CER').value = cert.CER;
    document.getElementById('KEY').value = cert.KEY;
    document.getElementById('Certificado').value = cert.Certificado;
    const modal = new bootstrap.Modal(document.getElementById('certificadoModal'));
    modal.show();
}

// Ver detalles del certificado
function viewSelected() {
    if (!selectedCert) return;
    const cert = selectedCert;
    const details = `
        <strong>ID:</strong> ${cert.id}<br>
        <strong>Usuario PAC:</strong> ${cert.usuarioPAC}<br>
        <strong>Nombre de la empresa:</strong> ${cert.nombreEmpresa || '-'}<br>
        <strong>No. Certificado:</strong> ${cert.noCertificado}<br>
        <strong>Vigencia:</strong> ${formatDate(cert.vigencia)}<br>
        <strong>CER (50c):</strong> ${cert.CER.substring(0,50)}...<br>
        <strong>KEY (50c):</strong> ${cert.KEY.substring(0,50)}...<br>
        <strong>Certificado (50c):</strong> ${cert.Certificado.substring(0,50)}...
    `;
    showAlert('info', details, 10000);
}

// Eliminar certificado
function deleteSelected() {
    if (!selectedCert) return;
    deleteId = selectedCert.id;
    const modal = new bootstrap.Modal(document.getElementById('confirmDeleteModal'));
    modal.show();
}

// Confirmar eliminación
async function confirmDelete() {
    if (!deleteId) return;

    try {
    await apiClient.deleteCertificado(deleteId);
        showAlert('success', 'Certificado eliminado correctamente.');
        
        // Cerrar modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('confirmDeleteModal'));
        modal.hide();
        
        // Recargar certificados
    await loadCertificados();
    selectedCert = null; selectedRow = null; toggleActionButtons(false);
        
    } catch (error) {
        showAlert('danger', `Error al eliminar certificado: ${error.message}`);
        console.error('Error deleting certificado:', error);
    } finally {
        deleteId = null;
    }
}

// Guardar certificado (crear o actualizar)
async function saveCertificado() {
    const form = document.getElementById('certificadoForm');
    
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }

    const certificadoData = {
        usuarioPAC: document.getElementById('usuarioPAC').value,
        nombreEmpresa: document.getElementById('nombreEmpresa')?.value || '',
        contrasenaPAC: document.getElementById('contrasenaPAC').value,
        noCertificado: document.getElementById('noCertificado').value,
        vigencia: document.getElementById('vigencia').value,
        CER: document.getElementById('CER').value,
        KEY: document.getElementById('KEY').value,
        Certificado: document.getElementById('Certificado').value
    };

    try {
        if (currentCertificadoId) {
            // Actualizar
            await apiClient.updateCertificado(currentCertificadoId, certificadoData);
            showAlert('success', 'Certificado actualizado correctamente.');
        } else {
            // Crear
            await apiClient.createCertificado(certificadoData);
            showAlert('success', 'Certificado creado correctamente.');
        }

        // Cerrar modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('certificadoModal'));
        modal.hide();
        
        // Recargar certificados
    await loadCertificados();
    selectedCert = null; selectedRow = null; toggleActionButtons(false);

    } catch (error) {
        showAlert('danger', `Error al guardar certificado: ${error.message}`);
        console.error('Error saving certificado:', error);
    }
}

// Mostrar alertas
function showAlert(type, message, duration = 5000) {
    const alertsContainer = document.getElementById('alerts');
    const alertId = `alert-${Date.now()}`;
    
    const alertHTML = `
        <div id="${alertId}" class="alert alert-${type} alert-dismissible fade show fade-in" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    alertsContainer.insertAdjacentHTML('beforeend', alertHTML);
    
    // Auto-ocultar después del tiempo especificado
    if (duration > 0) {
        setTimeout(() => {
            const alert = document.getElementById(alertId);
            if (alert) {
                const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
                bsAlert.close();
            }
        }, duration);
    }
}

// Mostrar/ocultar loading
function showLoading(show) {
    // Aquí podrías agregar un spinner de carga si lo deseas
    const loadingText = show ? 'Cargando...' : '';
    // Por ahora, simplemente cambiaremos el cursor
    document.body.style.cursor = show ? 'wait' : 'default';
}

// Event listeners para el modal
document.getElementById('certificadoModal').addEventListener('show.bs.modal', function () {
    if (!currentCertificadoId) {
        document.getElementById('modalTitleText').textContent = 'Agregar Certificado';
        openAddModal();
    }
});

// Limpiar formulario al cerrar modal
document.getElementById('certificadoModal').addEventListener('hidden.bs.modal', function (event) {
    document.getElementById('certificadoForm').reset();
    currentCertificadoId = null;
});

// Funciones de utilidad para búsqueda (para implementar en el futuro)
function searchCertificados(query) {
    const q = query.trim().toLowerCase();
    if (!q) { renderCertificados(); toggleActionButtons(false); selectedCert=null; selectedRow=null; return; }
    const filtered = certificados.filter(cert =>
        cert.usuarioPAC.toLowerCase().includes(q) ||
        cert.noCertificado.toLowerCase().includes(q)
    );
    const tbody = document.getElementById('certificadosTableBody');
    tbody.innerHTML = '';
    if (filtered.length === 0) {
        tbody.innerHTML = `<tr><td colspan="4" class="text-center text-muted py-4">Sin resultados</td></tr>`;
        return;
    }
    filtered.forEach(cert => {
        const row = document.createElement('tr');
        row.setAttribute('data-id', cert.id);
        row.innerHTML = `
            <td>${cert.id}</td>
            <td>${cert.usuarioPAC}</td>
            <td>${cert.noCertificado}</td>
            <td><span class="badge ${getVigenciaBadgeClass(cert.vigencia)}">${formatDate(cert.vigencia)}</span></td>`;
        row.addEventListener('click', () => selectRow(row, cert));
        tbody.appendChild(row);
    });
}

// Eventos UI nuevos
document.getElementById('btnEditar')?.addEventListener('click', editSelected);
document.getElementById('btnVer')?.addEventListener('click', viewSelected);
document.getElementById('btnEliminar')?.addEventListener('click', deleteSelected);
document.getElementById('btnBuscar')?.addEventListener('click', () => searchCertificados(document.getElementById('searchInput').value));
document.getElementById('searchInput')?.addEventListener('keyup', (e) => { if (e.key==='Enter') searchCertificados(e.target.value); });
document.getElementById('btnAgregar')?.addEventListener('click', () => { currentCertificadoId=null; selectedCert=null; });

// salir (placeholder)
document.getElementById('btnSalir')?.addEventListener('click', () => {
    showAlert('warning','Función de salir aún no implementada.',2500);
});