// src/components/competitions/CategoryAssignmentForm.jsx

import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { fetchCategories, assignCategories } from '../../services/api';
import Button from '../common/Button';
import Input from '../common/Input';

const CategoryAssignmentForm = ({ competitionId, onSuccess, onCancel }) => {
  const [categories, setCategories] = useState([]);
  const [selectedCategories, setSelectedCategories] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [filteredCategories, setFilteredCategories] = useState([]);
  
  // Cargar categorías disponibles
  useEffect(() => {
    const loadCategories = async () => {
      setIsLoading(true);
      try {
        const response = await fetchCategories();
        setCategories(response.data);
        setFilteredCategories(response.data);
      } catch (err) {
        setError('Error al cargar categorías: ' + err.message);
      } finally {
        setIsLoading(false);
      }
    };
    
    loadCategories();
  }, []);
  
  // Filtrar categorías cuando cambia la búsqueda
  useEffect(() => {
    if (!searchQuery.trim()) {
      setFilteredCategories(categories);
      return;
    }
    
    const query = searchQuery.toLowerCase();
    const filtered = categories.filter(category => 
      category.name.toLowerCase().includes(query) ||
      category.code.toLowerCase().includes(query) ||
      (category.description && category.description.toLowerCase().includes(query))
    );
    
    setFilteredCategories(filtered);
  }, [searchQuery, categories]);
  
  // Manejar selección de categoría
  const handleCategorySelect = (categoryId, isSelected) => {
    if (isSelected) {
      setSelectedCategories(prev => [...prev, categoryId]);
    } else {
      setSelectedCategories(prev => prev.filter(id => id !== categoryId));
    }
  };
  
  // Seleccionar/deseleccionar todas las categorías
  const handleSelectAll = () => {
    if (selectedCategories.length === filteredCategories.length) {
      // Si todas están seleccionadas, deseleccionar todas
      setSelectedCategories([]);
    } else {
      // Seleccionar todas las filtradas
      setSelectedCategories(filteredCategories.map(cat => cat.id));
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
    return <LoadingMessage>Cargando categorías disponibles...</LoadingMessage>;
  }
  
  return (
    <FormContainer>
      {error && <ErrorMessage>{error}</ErrorMessage>}
      
      <p>Seleccione las categorías para asignar a esta competencia:</p>
      
      <SearchBox>
        <Input
          id="search-categories"
          placeholder="Buscar categorías..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          fullWidth
        />
      </SearchBox>
      
      <SelectAllContainer>
        <Button 
          type="button" 
          variant="text" 
          size="small"
          onClick={handleSelectAll}
        >
          {selectedCategories.length === filteredCategories.length ? 
            'Deseleccionar todas' : 'Seleccionar todas'}
        </Button>
      </SelectAllContainer>
      
      <CategoriesList>
        {filteredCategories.length > 0 ? (
          filteredCategories.map(category => (
            <CategoryItem key={category.id}>
              <CategoryCheckbox
                type="checkbox"
                id={`category-${category.id}`}
                checked={selectedCategories.includes(category.id)}
                onChange={(e) => handleCategorySelect(category.id, e.target.checked)}
              />
              <CategoryDetails>
                <CategoryName>{category.name}</CategoryName>
                <CategoryCode>{category.code}</CategoryCode>
                {category.description && (
                  <CategoryDescription>{category.description}</CategoryDescription>
                )}
              </CategoryDetails>
            </CategoryItem>
          ))
        ) : (
          <EmptyMessage>No se encontraron categorías con esos criterios</EmptyMessage>
        )}
      </CategoriesList>
      
      <CategoryCounter>
        {selectedCategories.length} categorías seleccionadas
      </CategoryCounter>
      
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

// Estilos para el componente
const FormContainer = styled.div`
  background-color: white;
  border-radius: 8px;
  padding: 24px;
`;

const SearchBox = styled.div`
  margin-bottom: 8px;
`;

const SelectAllContainer = styled.div`
  text-align: right;
  margin-bottom: 8px;
`;

const CategoriesList = styled.div`
  max-height: 300px;
  overflow-y: auto;
  margin-bottom: 16px;
  border: 1px solid ${props => props.theme.colors.lightGray};
  border-radius: 4px;
  padding: 16px;
`;

const CategoryItem = styled.div`
  display: flex;
  align-items: flex-start;
  padding: 12px 0;
  border-bottom: 1px solid ${props => props.theme.colors.lightGray};
  
  &:last-child {
    border-bottom: none;
  }
`;

const CategoryCheckbox = styled.input`
  margin-right: 16px;
  margin-top: 4px;
  width: 18px;
  height: 18px;
  cursor: pointer;
`;

const CategoryDetails = styled.div`
  flex: 1;
`;

const CategoryName = styled.div`
  font-weight: 500;
`;

const CategoryCode = styled.div`
  font-size: 14px;
  color: ${props => props.theme.colors.primary};
  margin-top: 4px;
`;

const CategoryDescription = styled.div`
  font-size: 14px;
  color: ${props => props.theme.colors.gray};
  margin-top: 4px;
`;

const CategoryCounter = styled.div`
  font-size: 14px;
  color: ${props => props.theme.colors.gray};
  margin-bottom: 16px;
`;

const ActionButtons = styled.div`
  display: flex;
  justify-content: flex-end;
  gap: 16px;
  margin-top: 24px;
`;

const ErrorMessage = styled.div`
  background-color: ${props => props.theme.colors.errorLight};
  color: ${props => props.theme.colors.error};
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 16px;
`;

const LoadingMessage = styled.div`
  text-align: center;
  padding: 24px;
  color: ${props => props.theme.colors.gray};
`;

const EmptyMessage = styled.div`
  text-align: center;
  padding: 24px;
  color: ${props => props.theme.colors.gray};
`;

export default CategoryAssignmentForm;