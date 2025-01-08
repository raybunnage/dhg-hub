# Using Cursor Composer: A Comprehensive Guide

## Basic Composer Usage

1. **Opening the Composer**
   - Use `/` to open the composer
   - Type a description of what you want to create
   - The composer will generate complete files or code snippets

2. **File Generation Commands**
   Examples:
   ```
   /create a FastAPI router for user authentication
   /create a React component for a login form with Material UI
   /create a TypeScript interface for user data
   ```

## Template Categories

### 1. Backend Templates

```bash
/create fastapi router
/create pydantic model
/create pytest fixture
/create supabase client
/create fastapi middleware
```

### 2. Frontend Templates

```bash
/create react component
/create custom hook
/create zustand store
/create api service
/create form validation
```

### 3. Testing Templates

```bash
/create unit test
/create integration test
/create test fixture
/create mock data
```

## Best Practices

### 1. Be Specific
- Bad: `/create api endpoint`
- Good: `/create FastAPI endpoint for user registration with email verification`

### 2. Include Context

Example:
```bash
/create React component that uses:
- User authentication store
- Material UI theme
- Form validation
- Error handling
```

### 3. Request Related Files Together

Example:
```bash
/create a complete user authentication system including:
- FastAPI router with JWT authentication
- User and Token Pydantic models
- React login/register forms with Material UI
- Authentication API client
- Protected route HOC
```

## Advanced Usage

### 1. File Structure Generation

```bash
/create project structure for a FastAPI backend with:
- /app
  - /auth
  - /models
  - /api
  - /tests
- /config
- /utils
```

### 2. Configuration Files

```bash
# TypeScript Configuration
/create tsconfig.json with:
- Strict mode enabled
- Path aliases
- ESNext features
- React JSX support

# ESLint Configuration
/create eslint config with:
- TypeScript support
- React hooks rules
- Import sorting
- Prettier integration

# PyTest Configuration
/create pytest.ini with:
- Async test support
- Coverage reporting
- Environment variables
```

### 3. Documentation

```bash
# API Documentation
/create OpenAPI documentation for:
- Authentication endpoints
- User management
- Error responses
- Security schemes

# Component Documentation
/create component documentation with:
- Props interface
- Usage examples
- Styling guide
- Testing instructions
```

## Tips for Better Results

### 1. Include Technology Stack

```bash
/create using:
- FastAPI 0.110.0
- React 18
- Material UI v5
- Zustand for state
- React Query v5
- TypeScript 5.2
```

### 2. Specify Patterns

```bash
# Repository Pattern
/create user service following repository pattern with:
- Interface definition
- Implementation class
- Dependency injection
- Error handling

# CRUD Operations
/create CRUD endpoints for user management:
- GET /users
- POST /users
- PUT /users/{id}
- DELETE /users/{id}
```

### 3. Request Modifications

```bash
# Add Error Handling
/modify the generated code to include:
- Try-catch blocks
- Error boundaries
- Custom error types
- Error logging

# Add TypeScript Types
/add TypeScript types to:
- Component props
- API responses
- State management
- Utility functions
```

## Example Complete Workflows

### 1. User Authentication System

```bash
/create complete auth system with:
1. FastAPI JWT authentication router:
   - Login endpoint
   - Register endpoint
   - Refresh token endpoint
   - Password reset

2. User Pydantic models:
   - User base model
   - User create model
   - User response model
   - Token models

3. React components:
   - Login form
   - Registration form
   - Password reset form
   - Protected route wrapper

4. Authentication store:
   - Token management
   - User state
   - Login/logout actions
   - Persistence
```

### 2. Data Management Feature

```bash
/create CRUD feature for:
1. FastAPI endpoints:
   - List items
   - Create item
   - Update item
   - Delete item
   - Batch operations

2. Data models:
   - Base model
   - Create/Update models
   - Response models
   - Validation rules

3. React data grid component:
   - Sorting
   - Filtering
   - Pagination
   - Row selection

4. API service layer:
   - API client methods
   - Error handling
   - Request/response types
   - Cache management

5. Unit tests:
   - API endpoint tests
   - Component tests
   - Integration tests
   - Mock data generators
```

## Template Customization

You can create your own templates by:
1. Creating a base template
2. Using the composer to modify it
3. Saving common patterns for reuse

Example:
```bash
/create template for React component with:
- TypeScript strict mode
- Props interface with documentation
- Styled components setup
- Unit test file with testing-library
- Storybook story
- README.md documentation
```

## Integration with Version Control

When using the composer:
1. Generate code in logical chunks
2. Review generated code before committing
3. Add appropriate comments and documentation
4. Make sure generated code follows project conventions

Remember that the composer is a tool to accelerate development, but you should always review and understand the generated code before using it in your project.
```

This version provides more detailed examples and better formatting for each section, making it more practical as a reference guide.