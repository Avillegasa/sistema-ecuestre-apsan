// src/components/competitions/CompetitionForm.jsx
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import Input from '../common/Input';
import Button from '../common/Button';
import { createCompetition, updateCompetition } from '../../services/api';
import useOffline from '../../hooks/useOffline';

// Contenedor del formulario
const FormContainer = styled.div`
  background-color: ${props => props.theme.colors.white};
  border-radius: ${props => props.theme.borderRadius.medium};
  box-shadow: ${props => props.theme.shadows.small};
  padding: ${props => props.theme.spacing.lg};
  margin-bottom: ${props => props.theme.spacing.lg};
`;

// Título del formulario
const FormTitle = styled.h2`
  font-family: ${props => props.theme.fonts.heading};
  color: ${props => props.theme.colors.primary};
  margin-bottom: ${props => props.theme.spacing.lg};
`;

// Grid para campos
const FormGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: ${props => props.theme.spacing.md};
`;

// Campo de texto para descripción
const TextArea = styled.textarea`
  width: 100%;
  min-height: 150px;
  padding: ${props => props.theme.spacing.md};
  border: 1px solid ${props => props.theme.colors.lightGray};
  border-radius: ${props => props.theme.borderRadius.medium};
  font-family: ${props => props.theme.fonts.main};
  font-size: ${props => props.theme.fontSizes.medium};
  margin-bottom: ${props => props.theme.spacing.md};
  resize: vertical;
  
  &:focus {
    border-color: ${props => props.theme.colors.primary};
    outline: none;
  }
`;

// Select para estados
const Select = styled.select`
  width: 100%;
  padding: ${props => props.theme.spacing.md};
  border: 1px solid ${props => props.theme.colors.lightGray};
  border-radius: ${props => props.theme.borderRadius.medium};
  font-family: ${props => props.theme.fonts.main};
  font-size: ${props => props.theme.fontSizes.medium};
  margin-bottom: ${props => props.theme.spacing.md};
  
  &:focus {
    border-color: ${props => props.theme.colors.primary};
    outline: none;
  }
`;

// Grupo para checkbox
const CheckboxGroup = styled.div`
  margin-bottom: ${props => props.theme.spacing.md};
`;

const CheckboxLabel = styled.label`
  display: flex;
  align-items: center;
  cursor: pointer;
`;

const CheckboxInput = styled.input`
  margin-right: ${props => props.theme.spacing.sm};
`;

// Mensaje de error
const ErrorMessage = styled.div`
  background-color: ${props => props.theme.colors.errorLight};
  color: ${props => props.theme.colors.error};
  padding: ${props => props.theme.spacing.md};
  border-radius: ${props => props.theme.borderRadius.medium};
  margin-bottom: ${props => props.theme.spacing.lg};
`;

// Botones de acción
const ActionButtons = styled.div`
  display: flex;
  justify-content: flex-end;
  gap: ${props => props.theme.spacing.md};
  margin-top: ${props => props.theme.spacing.lg};
`;

/**
 * Formulario para crear o editar competencias
 * 
 * @param {Object} props - Propiedades del componente
 * @param {Object} [props.initialData] - Datos iniciales para edición
 * @param {boolean} [props.isEditing=false] - Si se está editando una competencia existente
 */
const CompetitionForm = ({ initialData, isEditing = false }) => {
  const navigate = useNavigate();
  const { isOnline } = useOffline();
  
  // Estado para los campos del formulario
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    location: '',
    start_date: '',
    end_date: '',
    status: 'pending',
    is_public: true
  });
  
  // Estado para errores
  const [errors, setErrors] = useState({});
  const [submitError, setSubmitError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  // Inicializar formulario con datos si está editando
  useEffect(() => {
    if (isEditing && initialData) {
      // Formatear fechas para input date
      const formatDateForInput = (dateString) => {
        const date = new Date(dateString);
        return date.toISOString().split('T')[0];
      };
      
      setFormData({
        name: initialData.name || '',
        description: initialData.description || '',
        location: initialData.location || '',
        start_date: formatDateForInput(initialData.start_date) || '',
        end_date: formatDateForInput(initialData.end_date) || '',
        status: initialData.status || 'pending',
        is_public: initialData.is_public !== undefined ? initialData.is_public : true
      });
    }
  }, [isEditing, initialData]);
  
  // Manejar cambios en los campos del formulario
  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
    
    // Limpiar error para este campo
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: null
      }));
    }
  };
  
  // Validar formulario
  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.name.trim()) {
      newErrors.name = 'El nombre es obligatorio';
    }
    
    if (!formData.location.trim()) {
      newErrors.location = 'La ubicación es obligatoria';
    }
    
    if (!formData.start_date) {
      newErrors.start_date = 'La fecha de inicio es obligatoria';
    }
    
    if (!formData.end_date) {
      newErrors.end_date = 'La fecha de fin es obligatoria';
    } else if (formData.end_date < formData.start_date) {
      newErrors.end_date = 'La fecha de fin debe ser posterior a la fecha de inicio';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };
  
  // Manejar envío del formulario
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validar formulario
    if (!validateForm()) {
      return;
    }
    
    setIsSubmitting(true);
    setSubmitError(null);
    
    try {
      if (!isOnline) {
        throw new Error('No hay conexión a internet. No se puede guardar la competencia.');
      }
      
      let response;
      
      if (isEditing) {
        response = await updateCompetition(initialData.id, formData);
      } else {
        response = await createCompetition(formData);
      }
      
      const competitionId = isEditing ? initialData.id : response.data.id;
      
      // Redireccionar a la página de detalle
      navigate(`/competitions/${competitionId}`);
    } catch (error) {
      console.error('Error al guardar la competencia:', error);
      
      const errorMessage = error.response?.data?.message || 
                          error.message || 
                          'Error al guardar la competencia. Inténtelo nuevamente.';
      
      setSubmitError(errorMessage);
    } finally {
      setIsSubmitting(false);
    }
  };
  
  return (
    <FormContainer>
      <FormTitle>{isEditing ? 'Editar Competencia' : 'Nueva Competencia'}</FormTitle>
      
      {submitError && <ErrorMessage>{submitError}</ErrorMessage>}
      
      <form onSubmit={handleSubmit}>
        <FormGrid>
          <Input
            id="name"
            name="name"
            label="Nombre de la Competencia"
            value={formData.name}
            onChange={handleChange}
            placeholder="Ej. Torneo Nacional de Adiestramiento 2025"
            required
            error={errors.name}
            fullWidth
          />
          
          <Input
            id="location"
            name="location"
            label="Ubicación"
            value={formData.location}
            onChange={handleChange}
            placeholder="Ej. La Paz, Bolivia"
            required
            error={errors.location}
            fullWidth
          />
          
          <Input
            id="start_date"
            name="start_date"
            label="Fecha de Inicio"
            type="date"
            value={formData.start_date}
            onChange={handleChange}
            required
            error={errors.start_date}
            fullWidth
          />
          
          <Input
            id="end_date"
            name="end_date"
            label="Fecha de Fin"
            type="date"
            value={formData.end_date}
            onChange={handleChange}
            required
            error={errors.end_date}
            fullWidth
          />
        </FormGrid>
        
        <div>
          <label htmlFor="description">Descripción</label>
          <TextArea
            id="description"
            name="description"
            value={formData.description}
            onChange={handleChange}
            placeholder="Descripción detallada de la competencia..."
          />
        </div>
        
        <FormGrid>
          <div>
            <label htmlFor="status">Estado</label>
            <Select
              id="status"
              name="status"
              value={formData.status}
              onChange={handleChange}
            >
              <option value="pending">Pendiente</option>
              <option value="active">Activa</option>
              <option value="completed">Completada</option>
              <option value="cancelled">Cancelada</option>
            </Select>
          </div>
          
          <CheckboxGroup>
            <CheckboxLabel>
              <CheckboxInput
                type="checkbox"
                name="is_public"
                checked={formData.is_public}
                onChange={handleChange}
              />
              Competencia Pública
            </CheckboxLabel>
            <p style={{ fontSize: '14px', color: '#666', marginTop: '4px' }}>
              Las competencias públicas serán visibles para todos los usuarios.
            </p>
          </CheckboxGroup>
        </FormGrid>
        
        <ActionButtons>
          <Button
            type="button"
            variant="outline"
            onClick={() => navigate(isEditing ? `/competitions/${initialData.id}` : '/competitions')}
          >
            Cancelar
          </Button>
          
          <Button
            type="submit"
            variant="primary"
            disabled={isSubmitting || !isOnline}
          >
            {isSubmitting 
              ? 'Guardando...' 
              : isEditing 
                ? 'Actualizar Competencia' 
                : 'Crear Competencia'
            }
          </Button>
        </ActionButtons>
      </form>
    </FormContainer>
  );
};

export default CompetitionForm;