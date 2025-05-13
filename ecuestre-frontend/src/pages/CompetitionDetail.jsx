// src/pages/CompetitionDetail.jsx
import React from 'react';
import styled from 'styled-components';
import Layout from '../components/layout/Layout';
import CompetitionDetailView from '../components/competitions/CompetitionDetailView';

const Container = styled.div`
  padding: 24px;
`;

const CompetitionDetail = () => {
  return (
    <Layout>
      <Container>
        <CompetitionDetailView />
      </Container>
    </Layout>
  );
};

export default CompetitionDetail;