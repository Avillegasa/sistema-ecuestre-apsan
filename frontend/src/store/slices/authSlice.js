
// frontend/src/store/slices/authSlice.js

import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import authService from '../../services/authService';

// Obtener token y usuario del localStorage si existen
const token = localStorage.getItem('token');
const refreshToken = localStorage.getItem('refreshToken');
const userJSON = localStorage.getItem('user');
const user = userJSON ? JSON.parse(userJSON) : null;

// Estado inicial
const initialState = {
  user: user,
  token: token,
  refreshToken: refreshToken,
  isAuthenticated: !!token,
  isLoading: false,
  error: null,
};

// Thunks para operaciones asíncronas
export const login = createAsyncThunk(
  'auth/login',
  async (credentials, { rejectWithValue }) => {
    try {
      const response = await authService.login(credentials);
      // Guardar datos en localStorage
      localStorage.setItem('token', response.token);
      localStorage.setItem('refreshToken', response.refreshToken);
      localStorage.setItem('user', JSON.stringify(response.user));
      return response;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Error en la autenticación' });
    }
  }
);

export const logout = createAsyncThunk(
  'auth/logout',
  async (_, { rejectWithValue }) => {
    try {
      await authService.logout();
      // Limpiar localStorage
      localStorage.removeItem('token');
      localStorage.removeItem('refreshToken');
      localStorage.removeItem('user');
      return true;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Error al cerrar sesión' });
    }
  }
);

export const refreshAccessToken = createAsyncThunk(
  'auth/refreshToken',
  async (_, { getState, rejectWithValue }) => {
    try {
      const { refreshToken } = getState().auth;
      if (!refreshToken) {
        throw new Error('No hay token de refresco disponible');
      }
      const response = await authService.refreshToken(refreshToken);
      // Actualizar token en localStorage
      localStorage.setItem('token', response.token);
      return response;
    } catch (error) {
      // Si falla el refresh, cerrar sesión
      localStorage.removeItem('token');
      localStorage.removeItem('refreshToken');
      localStorage.removeItem('user');
      return rejectWithValue(error.response?.data || { message: 'Error al refrescar token' });
    }
  }
);

// Slice de autenticación
const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    resetAuthError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Login
      .addCase(login.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(login.fulfilled, (state, action) => {
        state.isLoading = false;
        state.isAuthenticated = true;
        state.user = action.payload.user;
        state.token = action.payload.token;
        state.refreshToken = action.payload.refreshToken;
      })
      .addCase(login.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload;
      })
      
      // Logout
      .addCase(logout.pending, (state) => {
        state.isLoading = true;
      })
      .addCase(logout.fulfilled, (state) => {
        state.isLoading = false;
        state.isAuthenticated = false;
        state.user = null;
        state.token = null;
        state.refreshToken = null;
      })
      .addCase(logout.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload;
      })
      
      // Refresh Token
      .addCase(refreshAccessToken.fulfilled, (state, action) => {
        state.token = action.payload.token;
      })
      .addCase(refreshAccessToken.rejected, (state) => {
        state.isAuthenticated = false;
        state.user = null;
        state.token = null;
        state.refreshToken = null;
      });
  },
});

export const { resetAuthError } = authSlice.actions;
export default authSlice.reducer;