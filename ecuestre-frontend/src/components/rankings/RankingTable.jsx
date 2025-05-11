import React, { useState, useEffect, useRef } from 'react';
import styled, { css, keyframes } from 'styled-components';
import { subscribeToRankings } from '../../services/firebase';
import { formatPercentage } from '../../utils/formatters';

// Animación de cambio de posición
const moveUp = keyframes`
  0% { transform: translateY(20px); opacity: 0.8; }
  100% { transform: translateY(0); opacity: 1; }
`;

const moveDown = keyframes`
  0% { transform: translateY(-20px); opacity: 0.8; }
  100% { transform: translateY(0); opacity: 1; }
`;

const highlight = keyframes`
  0% { background-color: rgba(255, 183, 77, 0.3); }
  100% { background-color: transparent; }
`;

// Contenedor principal
const TableContainer = styled.div`
  background-color: ${props => props.theme.colors.white};
  border-radius: ${props => props.theme.borderRadius.medium};
  box-shadow: ${props => props.theme.shadows.medium};
  overflow: hidden;
  margin-bottom: ${props => props.theme.spacing.lg};
`;

// Cabecera de la tabla
const TableHeading = styled.div`
  background-color: ${props => props.theme.colors.primary};
  color: ${props => props.theme.colors.white};
  padding: ${props => props.theme.spacing.lg};
  text-align: center;
`;

const Title = styled.h2`
  font-family: ${props => props.theme.fonts.heading};
  margin: 0;
  font-size: ${props => props.theme.fontSizes.xl};
`;

const Subtitle = styled.div`
  margin-top: ${props => props.theme.spacing.xs};
  font-size: ${props => props.theme.fontSizes.medium};
  opacity: 0.9;
`;

// Tabla de rankings
const Table = styled.table`
  width: 100%;
  border-collapse: collapse;
`;

// Animación según la dirección del movimiento
const getRowAnimation = (direction) => {
  switch (direction) {
    case 'up': return css`animation: ${moveUp} 1s ease;`;
    case 'down': return css`animation: ${moveDown} 1s ease;`;
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
`;

// Encabezados de columna
const TableHeaderCell = styled.th`
  padding: ${props => props.theme.spacing.md};
  text-align: ${props => props.align || 'left'};
  font-weight: 600;
  border-bottom: 2px solid ${props => props.theme.colors.primary};
`;

// Celdas de datos
const TableCell = styled.td`
  padding: ${props => props.theme.spacing.md};
  text-align: ${props => props.align || 'left'};
`;

// Celda de posición
const PositionCell = styled(TableCell)`
  font-weight: 700;
  font-size: ${props => props.theme.fontSizes.large};
  color: ${props => props.theme.colors.primary};
  width: 60px;
  text-align: center;
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
`;

// Celda de porcentaje
const PercentageCell = styled(TableCell)`
  font-weight: 600;
  font-size: ${props => props.theme.fontSizes.large};
  color: ${props => props.theme.colors.text};
  text-align: center;
`;

// Footer con información de actualización
const TableFooter = styled.div`
  padding: ${props => props.theme.spacing.md};
  text-align: center;
  font-size: ${props => props.theme.fontSizes.small};
  color: ${props => props.theme.colors.gray};
  border-top: 1px solid ${props => props.theme.colors.lightGray};
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
    background-color: ${props => props.isLive ? props.theme.colors.success : props.theme.colors.gray};
    margin-right: ${props => props.theme.spacing.xs};
  }
`;

/**
 * Componente RankingTable para mostrar clasificaciones en tiempo real
 * 
 * @param {Object} props - Propiedades del componente
 * @param {string} props.competitionId - ID de la competencia
 * @param {string} props.title - Título de la tabla
 * @param {string} [props.subtitle] - Subtítulo opcional
 * @param {boolean} [props.showAnimation=true] - Si mostrar animaciones de cambio de posición
 * @param {boolean} [props.showChangeIndicator=true] - Si mostrar indicadores de cambio
 */
const RankingTable = ({
  competitionId,
  title,
  subtitle,
  showAnimation = true,
  showChangeIndicator = true
}) => {
  // Estado para almacenar los rankings
  const [rankings, setRankings] = useState([]);
  // Estado para almacenar la última actualización
  const [lastUpdate, setLastUpdate] = useState(null);
  // Estado para almacenar el estado de conexión
  const [isLive, setIsLive] = useState(true);
  // Ref para almacenar las posiciones anteriores
  const prevPositionsRef = useRef({});
  
  // Suscribirse a los rankings en tiempo real
  useEffect(() => {
    if (!competitionId) return;
    
    // Función para manejar actualizaciones
    const handleRankingUpdate = (data) => {
      if (!data) {
        setIsLive(false);
        return;
      }
      
      // Convertir a array y ordenar por porcentaje
      const rankingsArray = Object.entries(data).map(([id, entry]) => ({
        id,
        ...entry
      })).sort((a, b) => b.percentage - a.percentage);
      
      // Añadir movimientos y cambios
      const updated = rankingsArray.map((entry, index) => {
        const position = index + 1;
        const prevPosition = prevPositionsRef.current[entry.id] || 0;
        
        let direction = 'none';
        let change = 'same';
        
        if (showAnimation) {
          // Determinar dirección de animación
          if (prevPosition === 0) {
            direction = 'new';
          } else if (prevPosition > position) {
            direction = 'up';
            change = 'better';
          } else if (prevPosition < position) {
            direction = 'down';
            change = 'worse';
          }
        }
        
        return {
          ...entry,
          position,
          direction,
          change
        };
      });
      
      // Actualizar estado
      setRankings(updated);
      setLastUpdate(new Date());
      setIsLive(true);
      
      // Actualizar posiciones anteriores
      const positions = {};
      updated.forEach(entry => {
        positions[entry.id] = entry.position;
      });
      prevPositionsRef.current = positions;
    };
    
    // Suscribirse a Firebase
    const unsubscribe = subscribeToRankings(competitionId, handleRankingUpdate);
    
    return () => unsubscribe();
  }, [competitionId, showAnimation]);
  
  // Formatear fecha de última actualización
  const formatLastUpdate = () => {
    if (!lastUpdate) return 'Sin datos';
    
    return lastUpdate.toLocaleTimeString('es-BO', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };
  
  return (
    <TableContainer>
      <TableHeading>
        <Title>{title}</Title>
        {subtitle && <Subtitle>{subtitle}</Subtitle>}
      </TableHeading>
      
      <Table>
        <thead>
          <tr>
            <TableHeaderCell align="center">Pos.</TableHeaderCell>
            <TableHeaderCell>Jinete</TableHeaderCell>
            <TableHeaderCell>Caballo</TableHeaderCell>
            <TableHeaderCell align="center">Porcentaje</TableHeaderCell>
          </tr>
        </thead>
        <tbody>
          {rankings.length > 0 ? (
            rankings.map(entry => (
              <TableRow key={entry.id} direction={entry.direction}>
                <PositionCell>
                  {entry.position}
                  {showChangeIndicator && (
                    <ChangeIndicator change={entry.change}>
                      {entry.change === 'better' ? '↑' : entry.change === 'worse' ? '↓' : '–'}
                    </ChangeIndicator>
                  )}
                </PositionCell>
                <TableCell>{entry.rider.firstName} {entry.rider.lastName}</TableCell>
                <TableCell>{entry.horse.name}</TableCell>
                <PercentageCell>{formatPercentage(entry.percentage)}</PercentageCell>
              </TableRow>
            ))
          ) : (
            <TableRow>
              <TableCell colSpan="4" align="center">
                No hay datos de clasificación disponibles
              </TableCell>
            </TableRow>
          )}
        </tbody>
      </Table>
      
      <TableFooter>
        <UpdateIndicator isLive={isLive}>
          <span />
          {isLive ? 'Actualización en tiempo real' : 'Sin conexión'}
        </UpdateIndicator>
        <div>Última actualización: {formatLastUpdate()}</div>
      </TableFooter>
    </TableContainer>
  );
};

export default RankingTable;