// frontend/src/store/index.js

import { configureStore } from '@reduxjs/toolkit';
import authReducer from './slices/authSlice';
import userReducer from './slices/userSlice';
import competitionReducer from './slices/competitionSlice';
import horseReducer from './slices/horseSlice';
import evaluationReducer from './slices/evaluationSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    user: userReducer,
    competition: competitionReducer,
    horse: horseReducer,
    evaluation: evaluationReducer,
  },
});
