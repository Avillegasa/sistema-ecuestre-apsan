// src/pages/ParticipantAdd.jsx
import React from 'react';
import styled from 'styled-components';
import Layout from '../components/layout/Layout';
import AddParticipantView from '../components/competitions/AddParticipantView';

const Container = styled.div`
  padding: 24px;
`;

const ParticipantAdd = () => {
  return (
    <Layout>
      <Container>
        <AddParticipantView />
      </Container>
    </Layout>
  );
};

export default ParticipantAdd;