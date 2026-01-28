// API service for the Todo application

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://sadiakhan123-todo-phase-2.hf.space';

class ApiService {
  constructor() {
    this.baseURL = API_BASE_URL;
  }

  // Generic request method
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;

    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    // Add auth token if available
    const token = localStorage.getItem('access_token');
    if (token && !config.headers.Authorization) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    try {
      const response = await fetch(url, config);

      // If response is not ok, throw error
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        let errorMessage = `HTTP error! status: ${response.status}`;

        if (errorData.detail) {
          if (Array.isArray(errorData.detail)) {
            // Handle Pydantic validation errors array
            errorMessage = errorData.detail.map(err => err.msg || err.detail || JSON.stringify(err)).join(', ');
          } else if (typeof errorData.detail === 'string') {
            // Handle simple string error
            errorMessage = errorData.detail;
          } else {
            // Handle other object types
            errorMessage = JSON.stringify(errorData.detail);
          }
        } else if (errorData.message) {
          errorMessage = errorData.message;
        }

        throw new Error(errorMessage);
      }

      // For successful responses that don't return JSON (like DELETE)
      if (response.status === 204) {
        return null;
      }

      return await response.json();
    } catch (error) {
      console.error('API request error:', error);
      throw error;
    }
  }

  // Authentication methods
  async register(userData) {
    return this.request('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  async login(credentials) {
    return this.request('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });
  }

  async logout() {
    // Remove token from localStorage
    localStorage.removeItem('access_token');
    // In a real JWT implementation, we might call a logout endpoint
    // but for stateless JWT, removing the token is sufficient
    return { message: 'Successfully logged out' };
  }

  async getProfile() {
    return this.request('/api/auth/me');
  }

  // Task methods
  async getTasks() {
    return this.request('/api/tasks');
  }

  async createTask(taskData) {
    return this.request('/api/tasks', {
      method: 'POST',
      body: JSON.stringify(taskData),
    });
  }

  async getTask(taskId) {
    return this.request(`/api/tasks/${taskId}`);
  }

  async updateTask(taskId, taskData) {
    return this.request(`/api/tasks/${taskId}`, {
      method: 'PUT',
      body: JSON.stringify(taskData),
    });
  }

  async toggleTaskCompletion(taskId) {
    return this.request(`/api/tasks/${taskId}/toggle`, {
      method: 'PATCH',
    });
  }

  async deleteTask(taskId) {
    return this.request(`/api/tasks/${taskId}`, {
      method: 'DELETE',
    });
  }
}

export default new ApiService();