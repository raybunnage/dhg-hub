# Using Cursor Composer: A Comprehensive Guide

## Getting Started with Composer

### What is Composer?
Composer is Cursor's AI-powered code generation tool that helps you create files, components, and entire features using natural language commands. Think of it as having a senior developer who can scaffold code based on your descriptions.

### Basic Commands
1. **Opening Composer**
   - Press `/` anywhere in Cursor
   - Start typing your request
   - Press Enter to generate code

2. **Simple Examples to Try First**
   ```bash
   # Create a simple React component
   /create a React button component called PrimaryButton

   # Create a Python function
   /create a function that calculates the average of a list of numbers

   # Create a TypeScript interface
   /create an interface for a User object with email, password, and name
   ```

### Learning to Describe What You Want

1. **Start Simple**
   ```bash
   # Bad ❌
   /create something for users

   # Good ✅
   /create a React component that displays user information
   ```

2. **Add Details Gradually**
   ```bash
   # Start basic
   /create a login form

   # Then add more details
   /create a login form with:
   - Email and password fields
   - Form validation
   - Error messages
   - Loading state
   - Remember me checkbox
   ```

3. **Use Technical Terms**
   ```bash
   # Less Clear ❌
   /create a thing that saves user info

   # More Clear ✅
   /create a TypeScript interface for user data with MongoDB types
   ```

## Real-World Examples

### 1. Creating a Full Feature

```bash
# Step 1: Start with the backend
/create a FastAPI endpoint for user registration with:
- Email validation
- Password hashing
- JWT token generation
- Supabase integration

# Step 2: Add the data model
/create a Pydantic model for user registration with:
- Email field with validation
- Password field with min length
- Optional name field
- Created at timestamp

# Step 3: Create the frontend form
/create a React registration form using:
- Material UI components
- React Hook Form
- Zod validation
- Error handling
- Loading states
```

### 2. Building Common Components

```bash
# Data Table Component
/create a reusable Material UI data table component with:
- Sorting
- Filtering
- Pagination
- Row selection
- TypeScript props
- Loading state
- Error handling

# Navigation Component
/create a responsive navigation bar using:
- Material UI AppBar
- Mobile menu
- User avatar
- Theme switching
- Authentication status
```

### 3. Setting Up Project Structure

```bash
# Frontend Structure
/create a React project structure following best practices with:
- Feature-based organization
- Shared components
- Custom hooks
- API services
- Type definitions
- Test setup
- State management

# Backend Structure
/create a FastAPI project structure with:
- Router organization
- Middleware setup
- Database connections
- Authentication
- Error handling
- Testing framework
```

## Tips for Better Results

### 1. Be Specific About Technologies

```bash
# Less Specific ❌
/create a login page

# More Specific ✅
/create a login page using:
- React 18
- Material UI v5
- React Hook Form
- Zod validation
- TypeScript
- Zustand for state
```

### 2. Include Error Cases

```bash
/create a user registration form that handles:
- Network errors
- Validation errors
- Duplicate email errors
- Password strength requirements
- Rate limiting errors
```

### 3. Request Documentation

```bash
/create documentation for this component including:
- Usage examples
- Props description
- Common patterns
- Edge cases
- Testing guidelines
```

## Common Patterns by Experience Level

### For Beginners

```bash
# Learning Component Structure
/create a simple React component showing:
- Basic structure
- Props usage
- Event handling
- State management
- Comments explaining each part

# Understanding TypeScript
/create a TypeScript example showing:
- Basic types
- Interfaces
- Type inference
- Generic usage
- Common patterns
```

### For Intermediate Developers

```bash
# Custom Hooks
/create a custom hook for:
- API data fetching
- Form handling
- Authentication
- Local storage
- Window events

# State Management
/create a Zustand store with:
- Multiple slices
- TypeScript types
- Action creators
- Persistence
- DevTools setup
```

### For Advanced Developers

```bash
# Architecture Patterns
/create an example of:
- Repository pattern implementation
- Service layer architecture
- Event-driven design
- Clean architecture
- Domain-driven design

# Performance Optimization
/create examples of:
- React memo usage
- Callback optimization
- Virtual list implementation
- Code splitting
- Performance monitoring
```

## Troubleshooting Tips

If the generated code isn't quite what you want:

1. **Iterate on Your Request**
   ```bash
   # First attempt
   /create a data table

   # Refined attempt
   /create a data table with specific features:
   - Column sorting
   - Row filtering
   - Pagination
   ```

2. **Ask for Modifications**
   ```bash
   /modify the previous code to:
   - Add error handling
   - Include TypeScript types
   - Add documentation
   ```

3. **Request Explanations**
   ```bash
   /explain how this code works, focusing on:
   - The main patterns used
   - Error handling approach
   - State management
   - Performance considerations
   ```

Remember: The key to effective use of Composer is being clear, specific, and iterative in your requests. Start simple and build up complexity as needed.
```

This version provides more detailed examples and better formatting for each section, making it more practical as a reference guide.