/**
 * Utilidades para formateo de datos
 */

/**
 * Formatea un porcentaje con 2 decimales y símbolo %
 * @param {number} value - Valor numérico a formatear
 * @returns {string} - Porcentaje formateado
 */
export const formatPercentage = (value) => {
  if (value === null || value === undefined) return '--';
  return `${value.toFixed(2)}%`;
};

/**
 * Formatea una fecha a formato local
 * @param {string} dateString - Fecha en formato ISO
 * @returns {string} - Fecha formateada
 */
export const formatDate = (dateString) => {
  if (!dateString) return '';
  
  const date = new Date(dateString);
  return date.toLocaleDateString('es-BO', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
};

/**
 * Formatea una hora a formato local
 * @param {string} dateString - Fecha/hora en formato ISO
 * @returns {string} - Hora formateada
 */
export const formatTime = (dateString) => {
  if (!dateString) return '';
  
  const date = new Date(dateString);
  return date.toLocaleTimeString('es-BO', {
    hour: '2-digit',
    minute: '2-digit'
  });
};

/**
 * Formatea una fecha y hora a formato local
 * @param {string} dateString - Fecha/hora en formato ISO
 * @returns {string} - Fecha y hora formateadas
 */
export const formatDateTime = (dateString) => {
  if (!dateString) return '';
  
  return `${formatDate(dateString)} ${formatTime(dateString)}`;
};

/**
 * Formatea un nombre completo (apellido primero)
 * @param {Object} person - Objeto con firstName y lastName
 * @returns {string} - Nombre formateado
 */
export const formatFullName = (person) => {
  if (!person) return '';
  
  const { firstName, lastName } = person;
  if (!firstName && !lastName) return '';
  
  return `${lastName || ''}, ${firstName || ''}`.trim();
};

/**
 * Trunca un texto a una longitud específica
 * @param {string} text - Texto a truncar
 * @param {number} length - Longitud máxima
 * @returns {string} - Texto truncado
 */
export const truncateText = (text, length = 100) => {
  if (!text) return '';
  if (text.length <= length) return text;
  
  return `${text.substring(0, length)}...`;
};

/**
 * Formatea un número con separador de miles
 * @param {number} value - Valor numérico
 * @returns {string} - Número formateado
 */
export const formatNumber = (value) => {
  if (value === null || value === undefined) return '--';
  
  return new Intl.NumberFormat('es-BO').format(value);
};

/**
 * Formatea un tiempo en segundos a formato mm:ss
 * @param {number} seconds - Tiempo en segundos
 * @returns {string} - Tiempo formateado
 */
export const formatDuration = (seconds) => {
  if (!seconds && seconds !== 0) return '--';
  
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
};

export default {
  formatPercentage,
  formatDate,
  formatTime,
  formatDateTime,
  formatFullName,
  truncateText,
  formatNumber,
  formatDuration
};