// Authentication service for the Todo application

import api from './api';

class AuthService {
  // Check if user is authenticated
  isAuthenticated() {
    const token = localStorage.getItem('access_token');
    return !!token;
  }

  // Get current user profile
  async getCurrentUser() {
    try {
      return await api.getProfile();
    } catch (error) {
      console.error('Error getting current user:', error);
      this.logout(); // If token is invalid, logout user
      throw error;
    }
  }

  // Register a new user
  async register(userData) {
    try {
      const response = await api.register(userData);
      return response;
    } catch (error) {
      console.error('Registration error:', error);
      throw error;
    }
  }

  // Login user
  async login(credentials) {
    try {
      const response = await api.login(credentials);

      // Store token in localStorage
      if (response && response.access_token) {
        localStorage.setItem('access_token', response.access_token);
      }

      return response;
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  }

  // Logout user
  async logout() {
    try {
      await api.logout();
    } catch (error) {
      console.error('Logout error:', error);
      // Even if logout API call fails, we should still remove the token
    } finally {
      // Remove token from localStorage regardless of API call result
      localStorage.removeItem('access_token');
    }
  }

  // Get token
  getToken() {
    return localStorage.getItem('access_token');
  }

  // Set token
  setToken(token) {
    localStorage.setItem('access_token', token);
  }

  // Remove token
  removeToken() {
    localStorage.removeItem('access_token');
  }
}

export default new AuthService();