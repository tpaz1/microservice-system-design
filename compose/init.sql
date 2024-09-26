-- Create user
CREATE USER auth_user WITH PASSWORD 'Auth123';

-- Create database
CREATE DATABASE auth;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE auth TO auth_user;

-- Connect to the auth database\c auth auth_user
\c auth auth_user

-- Create table
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) NOT NULL UNIQUE,
  password VARCHAR(255) NOT NULL
);

-- Insert data
INSERT INTO users (email, password) VALUES ('<your-username>', '<your-password>');
