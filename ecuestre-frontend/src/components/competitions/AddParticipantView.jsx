// src/components/competitions/AddParticipantView.jsx

import React, { useState, useEffect, useContext } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import Button from '../common/Button';
import Input from '../common/Input';
import { CompetitionContext } from '../../context/CompetitionContext';
import { fetchRiders, fetchHorses, fetchCategories, assignParticipant } from '../../services/api';
import useOffline from '../../hooks/useOffline';

const AddParticipantView = () => {
  const { competitionId } = useParams();
  const navigate = useNavigate();
  const { currentCompetition, loading, error, loadCompetition } = useContext(CompetitionContext);
  const { isOnline } = useOffline();
  
  // Estados para datos del formulario
  const [riders, setRiders] = useState([]);
  const [horses, setHorses] = useState([]);
  const [categories, setCategories] = useState([]);
  const [formData, setFormData] = useState({
    rider_id: '',
    horse_id: '',
    category_id: '',
    number: '',
    order: ''
  });
  
  // Estados para búsquedas
  const [riderSearch, setRiderSearch] = useState('');
  const [horseSearch, setHorseSearch] = useState('');
  
  // Estados para errores y carga
  const [formErrors, setFormErrors] = useState({});
  const [submitError, setSubmitError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  
  // Cargar datos de la competencia
  useEffect(() => {
    loadCompetition(parseInt(competitionId));
  }, [competitionId, loadCompetition]);
  
  // Cargar jinetes, caballos y categorías
  useEffect(() => {
    const loadFormData = async () => {
      setIsLoading(true);
      try {
        // Cargar datos iniciales
        const [ridersRes, horsesRes, categoriesRes] = await Promise.all([
          fetchRiders(),
          fetchHorses(),
          fetchCategories()
        ]);
        
        setRiders(ridersRes.data);
        setHorses(horsesRes.data);
        setCategories(categoriesRes.data);
      } catch (error) {
        console.error('Error al cargar datos iniciales:', error);
        setSubmitError('Error al cargar los datos necesarios');
      } finally {
        setIsLoading(false);
      }
    };
    
    loadFormData();
  }, []);
  
  // Manejar cambios en los campos del formulario
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Limpiar error para este campo
    if (formErrors[name]) {
      setFormErrors(prev => ({
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
    
    setFormErrors(newErrors);
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
        throw new Error('No hay conexión a internet. No se puede añadir el participante.');
      }
      
      // Enviar datos al servidor
      await assignParticipant(competitionId, formData);
      
      // Redirigir a detalles de la competencia
      navigate(`/competitions/${competitionId}`);
    } catch (error) {
      console.error('Error al añadir participante:', error);
      
      const errorMessage = error.response?.data?.message || 
                          error.message || 
                          'Error al añadir el participante. Inténtelo nuevamente.';
      
      setSubmitError(errorMessage);
    } finally {
      setIsSubmitting(false);
    }
  };
  
  // Formatear fecha para mostrar
  const formatDate = (dateString) => {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString('es-BO', options);
  };
  
  // Si está cargando, mostrar indicador
  if (loading || isLoading) {
    return <LoadingIndicator>Cargando datos...</LoadingIndicator>;
  }
  
  // Si hay error, mostrar mensaje
  if (error) {
    return (
      <ErrorContainer>
        <ErrorMessage>{error}</ErrorMessage>
        <Button onClick={() => navigate('/competitions')} variant="primary">
          Volver a Competencias
        </Button>
      </ErrorContainer>
    );
  }
  
  // Si no hay competencia, mostrar mensaje
  if (!currentCompetition) {
    return (
      <ErrorContainer>
        <ErrorMessage>No se encontró la competencia</ErrorMessage>
        <Button onClick={() => navigate('/competitions')} variant="primary">
          Volver a Competencias
        </Button>
      </ErrorContainer>
    );
  }
  
  return (
    <Container>
      <PageTitle>Añadir Participante</PageTitle>
      
      <CompetitionInfoCard>
        <CompetitionName>{currentCompetition.name}</CompetitionName>
        <CompetitionDetails>
          {currentCompetition.location} • {formatDate(currentCompetition.start_date)} 
          {currentCompetition.end_date !== currentCompetition.start_date && 
            ` - ${formatDate(currentCompetition.end_date)}`}
        </CompetitionDetails>
      </CompetitionInfoCard>
      
      <FormContainer>
        <FormTitle>Detalles del Participante</FormTitle>
        
        {submitError && <ErrorMessage>{submitError}</ErrorMessage>}
        
        <form onSubmit={handleSubmit}>
          <FormGrid>
            <div>
              <LabelContainer>
                <Label htmlFor="rider_id">Jinete</Label>
                {formErrors.rider_id && <ErrorText>{formErrors.rider_id}</ErrorText>}
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
                {formErrors.horse_id && <ErrorText>{formErrors.horse_id}</ErrorText>}
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
                {formErrors.category_id && <ErrorText>{formErrors.category_id}</ErrorText>}
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
              {isSubmitting ? 'Añadiendo...' : 'Añadir Participante'}
            </Button>
          </ActionButtons>
        </form>
      </FormContainer>
      
      {!isOnline && (
        <OfflineIndicator>
          Modo Offline - No es posible añadir participantes sin conexión a internet
        </OfflineIndicator>
      )}
    </Container>
  );
};

// Estilos para el componente
const Container = styled.div`
  max-width: 1000px;
  margin: 0 auto;
`;

const PageTitle = styled.h1`
  font-family: ${props => props.theme.fonts.heading};
  color: ${props => props.theme.colors.primary};
  margin-bottom: 24px;
`;

const CompetitionInfoCard = styled.div`
  background-color: ${props => props.theme.colors.background};
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 24px;
  border-left: 4px solid ${props => props.theme.colors.primary};
`;

const CompetitionName = styled.h2`
  font-family: ${props => props.theme.fonts.heading};
  margin: 0 0 4px;
  font-size: 18px;
`;

const CompetitionDetails = styled.div`
  color: ${props => props.theme.colors.gray};
  font-size: 14px;
`;

const FormContainer = styled.div`
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12);
  padding: 24px;
  margin-bottom: 24px;
`;

const FormTitle = styled.h2`
  font-family: ${props => props.theme.fonts.heading};
  color: ${props => props.theme.colors.primary};
  margin-bottom: 24px;
  font-size: 18px;
`;

const FormGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px;
`;

const LabelContainer = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
`;

const Label = styled.label`
  font-weight: 500;
`;

const ErrorText = styled.span`
  color: ${props => props.theme.colors.error};
  font-size: 12px;
`;

const Select = styled.select`
  width: 100%;
  padding: 16px;
  border: 1px solid ${props => props.theme.colors.lightGray};
  border-radius: 8px;
  font-family: ${props => props.theme.fonts.main};
  font-size: 16px;
  margin-bottom: 16px;
  
  &:focus {
    border-color: ${props => props.theme.colors.primary};
    outline: none;
  }
`;

const SearchContainer = styled.div`
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
`;

const ActionButtons = styled.div`
  display: flex;
  justify-content: flex-end;
  gap: 16px;
  margin-top: 24px;
`;

const LoadingIndicator = styled.div`
  text-align: center;
  padding: 32px;
  color: ${props => props.theme.colors.gray};
`;

const ErrorContainer = styled.div`
  max-width: 1000px;
  margin: 0 auto;
  text-align: center;
  padding: 32px;
`;

const ErrorMessage = styled.div`
  background-color: ${props => props.theme.colors.errorLight};
  color: ${props => props.theme.colors.error};
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 24px;
`;

const OfflineIndicator = styled.div`
  background-color: ${props => props.theme.colors.warning};
  color: white;
  padding: 8px 16px;
  text-align: center;
  border-radius: 4px;
  margin-top: 16px;
  margin-bottom: 16px;
`;

export default AddParticipantView;