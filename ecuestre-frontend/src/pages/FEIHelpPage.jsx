import React from 'react';
import styled from 'styled-components';
import { Link } from 'react-router-dom';
import Header from '../components/layout/Header';
import Footer from '../components/layout/Footer';
import Button from '../components/common/Button';

// Contenedor principal
const PageContainer = styled.div`
  max-width: 1000px;
  margin: 0 auto;
  padding: ${props => props.theme.spacing.lg};
`;

// Título principal
const PageTitle = styled.h1`
  font-family: ${props => props.theme.fonts.heading};
  margin-bottom: ${props => props.theme.spacing.lg};
  color: ${props => props.theme.colors.primary};
  font-size: ${props => props.theme.fontSizes.xxl};
  text-align: center;
`;

// Sección
const Section = styled.section`
  margin-bottom: ${props => props.theme.spacing.xl};
`;

// Título de sección
const SectionTitle = styled.h2`
  font-family: ${props => props.theme.fonts.heading};
  margin-bottom: ${props => props.theme.spacing.md};
  color: ${props => props.theme.colors.secondary};
  font-size: ${props => props.theme.fontSizes.xl};
  border-bottom: 1px solid ${props => props.theme.colors.lightGray};
  padding-bottom: ${props => props.theme.spacing.sm};
`;

// Párrafo
const Paragraph = styled.p`
  margin-bottom: ${props => props.theme.spacing.md};
  line-height: 1.6;
`;

// Tabla FEI
const FEITable = styled.table`
  width: 100%;
  border-collapse: collapse;
  margin-bottom: ${props => props.theme.spacing.lg};
  box-shadow: ${props => props.theme.shadows.small};
  
  th, td {
    border: 1px solid ${props => props.theme.colors.lightGray};
    padding: ${props => props.theme.spacing.md};
    text-align: center;
  }
  
  th {
    background-color: ${props => props.theme.colors.primary};
    color: ${props => props.theme.colors.white};
    font-weight: 600;
  }
  
  tr:nth-child(even) {
    background-color: ${props => props.theme.colors.background};
  }
`;

// Ejemplo visual
const FEIExample = styled.div`
  background-color: ${props => props.theme.colors.background};
  border: 1px solid ${props => props.theme.colors.lightGray};
  border-radius: ${props => props.theme.borderRadius.medium};
  padding: ${props => props.theme.spacing.lg};
  margin-bottom: ${props => props.theme.spacing.lg};
  display: flex;
  flex-direction: column;
  align-items: center;
`;

// Lista numerada
const NumberedList = styled.ol`
  margin-bottom: ${props => props.theme.spacing.lg};
  padding-left: ${props => props.theme.spacing.lg};
  
  li {
    margin-bottom: ${props => props.theme.spacing.sm};
    line-height: 1.6;
  }
`;

// Lista con viñetas
const BulletList = styled.ul`
  margin-bottom: ${props => props.theme.spacing.lg};
  padding-left: ${props => props.theme.spacing.lg};
  
  li {
    margin-bottom: ${props => props.theme.spacing.sm};
    line-height: 1.6;
  }
`;

// Contenedor de botones
const ButtonContainer = styled.div`
  display: flex;
  justify-content: center;
  gap: ${props => props.theme.spacing.md};
  margin-top: ${props => props.theme.spacing.xl};
`;

/**
 * Página de ayuda sobre el Sistema FEI (3 Celdas)
 */
const FEIHelpPage = () => {
  return (
    <>
      <Header />
      <PageContainer>
        <PageTitle>Sistema de Calificación FEI (3 Celdas)</PageTitle>
        
        <Section>
          <SectionTitle>Introducción al Sistema FEI</SectionTitle>
          <Paragraph>
            El sistema de 3 celdas de la Federación Ecuestre Internacional (FEI) es el método oficial
            para evaluar competencias ecuestres. Este sistema asegura una calificación objetiva y estandarizada
            en todas las competencias a nivel mundial.
          </Paragraph>
          <Paragraph>
            El nombre "3 celdas" hace referencia a las tres columnas que se utilizan en la planilla
            de calificación: Máximo, Coeficiente y Calificación del Juez.
          </Paragraph>
        </Section>
        
        <Section>
          <SectionTitle>Estructura del Sistema</SectionTitle>
          <FEITable>
            <thead>
              <tr>
                <th>Columna</th>
                <th>Descripción</th>
                <th>Rango/Valor</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><strong>Celda 1: Máximo</strong></td>
                <td>El valor máximo posible para cualquier parámetro.</td>
                <td>Siempre 10</td>
              </tr>
              <tr>
                <td><strong>Celda 2: Coeficiente</strong></td>
                <td>Multiplicador que indica la importancia relativa del parámetro.</td>
                <td>Normalmente 1, 2 o 3</td>
              </tr>
              <tr>
                <td><strong>Celda 3: Calificación</strong></td>
                <td>La calificación asignada por el juez.</td>
                <td>0 a 10 (puede usar decimales)</td>
              </tr>
            </tbody>
          </FEITable>
          
          <Paragraph>
            <strong>Fórmula de cálculo:</strong> Resultado = Calificación del Juez × Coeficiente
          </Paragraph>
          <Paragraph>
            <strong>Reglas importantes:</strong>
          </Paragraph>
          <BulletList>
            <li>El resultado nunca debe exceder 10 puntos, incluso si el cálculo da un número mayor.</li>
            <li>El resultado final debe ser un número entero (se redondea).</li>
            <li>La calificación del juez puede incluir decimales (ejemplo: 7.5).</li>
          </BulletList>
        </Section>
        
        <Section>
          <SectionTitle>Ejemplo de Calificación</SectionTitle>
          <FEIExample>
            <h3>Parámetro: Transición al trote</h3>
            <FEITable>
              <thead>
                <tr>
                  <th>Máximo</th>
                  <th>Coeficiente</th>
                  <th>Calificación del Juez</th>
                  <th>Resultado</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>10</td>
                  <td>2</td>
                  <td>7.5</td>
                  <td>10* (Limitado al máximo)</td>
                </tr>
              </tbody>
            </FEITable>
            <p>* Cálculo: 7.5 × 2 = 15, pero se limita a 10 por ser el máximo permitido.</p>
            
            <h3>Otro ejemplo:</h3>
            <FEITable>
              <thead>
                <tr>
                  <th>Máximo</th>
                  <th>Coeficiente</th>
                  <th>Calificación del Juez</th>
                  <th>Resultado</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>10</td>
                  <td>1</td>
                  <td>6.5</td>
                  <td>7</td>
                </tr>
              </tbody>
            </FEITable>
            <p>Cálculo: 6.5 × 1 = 6.5, que se redondea a 7.</p>
          </FEIExample>
        </Section>
        
        <Section>
          <SectionTitle>Guía de Calificación</SectionTitle>
          <Paragraph>
            Para asignar calificaciones consistentes, los jueces deben seguir esta escala:
          </Paragraph>
          <FEITable>
            <thead>
              <tr>
                <th>Calificación</th>
                <th>Descripción</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>10</td>
                <td>Excelente</td>
              </tr>
              <tr>
                <td>9</td>
                <td>Muy Bueno</td>
              </tr>
              <tr>
                <td>8</td>
                <td>Bueno</td>
              </tr>
              <tr>
                <td>7</td>
                <td>Bastante Bueno</td>
              </tr>
              <tr>
                <td>6</td>
                <td>Satisfactorio</td>
              </tr>
              <tr>
                <td>5</td>
                <td>Suficiente</td>
              </tr>
              <tr>
                <td>4</td>
                <td>Insuficiente</td>
              </tr>
              <tr>
                <td>3</td>
                <td>Bastante Malo</td>
              </tr>
              <tr>
                <td>2</td>
                <td>Malo</td>
              </tr>
              <tr>
                <td>1</td>
                <td>Muy Malo</td>
              </tr>
              <tr>
                <td>0</td>
                <td>No Ejecutado</td>
              </tr>
            </tbody>
          </FEITable>
          
          <Paragraph>
            Se recomienda usar decimales (0.5) para proporcionar una evaluación más precisa
            entre dos niveles consecutivos.
          </Paragraph>
        </Section>
        
        <Section>
          <SectionTitle>Cálculo del Ranking Final</SectionTitle>
          <Paragraph>
            El sistema de ranking combina las calificaciones de todos los jueces para generar
            la clasificación final de los participantes:
          </Paragraph>
          <NumberedList>
            <li>Cada juez evalúa todos los parámetros para un participante.</li>
            <li>Se calcula el promedio de los resultados de cada juez.</li>
            <li>El promedio se convierte a un porcentaje (0-100%).</li>
            <li>El ranking final se determina por el porcentaje promedio de todos los jueces.</li>
            <li>En caso de empate, el participante con mayor calificación del juez principal prevalece.</li>
          </NumberedList>
        </Section>
        
        <ButtonContainer>
          <Button as={Link} to="/judging" variant="primary" size="large">
            Volver al Panel de Calificación
          </Button>
          <Button as="a" href="https://www.fei.org/dressage" target="_blank" variant="outline" size="large">
            Visitar Sitio Oficial FEI
          </Button>
        </ButtonContainer>
      </PageContainer>
      <Footer />
    </>
  );
};

export default FEIHelpPage;