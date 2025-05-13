// src/pages/CompetitionList.jsx
import React from 'react';
import styled from 'styled-components';
import Layout from '../components/layout/Layout';
import CompetitionListView from '../components/competitions/CompetitionListView';

const Container = styled.div`
  padding: 24px;
`;

const CompetitionList = () => {
  return (
    <Layout>
      <Container>
        <CompetitionListView />
      </Container>
    </Layout>
  );
};

export default CompetitionList;