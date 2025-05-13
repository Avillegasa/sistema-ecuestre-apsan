// src/pages/CompetitionDetail.jsx
import React, { useState, useEffect, useContext } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import styled from 'styled-components';
import Layout from '../components/layout/Layout';
import Button from '../components/common/Button';
import Modal from '../components/common/Modal';
import { CompetitionContext } from '../context/CompetitionContext';
import { AuthContext } from '../context/AuthContext';
import { fetchCompetition } from '../services/api';
import useOffline from '../hooks/useOffline';
import JudgeAssignmentForm from '../components/competitions/JudgeAssignmentForm';
import CategoryAssignmentForm from '../components/competitions/CategoryAssignmentForm';
import { removeJudge } from '../services/apiJudges';

// Contenedor principal
const DetailContainer = styled.div`
  max-width: 1200px;
  margin: 0 auto;
`;

// Cabecera con información principal
const Header = styled.div`
  margin-bottom: ${props => props.theme.spacing.xl};
`;

const HeaderTop = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: ${props => props.theme.spacing.md};
  flex-wrap: wrap;
  gap: ${props => props.theme.spacing.md};
  
  @media (max-width: ${props => props.theme.breakpoints.tablet}) {
    flex-direction: column;
    align-items: flex-start;
  }
`;

const Title = styled.h1`
  font-family: ${props => props.theme.fonts.heading};
  color: ${props => props.theme.colors.primary};
  margin: 0 0 ${props => props.theme.spacing.xs};
`;

const StatusBadge = styled.span`
  display: inline-block;
  padding: ${props => props.theme.spacing.xs} ${props => props.theme.spacing.sm};
  border-radius: ${props => props.theme.borderRadius.small};
  font-size: ${props => props.theme.fontSizes.small};
  font-weight: 500;
  margin-right: ${props => props.theme.spacing.sm};
  background-color: ${props => {
    switch (props.status) {
      case 'active': return props.theme.colors.success;
      case 'pending': return props.theme.colors.warning;
      case 'completed': return props.theme.colors.gray;
      case 'cancelled': return props.theme.colors.error;
      default: return props.theme.colors.primary;
    }
  }};
  color: ${props => props.theme.colors.white};
`;

const Location = styled.div`
  font-size: ${props => props.theme.fontSizes.medium};
  color: ${props => props.theme.colors.gray};
  display: flex;
  align-items: center;
  
  &:before {
    content: "📍";
    margin-right: ${props => props.theme.spacing.xs};
  }
`;

const ActionButtons = styled.div`
  display: flex;
  gap: ${props => props.theme.spacing.sm};
  flex-wrap: wrap;
`;

// Información detallada
const InfoContainer = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: ${props => props.theme.spacing.lg};
  margin-bottom: ${props => props.theme.spacing.xl};
`;

const InfoCard = styled.div`
  background-color: ${props => props.theme.colors.white};
  border-radius: ${props => props.theme.borderRadius.medium};
  box-shadow: ${props => props.theme.shadows.small};
  padding: ${props => props.theme.spacing.lg};
`;

const InfoTitle = styled.h2`
  font-family: ${props => props.theme.fonts.heading};
  font-size: ${props => props.theme.fontSizes.large};
  margin: 0 0 ${props => props.theme.spacing.md};
  color: ${props => props.theme.colors.primary};
  display: flex;
  align-items: center;
  
  &:before {
    content: "${props => props.icon || ''}";
    margin-right: ${props => props.theme.spacing.sm};
  }
`;

const InfoItem = styled.div`
  margin-bottom: ${props => props.theme.spacing.md};
  
  &:last-child {
    margin-bottom: 0;
  }
`;

const InfoLabel = styled.div`
  font-weight: 500;
  margin-bottom: ${props => props.theme.spacing.xs};
`;

const InfoValue = styled.div`
  color: ${props => props.theme.colors.gray};
`;

// Tabla de participantes
const Table = styled.table`
  width: 100%;
  border-collapse: collapse;
  margin-bottom: ${props => props.theme.spacing.lg};
  background-color: ${props => props.theme.colors.white};
  border-radius: ${props => props.theme.borderRadius.medium};
  box-shadow: ${props => props.theme.shadows.small};
  overflow: hidden;
`;

const TableHead = styled.thead`
  background-color: ${props => props.theme.colors.primary};
  color: ${props => props.theme.colors.white};
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

const TableHeader = styled.th`
  text-align: left;
  padding: ${props => props.theme.spacing.md};
`;

const TableCell = styled.td`
  padding: ${props => props.theme.spacing.md};
  border-top: 1px solid ${props => props.theme.colors.lightGray};
`;

// Descripción
const Description = styled.div`
  background-color: ${props => props.theme.colors.white};
  border-radius: ${props => props.theme.borderRadius.medium};
  box-shadow: ${props => props.theme.shadows.small};
  padding: ${props => props.theme.spacing.lg};
  margin-bottom: ${props => props.theme.spacing.lg};
  
  p {
    margin: 0;
    white-space: pre-line;
  }
`;

// Tabs para secciones
const TabsContainer = styled.div`
  margin-bottom: ${props => props.theme.spacing.lg};
`;

const TabsList = styled.div`
  display: flex;
  border-bottom: 1px solid ${props => props.theme.colors.lightGray};
  margin-bottom: ${props => props.theme.spacing.lg};
  overflow-x: auto;
  
  @media (max-width: ${props => props.theme.breakpoints.mobile}) {
    padding-bottom: ${props => props.theme.spacing.xs};
  }
`;

const TabButton = styled.button`
  padding: ${props => props.theme.spacing.md} ${props => props.theme.spacing.lg};
  background: none;
  border: none;
  border-bottom: 3px solid ${props => props.active ? props.theme.colors.primary : 'transparent'};
  color: ${props => props.active ? props.theme.colors.primary : props.theme.colors.text};
  font-family: ${props => props.theme.fonts.main};
  font-size: ${props => props.theme.fontSizes.medium};
  font-weight: ${props => props.active ? '600' : '400'};
  cursor: pointer;
  transition: all ${props => props.theme.transitions.fast};
  
  &:hover {
    color: ${props => props.theme.colors.primary};
  }
`;

// Estados de carga y error
const LoadingMessage = styled.div`
  text-align: center;
  padding: ${props => props.theme.spacing.xl};
  color: ${props => props.theme.colors.gray};
`;

const ErrorMessage = styled.div`
  background-color: ${props => props.theme.colors.errorLight};
  color: ${props => props.theme.colors.error};
  padding: ${props => props.theme.spacing.md};
  border-radius: ${props => props.theme.borderRadius.medium};
  margin-bottom: ${props => props.theme.spacing.lg};
`;

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

/**
 * Pantalla de detalle de competencia
 */
const CompetitionDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useContext(AuthContext);
  const { currentCompetition, participants, judges, loading, error, loadCompetition } = useContext(CompetitionContext);
  const { isOnline } = useOffline();
  
  const [activeTab, setActiveTab] = useState('participants');
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [showJudgeAssignmentModal, setShowJudgeAssignmentModal] = useState(false);
  const [showCategoryAssignmentModal, setShowCategoryAssignmentModal] = useState(false);
  
  // Cargar datos de la competencia
  useEffect(() => {
    loadCompetition(parseInt(id));
  }, [id, loadCompetition]);
  
  // Manejar cambio de pestaña
  const handleTabChange = (tab) => {
    setActiveTab(tab);
  };
  
  // Verificar si el usuario es administrador o creador
  const canManageCompetition = () => {
    return user && (
      user.role === 'admin' || 
      (currentCompetition && currentCompetition.creator === user.id)
    );
  };

  // Añadir esta función dentro del componente
    const handleJudgeAssignmentSuccess = () => {
        setShowJudgeAssignmentModal(false);
    // Recargar los datos de la competencia
        loadCompetition(parseInt(id), true);
    };
  
  // Manejar eliminación de competencia
  const handleDeleteCompetition = async () => {
    // Aquí iría la lógica para eliminar la competencia
    setShowDeleteModal(false);
    navigate('/competitions');
  };

  const handleCategoryAssignmentSuccess = () => {
    setShowCategoryAssignmentModal(false);
    // Recargar los datos de la competencia
    loadCompetition(parseInt(id), true);
};

// Manejar eliminación de juez
const handleRemoveJudge = async (judgeId) => {
  if (!window.confirm('¿Está seguro que desea remover este juez de la competencia?')) {
    return;
  }
  
  try {
    await removeJudge(id, judgeId);
    // Recargar datos
    loadCompetition(parseInt(id), true);
  } catch (error) {
    console.error('Error al remover juez:', error);
    alert('Error al remover el juez');
  }
};
  
  // Si está cargando, mostrar mensaje
  if (loading) {
    return (
      <Layout>
        <DetailContainer>
          <LoadingMessage>Cargando detalles de la competencia...</LoadingMessage>
        </DetailContainer>
      </Layout>
    );
  }
  
  // Si hay error, mostrar mensaje
  if (error) {
    return (
      <Layout>
        <DetailContainer>
          <ErrorMessage>{error}</ErrorMessage>
          <Button 
            onClick={() => navigate('/competitions')} 
            variant="primary"
          >
            Volver a Competencias
          </Button>
        </DetailContainer>
      </Layout>
    );
  }
  
  // Si no hay competencia, mostrar mensaje
  if (!currentCompetition) {
    return (
      <Layout>
        <DetailContainer>
          <ErrorMessage>No se encontró la competencia</ErrorMessage>
          <Button 
            onClick={() => navigate('/competitions')} 
            variant="primary"
          >
            Volver a Competencias
          </Button>
        </DetailContainer>
      </Layout>
    );
  }
  
  return (
    <Layout>
      <DetailContainer>
        <Header>
          <HeaderTop>
            <div>
              <Title>{currentCompetition.name}</Title>
              <Location>{currentCompetition.location}</Location>
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
        </Header>
        
        <InfoContainer>
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
                {currentCompetition.categories ? 
                  currentCompetition.categories.map(cat => cat.category_details.name).join(', ') : 
                  'No hay categorías asignadas'}
              </InfoValue>
            </InfoItem>
            
            {canManageCompetition() && (
              <Button 
                as={Link} 
                to={`/competitions/${id}/participants/add`} 
                variant="primary" 
                size="small" 
                style={{ marginTop: '16px' }}
              >
                Añadir Participante
              </Button>
            )}
          </InfoCard>
        </InfoContainer>
        
        {currentCompetition.description && (
          <Description>
            <InfoTitle icon="📝">Descripción</InfoTitle>
            <p>{currentCompetition.description}</p>
          </Description>
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
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableHeader>Número</TableHeader>
                      <TableHeader>Jinete</TableHeader>
                      <TableHeader>Caballo</TableHeader>
                      <TableHeader>Categoría</TableHeader>
                      <TableHeader>Orden de Salida</TableHeader>
                      <TableHeader>Acciones</TableHeader>
                    </TableRow>
                  </TableHead>
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
                </Table>
              ) : (
                <div>No hay participantes registrados en esta competencia.</div>
              )}
            </>
          )}
          
          {activeTab === 'judges' && (
            <>
              {judges.length > 0 ? (
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableHeader>Nombre</TableHeader>
                      <TableHeader>Email</TableHeader>
                      <TableHeader>Rol</TableHeader>
                      <TableHeader>Juez Principal</TableHeader>
                      {canManageCompetition() && <TableHeader>Acciones</TableHeader>}
                    </TableRow>
                  </TableHead>
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
                </Table>
              ) : (
                <div>No hay jueces asignados a esta competencia.</div>
              )}
              
              {canManageCompetition() && (
                <Button 
                    variant="primary"
                    onClick={() => setShowJudgeAssignmentModal(true)}
                    style={{ marginTop: '16px' }}
                >
                    Asignar Jueces
                </Button>
                )}
            </>
          )}
          
          {activeTab === 'categories' && (
            <>
              {currentCompetition.categories && currentCompetition.categories.length > 0 ? (
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableHeader>Nombre</TableHeader>
                      <TableHeader>Código</TableHeader>
                      <TableHeader>Descripción</TableHeader>
                      <TableHeader>Edad Mínima</TableHeader>
                      <TableHeader>Edad Máxima</TableHeader>
                    </TableRow>
                  </TableHead>
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
                </Table>
              ) : (
                <div>No hay categorías asignadas a esta competencia.</div>
              )}
              
              {canManageCompetition() && (
                <Button 
                    variant="primary"
                    onClick={() => setShowCategoryAssignmentModal(true)}
                    style={{ marginTop: '16px' }}
                >
                    Asignar Categorías
                </Button>
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
      </DetailContainer>
    </Layout>
  );
};

export default CompetitionDetail;