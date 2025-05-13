
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import styled from 'styled-components';
import Button from '../common/Button';
import Input from '../common/Input';
import useOffline from '../../hooks/useOffline';
import { fetchCompetitions } from '../../services/api';

// Componente para mostrar una tarjeta de competencia individual
const CompetitionCard = ({ competition }) => {
  const formatDate = (dateString) => {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString('es-BO', options);
  };

  const translateStatus = (status) => {
    const statusMap = {
      'pending': 'Pendiente',
      'active': 'Activa',
      'completed': 'Completada',
      'cancelled': 'Cancelada'
    };
    return statusMap[status] || status;
  };

  return (
    <CardContainer>
      <CardHeader status={competition.status}>
        <StatusBadge>{translateStatus(competition.status)}</StatusBadge>
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
    </CardContainer>
  );
};

// Componente principal de listado de competencias
const CompetitionListView = () => {
  const [competitions, setCompetitions] = useState([]);
  const [filteredCompetitions, setFilteredCompetitions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const { isOnline } = useOffline();
  
  // Cargar competencias al montar el componente
  useEffect(() => {
    const loadCompetitions = async () => {
      setLoading(true);
      setError(null);
      
      try {
        const response = await fetchCompetitions();
        const data = response.data;
        
        // Guardar para uso offline si está online
        if (isOnline) {
          try {
            const { saveCompetitionData } = await import('../../services/offline');
            for (const competition of data) {
              await saveCompetitionData(competition);
            }
          } catch (err) {
            console.error("Error guardando datos offline:", err);
          }
        }
        
        setCompetitions(data);
        setFilteredCompetitions(data);
      } catch (err) {
        console.error("Error fetching competitions:", err);
        
        // Intentar cargar desde offline si no hay conexión
        if (!isOnline) {
          try {
            const { getOfflineCompetitions } = await import('../../services/offline');
            const offlineData = await getOfflineCompetitions();
            if (offlineData && offlineData.length > 0) {
              setCompetitions(offlineData);
              setFilteredCompetitions(offlineData);
            } else {
              setError("No hay datos disponibles offline");
            }
          } catch (offlineErr) {
            setError("Error al cargar datos offline: " + offlineErr.message);
          }
        } else {
          setError("Error al cargar competencias: " + err.message);
        }
      } finally {
        setLoading(false);
      }
    };
    
    loadCompetitions();
  }, [isOnline]);
  
  // Aplicar filtros cuando cambian
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
  
  // Manejadores de eventos
  const handleSearchChange = (e) => {
    setSearchQuery(e.target.value);
  };
  
  const handleStatusFilterChange = (e) => {
    setStatusFilter(e.target.value);
  };
  
  // Renderizado condicional basado en estado
  if (loading) {
    return <LoadingIndicator>Cargando competencias...</LoadingIndicator>;
  }
  
  return (
    <ContainerView>
      <HeaderSection>
        <PageTitle>Competencias</PageTitle>
        <Button 
          as={Link} 
          to="/competitions/new" 
          variant="primary"
        >
          Nueva Competencia
        </Button>
      </HeaderSection>
      
      {error && <ErrorMessage>{error}</ErrorMessage>}
      
      <FiltersSection>
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
      </FiltersSection>
      
      {filteredCompetitions.length > 0 ? (
        <CompetitionsGrid>
          {filteredCompetitions.map(competition => (
            <CompetitionCard 
              key={competition.id} 
              competition={competition} 
            />
          ))}
        </CompetitionsGrid>
      ) : (
        <EmptyMessage>
          No se encontraron competencias con los filtros actuales.
        </EmptyMessage>
      )}
      
      {!isOnline && (
        <OfflineIndicator>
          Modo Offline - Se están mostrando datos almacenados localmente
        </OfflineIndicator>
      )}
    </ContainerView>
  );
};

// Estilos para los componentes
const ContainerView = styled.div`
  max-width: 1200px;
  margin: 0 auto;
`;

const HeaderSection = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
  
  @media (max-width: 768px) {
    flex-direction: column;
    align-items: flex-start;
  }
`;

const PageTitle = styled.h1`
  font-family: ${props => props.theme.fonts.heading};
  color: ${props => props.theme.colors.primary};
  margin: 0;
`;

const FiltersSection = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 24px;
  background-color: white;
  padding: 16px;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12);
`;

const SearchInput = styled(Input)`
  flex: 1;
  min-width: 250px;
`;

const FilterSelect = styled.select`
  font-family: ${props => props.theme.fonts.main};
  padding: 8px 16px;
  border-radius: 4px;
  border: 1px solid ${props => props.theme.colors.lightGray};
  min-width: 150px;
  height: 44px;
`;

const CompetitionsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
`;

const CardContainer = styled.div`
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12);
  overflow: hidden;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  
  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
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
  color: white;
  padding: 16px;
`;

const StatusBadge = styled.span`
  font-size: 12px;
  font-weight: 500;
  text-transform: uppercase;
`;

const CardTitle = styled.h2`
  font-family: ${props => props.theme.fonts.heading};
  margin: 8px 0 0;
  font-size: 18px;
`;

const CardBody = styled.div`
  padding: 16px;
`;

const CardLocation = styled.div`
  display: flex;
  align-items: center;
  margin-bottom: 16px;
  color: ${props => props.theme.colors.gray};
  
  &:before {
    content: "📍";
    margin-right: 8px;
  }
`;

const CardDate = styled.div`
  display: flex;
  align-items: center;
  margin-bottom: 16px;
  color: ${props => props.theme.colors.gray};
  
  &:before {
    content: "📅";
    margin-right: 8px;
  }
`;

const CardFooter = styled.div`
  padding: 16px;
  border-top: 1px solid ${props => props.theme.colors.lightGray};
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const ParticipantsCount = styled.span`
  font-size: 14px;
  color: ${props => props.theme.colors.gray};
  
  &:before {
    content: "👥";
    margin-right: 8px;
  }
`;

const LoadingIndicator = styled.div`
  text-align: center;
  padding: 32px;
  color: ${props => props.theme.colors.gray};
`;

const ErrorMessage = styled.div`
  background-color: ${props => props.theme.colors.errorLight};
  color: ${props => props.theme.colors.error};
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 24px;
`;

const EmptyMessage = styled.div`
  text-align: center;
  padding: 32px;
  color: ${props => props.theme.colors.gray};
  background-color: ${props => props.theme.colors.background};
  border-radius: 8px;
`;

const OfflineIndicator = styled.div`
  background-color: ${props => props.theme.colors.warning};
  color: white;
  padding: 8px 16px;
  text-align: center;
  border-radius: 4px;
  margin-top: 16px;
`;

export default CompetitionListView;