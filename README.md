# Sistema Ecuestre APSAN

Sistema para automatizar el proceso de evaluación ecuestre según normativas FEI, permitiendo que 3 jueces evalúen a cada jinete usando dispositivos móviles y computadoras, con cálculo automático y actualización de rankings en tiempo real.

## Tecnologías Utilizadas

### Backend:
- Django 4.2.7
- Django REST Framework
- Django Channels (WebSockets)
- Firebase (para datos en tiempo real)

### Frontend:
- React 18
- React Router Dom
- Styled Components
- Firebase SDK
- IndexedDB (para funcionalidad offline)

## Requisitos Previos

- Python 3.8+
- Node.js 16+
- npm o yarn
- PostgreSQL (para producción)
- Firebase Realtime Database

## Configuración Inicial

### Configuración del Backend (Django)

1. Clonar el repositorio:
```bash
git clone https://github.com/tu-usuario/sistema-ecuestre-apsan.git
cd sistema-ecuestre-apsan
```

2. Crear y activar entorno virtual:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Realizar migraciones iniciales:
```bash
python manage.py migrate
```

5. Crear superusuario:
```bash
python manage.py createsuperuser
```

6. Ejecutar servidor:
```bash
python manage.py runserver
```

### Configuración del Frontend (React)

1. Ingresar al directorio del frontend:
```bash
cd ecuestre-frontend
```

2. Instalar dependencias:
```bash
npm install
```

3. Crear archivo `.env.local` con las variables de entorno para Firebase:
```
REACT_APP_FIREBASE_API_KEY=tu_api_key
REACT_APP_FIREBASE_AUTH_DOMAIN=tu_dominio.firebaseapp.com
REACT_APP_FIREBASE_DATABASE_URL=https://tu_proyecto.firebaseio.com
REACT_APP_FIREBASE_PROJECT_ID=tu_proyecto_id
REACT_APP_FIREBASE_STORAGE_BUCKET=tu_proyecto.appspot.com
REACT_APP_FIREBASE_MESSAGING_SENDER_ID=tu_sender_id
REACT_APP_FIREBASE_APP_ID=tu_app_id
```

4. Ejecutar servidor de desarrollo:
```bash
npm start
```

## Estructura del Proyecto

### Backend (Django)

- `ecuestre_project/`: Configuración principal del proyecto
  - `settings/`: Configuraciones separadas para desarrollo y producción
  - `urls.py`: Rutas principales
  - `asgi.py`: Configuración para WebSockets
- `users/`: Aplicación para usuarios y autenticación
- `competitions/`: Aplicación para gestionar competencias
- `judging/`: Aplicación para evaluación y cálculos FEI

### Frontend (React)

- `src/components/`: Componentes reutilizables
  - `common/`: Componentes básicos (Button, Input, Modal)
  - `layout/`: Componentes de estructura (Header, Sidebar, Footer)
  - `judging/`: Componentes de calificación
  - `rankings/`: Componentes de rankings
- `src/pages/`: Páginas principales de la aplicación
- `src/services/`: Servicios para APIs y Firebase
- `src/hooks/`: Custom hooks para lógica reutilizable
- `src/context/`: Contextos de React (Auth, Competition)
- `src/utils/`: Utilidades y funciones auxiliares
- `src/styles/`: Estilos compartidos

## Características Principales

1. **Evaluación por Jueces**:
   - 3 jueces simultáneos por competencia
   - Calificación según sistema FEI (3 celdas)
   - Cálculo automático de resultados

2. **Ranking en Tiempo Real**:
   - Actualización automática vía Firebase
   - Animación de cambios de posición
   - Visualización en pantallas grandes

3. **Funcionamiento Offline**:
   - Detección automática de estado de conexión
   - Almacenamiento local de calificaciones
   - Sincronización automática al recuperar conexión

4. **Interfaz Optimizada**:
   - Diseño responsivo para móviles y computadoras
   - Botones grandes para uso con guantes
   - Alto contraste para visibilidad en exteriores

## Licencia

Este proyecto es propiedad exclusiva de APSAN (Asociación Paceña de Salto y Adiestramiento).