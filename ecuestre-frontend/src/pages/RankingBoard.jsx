// Crear un nuevo archivo: src/pages/RankingBoard.jsx

import React, { useState, useEffect, useContext } from 'react';
import { useParams, Link } from 'react-router-dom';
import styled from 'styled-components';
import Layout from '../components/layout/Layout';
import Button from '../components/common/Button';
import { CompetitionContext } from '../context/CompetitionContext';
import { fetchRankings } from '../services/api';
import { formatPercentage } from '../utils/formatters';

// Contenedor principal
const RankingContainer = styled.div`
  max-width: 1200px;
  margin: 0 auto;
`;

// Cabecera
const Header = styled.div`
  margin-bottom: ${props => props.theme.spacing.xl};
`;

const Title = styled.h1`
  font-family: ${props => props.theme.fonts.heading};
  color: ${props => props.theme.colors.primary};
  margin-bottom: ${props => props.theme.spacing.sm};
`;

const Subtitle = styled.div`
  font-size: ${props => props.theme.fontSizes.medium};
  color: ${props => props.theme.colors.gray};
`;

// Tabla de rankings
const Table = styled.table`
  width: 100%;
  border-collapse: collapse;
  margin-bottom: ${props => props.theme.spacing.lg};
  background-color: ${props => props.theme.colors.white};
  border-radius: ${props => props.theme.borderRadius.medium};
  box-shadow: ${props => props.theme.shadows.small};
  overflow: hidden;
`;

const TableHead = styled.thead`
  background-color: ${props => props.theme.colors.primary};
  color: ${props => props.theme.colors.white};
`;

const TableRow = styled.tr`
  &:nth-child(even) {
    background-color: ${props => props.theme.colors.background};
  }
`;

const TableHeader = styled.th`
  text-align: left;
  padding: ${props => props.theme.spacing.md};
`;

const TableCell = styled.td`
  padding: ${props => props.theme.spacing.md};
  border-top: 1px solid ${props => props.theme.colors.lightGray};
`;

// Panel de rankings en tiempo real
const RealtimePanel = styled.div`
  background-color: ${props => props.theme.colors.background};
  border-radius: ${props => props.theme.borderRadius.medium};
  padding: ${props => props.theme.spacing.lg};
  text-align: center;
  margin-bottom: ${props => props.theme.spacing.lg};
  
  h2 {
    color: ${props => props.theme.colors.primary};
    margin-bottom: ${props => props.theme.spacing.md};
  }
  
  p {
    margin-bottom: ${props => props.theme.spacing.lg};
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

/**
 * Componente para mostrar rankings de competencia
 */
const RankingBoard = () => {
  const { competition_id } = useParams();
  const { currentCompetition, loading: competitionLoading, error: competitionError, loadCompetition } = useContext(CompetitionContext);
  const [rankings, setRankings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Cargar datos de la competencia
  useEffect(() => {
    loadCompetition(parseInt(competition_id));
  }, [competition_id, loadCompetition]);
  
  // Cargar rankings
  useEffect(() => {
    const loadRankings = async () => {
      setLoading(true);
      setError(null);
      
      try {
        const response = await fetchRankings(competition_id);
        setRankings(response.data);
      } catch (err) {
        console.error('Error al cargar rankings:', err);
        setError('Error al cargar los rankings. ' + err.message);
      } finally {
        setLoading(false);
      }
    };
    
    loadRankings();
  }, [competition_id]);
  
  // Si está cargando, mostrar mensaje
  if (competitionLoading || loading) {
    return (
      <Layout>
        <RankingContainer>
          <LoadingMessage>Cargando datos...</LoadingMessage>
        </RankingContainer>
      </Layout>
    );
  }
  
  // Si hay error, mostrar mensaje
  if (competitionError || error) {
    return (
      <Layout>
        <RankingContainer>
          <ErrorMessage>{competitionError || error}</ErrorMessage>
          <Button as={Link} to="/competitions">Volver a Competencias</Button>
        </RankingContainer>
      </Layout>
    );
  }
  
  // Si no hay competencia, mostrar mensaje
  if (!currentCompetition) {
    return (
      <Layout>
        <RankingContainer>
          <ErrorMessage>No se encontró la competencia</ErrorMessage>
          <Button as={Link} to="/competitions">Volver a Competencias</Button>
        </RankingContainer>
      </Layout>
    );
  }
  
  return (
    <Layout>
      <RankingContainer>
        <Header>
          <Title>Rankings de la Competencia</Title>
          <Subtitle>{currentCompetition.name}</Subtitle>
        </Header>
        
        {rankings.length > 0 ? (
          <Table>
            <TableHead>
              <TableRow>
                <TableHeader>Posición</TableHeader>
                <TableHeader>Participante</TableHeader>
                <TableHeader>Caballo</TableHeader>
                <TableHeader>Puntuación</TableHeader>
                <TableHeader>Porcentaje</TableHeader>
              </TableRow>
            </TableHead>
            <tbody>
              {rankings.map(ranking => (
                <TableRow key={ranking.id}>
                  <TableCell>{ranking.position}</TableCell>
                  <TableCell>
                    {ranking.participant_details ? 
                      `${ranking.participant_details.rider_details.first_name} ${ranking.participant_details.rider_details.last_name}` : 
                      'Desconocido'}
                  </TableCell>
                  <TableCell>
                    {ranking.participant_details ? 
                      ranking.participant_details.horse_details.name : 
                      'Desconocido'}
                  </TableCell>
                  <TableCell>{ranking.average_score}</TableCell>
                  <TableCell>{formatPercentage(ranking.percentage)}</TableCell>
                </TableRow>
              ))}
            </tbody>
          </Table>
        ) : (
          <div>No hay rankings disponibles para esta competencia.</div>
        )}
        
        <RealtimePanel>
          <h2>Rankings en tiempo real</h2>
          <p>
            La implementación completa de rankings en tiempo real está programada
            para la siguiente fase del desarrollo. Esta pantalla mostrará actualizaciones
            instantáneas de las posiciones.
          </p>
          
          <Button as={Link} to={`/competitions/${competition_id}`} variant="primary">
            Volver a la Competencia
          </Button>
        </RealtimePanel>
      </RankingContainer>
    </Layout>
  );
};

export default RankingBoard;