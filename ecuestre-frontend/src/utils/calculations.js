/**
 * Utilidades para cálculos del sistema FEI (3 celdas)
 */

/**
 * Calcula el resultado para un parámetro según la normativa FEI
 * @param {number} judgeScore - Calificación del juez (0-10)
 * @param {number} coefficient - Coeficiente según tablas FEI
 * @returns {number} - Resultado calculado (no debe exceder 10)
 */
export const calculateParameterScore = (judgeScore, coefficient) => {
  // Asegurarse de que los valores sean numéricos
  const score = Number(judgeScore);
  const coef = Number(coefficient);
  
  // Validar rango de calificación (0-10)
  if (score < 0 || score > 10) {
    throw new Error('La calificación debe estar entre 0 y 10');
  }
  
  // Realizar el cálculo según la fórmula FEI
  let result = score * coef;
  
  // El resultado no debe exceder 10
  result = Math.min(result, 10);
  
  // El resultado debe ser un número entero
  return Math.round(result);
};

/**
 * Calcula el promedio de todas las calificaciones de un jinete
 * @param {Array} scores - Array de calificaciones de todos los parámetros
 * @returns {number} - Promedio de calificaciones
 */
export const calculateAverage = (scores) => {
  if (!scores || scores.length === 0) {
    return 0;
  }
  
  const sum = scores.reduce((total, score) => total + score, 0);
  return sum / scores.length;
};

/**
 * Convierte un promedio a porcentaje (0-100%)
 * @param {number} average - Promedio de calificaciones (0-10)
 * @returns {number} - Porcentaje (0-100)
 */
export const convertToPercentage = (average) => {
  return (average / 10) * 100;
};

/**
 * Calcula el ranking completo de un jinete
 * @param {Object} parameterScores - Objeto con todas las calificaciones por parámetro
 * @param {Object} parameters - Objeto con información de parámetros (coeficientes, etc.)
 * @returns {Object} - Objeto con promedio y porcentaje
 */
export const calculateRanking = (parameterScores, parameters) => {
  // Validar entradas
  if (!parameterScores || !parameters) {
    return { average: 0, percentage: 0 };
  }
  
  // Calcular resultados para cada parámetro
  const scores = Object.keys(parameterScores).map(paramId => {
    const parameter = parameters[paramId];
    if (!parameter) return 0;
    
    const judgeScore = parameterScores[paramId];
    const coefficient = parameter.coefficient || 1;
    
    return calculateParameterScore(judgeScore, coefficient);
  });
  
  // Calcular promedio
  const average = calculateAverage(scores);
  
  // Convertir a porcentaje
  const percentage = convertToPercentage(average);
  
  return {
    average: parseFloat(average.toFixed(2)),
    percentage: parseFloat(percentage.toFixed(2)),
    scores
  };
};

/**
 * Calcula el ranking final combinando las calificaciones de todos los jueces
 * @param {Array} judgeScores - Array con calificaciones de todos los jueces
 * @param {Object} parameters - Objeto con información de parámetros
 * @returns {Object} - Ranking final
 */
export const calculateFinalRanking = (judgeScores, parameters) => {
  // Validar entradas
  if (!judgeScores || judgeScores.length === 0 || !parameters) {
    return { average: 0, percentage: 0 };
  }
  
  // Calcular ranking para cada juez
  const rankings = judgeScores.map(judgeScore => 
    calculateRanking(judgeScore, parameters)
  );
  
  // Promediar los porcentajes de todos los jueces
  const totalPercentage = rankings.reduce(
    (sum, ranking) => sum + ranking.percentage, 
    0
  );
  const averagePercentage = totalPercentage / rankings.length;
  
  // Convertir de nuevo a promedio (0-10)
  const finalAverage = (averagePercentage / 100) * 10;
  
  return {
    average: parseFloat(finalAverage.toFixed(2)),
    percentage: parseFloat(averagePercentage.toFixed(2))
  };
};

export default {
  calculateParameterScore,
  calculateAverage,
  convertToPercentage,
  calculateRanking,
  calculateFinalRanking
};