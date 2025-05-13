// src/context/CompetitionContext.js
import React, { createContext, useState, useEffect } from 'react';
import { fetchCompetition } from '../services/api';

// Crear el contexto de competencia
export const CompetitionContext = createContext();

// Proveedor del contexto
export const CompetitionProvider = ({ children }) => {
  const [currentCompetition, setCurrentCompetition] = useState(null);
  const [participants, setParticipants] = useState([]);
  const [judges, setJudges] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Cargar una competencia específica
  const loadCompetition = async (competitionId, forceRefresh = false) => {
    setLoading(true);
    setError(null);
    
    try {
      let competitionData;
      
      // Intentar obtener datos online
      try {
        const response = await fetchCompetition(competitionId);
        competitionData = response.data;
        
        // Guardar datos para uso offline
        try {
          const { saveCompetitionData, saveParticipantsData } = await import('../services/offline');
          await saveCompetitionData(competitionData);
          
          // También guardar participantes para uso offline si existen
          if (competitionData.participants && competitionData.participants.length > 0) {
            await saveParticipantsData(competitionData.participants);
          }
        } catch (offlineErr) {
          console.warn("No se pudieron guardar datos para uso offline:", offlineErr.message);
        }
      } catch (onlineError) {
        console.warn("No se pudieron obtener datos online:", onlineError.message);
        
        // Si falla la conexión, intentar cargar datos offline
        if (!forceRefresh) { // Solo intentar cargar desde offline si no es una actualización forzada
          try {
            const { getOfflineCompetition, getOfflineParticipants } = await import('../services/offline');
            competitionData = await getOfflineCompetition(competitionId);
            
            if (!competitionData) {
              throw new Error('No hay datos disponibles de esta competencia');
            }
            
            // Intentar cargar participantes offline
            try {
              const offlineParticipants = await getOfflineParticipants(competitionId);
              if (offlineParticipants && offlineParticipants.length > 0) {
                competitionData.participants = offlineParticipants;
              }
            } catch (participantsError) {
              console.warn("Error al cargar participantes offline:", participantsError.message);
            }
          } catch (offlineError) {
            throw new Error('No se pudo conectar al servidor y no hay datos guardados localmente');
          }
        } else {
          throw new Error('No se pudo conectar al servidor para obtener datos actualizados');
        }
      }
      
      setCurrentCompetition(competitionData);
      setParticipants(competitionData.participants || []);
      setJudges(competitionData.judges || []);
      
      setLoading(false);
      return competitionData;
    } catch (err) {
      console.error('Error al cargar la competencia:', err);
      setError(err.message || 'Error al cargar los datos de la competencia');
      setLoading(false);
      return null;
    }
  };

  // Limpiar datos de competencia actual
  const clearCompetition = () => {
    setCurrentCompetition(null);
    setParticipants([]);
    setJudges([]);
  };

  // Añadir participante localmente (para actualización optimista)
  const addParticipantLocally = (participant) => {
    setParticipants(prev => [...prev, participant]);
    
    // Actualizar también en la competencia actual
    if (currentCompetition) {
      setCurrentCompetition(prev => ({
        ...prev,
        participants: [...(prev.participants || []), participant]
      }));
    }
  };

  // Actualizar participante localmente
  const updateParticipantLocally = (participantId, updatedData) => {
    setParticipants(prev => 
      prev.map(p => p.id === participantId ? { ...p, ...updatedData } : p)
    );
    
    // Actualizar también en la competencia actual
    if (currentCompetition && currentCompetition.participants) {
      setCurrentCompetition(prev => ({
        ...prev,
        participants: prev.participants.map(p => 
          p.id === participantId ? { ...p, ...updatedData } : p
        )
      }));
    }
  };

  // Añadir juez localmente
  const addJudgeLocally = (judge) => {
    setJudges(prev => [...prev, judge]);
    
    // Actualizar también en la competencia actual
    if (currentCompetition) {
      setCurrentCompetition(prev => ({
        ...prev,
        judges: [...(prev.judges || []), judge]
      }));
    }
  };

  // Eliminar juez localmente
  const removeJudgeLocally = (judgeId) => {
    setJudges(prev => prev.filter(j => j.judge_details.id !== judgeId));
    
    // Actualizar también en la competencia actual
    if (currentCompetition && currentCompetition.judges) {
      setCurrentCompetition(prev => ({
        ...prev,
        judges: prev.judges.filter(j => j.judge_details.id !== judgeId)
      }));
    }
  };

  return (
    <CompetitionContext.Provider value={{ 
      currentCompetition,
      participants,
      judges,
      loading,
      error,
      loadCompetition,
      clearCompetition,
      addParticipantLocally,
      updateParticipantLocally,
      addJudgeLocally,
      removeJudgeLocally
    }}>
      {children}
    </CompetitionContext.Provider>
  );
};

export default CompetitionProvider;