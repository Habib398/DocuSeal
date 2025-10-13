// Configuración de API - Detectar automáticamente si estamos en Cloudflare o local
const API_URL = (() => {
  const currentOrigin = window.location.origin;
  // Si estamos en un dominio de Cloudflare o el mismo origen, usar rutas relativas
  if (currentOrigin && currentOrigin.includes('trycloudflare.com')) {
    return currentOrigin + '/api';
  }
  // Si estamos en localhost con Vite (puerto 3000), usar proxy relativo
  if (currentOrigin && currentOrigin.includes('localhost:3000')) {
    return '/api'; // El proxy de Vite redirigirá a localhost:8002
  }
  // Si estamos en localhost accediendo al HTML directamente, usar el puerto del admin
  if (currentOrigin && currentOrigin.includes('localhost:8002')) {
    return currentOrigin + '/api';
  }
  // Fallback: API Admin en puerto 8002
  return 'http://localhost:8002/api';
})();

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  name: string;
  email: string;
  password: string;
  confirm_password: string;
}

export interface User {
  id: number;
  name: string;
  email: string;
}

export interface ApiResponse<T> {
  success: boolean;
  detail?: string;
  user?: T;
}

class ApiClient {
  private baseURL: string;

  constructor() {
    this.baseURL = API_URL;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Error en la solicitud');
      }

      return data;
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  }

  async login(credentials: LoginCredentials): Promise<ApiResponse<User>> {
    return this.request<User>('/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });
  }

  async register(data: RegisterData): Promise<ApiResponse<User>> {
    return this.request<User>('/register', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Métodos para certificados
  async getAllCertificados(): Promise<Certificate[]> {
    const response = await fetch(`${this.baseURL}/v1/certificados/`);
    if (!response.ok) throw new Error('Error al cargar certificados');
    return response.json();
  }

  async getCertificadosInactivos(): Promise<Certificate[]> {
    const response = await fetch(`${this.baseURL}/v1/certificados/inactivos`);
    if (!response.ok) throw new Error('Error al cargar certificados inactivos');
    return response.json();
  }

  async createCertificado(data: CertificateFormData): Promise<Certificate> {
    const response = await fetch(`${this.baseURL}/v1/certificados/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error('Error al crear certificado');
    return response.json();
  }

  async updateCertificado(id: number, data: CertificateFormData): Promise<Certificate> {
    const response = await fetch(`${this.baseURL}/v1/certificados/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error('Error al actualizar certificado');
    return response.json();
  }

  async deleteCertificado(id: number): Promise<void> {
    const response = await fetch(`${this.baseURL}/v1/certificados/${id}`, {
      method: 'DELETE',
    });
    if (!response.ok) throw new Error('Error al desactivar certificado');
  }

  async reactivarCertificado(id: number): Promise<void> {
    const response = await fetch(`${this.baseURL}/v1/certificados/${id}/reactivar`, {
      method: 'PATCH',
    });
    if (!response.ok) throw new Error('Error al reactivar certificado');
  }
}

export interface Certificate {
  id: number;
  usuarioPAC: string;
  contrasenaPAC: string;
  nombreEmpresa?: string;
  noCertificado: string;
  vigencia: string;
  correo?: string;
  telefono?: string;
  CER: string;
  KEY: string;
  activo?: boolean;
}

export interface CertificateFormData {
  usuarioPAC: string;
  contrasenaPAC: string;
  nombreEmpresa?: string;
  noCertificado: string;
  vigencia: string;
  correo?: string;
  telefono?: string;
  CER: string;
  KEY: string;
}

export const apiClient = new ApiClient();
