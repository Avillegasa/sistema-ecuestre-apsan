import React, { createContext, useState, useEffect } from 'react';
import { fetchCompetition } from '../services/api';
import { getOfflineCompetition } from '../services/offline';

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
        // Este método se implementará en el servicio offline
        // para guardar en IndexedDB
      } catch (onlineError) {
        // Si falla la conexión, intentar cargar datos offline
        competitionData = await getOfflineCompetition(competitionId);
        
        if (!competitionData) {
          throw new Error('No se pudieron obtener los datos de la competencia');
        }
      }
      
      setCurrentCompetition(competitionData);
      setParticipants(competitionData.participants || []);
      setJudges(competitionData.judges || []);
      
      setLoading(false);
      return competitionData;
    } catch (err) {
      console.error('Error al cargar la competencia:', err);
      setError(err.message || 'Error al cargar la competencia');
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

  return (
    <CompetitionContext.Provider value={{ 
      currentCompetition,
      participants,
      judges,
      loading,
      error,
      loadCompetition,
      clearCompetition
    }}>
      {children}
    </CompetitionContext.Provider>
  );
};

export default CompetitionProvider;