// API service for the Todo application

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

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
    const response = await this.request('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });

    // After successful registration, user ID might be in the response
    if (response && response.id) {
      localStorage.setItem('user_id', response.id);
    }

    return response;
  }

  async login(credentials) {
    const response = await this.request('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });

    // Get user profile to retrieve user ID
    if (response && response.access_token) {
      // Store the token first
      localStorage.setItem('access_token', response.access_token);

      try {
        // Get user profile to retrieve user ID
        const profile = await this.getProfile();
        if (profile && profile.id) {
          localStorage.setItem('user_id', profile.id);
        }
      } catch (error) {
        console.error('Error fetching user profile after login:', error);
      }
    }

    return response;
  }

  async logout() {
    // Remove token and user ID from localStorage
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_id');
    // In a real JWT implementation, we might call a logout endpoint
    // but for stateless JWT, removing the token is sufficient
    return { message: 'Successfully logged out' };
  }

  async getProfile() {
    return this.request('/api/auth/me');
  }

  // Task methods
  async getTasks() {
    // Get user ID from localStorage or however it's stored
    const userId = localStorage.getItem('user_id'); // Assuming user ID is stored after login
    if (!userId) {
      throw new Error('User ID not found. Please log in again.');
    }
    return this.request(`/api/${userId}/tasks`);
  }

  async createTask(taskData) {
    // Get user ID from localStorage or however it's stored
    const userId = localStorage.getItem('user_id'); // Assuming user ID is stored after login
    if (!userId) {
      throw new Error('User ID not found. Please log in again.');
    }
    return this.request(`/api/${userId}/tasks`, {
      method: 'POST',
      body: JSON.stringify(taskData),
    });
  }

  async getTask(taskId) {
    // Get user ID from localStorage or however it's stored
    const userId = localStorage.getItem('user_id'); // Assuming user ID is stored after login
    if (!userId) {
      throw new Error('User ID not found. Please log in again.');
    }
    return this.request(`/api/${userId}/tasks/${taskId}`);
  }

  async updateTask(taskId, taskData) {
    // Get user ID from localStorage or however it's stored
    const userId = localStorage.getItem('user_id'); // Assuming user ID is stored after login
    if (!userId) {
      throw new Error('User ID not found. Please log in again.');
    }
    return this.request(`/api/${userId}/tasks/${taskId}`, {
      method: 'PUT',
      body: JSON.stringify(taskData),
    });
  }

  async toggleTaskCompletion(taskId) {
    // Get user ID from localStorage or however it's stored
    const userId = localStorage.getItem('user_id'); // Assuming user ID is stored after login
    if (!userId) {
      throw new Error('User ID not found. Please log in again.');
    }
    return this.request(`/api/${userId}/tasks/${taskId}/complete`, {
      method: 'PATCH',
    });
  }

  async deleteTask(taskId) {
    // Get user ID from localStorage or however it's stored
    const userId = localStorage.getItem('user_id'); // Assuming user ID is stored after login
    if (!userId) {
      throw new Error('User ID not found. Please log in again.');
    }
    return this.request(`/api/${userId}/tasks/${taskId}`, {
      method: 'DELETE',
    });
  }
}

export default new ApiService();