// src/components/competitions/CompetitionDetailView.jsx

import React, { useState, useEffect, useContext } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import Button from '../common/Button';
import Modal from '../common/Modal';
import { AuthContext } from '../../context/AuthContext';
import { CompetitionContext } from '../../context/CompetitionContext';
import JudgeAssignmentForm from './JudgeAssignmentForm';
import CategoryAssignmentForm from './CategoryAssignmentForm';
import useOffline from '../../hooks/useOffline';

const CompetitionDetailView = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useContext(AuthContext);
  const { 
    currentCompetition, 
    participants, 
    judges, 
    loading, 
    error, 
    loadCompetition 
  } = useContext(CompetitionContext);
  const { isOnline } = useOffline();
  
  const [activeTab, setActiveTab] = useState('participants');
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [showJudgeAssignmentModal, setShowJudgeAssignmentModal] = useState(false);
  const [showCategoryAssignmentModal, setShowCategoryAssignmentModal] = useState(false);
  
  // Cargar datos de la competencia
  useEffect(() => {
    loadCompetition(parseInt(id));
  }, [id, loadCompetition]);
  
  // Verificar si el usuario es administrador o creador
  const canManageCompetition = () => {
    return user && (
      user.role === 'admin' || 
      (currentCompetition && currentCompetition.creator === user.id)
    );
  };
  
  // Manejar cambio de pestaña
  const handleTabChange = (tab) => {
    setActiveTab(tab);
  };
  
  // Manejar eliminación de competencia
  const handleDeleteCompetition = async () => {
    try {
      // Import dynamically to avoid circular dependencies
      const { deleteCompetition } = await import('../../services/api');
      await deleteCompetition(id);
      navigate('/competitions');
    } catch (error) {
      console.error('Error al eliminar competencia:', error);
      // Show error message
    } finally {
      setShowDeleteModal(false);
    }
  };
  
  // Manejar asignación de jueces
  const handleJudgeAssignmentSuccess = () => {
    setShowJudgeAssignmentModal(false);
    // Recargar datos
    loadCompetition(parseInt(id), true);
  };
  
  // Manejar asignación de categorías
  const handleCategoryAssignmentSuccess = () => {
    setShowCategoryAssignmentModal(false);
    // Recargar datos
    loadCompetition(parseInt(id), true);
  };
  
  // Manejar eliminación de juez
  const handleRemoveJudge = async (judgeId) => {
    if (!window.confirm('¿Está seguro que desea remover este juez de la competencia?')) {
      return;
    }
    
    try {
      // Import dynamically to avoid circular dependencies
      const { removeJudge } = await import('../../services/apiJudges');
      await removeJudge(id, judgeId);
      // Recargar datos
      loadCompetition(parseInt(id), true);
    } catch (error) {
      console.error('Error al remover juez:', error);
      alert('Error al remover el juez');
    }
  };
  
  // Formatear fecha
  const formatDate = (dateString) => {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString('es-BO', options);
  };
  
  // Traducir estado
  const translateStatus = (status) => {
    const statusMap = {
      'pending': 'Pendiente',
      'active': 'Activa',
      'completed': 'Completada',
      'cancelled': 'Cancelada'
    };
    return statusMap[status] || status;
  };
  
  // Renderizados condicionales
  if (loading) {
    return <LoadingIndicator>Cargando detalles de la competencia...</LoadingIndicator>;
  }
  
  if (error) {
    return (
      <ErrorContainer>
        <ErrorMessage>{error}</ErrorMessage>
        <Button onClick={() => navigate('/competitions')} variant="primary">
          Volver a Competencias
        </Button>
      </ErrorContainer>
    );
  }
  
  if (!currentCompetition) {
    return (
      <ErrorContainer>
        <ErrorMessage>No se encontró la competencia</ErrorMessage>
        <Button onClick={() => navigate('/competitions')} variant="primary">
          Volver a Competencias
        </Button>
      </ErrorContainer>
    );
  }
  
  return (
    <DetailContainer>
      <HeaderSection>
        <HeaderTop>
          <div>
            <PageTitle>{currentCompetition.name}</PageTitle>
            <LocationText>{currentCompetition.location}</LocationText>
          </div>
          
          <ActionButtons>
            {canManageCompetition() && (
              <>
                <Button 
                  as={Link} 
                  to={`/competitions/${id}/edit`} 
                  variant="outline"
                >
                  Editar
                </Button>
                
                <Button 
                  variant="error" 
                  onClick={() => setShowDeleteModal(true)}
                >
                  Eliminar
                </Button>
              </>
            )}
            
            <Button 
              as={Link} 
              to={`/rankings/${id}`} 
              variant="primary"
            >
              Ver Rankings
            </Button>
          </ActionButtons>
        </HeaderTop>
        
        <StatusBadge status={currentCompetition.status}>
          {translateStatus(currentCompetition.status)}
        </StatusBadge>
      </HeaderSection>
      
      <InfoGridContainer>
        <InfoCard>
          <InfoTitle icon="📅">Información General</InfoTitle>
          
          <InfoItem>
            <InfoLabel>Fecha de Inicio</InfoLabel>
            <InfoValue>{formatDate(currentCompetition.start_date)}</InfoValue>
          </InfoItem>
          
          <InfoItem>
            <InfoLabel>Fecha de Finalización</InfoLabel>
            <InfoValue>{formatDate(currentCompetition.end_date)}</InfoValue>
          </InfoItem>
          
          <InfoItem>
            <InfoLabel>Estado</InfoLabel>
            <InfoValue>{translateStatus(currentCompetition.status)}</InfoValue>
          </InfoItem>
          
          <InfoItem>
            <InfoLabel>Tipo de Competencia</InfoLabel>
            <InfoValue>{currentCompetition.is_public ? 'Pública' : 'Privada'}</InfoValue>
          </InfoItem>
          
          <InfoItem>
            <InfoLabel>Creador</InfoLabel>
            <InfoValue>
              {currentCompetition.creator_details ? 
                `${currentCompetition.creator_details.first_name} ${currentCompetition.creator_details.last_name}` : 
                'Desconocido'}
            </InfoValue>
          </InfoItem>
        </InfoCard>
        
        <InfoCard>
          <InfoTitle icon="👥">Participación</InfoTitle>
          
          <InfoItem>
            <InfoLabel>Total de Participantes</InfoLabel>
            <InfoValue>{participants.length}</InfoValue>
          </InfoItem>
          
          <InfoItem>
            <InfoLabel>Jueces Asignados</InfoLabel>
            <InfoValue>{judges.length}</InfoValue>
          </InfoItem>
          
          <InfoItem>
            <InfoLabel>Categorías</InfoLabel>
            <InfoValue>
              {currentCompetition.categories && currentCompetition.categories.length > 0 ? 
                currentCompetition.categories.map(cat => cat.category_details.name).join(', ') : 
                'No hay categorías asignadas'}
            </InfoValue>
          </InfoItem>
          
          {canManageCompetition() && (
            <AddParticipantButton 
              as={Link} 
              to={`/competitions/${id}/participants/add`} 
              variant="primary" 
              size="small"
            >
              Añadir Participante
            </AddParticipantButton>
          )}
        </InfoCard>
      </InfoGridContainer>
      
      {currentCompetition.description && (
        <DescriptionCard>
          <InfoTitle icon="📝">Descripción</InfoTitle>
          <DescriptionText>{currentCompetition.description}</DescriptionText>
        </DescriptionCard>
      )}
      
      <TabsContainer>
        <TabsList>
          <TabButton
            active={activeTab === 'participants'}
            onClick={() => handleTabChange('participants')}
          >
            Participantes
          </TabButton>
          
          <TabButton
            active={activeTab === 'judges'}
            onClick={() => handleTabChange('judges')}
          >
            Jueces
          </TabButton>
          
          <TabButton
            active={activeTab === 'categories'}
            onClick={() => handleTabChange('categories')}
          >
            Categorías
          </TabButton>
        </TabsList>
        
        {activeTab === 'participants' && (
          <>
            {participants.length > 0 ? (
              <DataTable>
                <thead>
                  <tr>
                    <TableHeader>Número</TableHeader>
                    <TableHeader>Jinete</TableHeader>
                    <TableHeader>Caballo</TableHeader>
                    <TableHeader>Categoría</TableHeader>
                    <TableHeader>Orden de Salida</TableHeader>
                    <TableHeader>Acciones</TableHeader>
                  </tr>
                </thead>
                <tbody>
                  {participants.map(participant => (
                    <TableRow 
                      key={participant.id}
                      className={participant.is_withdrawn ? 'withdrawn' : ''}
                    >
                      <TableCell>{participant.number}</TableCell>
                      <TableCell>
                        {participant.rider_details ? 
                          `${participant.rider_details.first_name} ${participant.rider_details.last_name}` : 
                          'Desconocido'}
                      </TableCell>
                      <TableCell>
                        {participant.horse_details ? participant.horse_details.name : 'Desconocido'}
                      </TableCell>
                      <TableCell>
                        {participant.category_details ? participant.category_details.name : 'Desconocida'}
                      </TableCell>
                      <TableCell>{participant.order}</TableCell>
                      <TableCell>
                        {currentCompetition.status === 'active' && user && user.role === 'judge' && (
                          <Button 
                            as={Link} 
                            to={`/judging/${currentCompetition.id}/${participant.id}`} 
                            variant="primary" 
                            size="small"
                          >
                            Calificar
                          </Button>
                        )}
                        
                        {canManageCompetition() && (
                          <Button 
                            as={Link} 
                            to={`/competitions/${id}/participants/${participant.id}/edit`} 
                            variant="outline" 
                            size="small" 
                            style={{ marginLeft: '8px' }}
                          >
                            Editar
                          </Button>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </tbody>
              </DataTable>
            ) : (
              <EmptyMessage>No hay participantes registrados en esta competencia.</EmptyMessage>
            )}
          </>
        )}
        
        {activeTab === 'judges' && (
          <>
            {judges.length > 0 ? (
              <DataTable>
                <thead>
                  <tr>
                    <TableHeader>Nombre</TableHeader>
                    <TableHeader>Email</TableHeader>
                    <TableHeader>Rol</TableHeader>
                    <TableHeader>Juez Principal</TableHeader>
                    {canManageCompetition() && <TableHeader>Acciones</TableHeader>}
                  </tr>
                </thead>
                <tbody>
                  {judges.map(judge => (
                    <TableRow key={judge.id}>
                      <TableCell>
                        {judge.judge_details ? 
                          `${judge.judge_details.first_name} ${judge.judge_details.last_name}` : 
                          'Desconocido'}
                      </TableCell>
                      <TableCell>{judge.judge_details ? judge.judge_details.email : ''}</TableCell>
                      <TableCell>Juez</TableCell>
                      <TableCell>{judge.is_head_judge ? 'Sí' : 'No'}</TableCell>
                      {canManageCompetition() && (
                        <TableCell>
                          <Button 
                            variant="outline" 
                            size="small"
                            onClick={() => handleRemoveJudge(judge.judge_details.id)}
                          >
                            Remover
                          </Button>
                        </TableCell>
                      )}
                    </TableRow>
                  ))}
                </tbody>
              </DataTable>
            ) : (
              <EmptyMessage>No hay jueces asignados a esta competencia.</EmptyMessage>
            )}
            
            {canManageCompetition() && (
              <ActionButton 
                variant="primary"
                onClick={() => setShowJudgeAssignmentModal(true)}
              >
                Asignar Jueces
              </ActionButton>
            )}
          </>
        )}
        
        {activeTab === 'categories' && (
          <>
            {currentCompetition.categories && currentCompetition.categories.length > 0 ? (
              <DataTable>
                <thead>
                  <tr>
                    <TableHeader>Nombre</TableHeader>
                    <TableHeader>Código</TableHeader>
                    <TableHeader>Descripción</TableHeader>
                    <TableHeader>Edad Mínima</TableHeader>
                    <TableHeader>Edad Máxima</TableHeader>
                  </tr>
                </thead>
                <tbody>
                  {currentCompetition.categories.map(category => (
                    <TableRow key={category.id}>
                      <TableCell>{category.category_details.name}</TableCell>
                      <TableCell>{category.category_details.code}</TableCell>
                      <TableCell>{category.category_details.description || '-'}</TableCell>
                      <TableCell>{category.category_details.min_age || '-'}</TableCell>
                      <TableCell>{category.category_details.max_age || '-'}</TableCell>
                    </TableRow>
                  ))}
                </tbody>
              </DataTable>
            ) : (
              <EmptyMessage>No hay categorías asignadas a esta competencia.</EmptyMessage>
            )}
            
            {canManageCompetition() && (
              <ActionButton 
                variant="primary"
                onClick={() => setShowCategoryAssignmentModal(true)}
              >
                Asignar Categorías
              </ActionButton>
            )}
          </>
        )}
      </TabsContainer>
      
      {/* Modal de confirmación para eliminar */}
      <Modal 
        isOpen={showDeleteModal}
        onClose={() => setShowDeleteModal(false)}
        title="Confirmar Eliminación"
        onConfirm={handleDeleteCompetition}
        confirmText="Eliminar"
        cancelText="Cancelar"
      >
        <p>¿Está seguro que desea eliminar esta competencia?</p>
        <p>Esta acción no se puede deshacer y eliminará todos los datos asociados a la competencia.</p>
      </Modal>
      
      {/* Modal de asignación de jueces */}
      <Modal 
        isOpen={showJudgeAssignmentModal}
        onClose={() => setShowJudgeAssignmentModal(false)}
        title="Asignar Jueces a la Competencia"
        showFooter={false}
      >
        <JudgeAssignmentForm
          competitionId={parseInt(id)}
          onSuccess={handleJudgeAssignmentSuccess}
          onCancel={() => setShowJudgeAssignmentModal(false)}
        />
      </Modal>
       {/* Modal de asignación de categorías */}
      <Modal 
        isOpen={showCategoryAssignmentModal}
        onClose={() => setShowCategoryAssignmentModal(false)}
        title="Asignar Categorías a la Competencia"
        showFooter={false}
      >
        <CategoryAssignmentForm
          competitionId={parseInt(id)}
          onSuccess={handleCategoryAssignmentSuccess}
          onCancel={() => setShowCategoryAssignmentModal(false)}
        />
      </Modal>
      
      {!isOnline && (
        <OfflineIndicator>
          Modo Offline - Algunos datos podrían no estar actualizados
        </OfflineIndicator>
      )}
    </DetailContainer>
  );
};

// Estilos para el componente
const DetailContainer = styled.div`
  max-width: 1200px;
  margin: 0 auto;
`;

const HeaderSection = styled.div`
  margin-bottom: 32px;
`;

const HeaderTop = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 16px;
  
  @media (max-width: 768px) {
    flex-direction: column;
    align-items: flex-start;
  }
`;

const PageTitle = styled.h1`
  font-family: ${props => props.theme.fonts.heading};
  color: ${props => props.theme.colors.primary};
  margin: 0 0 8px;
`;

const LocationText = styled.div`
  font-size: ${props => props.theme.fontSizes.medium};
  color: ${props => props.theme.colors.gray};
  display: flex;
  align-items: center;
  
  &:before {
    content: "📍";
    margin-right: 8px;
  }
`;

const ActionButtons = styled.div`
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
`;

const StatusBadge = styled.span`
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  margin-right: 8px;
  background-color: ${props => {
    switch (props.status) {
      case 'active': return props.theme.colors.success;
      case 'pending': return props.theme.colors.warning;
      case 'completed': return props.theme.colors.gray;
      case 'cancelled': return props.theme.colors.error;
      default: return props.theme.colors.primary;
    }
  }};
  color: white;
`;

const InfoGridContainer = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
`;

const InfoCard = styled.div`
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12);
  padding: 24px;
`;

const InfoTitle = styled.h2`
  font-family: ${props => props.theme.fonts.heading};
  font-size: 18px;
  margin: 0 0 16px;
  color: ${props => props.theme.colors.primary};
  display: flex;
  align-items: center;
  
  &:before {
    content: "${props => props.icon || ''}";
    margin-right: 8px;
  }
`;

const InfoItem = styled.div`
  margin-bottom: 16px;
  
  &:last-child {
    margin-bottom: 0;
  }
`;

const InfoLabel = styled.div`
  font-weight: 500;
  margin-bottom: 4px;
`;

const InfoValue = styled.div`
  color: ${props => props.theme.colors.gray};
`;

const AddParticipantButton = styled(Button)`
  margin-top: 16px;
`;

const DescriptionCard = styled.div`
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12);
  padding: 24px;
  margin-bottom: 24px;
`;

const DescriptionText = styled.p`
  margin: 0;
  white-space: pre-line;
`;

const TabsContainer = styled.div`
  margin-bottom: 24px;
`;

const TabsList = styled.div`
  display: flex;
  border-bottom: 1px solid ${props => props.theme.colors.lightGray};
  margin-bottom: 24px;
  overflow-x: auto;
  
  @media (max-width: 480px) {
    padding-bottom: 4px;
  }
`;

const TabButton = styled.button`
  padding: 16px 24px;
  background: none;
  border: none;
  border-bottom: 3px solid ${props => props.active ? props.theme.colors.primary : 'transparent'};
  color: ${props => props.active ? props.theme.colors.primary : props.theme.colors.text};
  font-family: ${props => props.theme.fonts.main};
  font-size: ${props => props.theme.fontSizes.medium};
  font-weight: ${props => props.active ? '600' : '400'};
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    color: ${props => props.theme.colors.primary};
  }
`;

const DataTable = styled.table`
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 24px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12);
  overflow: hidden;
`;

const TableHeader = styled.th`
  background-color: ${props => props.theme.colors.primary};
  color: white;
  text-align: left;
  padding: 16px;
`;

const TableRow = styled.tr`
  &:nth-child(even) {
    background-color: ${props => props.theme.colors.background};
  }
  
  &.withdrawn {
    background-color: ${props => props.theme.colors.errorLight};
    color: ${props => props.theme.colors.gray};
    text-decoration: line-through;
  }
`;

const TableCell = styled.td`
  padding: 16px;
  border-top: 1px solid ${props => props.theme.colors.lightGray};
`;

const ActionButton = styled(Button)`
  margin-top: 16px;
`;

const LoadingIndicator = styled.div`
  text-align: center;
  padding: 32px;
  color: ${props => props.theme.colors.gray};
`;

const ErrorContainer = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  text-align: center;
  padding: 32px;
`;

const ErrorMessage = styled.div`
  background-color: ${props => props.theme.colors.errorLight};
  color: ${props => props.theme.colors.error};
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 24px;
`;

const EmptyMessage = styled.div`
  text-align: center;
  padding: 24px;
`;

const OfflineIndicator = styled.div`
  background-color: ${props => props.theme.colors.warning};
  color: white;
  padding: 8px 16px;
  text-align: center;
  border-radius: 4px;
  margin-top: 16px;
  margin-bottom: 16px;
`;

export default CompetitionDetailView;