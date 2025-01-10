# Installed Libraries Documentation

A comprehensive guide to the libraries in this project's virtual environment, explaining their purposes and common use cases.

## Web Framework & API Libraries

### FastAPI (0.110.0)
- Modern, high-performance web framework for building APIs with Python
- **Key Strengths**:
  - Automatic OpenAPI/Swagger documentation generation
  - Built-in data validation via Pydantic
  - Asynchronous support by default
  - Type hints that actually enforce validation
  - Up to 300% faster than traditional frameworks
- **Best For**: Building modern, fast, production-ready APIs

### Starlette (0.36.3)
- Lightweight ASGI framework that powers FastAPI
- **Features**:
  - WebSocket support
  - GraphQL support
  - In-memory session storage
  - Static file serving
- **Why Important**: Provides the foundational async capabilities that make FastAPI fast

### Uvicorn (0.27.1)
- Lightning-fast ASGI server implementation
- **Why Use It**:
  - Built on uvloop and httptools for maximum performance
  - Supports HTTP/1.1 and WebSocket protocols
  - Hot reloading for development
  - Production-ready with process management
- **Common Usage**: Running FastAPI and other ASGI applications

### Gunicorn (22.0.0)
- Production-grade WSGI HTTP Server
- **Key Features**:
  - Pre-fork worker model
  - Multiple worker configurations
  - Process management and monitoring
  - Automatic worker process recycling
- **Why Use It**: Handles production workloads reliably with features like load balancing and process management

## Data Validation & Processing

### Pydantic (2.6.1)
- Data validation using Python type annotations
- **Why It's Essential**:
  - Validates complex data structures
  - Automatic JSON schema generation
  - Seamless integration with FastAPI
  - Type checking at runtime
  - High performance through Rust-based validator
- **Common Uses**:
  - API request/response validation
  - Configuration management
  - Data parsing and serialization

### SQLAlchemy (2.0.27)
- Comprehensive SQL toolkit and Object-Relational Mapping (ORM)
- **Key Features**:
  - Database engine abstraction
  - Powerful query construction
  - Schema migration tools (via Alembic)
  - Connection pooling
  - Transaction management
- **Why Use It**:
  - Write database-agnostic code
  - Avoid SQL injection vulnerabilities
  - Manage database operations in a Pythonic way
  - Handle complex database relationships easily

## HTTP & API Clients

### Requests (2.32.0)
- Human-friendly HTTP library
- **Why It's Popular**:
  - Intuitive API for HTTP operations
  - Automatic JSON decoding
  - Session persistence
  - Cookie handling
  - SSL/TLS verification
- **Best For**: Making HTTP requests in a simple, straightforward way

### HTTPX (0.25.2)
- Modern HTTP client with async support
- **Advantages over Requests**:
  - Async/await support
  - HTTP/2 support
  - Type annotations
  - Compatible with Requests API
- **When to Use**: Modern applications requiring async HTTP calls or HTTP/2 support

## Authentication & Security

### Python-Jose (3.3.0)
- JavaScript Object Signing and Encryption implementation
- **Key Capabilities**:
  - JWT token generation and validation
  - JWS (signed tokens)
  - JWE (encrypted tokens)
- **Common Usage**: Implementing secure token-based authentication

### BCrypt (4.2.1) & Passlib (1.7.4)
- Password hashing and verification libraries
- **Security Features**:
  - Adaptive hashing
  - Salt generation
  - Timing attack resistance
  - Multiple algorithm support (in Passlib)
- **Best Practices**: Use for secure password storage and verification

## Testing & Development Tools

### Pytest (8.0.2)
- Modern testing framework for Python
- **Why It's Better**:
  - Simple, readable test syntax
  - Powerful fixture system
  - Extensive plugin ecosystem
  - Detailed failure reports
  - Parameterized testing
- **Key Features**:
  - Auto-discovery of test files
  - Built-in assert statements
  - Parallel test execution
  - Code coverage integration

### Black (24.3.0)
- Uncompromising code formatter
- **Benefits**:
  - Eliminates formatting debates
  - Consistent style across projects
  - PEP 8 compliant
  - Integrates with most editors
- **Why Use It**: Saves time and mental energy by automating code formatting

### Ruff (0.3.0)
- Extremely fast Python linter
- **Advantages**:
  - 10-100x faster than traditional linters
  - Replaces multiple tools (Flake8, isort, etc.)
  - Automatic code fixes
  - Extensible rule set
- **Best For**: Large codebases needing quick feedback

## AI & Machine Learning

### Anthropic (0.18.1)
- Official client for Anthropic's AI models
- **Features**:
  - Access to Claude and other AI models
  - Streaming responses
  - Message threading
  - Error handling
- **Use Cases**: AI-powered applications, chatbots, content generation

### HuggingFace-Hub (0.27.1)
- Interface to HuggingFace's model ecosystem
- **Capabilities**:
  - Access to thousands of ML models
  - Model downloading and caching
  - Dataset management
  - Model card access
- **Best For**: ML model deployment and experimentation

## Database & Storage

### Supabase (2.3.4)
- Open source Firebase alternative
- **Features**:
  - PostgreSQL database
  - Authentication
  - Real-time subscriptions
  - Storage
  - Edge functions
- **Why Use It**: Full-featured backend as a service with PostgreSQL at its core

## Utilities & Helper Libraries

### Python-dotenv (1.0.0)
- Environment variable management
- **Why It's Important**:
  - Keeps sensitive data out of code
  - Different configs for different environments
  - Easy local development setup
- **Best Practice**: Use for managing configuration in different environments

### Rich (13.9.4)
- Terminal formatting and output library
- **Capabilities**:
  - Beautiful console output
  - Progress bars
  - Tables and panels
  - Syntax highlighting
  - Markdown rendering
- **Use Cases**: CLI applications, debugging, logging

Note: Version numbers are included for reference. Run `pip freeze` to get the most current versions in your environment.
