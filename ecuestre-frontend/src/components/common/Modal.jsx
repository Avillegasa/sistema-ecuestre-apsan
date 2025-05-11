import React, { useEffect, useRef } from 'react';
import styled from 'styled-components';
import Button from './Button';

// Overlay que cubre toda la pantalla
const Overlay = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: ${props => props.theme.spacing.md};
`;

// Contenedor principal del modal
const ModalContainer = styled.div`
  background-color: ${props => props.theme.colors.white};
  border-radius: ${props => props.theme.borderRadius.medium};
  box-shadow: ${props => props.theme.shadows.large};
  width: 100%;
  max-width: ${props => {
    switch (props.size) {
      case 'small': return '400px';
      case 'large': return '800px';
      case 'xlarge': return '1000px';
      default: return '600px'; // medium
    }
  }};
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  animation: modalFadeIn 0.3s ease;
  
  @keyframes modalFadeIn {
    from {
      opacity: 0;
      transform: translateY(-20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
`;

// Cabecera del modal
const ModalHeader = styled.div`
  padding: ${props => props.theme.spacing.md} ${props => props.theme.spacing.lg};
  border-bottom: 1px solid ${props => props.theme.colors.lightGray};
  display: flex;
  align-items: center;
  justify-content: space-between;
`;

// Título del modal
const ModalTitle = styled.h3`
  margin: 0;
  font-family: ${props => props.theme.fonts.heading};
  font-size: ${props => props.theme.fontSizes.large};
  color: ${props => props.theme.colors.text};
`;

// Botón para cerrar el modal
const CloseButton = styled.button`
  background: none;
  border: none;
  cursor: pointer;
  font-size: ${props => props.theme.fontSizes.xl};
  line-height: 1;
  color: ${props => props.theme.colors.gray};
  padding: ${props => props.theme.spacing.xs};
  transition: color ${props => props.theme.transitions.fast};
  
  &:hover {
    color: ${props => props.theme.colors.text};
  }
`;

// Cuerpo del modal
const ModalBody = styled.div`
  padding: ${props => props.theme.spacing.lg};
  overflow-y: auto;
  flex: 1;
`;

// Pie del modal
const ModalFooter = styled.div`
  padding: ${props => props.theme.spacing.md} ${props => props.theme.spacing.lg};
  border-top: 1px solid ${props => props.theme.colors.lightGray};
  display: flex;
  justify-content: flex-end;
  gap: ${props => props.theme.spacing.md};
`;

/**
 * Componente Modal reutilizable
 * 
 * @param {Object} props - Propiedades del componente
 * @param {boolean} props.isOpen - Si el modal está abierto
 * @param {Function} props.onClose - Función a ejecutar cuando se cierra el modal
 * @param {string} props.title - Título del modal
 * @param {React.ReactNode} props.children - Contenido del modal
 * @param {string} [props.size='medium'] - Tamaño del modal: small, medium, large, xlarge
 * @param {boolean} [props.showCloseButton=true] - Si mostrar el botón de cerrar
 * @param {Array} [props.footerButtons] - Botones para el pie del modal
 * @param {Function} [props.onConfirm] - Función a ejecutar cuando se confirma la acción
 * @param {string} [props.confirmText='Confirmar'] - Texto del botón de confirmar
 * @param {string} [props.cancelText='Cancelar'] - Texto del botón de cancelar
 * @param {boolean} [props.showFooter=true] - Si mostrar el pie del modal
 */
const Modal = ({
  isOpen,
  onClose,
  title,
  children,
  size = 'medium',
  showCloseButton = true,
  footerButtons,
  onConfirm,
  confirmText = 'Confirmar',
  cancelText = 'Cancelar',
  showFooter = true,
}) => {
  // Ref para el contenedor del modal
  const modalRef = useRef();
  
  // Cerrar modal con Escape
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };
    
    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
    }
    
    return () => {
      document.removeEventListener('keydown', handleEscape);
    };
  }, [isOpen, onClose]);
  
  // Evitar scroll en el body cuando el modal está abierto
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'auto';
    }
    
    return () => {
      document.body.style.overflow = 'auto';
    };
  }, [isOpen]);
  
  // No renderizar nada si el modal no está abierto
  if (!isOpen) return null;
  
  // Evitar que los clics dentro del modal lo cierren
  const handleContainerClick = (e) => {
    e.stopPropagation();
  };
  
  return (
    <Overlay onClick={onClose}>
      <ModalContainer 
        ref={modalRef}
        onClick={handleContainerClick}
        size={size}
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
      >
        <ModalHeader>
          <ModalTitle id="modal-title">{title}</ModalTitle>
          {showCloseButton && (
            <CloseButton onClick={onClose} aria-label="Cerrar">
              &times;
            </CloseButton>
          )}
        </ModalHeader>
        
        <ModalBody>{children}</ModalBody>
        
        {showFooter && (
          <ModalFooter>
            {footerButtons ? (
              // Botones personalizados
              footerButtons
            ) : (
              // Botones predeterminados
              <>
                <Button variant="outline" onClick={onClose}>
                  {cancelText}
                </Button>
                <Button variant="primary" onClick={onConfirm}>
                  {confirmText}
                </Button>
              </>
            )}
          </ModalFooter>
        )}
      </ModalContainer>
    </Overlay>
  );
};

export default Modal;