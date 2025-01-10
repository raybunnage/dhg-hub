## Getting Started
(Coming soon: Setup instructions, environment configuration, and development guidelines)

[← Back to Main Documentation](./README.MD)

# Getting Started

when to do these?
uv pip uninstall dhg-hub  # Remove old installation
uv pip install -e .       # Reinstall in editable mode

diff pyproject.toml backend/pyproject.toml

grep -r "from pydantic import Secret" backend/src/dhg/

uv pip uninstall pydantic pydantic-settings
uv pip install -e .

# Verify installed versions
pip freeze | grep pydantic




## Initial Setup

### Virtual Environment
```bash
source .venv/bin/activate
```


flask test run --env dev

flask test run --env test

flask test run --env prod

flask test run --env dev --coverage

rm -rf .pytest_cache

**When to use**: Always run this first before any development work. Creates an isolated environment for your project.

## Run Tests 
pytest backend/tests -v -s
pytest backend/tests -v -s --cov=backend/src/dhg
pytest backend/tests -v -s --tb=long
pytest backend/tests -v -s -x
pytest backend/tests -v -s --showlocals
pytest backend/tests -v -s -x --showlocals


pytest backend/tests/test_imports.py -v -s --showlocals
pytest backend/tests/services/supabase/mixins/test_utils_mixin.py -v -s --showlocals
pytest backend/tests/services/supabase/test_integration.py -v -s --showlocals
pytest backend/tests/test_experts.py -v -s --showlocals
pytest backend/tests/test_supabase_service.py -v -s --showlocals
pytest backend/tests/test_uni_document_types.py -v -s --showlocals
pytest backend/tests/unit/test_supabase_service.py -v -s --showlocals

chmod +x scripts/refresh_tests.sh

./scripts/refresh_tests.sh

this works
PYTHONPATH=. pytest

**Tip**: You should see `(.venv)` in your terminal prompt when activated.

### Verify Setup
```bash
which python
```
**When to use**: To confirm you're using the Python installation from your virtual environment.

## Managing Dependencies

### Update Requirements Files
```bash
# Generate main requirements
uv pip compile pyproject.toml -o requirements.txt

# Generate development requirements
uv pip compile pyproject.toml --extra dev -o requirements-dev.txt
```
**When to use**: After adding new dependencies to `pyproject.toml`

### Install Dependencies
```bash
# Install all dependencies (main + dev)
uv pip install -r requirements.txt -r requirements-dev.txt

# OR install separately:
uv pip install -e .           # main dependencies
uv pip install -e ".[dev]"    # dev dependencies
```
**When to use**: 
- After first cloning the project
- After pulling changes with new dependencies
- After updating requirements files

**Note**: The `-e` flag enables "editable" mode, so your code changes take effect immediately.

## Project Structure
```bash
# Create Python package directories
touch backend/src/__init__.py
touch backend/src/dhg/__init__.py
touch backend/src/dhg/api/__init__.py
touch backend/src/dhg/core/__init__.py
touch backend/src/dhg/models/__init__.py
touch backend/src/dhg/services/__init__.py
touch backend/src/dhg/services/supabase/__init__.py
```
**When to use**: One-time setup when initializing the project structure.

## Testing
```bash
pytest tests/test_imports.py -v -s
```
**When to use**: To verify Python imports are working correctly
- `-v`: verbose output
- `-s`: shows print statements

## Pro Tips
1. **Always activate** your virtual environment first
2. Run commands **one at a time**, checking for success
3. Read error messages carefully - they usually point to the solution
4. Keep this guide handy - you'll reference it often
5. **View project structure** with:
```bash
tree -I "node_modules|__pycache__|.git|.pytest_cache|*.pyc|.DS_Store" backend/src/dhg
```
**When to use**: To get a clean view of your project structure, excluding common temporary/generated files

[← Back to Main Documentation](./README.MD)

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


Key changes made:
Replaced class Config with model_config = SettingsConfigDict
Added SecretStr for all sensitive fields like:
API keys
Passwords
Private keys
Authentication tokens
Left non-sensitive fields as str
When you need to use these values in your code:


# Access the secret value
secret_key = settings.supabase_key.get_secret_value()

# Or just pass the SecretStr object directly to libraries that know how to handle it
client = SomeClient(api_key=settings.openai_api_key)


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

