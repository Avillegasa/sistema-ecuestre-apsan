// src/components/competitions/JudgeAssignmentForm.jsx

import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { fetchJudges, assignJudges } from '../../services/api';
import Button from '../common/Button';
import Input from '../common/Input';

const JudgeAssignmentForm = ({ competitionId, onSuccess, onCancel }) => {
  const [judges, setJudges] = useState([]);
  const [selectedJudges, setSelectedJudges] = useState([]);
  const [headJudge, setHeadJudge] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [filteredJudges, setFilteredJudges] = useState([]);
  
  // Cargar jueces disponibles
  useEffect(() => {
    const loadJudges = async () => {
      setIsLoading(true);
      try {
        const response = await fetchJudges();
        setJudges(response.data);
        setFilteredJudges(response.data);
      } catch (err) {
        setError('Error al cargar jueces: ' + err.message);
      } finally {
        setIsLoading(false);
      }
    };
    
    loadJudges();
  }, []);
  
  // Filtrar jueces cuando cambia la búsqueda
  useEffect(() => {
    if (!searchQuery.trim()) {
      setFilteredJudges(judges);
      return;
    }
    
    const query = searchQuery.toLowerCase();
    const filtered = judges.filter(judge => 
      `${judge.first_name} ${judge.last_name}`.toLowerCase().includes(query) ||
      judge.email.toLowerCase().includes(query)
    );
    
    setFilteredJudges(filtered);
  }, [searchQuery, judges]);
  
  // Manejar selección de juez
  const handleJudgeSelect = (judgeId, isSelected) => {
    if (isSelected) {
      setSelectedJudges(prev => [...prev, judgeId]);
    } else {
      setSelectedJudges(prev => prev.filter(id => id !== judgeId));
      
      // Si se deselecciona el juez principal, quitarlo
      if (headJudge === judgeId) {
        setHeadJudge(null);
      }
    }
  };
  
  // Manejar selección de juez principal
  const handleHeadJudgeSelect = (judgeId) => {
    setHeadJudge(judgeId);
    
    // Asegurarse de que el juez principal esté seleccionado
    if (!selectedJudges.includes(judgeId)) {
      setSelectedJudges(prev => [...prev, judgeId]);
    }
  };
  
  // Enviar asignación de jueces
  const handleSubmit = async () => {
    if (selectedJudges.length === 0) {
      setError('Debe seleccionar al menos un juez');
      return;
    }
    
    setIsSubmitting(true);
    setError(null);
    
    try {
      // Preparar datos para enviar
      const judgesData = selectedJudges.map(judgeId => ({
        judge_id: judgeId,
        is_head_judge: judgeId === headJudge
      }));
      
      // Enviar asignación
      await assignJudges(competitionId, judgesData);
      
      // Notificar éxito
      onSuccess();
    } catch (err) {
      setError('Error al asignar jueces: ' + err.message);
    } finally {
      setIsSubmitting(false);
    }
  };
  
  if (isLoading) {
    return <LoadingMessage>Cargando jueces disponibles...</LoadingMessage>;
  }
  
  return (
    <FormContainer>
      {error && <ErrorMessage>{error}</ErrorMessage>}
      
      <p>Seleccione los jueces para asignar a esta competencia:</p>
      
      <SearchBox>
        <Input
          id="search-judges"
          placeholder="Buscar jueces por nombre o email..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          fullWidth
        />
      </SearchBox>
      
      <JudgesList>
        {filteredJudges.length > 0 ? (
          filteredJudges.map(judge => (
            <JudgeItem key={judge.id}>
              <JudgeCheckbox
                type="checkbox"
                id={`judge-${judge.id}`}
                checked={selectedJudges.includes(judge.id)}
                onChange={(e) => handleJudgeSelect(judge.id, e.target.checked)}
              />
              <JudgeDetails>
                <JudgeName>{judge.first_name} {judge.last_name}</JudgeName>
                <JudgeEmail>{judge.email}</JudgeEmail>
              </JudgeDetails>
              <HeadJudgeContainer>
                <label>
                  Juez Principal
                  <HeadJudgeRadio
                    type="radio"
                    name="headJudge"
                    disabled={!selectedJudges.includes(judge.id)}
                    checked={headJudge === judge.id}
                    onChange={() => handleHeadJudgeSelect(judge.id)}
                  />
                </label>
              </HeadJudgeContainer>
            </JudgeItem>
          ))
        ) : (
          <EmptyMessage>No se encontraron jueces con esos criterios</EmptyMessage>
        )}
      </JudgesList>
      
      <JudgeCounter>
        {selectedJudges.length} jueces seleccionados
        {headJudge && ` (1 juez principal)`}
      </JudgeCounter>
      
      <ActionButtons>
        <Button
          variant="outline"
          onClick={onCancel}
        >
          Cancelar
        </Button>
        <Button
          variant="primary"
          onClick={handleSubmit}
          disabled={isSubmitting}
        >
          {isSubmitting ? 'Asignando...' : 'Asignar Jueces'}
        </Button>
      </ActionButtons>
    </FormContainer>
  );
};

// Estilos para el componente
const FormContainer = styled.div`
  background-color: white;
  border-radius: 8px;
  padding: 24px;
`;

const SearchBox = styled.div`
  margin-bottom: 16px;
`;

const JudgesList = styled.div`
  max-height: 300px;
  overflow-y: auto;
  margin-bottom: 16px;
  border: 1px solid ${props => props.theme.colors.lightGray};
  border-radius: 4px;
  padding: 16px;
`;

const JudgeItem = styled.div`
  display: flex;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid ${props => props.theme.colors.lightGray};
  
  &:last-child {
    border-bottom: none;
  }
`;

const JudgeCheckbox = styled.input`
  margin-right: 16px;
  width: 18px;
  height: 18px;
  cursor: pointer;
`;

const JudgeDetails = styled.div`
  flex: 1;
`;

const JudgeName = styled.div`
  font-weight: 500;
`;

const JudgeEmail = styled.div`
  font-size: 14px;
  color: ${props => props.theme.colors.gray};
`;

const HeadJudgeContainer = styled.div`
  display: flex;
  align-items: center;
  margin-left: 16px;
`;

const HeadJudgeRadio = styled.input`
  margin-left: 8px;
  width: 16px;
  height: 16px;
  cursor: pointer;
`;

const JudgeCounter = styled.div`
  font-size: 14px;
  color: ${props => props.theme.colors.gray};
  margin-bottom: 16px;
`;

const ActionButtons = styled.div`
  display: flex;
  justify-content: flex-end;
  gap: 16px;
  margin-top: 24px;
`;

const ErrorMessage = styled.div`
  background-color: ${props => props.theme.colors.errorLight};
  color: ${props => props.theme.colors.error};
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 16px;
`;

const LoadingMessage = styled.div`
  text-align: center;
  padding: 24px;
  color: ${props => props.theme.colors.gray};
`;

const EmptyMessage = styled.div`
  text-align: center;
  padding: 24px;
  color: ${props => props.theme.colors.gray};
`;

export default JudgeAssignmentForm;