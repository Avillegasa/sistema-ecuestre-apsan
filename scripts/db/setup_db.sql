-- Script de configuración de base de datos PostgreSQL para Sistema Ecuestre APSAN

-- Crear base de datos
CREATE DATABASE sistema_ecuestre;

-- Crear usuario con privilegios
CREATE USER sistema_ecuestre_admin WITH PASSWORD 'password_seguro';
GRANT ALL PRIVILEGES ON DATABASE sistema_ecuestre TO sistema_ecuestre_admin;

-- Conectar a la base de datos
\c sistema_ecuestre

-- Configurar extensiones que podríamos necesitar
CREATE EXTENSION IF NOT EXISTS pg_trgm; -- Para búsquedas de texto
CREATE EXTENSION IF NOT EXISTS unaccent; -- Para búsquedas sin acentos
CREATE EXTENSION IF NOT EXISTS "uuid-ossp"; -- Para generar UUIDs
