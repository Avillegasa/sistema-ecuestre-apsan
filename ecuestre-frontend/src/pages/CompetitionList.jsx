// src/pages/CompetitionList.jsx
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import styled from 'styled-components';
import Layout from '../components/layout/Layout';
import Button from '../components/common/Button';
import Input from '../components/common/Input';
import { fetchCompetitions } from '../services/api';
import useOffline from '../hooks/useOffline';

// Contenedor principal
const CompetitionsContainer = styled.div`
  max-width: 1200px;
  margin: 0 auto;
`;

// Cabecera de la página
const PageHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: ${props => props.theme.spacing.lg};
  flex-wrap: wrap;
  gap: ${props => props.theme.spacing.md};
  
  @media (max-width: ${props => props.theme.breakpoints.tablet}) {
    flex-direction: column;
    align-items: flex-start;
  }
`;

const PageTitle = styled.h1`
  font-family: ${props => props.theme.fonts.heading};
  color: ${props => props.theme.colors.primary};
  margin: 0;
`;

// Filtros
const FiltersContainer = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: ${props => props.theme.spacing.md};
  margin-bottom: ${props => props.theme.spacing.lg};
  background-color: ${props => props.theme.colors.white};
  padding: ${props => props.theme.spacing.md};
  border-radius: ${props => props.theme.borderRadius.medium};
  box-shadow: ${props => props.theme.shadows.small};
`;

const SearchInput = styled(Input)`
  flex: 1;
  min-width: 250px;
`;

const FilterSelect = styled.select`
  font-family: ${props => props.theme.fonts.main};
  padding: ${props => props.theme.spacing.sm} ${props => props.theme.spacing.md};
  border-radius: ${props => props.theme.borderRadius.small};
  border: 1px solid ${props => props.theme.colors.lightGray};
  min-width: 150px;
  height: 44px;
  
  &:focus {
    border-color: ${props => props.theme.colors.primary};
    outline: none;
  }
`;

// Grilla de competencias
const CompetitionsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: ${props => props.theme.spacing.lg};
  margin-bottom: ${props => props.theme.spacing.xl};
`;

// Tarjeta de competencia
const CompetitionCard = styled.div`
  background-color: ${props => props.theme.colors.white};
  border-radius: ${props => props.theme.borderRadius.medium};
  box-shadow: ${props => props.theme.shadows.small};
  overflow: hidden;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  
  &:hover {
    transform: translateY(-5px);
    box-shadow: ${props => props.theme.shadows.medium};
  }
`;

const CardHeader = styled.div`
  background-color: ${props => {
    switch (props.status) {
      case 'active': return props.theme.colors.success;
      case 'pending': return props.theme.colors.warning;
      case 'completed': return props.theme.colors.gray;
      case 'cancelled': return props.theme.colors.error;
      default: return props.theme.colors.primary;
    }
  }};
  color: ${props => props.theme.colors.white};
  padding: ${props => props.theme.spacing.md};
`;

const CardStatus = styled.span`
  font-size: ${props => props.theme.fontSizes.small};
  font-weight: 500;
  text-transform: uppercase;
`;

const CardTitle = styled.h2`
  font-family: ${props => props.theme.fonts.heading};
  margin: ${props => props.theme.spacing.xs} 0 0;
  font-size: ${props => props.theme.fontSizes.large};
`;

const CardBody = styled.div`
  padding: ${props => props.theme.spacing.md};
`;

const CardLocation = styled.div`
  display: flex;
  align-items: center;
  margin-bottom: ${props => props.theme.spacing.md};
  color: ${props => props.theme.colors.gray};
  
  &:before {
    content: "📍";
    margin-right: ${props => props.theme.spacing.xs};
  }
`;

const CardDate = styled.div`
  display: flex;
  align-items: center;
  margin-bottom: ${props => props.theme.spacing.md};
  color: ${props => props.theme.colors.gray};
  
  &:before {
    content: "📅";
    margin-right: ${props => props.theme.spacing.xs};
  }
`;

const CardFooter = styled.div`
  padding: ${props => props.theme.spacing.md};
  border-top: 1px solid ${props => props.theme.colors.lightGray};
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const ParticipantsCount = styled.span`
  font-size: ${props => props.theme.fontSizes.small};
  color: ${props => props.theme.colors.gray};
  
  &:before {
    content: "👥";
    margin-right: ${props => props.theme.spacing.xs};
  }
`;

// Estado de carga
const LoadingMessage = styled.div`
  text-align: center;
  padding: ${props => props.theme.spacing.xl};
  color: ${props => props.theme.colors.gray};
`;

// Mensaje de error
const ErrorMessage = styled.div`
  background-color: ${props => props.theme.colors.errorLight};
  color: ${props => props.theme.colors.error};
  padding: ${props => props.theme.spacing.md};
  border-radius: ${props => props.theme.borderRadius.medium};
  margin-bottom: ${props => props.theme.spacing.lg};
`;

// Mensaje de no hay datos
const EmptyMessage = styled.div`
  text-align: center;
  padding: ${props => props.theme.spacing.xl};
  color: ${props => props.theme.colors.gray};
  background-color: ${props => props.theme.colors.background};
  border-radius: ${props => props.theme.borderRadius.medium};
`;

// Formatear fecha
const formatDate = (dateString) => {
  const options = { year: 'numeric', month: 'long', day: 'numeric' };
  return new Date(dateString).toLocaleDateString('es-BO', options);
};

// Traducir estado
const translateStatus = (status) => {
  const statusMap = {
    'pending': 'Pendiente',
    'active': 'Activa',
    'completed': 'Completada',
    'cancelled': 'Cancelada'
  };
  return statusMap[status] || status;
};

/**
 * Pantalla de listado de competencias
 */
const CompetitionList = () => {
  const [competitions, setCompetitions] = useState([]);
  const [filteredCompetitions, setFilteredCompetitions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const { isOnline } = useOffline();
  
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      
      try {
        const response = await fetchCompetitions();
        const competitionsData = response.data;
        
        // Guardar competencias para uso offline
        if (isOnline) {
          try {
            const { saveCompetitionData } = await import('../services/offline');
            for (const competition of competitionsData) {
              await saveCompetitionData(competition);
            }
          } catch (err) {
            console.error("Error guardando datos offline:", err);
          }
        }
        
        setCompetitions(competitionsData);
        setFilteredCompetitions(competitionsData);
      } catch (err) {
        console.error("Error fetching competitions:", err);
        
        // Si está offline, intentar cargar desde almacenamiento local
        if (!isOnline) {
          try {
            const { getOfflineCompetitions } = await import('../services/offline');
            const offlineData = await getOfflineCompetitions();
            if (offlineData && offlineData.length > 0) {
              setCompetitions(offlineData);
              setFilteredCompetitions(offlineData);
            } else {
              setError("No hay datos disponibles offline");
            }
          } catch (offlineErr) {
            setError("No se pudieron cargar los datos: " + err.message);
          }
        } else {
          setError("Error al cargar competencias: " + err.message);
        }
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, [isOnline]);
  
  // Filtrar competencias cuando cambian los filtros
  useEffect(() => {
    let result = [...competitions];
    
    // Filtrar por búsqueda (nombre o ubicación)
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      result = result.filter(
        comp => comp.name.toLowerCase().includes(query) || 
               comp.location.toLowerCase().includes(query)
      );
    }
    
    // Filtrar por estado
    if (statusFilter !== 'all') {
      result = result.filter(comp => comp.status === statusFilter);
    }
    
    setFilteredCompetitions(result);
  }, [searchQuery, statusFilter, competitions]);
  
  // Manejar cambio en el campo de búsqueda
  const handleSearchChange = (e) => {
    setSearchQuery(e.target.value);
  };
  
  // Manejar cambio en el filtro de estado
  const handleStatusFilterChange = (e) => {
    setStatusFilter(e.target.value);
  };
  
  // Si está cargando, mostrar mensaje
  if (loading) {
    return (
      <Layout>
        <CompetitionsContainer>
          <PageHeader>
            <PageTitle>Competencias</PageTitle>
          </PageHeader>
          <LoadingMessage>Cargando competencias...</LoadingMessage>
        </CompetitionsContainer>
      </Layout>
    );
  }
  
  return (
    <Layout>
      <CompetitionsContainer>
        <PageHeader>
          <PageTitle>Competencias</PageTitle>
          <Button 
            as={Link} 
            to="/competitions/new" 
            variant="primary"
          >
            Nueva Competencia
          </Button>
        </PageHeader>
        
        {error && <ErrorMessage>{error}</ErrorMessage>}
        
        <FiltersContainer>
          <SearchInput
            id="search"
            placeholder="Buscar por nombre o ubicación"
            value={searchQuery}
            onChange={handleSearchChange}
            fullWidth
          />
          
          <FilterSelect 
            value={statusFilter} 
            onChange={handleStatusFilterChange}
          >
            <option value="all">Todos los estados</option>
            <option value="pending">Pendientes</option>
            <option value="active">Activas</option>
            <option value="completed">Completadas</option>
            <option value="cancelled">Canceladas</option>
          </FilterSelect>
        </FiltersContainer>
        
        {filteredCompetitions.length > 0 ? (
          <CompetitionsGrid>
            {filteredCompetitions.map(competition => (
              <CompetitionCard key={competition.id}>
                <CardHeader status={competition.status}>
                  <CardStatus>{translateStatus(competition.status)}</CardStatus>
                  <CardTitle>{competition.name}</CardTitle>
                </CardHeader>
                
                <CardBody>
                  <CardLocation>{competition.location}</CardLocation>
                  <CardDate>
                    {formatDate(competition.start_date)} 
                    {competition.end_date !== competition.start_date && 
                      ` - ${formatDate(competition.end_date)}`}
                  </CardDate>
                </CardBody>
                
                <CardFooter>
                  <ParticipantsCount>
                    {competition.participant_count || 0} participantes
                  </ParticipantsCount>
                  
                  <Button 
                    as={Link} 
                    to={`/competitions/${competition.id}`} 
                    variant="outline" 
                    size="small"
                  >
                    Ver Detalles
                  </Button>
                </CardFooter>
              </CompetitionCard>
            ))}
          </CompetitionsGrid>
        ) : (
          <EmptyMessage>
            No se encontraron competencias con los filtros actuales.
          </EmptyMessage>
        )}
      </CompetitionsContainer>
    </Layout>
  );
};

export default CompetitionList;