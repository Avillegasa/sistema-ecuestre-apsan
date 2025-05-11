import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from 'styled-components';
import GlobalStyles from './styles/GlobalStyles';
import theme from './styles/theme';

// Importar páginas (se implementarán más adelante)
// import Home from './pages/Home';
// import Login from './pages/Login';
// import CompetitionList from './pages/CompetitionList';
// import CompetitionDetail from './pages/CompetitionDetail';
// import JudgingPanel from './pages/JudgingPanel';
// import RankingBoard from './pages/RankingBoard';

// Componente temporal mientras se desarrollan las páginas
const TemporaryPage = ({ name }) => (
  <div style={{ padding: '20px', textAlign: 'center' }}>
    <h1>Sistema Ecuestre APSAN</h1>
    <p>Página: {name}</p>
    <p>Esta página está en desarrollo.</p>
  </div>
);

function App() {
  return (
    <ThemeProvider theme={theme}>
      <GlobalStyles />
      <Router>
        <Routes>
          <Route path="/" element={<TemporaryPage name="Inicio" />} />
          <Route path="/login" element={<TemporaryPage name="Login" />} />
          <Route path="/competitions" element={<TemporaryPage name="Lista de Competencias" />} />
          <Route path="/competitions/:id" element={<TemporaryPage name="Detalle de Competencia" />} />
          <Route path="/judging/:competition_id/:participant_id" element={<TemporaryPage name="Panel de Jueces" />} />
          <Route path="/rankings/:competition_id" element={<TemporaryPage name="Tabla de Rankings" />} />
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App;