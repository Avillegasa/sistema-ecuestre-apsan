// src/components/rankings/RealtimeRankingTable.jsx
import React, { useState, useEffect, useRef } from 'react';
import styled, { css, keyframes } from 'styled-components';
import { formatPercentage } from '../../utils/formatters';
import { useRealtimeSync } from '../../hooks/useRealtimeSync';
// Importar componente de animación
import RankingAnimation from './RankingAnimation';

// Animaciones para los cambios de posición
const moveUp = keyframes`
  0% { transform: translateY(20px); opacity: 0.8; background-color: rgba(76, 255, 76, 0.2); }
  50% { background-color: rgba(76, 255, 76, 0.1); }
  100% { transform: translateY(0); opacity: 1; background-color: transparent; }
`;

const moveDown = keyframes`
  0% { transform: translateY(-20px); opacity: 0.8; background-color: rgba(255, 76, 76, 0.2); }
  50% { background-color: rgba(255, 76, 76, 0.1); }
  100% { transform: translateY(0); opacity: 1; background-color: transparent; }
`;

const highlight = keyframes`
  0% { background-color: rgba(255, 183, 77, 0.3); }
  50% { background-color: rgba(255, 183, 77, 0.2); }
  100% { background-color: transparent; }
`;

const pulse = keyframes`
  0% { box-shadow: 0 0 0 0 rgba(41, 98, 255, 0.4); }
  70% { box-shadow: 0 0 0 10px rgba(41, 98, 255, 0); }
  100% { box-shadow: 0 0 0 0 rgba(41, 98, 255, 0); }
`;

// Contenedor principal
const TableContainer = styled.div`
  background-color: ${props => props.theme.colors.white};
  border-radius: ${props => props.theme.borderRadius.medium};
  box-shadow: ${props => props.theme.shadows.medium};
  overflow: hidden;
  margin-bottom: ${props => props.theme.spacing.lg};
  transition: all 0.3s ease;
  animation: ${pulse} 2s infinite;
  
  ${props => props.isProjection && css`
    background-color: rgba(255, 255, 255, 0.95);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  `}
`;

// Cabecera de la tabla
const TableHeading = styled.div`
  background-color: ${props => props.theme.colors.primary};
  color: ${props => props.theme.colors.white};
  padding: ${props => props.theme.spacing.lg};
  text-align: center;
  
  ${props => props.isProjection && css`
    padding: ${props => props.theme.spacing.xl};
  `}
`;

const Title = styled.h2`
  font-family: ${props => props.theme.fonts.heading};
  margin: 0;
  font-size: ${props => props.isProjection ? '2.5rem' : props.theme.fontSizes.xl};
  
  ${props => props.isProjection && css`
    font-size: 2.5rem;
    letter-spacing: 1px;
  `}
`;

const Subtitle = styled.div`
  margin-top: ${props => props.theme.spacing.xs};
  font-size: ${props => props.isProjection ? '1.5rem' : props.theme.fontSizes.medium};
  opacity: 0.9;
`;

// Tabla de rankings
const Table = styled.table`
  width: 100%;
  border-collapse: collapse;
  
  ${props => props.isProjection && css`
    font-size: 1.2rem;
  `}
`;

// Animación según la dirección del movimiento
const getRowAnimation = (direction) => {
  switch (direction) {
    case 'up': return css`animation: ${moveUp} 1.5s ease;`;
    case 'down': return css`animation: ${moveDown} 1.5s ease;`;
    case 'new': return css`animation: ${highlight} 3s ease;`;
    default: return '';
  }
};

// Fila de la tabla
const TableRow = styled.tr`
  border-bottom: 1px solid ${props => props.theme.colors.lightGray};
  ${props => getRowAnimation(props.direction)}
  
  &:nth-child(even) {
    background-color: ${props => props.theme.colors.background};
  }
  
  &:hover {
    background-color: rgba(0, 0, 0, 0.05);
  }
  
  ${props => props.isTop3 && css`
    font-weight: 600;
    
    &:nth-child(1) td:first-child {
      color: gold;
      font-size: 1.2em;
    }
    &:nth-child(2) td:first-child {
      color: silver;
      font-size: 1.1em;
    }
    &:nth-child(3) td:first-child {
      color: #cd7f32; /* bronze */
      font-size: 1.05em;
    }
  `}
  
  ${props => props.isProjection && css`
    transition: background-color 0.3s ease;
    
    &:hover {
      background-color: rgba(41, 98, 255, 0.1);
    }
  `}
`;

// Encabezados de columna
const TableHeaderCell = styled.th`
  padding: ${props => props.theme.spacing.md};
  text-align: ${props => props.align || 'left'};
  font-weight: 600;
  border-bottom: 2px solid ${props => props.theme.colors.primary};
  
  ${props => props.isProjection && css`
    padding: ${props => props.theme.spacing.lg};
    font-size: 1.2rem;
  `}
`;

// Celdas de datos
const TableCell = styled.td`
  padding: ${props => props.theme.spacing.md};
  text-align: ${props => props.align || 'left'};
  
  ${props => props.isProjection && css`
    padding: ${props => props.theme.spacing.lg};
  `}
`;

// Celda de posición
const PositionCell = styled(TableCell)`
  font-weight: 700;
  font-size: ${props => props.theme.fontSizes.large};
  color: ${props => props.theme.colors.primary};
  width: 60px;
  text-align: center;
  
  ${props => props.highlight && css`
    background-color: ${props => props.theme.colors.primaryLight};
  `}
`;

// Estado de cambio (mejor, peor, igual)
const ChangeIndicator = styled.span`
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  margin-left: ${props => props.theme.spacing.xs};
  background-color: ${props => {
    switch (props.change) {
      case 'better': return props.theme.colors.success;
      case 'worse': return props.theme.colors.error;
      default: return 'transparent';
    }
  }};
  color: ${props => {
    switch (props.change) {
      case 'better':
      case 'worse':
        return props.theme.colors.white;
      default:
        return props.theme.colors.text;
    }
  }};
  font-size: 12px;
  visibility: ${props => props.change === 'same' ? 'hidden' : 'visible'};
  
  ${props => props.isProjection && css`
    width: 32px;
    height: 32px;
    font-size: 16px;
  `}
`;

// Celda de porcentaje
const PercentageCell = styled(TableCell)`
  font-weight: 600;
  font-size: ${props => props.isProjection ? '1.5rem' : props.theme.fontSizes.large};
  color: ${props => props.theme.colors.text};
  text-align: center;
`;

// Indicador de sincronización con Firebase/WebSocket
const SyncIndicator = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 8px;
  background-color: ${props => {
    switch (props.syncMethod) {
      case 'firebase': return props.theme.colors.accent;
      case 'websocket': return props.theme.colors.success;
      case 'both': return props.theme.colors.primary;
      default: return props.theme.colors.error;
    }
  }};
  color: ${props => props.theme.colors.white};
  margin-bottom: 10px;
  border-radius: ${props => props.theme.borderRadius.small};
  font-size: ${props => props.theme.fontSizes.small};
  
  ${props => props.isProjection && css`
    font-size: ${props => props.theme.fontSizes.medium};
    padding: 12px;
  `}
`;

// Footer con información de actualización
const TableFooter = styled.div`
  padding: ${props => props.theme.spacing.md};
  text-align: center;
  font-size: ${props => props.theme.fontSizes.small};
  color: ${props => props.theme.colors.gray};
  border-top: 1px solid ${props => props.theme.colors.lightGray};
  
  ${props => props.isProjection && css`
    font-size: ${props => props.theme.fontSizes.medium};
    padding: ${props => props.theme.spacing.lg};
  `}
`;

// Indicador de actualización
const UpdateIndicator = styled.div`
  display: inline-flex;
  align-items: center;
  
  span {
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background-color: ${props => props.syncMethod !== 'unavailable' ? props.theme.colors.success : props.theme.colors.error};
    margin-right: ${props => props.theme.spacing.xs};
  }
`;

// Filtros y controles
const FilterContainer = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: ${props => props.theme.spacing.md};
  background-color: ${props => props.theme.colors.background};
  margin-bottom: ${props => props.theme.spacing.sm};
  border-bottom: 1px solid ${props => props.theme.colors.lightGray};
  
  ${props => props.isProjection && css`
    padding: ${props => props.theme.spacing.lg};
  `}
`;

const CategoryFilter = styled.select`
  padding: ${props => props.theme.spacing.sm};
  border: 1px solid ${props => props.theme.colors.lightGray};
  border-radius: ${props => props.theme.borderRadius.small};
  background-color: white;
  
  ${props => props.isProjection && css`
    padding: ${props => props.theme.spacing.md};
    font-size: ${props => props.theme.fontSizes.medium};
  `}
`;

// Componente principal
const RealtimeRankingTable = ({
  competitionId,
  title,
  subtitle,
  showAnimation = true,
  showChangeIndicator = true,
  isProjection = false,
  initialCategory = 'all'
}) => {
  // Estado para rankings
  const [rankings, setRankings] = useState([]);
  // Estado para la última actualización
  const [lastUpdate, setLastUpdate] = useState(new Date());
  // Ref para posiciones anteriores
  const prevPositionsRef = useRef({});
  // Estado para filtro de categoría
  const [categoryFilter, setCategoryFilter] = useState(initialCategory);
  // Estado para categorías disponibles
  const [categories, setCategories] = useState([]);
  // Estado para la animación de cambio de ranking
  const [animatedRanking, setAnimatedRanking] = useState(null);
  const [showRankingAnimation, setShowRankingAnimation] = useState(false);
  
  // Usar el hook de sincronización en tiempo real
  const { 
    isOnline, 
    syncMethod,
    subscribeToRealtimeRankings 
  } = useRealtimeSync();
  
  // Suscribirse a actualizaciones de rankings
  useEffect(() => {
    if (!competitionId) return () => {};
    
    const handleRankingsUpdate = (data) => {
      if (!data || !Array.isArray(data)) {
        console.warn('Datos de rankings inválidos:', data);
        return;
      }
      
      // Procesar los rankings y añadir animaciones
      const processedRankings = data.map(ranking => {
        const participantId = ranking.participantId || ranking.participant_id;
        const prevPosition = prevPositionsRef.current[participantId] || 0;
        const currentPosition = ranking.position;
        
        let direction = 'none';
        let change = 'same';
        
        if (showAnimation) {
          if (prevPosition === 0) {
            direction = 'new';
          } else if (prevPosition > currentPosition) {
            direction = 'up';
            change = 'better';
          } else if (prevPosition < currentPosition) {
            direction = 'down';
            change = 'worse';
          }
        }
        
        // Si hay un cambio significativo, mostrar animación
        if ((direction === 'up' || direction === 'down') && showAnimation) {
          // Mostrar animación solo para cambios de más de una posición o primeras posiciones
          if (Math.abs(prevPosition - currentPosition) > 1 || currentPosition <= 3) {
            setAnimatedRanking({...ranking, direction, change});
            setShowRankingAnimation(true);
          }
        }
        
        return {
          ...ranking,
          direction,
          change
        };
      });
      
      setRankings(processedRankings);
      setLastUpdate(new Date());
      
      // Actualizar posiciones anteriores
      const newPositions = {};
      processedRankings.forEach(ranking => {
        const participantId = ranking.participantId || ranking.participant_id;
        newPositions[participantId] = ranking.position;
      });
      prevPositionsRef.current = newPositions;
      
      // Extraer categorías disponibles
      const uniqueCategories = new Set();
      processedRankings.forEach(ranking => {
        if (ranking.horse_details?.category || ranking.category) {
          uniqueCategories.add(ranking.horse_details?.category || ranking.category);
        }
      });
      
      setCategories([...uniqueCategories]);
    };
    
    // Suscribirse a ambos métodos de sincronización
    const unsubscribe = subscribeToRealtimeRankings(competitionId, handleRankingsUpdate);
    
    return unsubscribe;
  }, [competitionId, showAnimation, subscribeToRealtimeRankings]);
  
  // Formatear la hora de última actualización
  const formatLastUpdate = () => {
    return lastUpdate.toLocaleTimeString('es-BO', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };
  
  // Obtener texto según el método de sincronización
  const getSyncMethodText = () => {
    switch (syncMethod) {
      case 'firebase': return 'Sincronización vía Firebase';
      case 'websocket': return 'Sincronización vía WebSocket';
      case 'both': return 'Sincronización redundante (Firebase + WebSocket)';
      default: return 'Sin conexión';
    }
  };
  
  // Filtrar rankings según la categoría seleccionada
  const filteredRankings = categoryFilter === 'all' 
    ? rankings 
    : rankings.filter(entry => {
        const entryCategory = entry.horse_details?.category || entry.category;
        return entryCategory === categoryFilter;
      });
  
  // Manejar cambio de filtro
  const handleCategoryChange = (e) => {
    setCategoryFilter(e.target.value);
  };
  
  // Manejar cierre de la animación
  const handleAnimationClose = () => {
    setShowRankingAnimation(false);
    setAnimatedRanking(null);
  };
  
  return (
    <TableContainer isProjection={isProjection}>
      <TableHeading isProjection={isProjection}>
        <Title isProjection={isProjection}>{title}</Title>
        {subtitle && <Subtitle isProjection={isProjection}>{subtitle}</Subtitle>}
      </TableHeading>
      
      <SyncIndicator syncMethod={syncMethod} isProjection={isProjection}>
        {getSyncMethodText()}
      </SyncIndicator>
      
      {categories.length > 0 && (
        <FilterContainer isProjection={isProjection}>
          <CategoryFilter 
            value={categoryFilter} 
            onChange={handleCategoryChange}
            isProjection={isProjection}
          >
            <option value="all">Todas las categorías</option>
            {categories.map(category => (
              <option key={category} value={category}>{category}</option>
            ))}
          </CategoryFilter>
        </FilterContainer>
      )}
      
      <Table isProjection={isProjection}>
        <thead>
          <tr>
            <TableHeaderCell align="center" isProjection={isProjection}>Pos.</TableHeaderCell>
            <TableHeaderCell isProjection={isProjection}>Jinete</TableHeaderCell>
            <TableHeaderCell isProjection={isProjection}>Caballo</TableHeaderCell>
            <TableHeaderCell isProjection={isProjection}>Categoría</TableHeaderCell>
            <TableHeaderCell align="center" isProjection={isProjection}>Porcentaje</TableHeaderCell>
          </tr>
        </thead>
        <tbody>
          {filteredRankings.length > 0 ? (
            filteredRankings.map((entry, index) => (
              <TableRow 
                key={entry.participantId || entry.participant_id} 
                direction={entry.direction}
                isTop3={index < 3}
                isProjection={isProjection}
              >
                <PositionCell 
                  highlight={entry.position <= 3}
                  isProjection={isProjection}
                >
                  {entry.position}
                  {showChangeIndicator && (
                    <ChangeIndicator 
                      change={entry.change}
                      isProjection={isProjection}
                    >
                      {entry.change === 'better' ? '↑' : entry.change === 'worse' ? '↓' : '–'}
                    </ChangeIndicator>
                  )}
                </PositionCell>
                <TableCell isProjection={isProjection}>
                  {entry.rider?.firstName || entry.rider?.first_name} {entry.rider?.lastName || entry.rider?.last_name}
                </TableCell>
                <TableCell isProjection={isProjection}>{entry.horse?.name}</TableCell>
                <TableCell isProjection={isProjection}>
                  {entry.horse?.category || entry.category || 'General'}
                </TableCell>
                <PercentageCell isProjection={isProjection}>
                  {formatPercentage(entry.percentage)}
                </PercentageCell>
              </TableRow>
            ))
          ) : (
            <TableRow>
              <TableCell colSpan="5" align="center" isProjection={isProjection}>
                No hay datos de clasificación disponibles
              </TableCell>
            </TableRow>
          )}
        </tbody>
      </Table>
      
      <TableFooter isProjection={isProjection}>
        <UpdateIndicator syncMethod={syncMethod}>
          <span />
          {isOnline ? 'Actualización en tiempo real' : 'Sin conexión'}
        </UpdateIndicator>
        <div>Última actualización: {formatLastUpdate()}</div>
      </TableFooter>
      
      {/* Componente de animación para cambios significativos en el ranking */}
      <RankingAnimation
        rankingEntry={animatedRanking}
        visible={showRankingAnimation}
        onClose={handleAnimationClose}
      />
    </TableContainer>
  );
};

export default RealtimeRankingTable;