// src/components/competitions/ParticipantForm.jsx
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import Input from '../common/Input';
import Button from '../common/Button';
import { fetchRiders, fetchHorses, fetchCategories, assignParticipant } from '../../services/api';
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

// Select personalizado
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

// Contenedor de label
const LabelContainer = styled.div`
  margin-bottom: ${props => props.theme.spacing.xs};
`;

const Label = styled.label`
  font-weight: 500;
`;

// Mensaje de error
const ErrorMessage = styled.div`
  background-color: ${props => props.theme.colors.errorLight};
  color: ${props => props.theme.colors.error};
  padding: ${props => props.theme.spacing.md};
  border-radius: ${props => props.theme.borderRadius.medium};
  margin-bottom: ${props => props.theme.spacing.lg};
`;

// Botones de búsqueda
const SearchContainer = styled.div`
  display: flex;
  gap: ${props => props.theme.spacing.sm};
  margin-bottom: ${props => props.theme.spacing.md};
`;

// Botones de acción
const ActionButtons = styled.div`
  display: flex;
  justify-content: flex-end;
  gap: ${props => props.theme.spacing.md};
  margin-top: ${props => props.theme.spacing.lg};
`;

/**
 * Formulario para asignar participantes a una competencia
 * 
 * @param {Object} props - Propiedades del componente
 * @param {number} props.competitionId - ID de la competencia
 * @param {Object} [props.initialData] - Datos iniciales para edición
 * @param {boolean} [props.isEditing=false] - Si se está editando un participante existente
 */
const ParticipantForm = ({ competitionId, initialData, isEditing = false }) => {
  const navigate = useNavigate();
  const { isOnline } = useOffline();
  
  // Estados para los datos
  const [riders, setRiders] = useState([]);
  const [horses, setHorses] = useState([]);
  const [categories, setCategories] = useState([]);
  
  // Estado para los campos del formulario
  const [formData, setFormData] = useState({
    rider_id: '',
    horse_id: '',
    category_id: '',
    number: '',
    order: ''
  });
  
  // Estado para búsquedas
  const [riderSearch, setRiderSearch] = useState('');
  const [horseSearch, setHorseSearch] = useState('');
  
  // Estado para errores
  const [errors, setErrors] = useState({});
  const [submitError, setSubmitError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  
  // Cargar datos iniciales
  useEffect(() => {
    const loadData = async () => {
      setIsLoading(true);
      try {
        // Cargar jinetes, caballos y categorías
        const [ridersRes, horsesRes, categoriesRes] = await Promise.all([
          fetchRiders(),
          fetchHorses(),
          fetchCategories()
        ]);
        
        setRiders(ridersRes.data);
        setHorses(horsesRes.data);
        setCategories(categoriesRes.data);
        
        // Si está editando, inicializar formulario con datos
        if (isEditing && initialData) {
          setFormData({
            rider_id: initialData.rider_id || '',
            horse_id: initialData.horse_id || '',
            category_id: initialData.category_id || '',
            number: initialData.number || '',
            order: initialData.order || ''
          });
        }
      } catch (error) {
        console.error('Error al cargar datos:', error);
        setSubmitError('Error al cargar los datos necesarios');
      } finally {
        setIsLoading(false);
      }
    };
    
    loadData();
  }, [isEditing, initialData]);
  
  // Manejar cambios en los campos del formulario
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Limpiar error para este campo
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: null
      }));
    }
  };
  
  // Manejar búsqueda de jinetes
  const handleRiderSearch = async () => {
    if (!riderSearch.trim()) return;
    
    try {
      const response = await fetchRiders({ search: riderSearch });
      setRiders(response.data);
    } catch (error) {
      console.error('Error al buscar jinetes:', error);
    }
  };
  
  // Manejar búsqueda de caballos
  const handleHorseSearch = async () => {
    if (!horseSearch.trim()) return;
    
    try {
      const response = await fetchHorses({ search: horseSearch });
      setHorses(response.data);
    } catch (error) {
      console.error('Error al buscar caballos:', error);
    }
  };
  
  // Validar formulario
  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.rider_id) {
      newErrors.rider_id = 'Debe seleccionar un jinete';
    }
    
    if (!formData.horse_id) {
      newErrors.horse_id = 'Debe seleccionar un caballo';
    }
    
    if (!formData.category_id) {
      newErrors.category_id = 'Debe seleccionar una categoría';
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
      throw new Error('No hay conexión a internet. No se puede guardar el participante.');
    }
    
    let response;
    
    if (isEditing) {
      // Lógica para actualizar participante
      const { updateParticipant } = await import('../../services/api');
      response = await updateParticipant(initialData.id, formData);
    } else {
      response = await assignParticipant(competitionId, formData);
    }
    
    // Redireccionar a la página de detalle de la competencia
    navigate(`/competitions/${competitionId}`);
  } catch (error) {
    console.error('Error al guardar el participante:', error);
    
    const errorMessage = error.response?.data?.message || 
                        error.message || 
                        'Error al guardar el participante. Inténtelo nuevamente.';
    
    setSubmitError(errorMessage);
  } finally {
    setIsSubmitting(false);
  }
};
  
  // Si está cargando, mostrar mensaje
  if (isLoading) {
    return (
      <FormContainer>
        <div>Cargando datos...</div>
      </FormContainer>
    );
  }
  
  return (
    <FormContainer>
      <FormTitle>
        {isEditing ? 'Editar Participante' : 'Añadir Participante a la Competencia'}
      </FormTitle>
      
      {submitError && <ErrorMessage>{submitError}</ErrorMessage>}
      
      <form onSubmit={handleSubmit}>
        <FormGrid>
          <div>
            <LabelContainer>
              <Label htmlFor="rider_id">Jinete</Label>
              {errors.rider_id && <span style={{ color: 'red', marginLeft: '8px' }}>{errors.rider_id}</span>}
            </LabelContainer>
            
            <SearchContainer>
              <Input
                id="rider_search"
                placeholder="Buscar jinete..."
                value={riderSearch}
                onChange={(e) => setRiderSearch(e.target.value)}
              />
              <Button 
                type="button" 
                variant="outline" 
                size="small"
                onClick={handleRiderSearch}
              >
                Buscar
              </Button>
            </SearchContainer>
            
            <Select
              id="rider_id"
              name="rider_id"
              value={formData.rider_id}
              onChange={handleChange}
            >
              <option value="">Seleccione un jinete</option>
              {riders.map(rider => (
                <option key={rider.id} value={rider.id}>
                  {rider.first_name} {rider.last_name}
                </option>
              ))}
            </Select>
          </div>
          
          <div>
            <LabelContainer>
              <Label htmlFor="horse_id">Caballo</Label>
              {errors.horse_id && <span style={{ color: 'red', marginLeft: '8px' }}>{errors.horse_id}</span>}
            </LabelContainer>
            
            <SearchContainer>
              <Input
                id="horse_search"
                placeholder="Buscar caballo..."
                value={horseSearch}
                onChange={(e) => setHorseSearch(e.target.value)}
              />
              <Button 
                type="button" 
                variant="outline" 
                size="small"
                onClick={handleHorseSearch}
              >
                Buscar
              </Button>
            </SearchContainer>
            
            <Select
              id="horse_id"
              name="horse_id"
              value={formData.horse_id}
              onChange={handleChange}
            >
              <option value="">Seleccione un caballo</option>
              {horses.map(horse => (
                <option key={horse.id} value={horse.id}>
                  {horse.name} ({horse.breed || 'Raza desconocida'})
                </option>
              ))}
            </Select>
          </div>
          
          <div>
            <LabelContainer>
              <Label htmlFor="category_id">Categoría</Label>
              {errors.category_id && <span style={{ color: 'red', marginLeft: '8px' }}>{errors.category_id}</span>}
            </LabelContainer>
            
            <Select
              id="category_id"
              name="category_id"
              value={formData.category_id}
              onChange={handleChange}
            >
              <option value="">Seleccione una categoría</option>
              {categories.map(category => (
                <option key={category.id} value={category.id}>
                  {category.name} ({category.code})
                </option>
              ))}
            </Select>
          </div>
          
          <Input
            id="number"
            name="number"
            label="Número de Participante"
            type="number"
            min="1"
            value={formData.number}
            onChange={handleChange}
            placeholder="Automático si se deja vacío"
            helperText="Si se deja vacío, se asignará automáticamente"
          />
          
          <Input
            id="order"
            name="order"
            label="Orden de Salida"
            type="number"
            min="1"
            value={formData.order}
            onChange={handleChange}
            placeholder="Automático si se deja vacío"
            helperText="Si se deja vacío, se asignará automáticamente"
          />
        </FormGrid>
        
        <ActionButtons>
          <Button
            type="button"
            variant="outline"
            onClick={() => navigate(`/competitions/${competitionId}`)}
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
                ? 'Actualizar Participante' 
                : 'Añadir Participante'
            }
          </Button>
        </ActionButtons>
      </form>
    </FormContainer>
  );
};

export default ParticipantForm;