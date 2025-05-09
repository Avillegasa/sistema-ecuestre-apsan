// frontend/src/pages/auth/Login.js

import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate, Link } from 'react-router-dom';
import { Formik, Form, Field, ErrorMessage } from 'formik';
import * as Yup from 'yup';
import { 
  Container, 
  Box, 
  Typography, 
  TextField, 
  Button, 
  Alert, 
  CircularProgress,
  Paper
} from '@mui/material';
import { login, resetAuthError } from '../../store/slices/authSlice';

// Esquema de validación con Yup
const validationSchema = Yup.object({
  username: Yup.string()
    .required('El nombre de usuario es obligatorio'),
  password: Yup.string()
    .required('La contraseña es obligatoria')
});

const Login = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { isAuthenticated, isLoading, error, user } = useSelector(state => state.auth);
  const [showError, setShowError] = useState(false);

  // Limpiar errores al montar el componente
  useEffect(() => {
    dispatch(resetAuthError());
  }, [dispatch]);

  // Redireccionar si el usuario ya está autenticado
  useEffect(() => {
    if (isAuthenticated && user) {
      // Redireccionar según el tipo de usuario
      switch (user.tipo_usuario) {
        case 'admin':
          navigate('/admin');
          break;
        case 'juez':
          navigate('/juez');
          break;
        case 'jinete':
          navigate('/jinete');
          break;
        case 'entrenador':
          navigate('/entrenador');
          break;
        default:
          navigate('/');
      }
    }
  }, [isAuthenticated, user, navigate]);

  // Mostrar error si existe
  useEffect(() => {
    if (error) {
      setShowError(true);
      const timer = setTimeout(() => {
        setShowError(false);
      }, 5000);
      
      return () => clearTimeout(timer);
    }
  }, [error]);

  // Manejar el envío del formulario
  const handleSubmit = async (values) => {
    await dispatch(login(values));
  };

  return (
    <Container component="main" maxWidth="xs">
      <Box
        sx={{
          marginTop: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        <Paper 
          elevation={3} 
          sx={{ 
            p: 4, 
            width: '100%', 
            borderRadius: 2,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center'
          }}
        >
          <Typography component="h1" variant="h5" sx={{ mb: 3 }}>
            Sistema Ecuestre APSAN
          </Typography>
          
          <Typography component="h2" variant="h6" sx={{ mb: 3 }}>
            Iniciar Sesión
          </Typography>
          
          {showError && error && (
            <Alert severity="error" sx={{ width: '100%', mb: 3 }}>
              {error.message || 'Error al iniciar sesión. Verifica tus credenciales.'}
            </Alert>
          )}
          
          <Formik
            initialValues={{ username: '', password: '' }}
            validationSchema={validationSchema}
            onSubmit={handleSubmit}
          >
            {({ errors, touched }) => (
              <Form style={{ width: '100%' }}>
                <Box sx={{ mb: 3 }}>
                  <Field
                    as={TextField}
                    name="username"
                    label="Nombre de Usuario"
                    variant="outlined"
                    fullWidth
                    error={touched.username && Boolean(errors.username)}
                    helperText={touched.username && errors.username}
                  />
                </Box>
                
                <Box sx={{ mb: 3 }}>
                  <Field
                    as={TextField}
                    name="password"
                    label="Contraseña"
                    type="password"
                    variant="outlined"
                    fullWidth
                    error={touched.password && Boolean(errors.password)}
                    helperText={touched.password && errors.password}
                  />
                </Box>
                
                <Button
                  type="submit"
                  fullWidth
                  variant="contained"
                  color="primary"
                  disabled={isLoading}
                  sx={{ 
                    py: 1.5, 
                    fontSize: '1rem',
                    textTransform: 'none',
                    fontWeight: 'bold',
                    mb: 2
                  }}
                >
                  {isLoading ? <CircularProgress size={24} /> : 'Iniciar Sesión'}
                </Button>
                
                <Box sx={{ mt: 1, textAlign: 'center' }}>
                  <Typography variant="body2" color="textSecondary">
                    ¿Olvidaste tu contraseña? Contacta al administrador
                  </Typography>
                </Box>
              </Form>
            )}
          </Formik>
        </Paper>
        
        <Box sx={{ mt: 3 }}>
          <Typography variant="body2" color="textSecondary" align="center">
            © {new Date().getFullYear()} Sistema Ecuestre APSAN
          </Typography>
        </Box>
      </Box>
    </Container>
  );
};

export default Login;