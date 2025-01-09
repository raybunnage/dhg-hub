## Getting Started
(Coming soon: Setup instructions, environment configuration, and development guidelines)

[← Back to Main Documentation](./README.MD)


# Common Development Commands

## Initial Setup Commands

### 1. Activate Virtual Environment
```bash
source .venv/bin/activate
```
**When to use**: Run this first before doing any Python development work. This creates an isolated environment for your project's dependencies.

### 2. Check Python Location
```bash
which python
```
**When to use**: Run this to verify you're using the correct Python installation from your virtual environment.

## Dependency Management

### 1. Generate Requirements Files
```bash
# For main dependencies
uv pip compile pyproject.toml -o requirements.txt

# For development dependencies
uv pip compile pyproject.toml --extra dev -o requirements-dev.txt
```
**When to use**: Run these when you've added new dependencies to your `pyproject.toml` file and need to update the requirements files.

### 2. Install Dependencies
```bash
# Install everything (both main and dev dependencies)
uv pip install -r requirements.txt -r requirements-dev.txt

# Install main project dependencies
uv pip install -e .

# Install development dependencies
uv pip install -e ".[dev]"
```
**When to use**: 
- Run after cloning the project for the first time
- Run after pulling changes that include new dependencies
- The `-e` flag installs in "editable" mode, meaning changes to the code are reflected immediately

## Project Structure Setup
```bash
# Create necessary Python package directories
touch backend/src/__init__.py
touch backend/src/dhg/__init__.py
touch backend/src/dhg/api/__init__.py
touch backend/src/dhg/core/__init__.py
touch backend/src/dhg/models/__init__.py
touch backend/src/dhg/services/__init__.py
touch backend/src/dhg/services/supabase/__init__.py
```
**When to use**: Run these commands when setting up the project structure for the first time. The `touch` command creates empty files that Python needs to recognize directories as packages.

## Testing
```bash
pytest tests/test_imports.py -v -s
```
**When to use**: Run this to test if your Python imports are working correctly. The flags mean:
- `-v`: verbose output (shows more details)
- `-s`: allows print statements to be displayed in the output

## Pro Tips for Beginners
1. Always make sure your virtual environment is activated (you should see `(.venv)` in your terminal prompt)
2. Run commands one at a time and make sure each succeeds before moving to the next
3. If you get errors, read the error message carefully - they often tell you exactly what's wrong
4. Keep these commands handy - you'll use them frequently during development



### 2. Check Python Location
```bash
which python
```
**When to use**: Run this to verify you're using the correct Python installation from your virtual environment.

When to use: Run this to verify you're using the correct Python installation from your virtual environment.
Dependency Management

1. Generate Requirements Files

# For main dependencies
uv pip compile pyproject.toml -o requirements.txt

# For development dependencies
uv pip compile pyproject.toml --extra dev -o requirements-dev.txt

When to use: Run these when you've added new dependencies to your pyproject.toml file and need to update the requirements files.
2. Install Dependencies

# Install everything (both main and dev dependencies)
uv pip install -r requirements.txt -r requirements-dev.txt

# Install main project dependencies
uv pip install -e .

# Install development dependencies
uv pip install -e ".[dev]"

When to use:
Run after cloning the project for the first time
Run after pulling changes that include new dependencies
The -e flag installs in "editable" mode, meaning changes to the code are reflected immediately
Project Structure Setup

# Create necessary Python package directories
touch backend/src/__init__.py
touch backend/src/dhg/__init__.py
touch backend/src/dhg/api/__init__.py
touch backend/src/dhg/core/__init__.py
touch backend/src/dhg/models/__init__.py
touch backend/src/dhg/services/__init__.py
touch backend/src/dhg/services/supabase/__init__.py

When to use: Run these commands when setting up the project structure for the first time. The touch command creates empty files that Python needs to recognize directories as packages.

Testing

pytest tests/test_imports.py -v -s


When to use: Run this to test if your Python imports are working correctly. The flags mean:
-v: verbose output (shows more details)
-s: allows print statements to be displayed in the output
Pro Tips for Beginners
Always make sure your virtual environment is activated (you should see (.venv) in your terminal prompt)
Run commands one at a time and make sure each succeeds before moving to the next
If you get errors, read the error message carefully - they often tell you exactly what's wrong
Keep these commands handy - you'll use them frequently during development


## Frequent Commands

## Git Commands
- `git checkout -b feature/name` - Creates and switches to a new branch
  - Use when starting work on a new feature or bugfix
  - Replace "name" with a descriptive branch name

- `git add .` - Stages all changed files for commit
  - Use before committing to include all your changes
  - Be careful as this includes ALL changes in current directory

- `git commit -m "message"` - Commits staged changes
  - Use to save your changes with a descriptive message
  - Keep messages clear and concise

- `git push origin branch-name` - Pushes commits to remote repository
  - Use when ready to share your changes with the team
  - Replace "branch-name" with your current branch

## Testing Commands
- `npm test` - Runs all tests
  - Use during development to ensure code quality
  - Run before submitting pull requests

- `npm run test:watch` - Runs tests in watch mode
  - Use during active development
  - Tests automatically rerun when files change

## Build Commands
- `npm run build` - Creates production build
  - Use when preparing code for deployment
  - Optimizes and minifies code

- `npm run dev` - Starts development server
  - Use during local development
  - Provides hot-reloading for faster development

// ... rest of file remains unchanged ...

## Documentation Structure
The following documentation sections will be expanded:

1. `/docs/backend/services/`
   - Supabase Integration Guide
   - Google Drive Integration
   - Anthropic AI Implementation
   - PDF Processing Service

2. `/docs/backend/database/`
   - Schema Design
   - Data Models
   - Migration Guides

3. `/docs/frontend/`
   - Component Library
   - State Management
   - UI/UX Guidelines

4. `/docs/deployment/`
   - Environment Setup
   - Deployment Procedures
   - Monitoring and Maintenance

## For New Developers
This project is designed for intermediate developers looking to expand their full-stack development skills. Key areas to focus on:

1. **Backend Development**
   - Understanding FastAPI and Python class-based architecture
   - Working with type hints and abstract classes
   - Implementing service integrations
   - Writing and maintaining tests

2. **Frontend Development**
   - React component architecture
   - State management
   - API integration
   - Modern JavaScript/TypeScript practices

3. **Document Processing**
   - PDF handling and text extraction
   - Document storage and retrieval
   - Search and categorization

4. **Database Management**
   - Supabase operations
   - Data modeling
   - Query optimization

## Next Steps
- Review the documentation structure
- Set up your local development environment
- Familiarize yourself with the codebase organization
- Start with small features or bug fixes to understand the workflow

More detailed documentation for each component will be added as the project evolves.

## Using Templates with Cursor AI

Templates in web development typically refer to reusable HTML/component structures. With Cursor AI, you can generate templates in different ways depending on your framework (React, Vue, etc.).

### Generating Templates

#### Basic Approach
Ask Cursor something like:

typescript
"Generate a template for a user profile card component in React"

#### More Specific Requests
You can be more detailed with requests like:
- "Create a TypeScript React template for a data table with sorting and filtering"
- "Generate a form template with Zod validation"

### Example Template

Here's an example of what Cursor might generate:

typescript
interface ProfileCardProps {
name: string;
email: string;
avatar?: string;
}
const ProfileCard: React.FC<ProfileCardProps> = ({ name, email, avatar }) => {
return (
<div className="card">
{avatar && <img src={avatar} alt={${name}'s avatar} />}
<h2>{name}</h2>
<p>{email}</p>
</div>
);
};


### Best Practices for Template Generation

#### Be specific about:
- Framework (React, Vue, etc.)
- TypeScript/JavaScript
- Styling approach (CSS, Tailwind, etc.)
- Validation requirements
- Props/data structure

#### Ask for:
- Type definitions
- Props interface
- Basic styling
- Common functionality

### Common Template Types
- Forms
- Cards
- Lists
- Tables
- Layouts
- Navigation components

> **Remember:** Templates generated by AI are starting points - you'll likely need to customize them for your specific needs.

Let me explain both concepts:

### Props Interface (TypeScript)
A Props interface defines the type structure for React component properties. It's like a contract that specifies what data a component can receive.

```typescript
// Basic Props Interface Example
interface ButtonProps {
  text: string;              // Required text to display
  onClick: () => void;       // Required click handler
  color?: 'red' | 'blue';    // Optional color
  disabled?: boolean;        // Optional disabled state
}

// Using the interface in a React component
const Button: React.FC<ButtonProps> = ({ text, onClick, color = 'blue', disabled = false }) => {
  return (
    <button 
      onClick={onClick}
      disabled={disabled}
      className={`btn ${color}`}
    >
      {text}
    </button>
  );
};

// Using the component
<Button 
  text="Click me" 
  onClick={() => alert('clicked')}
  color="red"
/>
```

### Tailwind CSS
Tailwind is a utility-first CSS framework that lets you style elements using predefined classes directly in your HTML/JSX.

```jsx
// Without Tailwind
<div className="card">
  <img className="avatar" src="..." />
  <h2 className="title">Hello</h2>
</div>

// With Tailwind
<div className="rounded-lg shadow-md p-4 bg-white">
  <img className="w-12 h-12 rounded-full" src="..." />
  <h2 className="text-xl font-bold text-gray-800">Hello</h2>
</div>
```

Common Tailwind utilities:
- `flex` - Display flex
- `p-4` - Padding (16px)
- `mt-2` - Margin top (8px)
- `text-xl` - Font size
- `bg-blue-500` - Background color
- `hover:bg-blue-600` - Hover state
- `rounded-lg` - Border radius

Benefits of Tailwind:
1. No need to write custom CSS
2. Consistent spacing/colors
3. Responsive design built-in
4. Better performance (only includes used styles)
5. Easy to maintain

Example combining both concepts:
```typescript
interface CardProps {
  title: string;
  description: string;
  imageUrl?: string;
}

const Card: React.FC<CardProps> = ({ title, description, imageUrl }) => {
  return (
    <div className="rounded-lg shadow-md p-6 bg-white">
      {imageUrl && (
        <img 
          src={imageUrl} 
          className="w-full h-48 object-cover rounded-t-lg"
          alt={title}
        />
      )}
      <h2 className="text-xl font-bold text-gray-800 mt-4">{title}</h2>
      <p className="text-gray-600 mt-2">{description}</p>
    </div>
  );
};
```


## Documentation
Access auto-generated docs at:
- `/docs` (Swagger UI)
- `/redoc` (ReDoc)

## Best Practices
- Use Pydantic models for request/response validation
- Implement proper error handling
- Use dependency injection
- Write tests for all endpoints
- Use async where appropriate
- Implement proper logging
- Use environment variables for configuration

## Security Checklist
- Implement proper authentication
- Use HTTPS in production
- Validate all inputs
- Rate limiting
- Proper CORS configuration
- Secure password handling

## Remember to:
- Keep routes organized in separate files
- Document your API endpoints
- Handle errors gracefully
- Write tests as you develop
- Use async functions for I/O operations 


## API Documentation Tools

### Swagger UI (`/docs`)
- Interactive API documentation
- Lets you test API endpoints directly in the browser
- Shows request/response schemas
- Allows you to input parameters and try requests
- Available at `http://localhost:8000/docs`

### ReDoc (`/redoc`)
- Clean, easy-to-read API documentation
- More user-friendly for non-developers
- Better for sharing with stakeholders
- Available at `http://localhost:8000/redoc`

### How to Access Documentation

1. Start your FastAPI server:
```bash
uvicorn app.main:app --reload
```

2. Visit the URLs:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Auto-Generation Features
Documentation is automatically generated from:
- Your route definitions
- Pydantic models
- Function docstrings
- Parameter types

### Example Code
```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class User(BaseModel):
    name: str
    email: str

@app.post("/users/")
async def create_user(user: User):
    """
    Create a new user with the following information:
    
    - **name**: user's full name
    - **email**: user's email address
    """
    return user
```
// ... existing documentation ...

## Authentication with Supabase

This project uses Supabase for authentication. The FastAPI backend validates Supabase JWT tokens using a custom dependency.

### Key Implementation Details

1. Removed FastAPI's built-in OAuth2PasswordBearer in favor of Supabase authentication
2. Added `verify_supabase_token` dependency to validate Supabase JWT tokens
3. Updated Settings to include Supabase JWT public key

### Setup Instructions

1. Add your Supabase JWT public key to your `.env` file:
```env
SUPABASE_JWT_PUBLIC_KEY=your_public_key_here
```

2. Use the authentication dependency on protected routes:
```python
@app.get("/protected")
async def protected_route(user_data: dict = Depends(verify_supabase_token)):
    return {"message": "This is protected", "user": user_data}
```

3. Include the Supabase token in client requests:
```typescript
const response = await fetch('your-api-endpoint', {
  headers: {
    Authorization: `Bearer ${supabase.auth.session()?.access_token}`
  }
});
```

> **Note**: When using the Supabase client library, token management is handled automatically. You just need to forward the token in your API requests.

# Understanding Mixins in Python

Mixins are a form of multiple inheritance in Python that allow you to add functionality to classes. Think of them as "plugins" that add functionality to your classes without requiring traditional parent-child inheritance relationships.

## What are Mixins?

A mixin is a class that contains methods for use by other classes without having to be the parent class of those other classes. They act as "plugins" that add functionality.

### Simple Example

```python
# A mixin that adds logging capability
class LoggerMixin:
    def log(self, message):
        print(f"[LOG] {message}")

# A mixin that adds string formatting capability
class FormatterMixin:
    def format_string(self, string):
        return string.strip().lower()

# A class that uses both mixins
class UserService(LoggerMixin, FormatterMixin):
    def create_user(self, username):
        # Uses methods from both mixins
        formatted_name = self.format_string(username)
        self.log(f"Creating user: {formatted_name}")
        # ... rest of the implementation
```

In this example:
- `LoggerMixin` provides logging functionality
- `FormatterMixin` provides string formatting
- `UserService` inherits from both mixins to gain their functionality

