// Configuración de la API

const API_BASE_URL = (function() {
    try {
        const origin = window.location.origin;
        if (origin && origin.startsWith('http')) {
            // Si estamos en el mismo dominio, usar rutas relativas
            return origin;
        }
    } catch (e) { /* ignore */ }
    // Fallback: Admin API en puerto 8002 local
    return 'http://localhost:8002';
})();

// Clase para manejar las llamadas a la API
class ApiClient {
    constructor(baseUrl) {
        this.baseUrl = baseUrl;
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
            ...options,
        };

        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API Request Error:', error);
            throw error;
        }
    }

    // Métodos para certificados
    async getAllCertificados() {
        return this.request('/api/v1/certificados/');
    }

    async getCertificadoByUsuario(usuario) {
        return this.request(`/api/v1/certificados/usuario/${encodeURIComponent(usuario)}`);
    }

    async getCertificadoByNumero(numero) {
        return this.request(`/api/v1/certificados/numero/${encodeURIComponent(numero)}`);
    }

    async createCertificado(certificadoData) {
        return this.request('/api/v1/certificados/', {
            method: 'POST',
            body: JSON.stringify(certificadoData),
        });
    }

    async updateCertificado(id, certificadoData) {
        return this.request(`/api/v1/certificados/${id}`, {
            method: 'PUT',
            body: JSON.stringify(certificadoData),
        });
    }

    async deleteCertificado(id) {
        return this.request(`/api/v1/certificados/${id}`, {
            method: 'DELETE',
        });
    }

    // Métodos para timbrado (si se necesitan en el futuro)
    async timbrarXML(xmlData, usuarioPAC, contrasenaPAC, pruebas = true) {
        return this.request('/timbrado/timbrar/', {
            method: 'POST',
            body: JSON.stringify({
                xml: xmlData,
                usuario_pac: usuarioPAC,
                contrasena_pac: contrasenaPAC,
                pruebas: pruebas
            }),
        });
    }

    async sellarXML(data) {
        return this.request('/timbrado/sellar/', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    async timbrarYSellarXML(data) {
        return this.request('/timbrado/timbrarSellar/', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    // Método para verificar la salud de la API
    async healthCheck() {
        try {
            const response = await fetch(`${this.baseUrl.replace('/api/v1', '')}/health`);
            return response.ok;
        } catch (error) {
            return false;
        }
    }
}

// Instancia global del cliente de API
const apiClient = new ApiClient(API_BASE_URL);