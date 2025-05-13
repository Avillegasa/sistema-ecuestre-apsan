// src/services/apiJudges.js
import api from './api';

export const removeJudge = (competitionId, judgeId) => {
  return api.delete(`/competitions/${competitionId}/judges/${judgeId}/`);
};

export default {
  removeJudge
};