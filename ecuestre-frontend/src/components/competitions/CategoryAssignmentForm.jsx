// Crear un nuevo archivo: src/components/competitions/CategoryAssignmentForm.jsx

import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { fetchCategories } from '../../services/api';
import Button from '../common/Button';

const FormContainer = styled.div`
  background-color: ${props => props.theme.colors.white};
  border-radius: ${props => props.theme.borderRadius.medium};
  padding: ${props => props.theme.spacing.lg};
`;

const CategoriesList = styled.div`
  max-height: 300px;
  overflow-y: auto;
  margin-bottom: ${props => props.theme.spacing.lg};
  border: 1px solid ${props => props.theme.colors.lightGray};
  border-radius: ${props => props.theme.borderRadius.small};
  padding: ${props => props.theme.spacing.md};
`;

const CategoryItem = styled.div`
  display: flex;
  align-items: center;
  padding: ${props => props.theme.spacing.sm} 0;
  border-bottom: 1px solid ${props => props.theme.colors.lightGray};
  
  &:last-child {
    border-bottom: none;
  }
`;

const CategoryCheckbox = styled.input`
  margin-right: ${props => props.theme.spacing.md};
`;

const CategoryName = styled.div`
  flex: 1;
`;

const CategoryCode = styled.div`
  font-size: ${props => props.theme.fontSizes.small};
  color: ${props => props.theme.colors.gray};
  margin-left: ${props => props.theme.spacing.md};
`;

const ActionButtons = styled.div`
  display: flex;
  justify-content: flex-end;
  gap: ${props => props.theme.spacing.md};
  margin-top: ${props => props.theme.spacing.lg};
`;

const ErrorMessage = styled.div`
  background-color: ${props => props.theme.colors.errorLight};
  color: ${props => props.theme.colors.error};
  padding: ${props => props.theme.spacing.md};
  border-radius: ${props => props.theme.borderRadius.small};
  margin-bottom: ${props => props.theme.spacing.md};
`;

const CategoryAssignmentForm = ({ competitionId, onSuccess, onCancel }) => {
  const [categories, setCategories] = useState([]);
  const [selectedCategories, setSelectedCategories] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  // Cargar categorías disponibles
  useEffect(() => {
    const loadCategories = async () => {
      setIsLoading(true);
      try {
        const response = await fetchCategories();
        setCategories(response.data);
      } catch (err) {
        setError('Error al cargar categorías: ' + err.message);
      } finally {
        setIsLoading(false);
      }
    };
    
    loadCategories();
  }, []);
  
  // Manejar selección de categoría
  const handleCategorySelect = (categoryId, isSelected) => {
    if (isSelected) {
      setSelectedCategories(prev => [...prev, categoryId]);
    } else {
      setSelectedCategories(prev => prev.filter(id => id !== categoryId));
    }
  };
  
  // Enviar asignación de categorías
  const handleSubmit = async () => {
    if (selectedCategories.length === 0) {
      setError('Debe seleccionar al menos una categoría');
      return;
    }
    
    setIsSubmitting(true);
    setError(null);
    
    try {
      // Esta es una función que debemos añadir al API
      // Modificaremos el servicio API después
      const assignCategories = (await import('../../services/api')).assignCategories;
      
      // Preparar datos para enviar
      const categoriesData = selectedCategories.map(categoryId => ({
        category_id: categoryId
      }));
      
      // Enviar asignación
      await assignCategories(competitionId, categoriesData);
      
      // Notificar éxito
      onSuccess();
    } catch (err) {
      setError('Error al asignar categorías: ' + err.message);
    } finally {
      setIsSubmitting(false);
    }
  };
  
  if (isLoading) {
    return <div>Cargando categorías disponibles...</div>;
  }
  
  return (
    <FormContainer>
      {error && <ErrorMessage>{error}</ErrorMessage>}
      
      <p>Seleccione las categorías para asignar a esta competencia:</p>
      
      <CategoriesList>
        {categories.length > 0 ? (
          categories.map(category => (
            <CategoryItem key={category.id}>
              <CategoryCheckbox
                type="checkbox"
                id={`category-${category.id}`}
                checked={selectedCategories.includes(category.id)}
                onChange={(e) => handleCategorySelect(category.id, e.target.checked)}
              />
              <CategoryName>
                {category.name}
              </CategoryName>
              <CategoryCode>
                {category.code}
              </CategoryCode>
            </CategoryItem>
          ))
        ) : (
          <p>No hay categorías disponibles</p>
        )}
      </CategoriesList>
      
      <ActionButtons>
        <Button
          variant="outline"
          onClick={onCancel}
        >
          Cancelar
        </Button>
        <Button
          variant="primary"
          onClick={handleSubmit}
          disabled={isSubmitting}
        >
          {isSubmitting ? 'Asignando...' : 'Asignar Categorías'}
        </Button>
      </ActionButtons>
    </FormContainer>
  );
};

export default CategoryAssignmentForm;