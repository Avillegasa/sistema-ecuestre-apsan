// Crear un nuevo archivo: src/components/competitions/JudgeAssignmentForm.jsx

import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { fetchJudges, assignJudges } from '../../services/api';
import Button from '../common/Button';

const FormContainer = styled.div`
  background-color: ${props => props.theme.colors.white};
  border-radius: ${props => props.theme.borderRadius.medium};
  padding: ${props => props.theme.spacing.lg};
`;

const JudgesList = styled.div`
  max-height: 300px;
  overflow-y: auto;
  margin-bottom: ${props => props.theme.spacing.lg};
  border: 1px solid ${props => props.theme.colors.lightGray};
  border-radius: ${props => props.theme.borderRadius.small};
  padding: ${props => props.theme.spacing.md};
`;

const JudgeItem = styled.div`
  display: flex;
  align-items: center;
  padding: ${props => props.theme.spacing.sm} 0;
  border-bottom: 1px solid ${props => props.theme.colors.lightGray};
  
  &:last-child {
    border-bottom: none;
  }
`;

const JudgeCheckbox = styled.input`
  margin-right: ${props => props.theme.spacing.md};
`;

const JudgeName = styled.div`
  flex: 1;
`;

const HeadJudgeRadio = styled.input`
  margin-left: ${props => props.theme.spacing.md};
`;

const ActionButtons = styled.div`
  display: flex;
  justify-content: flex-end;
  gap: ${props => props.theme.spacing.md};
  margin-top: ${props => props.theme.spacing.lg};
`;

const ErrorMessage = styled.div`
  background-color: ${props => props.theme.colors.errorLight};
  color: ${props => props.theme.colors.error};
  padding: ${props => props.theme.spacing.md};
  border-radius: ${props => props.theme.borderRadius.small};
  margin-bottom: ${props => props.theme.spacing.md};
`;

const JudgeAssignmentForm = ({ competitionId, onSuccess, onCancel }) => {
  const [judges, setJudges] = useState([]);
  const [selectedJudges, setSelectedJudges] = useState([]);
  const [headJudge, setHeadJudge] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  // Cargar jueces disponibles
  useEffect(() => {
    const loadJudges = async () => {
      setIsLoading(true);
      try {
        const response = await fetchJudges();
        setJudges(response.data);
      } catch (err) {
        setError('Error al cargar jueces: ' + err.message);
      } finally {
        setIsLoading(false);
      }
    };
    
    loadJudges();
  }, []);
  
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
    return <div>Cargando jueces disponibles...</div>;
  }
  
  return (
    <FormContainer>
      {error && <ErrorMessage>{error}</ErrorMessage>}
      
      <p>Seleccione los jueces para asignar a esta competencia:</p>
      
      <JudgesList>
        {judges.length > 0 ? (
          judges.map(judge => (
            <JudgeItem key={judge.id}>
              <JudgeCheckbox
                type="checkbox"
                id={`judge-${judge.id}`}
                checked={selectedJudges.includes(judge.id)}
                onChange={(e) => handleJudgeSelect(judge.id, e.target.checked)}
              />
              <JudgeName>
                {judge.first_name} {judge.last_name}
              </JudgeName>
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
            </JudgeItem>
          ))
        ) : (
          <p>No hay jueces disponibles</p>
        )}
      </JudgesList>
      
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

export default JudgeAssignmentForm;