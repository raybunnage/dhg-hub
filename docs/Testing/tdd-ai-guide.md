# AI-Assisted Test-Driven Development Guide

## Table of Contents
- [Overview](#overview)
- [Project Structure Analysis](#project-structure-analysis)
- [TDD Workflow with AI](#tdd-workflow-with-ai)
- [Prompting Strategies](#prompting-strategies)
- [Example Workflows](#example-workflows)
- [Best Practices](#best-practices)
- [Templates](#templates)

## Overview

This guide outlines how to effectively use AI assistants (like Claude) for test-driven development in your Python/React project with FastAPI and Supabase integration.

## Project Structure Analysis

Current test structure:
```
backend/tests/
├── core/                  # Core functionality tests
├── development/          # Development-specific tests
├── integration/         # Integration tests
├── services/           # Service-specific tests
├── unit/              # Unit tests
└── various test files at root level
```

Coverage metrics show room for improvement:
- Overall coverage: 23-25%
- Strong coverage in core components (supabase_client.py, types.py)
- Areas needing attention: API routes, CLI, services

## TDD Workflow with AI

### 1. Database Model Definition Phase

```sql
-- Example prompt for defining a new model:
"I need to create a new data model for [feature]. Here's the requirements:
- Fields needed: [list fields]
- Relationships: [describe relationships]
- Constraints: [list constraints]
Please provide:
1. Supabase table definition
2. SQLAlchemy model
3. Pydantic schemas for request/response"
```

### 2. Test Suite Generation Phase

For each new feature, follow this sequence:

1. **Unit Tests**
```python
"Generate a comprehensive unit test suite for [model/feature] that covers:
- CRUD operations
- Edge cases
- Validation
- Error handling
Use pytest fixtures and parameterized tests where appropriate."
```

2. **Integration Tests**
```python
"Create integration tests for [feature] that verify:
- API endpoint behavior
- Database interactions
- Service layer integration
Include setup/teardown with proper test data."
```

3. **Service Layer Tests**
```python
"Design test cases for the service layer of [feature] including:
- Business logic validation
- Complex operations
- Error handling scenarios
Use mocking where appropriate for external dependencies."
```

## Prompting Strategies

### Effective AI Prompts

1. **Context Setting**
```
"I'm working on [feature] in my FastAPI/Supabase project. Here's my current project structure:
[paste relevant directory tree]
[paste relevant existing code]

I need to create tests for..."
```

2. **Incremental Development**
```
"Based on the previous tests, let's expand coverage for [specific aspect].
Current coverage report shows gaps in:
[paste coverage report section]
Please generate additional tests focusing on..."
```

3. **Test Data Generation**
```
"Generate realistic test data for [feature] including:
- Valid cases
- Edge cases
- Invalid data
Use Pydantic's Field validations and provide factory functions."
```

### Using AI Tools Effectively

1. **Cursor AI Integration**
- Use split screen to keep test output visible
- Iterate on test cases in real-time
- Use AI suggestions for test improvements

2. **Claude Specifics**
- Provide full context in initial prompt
- Use code blocks for sharing current implementation
- Ask for explanations of generated tests

## Example Workflows

### 1. New Feature Development

```markdown
1. Initial Model Definition:
   "I'm creating a new feature for [description]. Generate:
   - Database schema
   - API models
   - Initial test structure"

2. Test Suite Creation:
   "Based on the models, generate:
   - Unit tests for model validation
   - Integration tests for API endpoints
   - Service layer tests"

3. Implementation Guidance:
   "With the tests in place, provide:
   - Implementation steps
   - Edge cases to consider
   - Error handling patterns"
```

### 2. Coverage Improvement

```markdown
1. Analysis:
   "Here's my current coverage report:
   [paste coverage]
   Identify areas needing attention."

2. Test Generation:
   "Generate additional tests for:
   - Uncovered code paths
   - Error scenarios
   - Edge cases"

3. Validation:
   "Review generated tests for:
   - Coverage improvement
   - Test quality
   - Implementation consistency"
```

## Best Practices

1. **Test Organization**
- Keep test files parallel to implementation
- Use clear naming conventions
- Group related tests logically

2. **Coverage Goals**
- Aim for 80%+ coverage in critical paths
- Focus on business logic coverage
- Include error handling paths

3. **AI Collaboration**
- Provide complete context
- Review generated tests carefully
- Iterate on test cases

## Templates

### 1. New Feature Test Suite Template

```python
"""
Generate a complete test suite for [feature] including:

1. Unit Tests
- Model validation
- Business logic
- Error cases

2. Integration Tests
- API endpoints
- Database operations
- Service integration

3. Test Data
- Fixtures
- Factory functions
- Mock data

Current project structure:
[paste structure]

Requirements:
[paste requirements]
"""
```

### 2. Coverage Improvement Template

```python
"""
Need to improve test coverage for [component].

Current coverage:
[paste coverage report]

Focus areas:
1. Untested code paths
2. Error scenarios
3. Edge cases

Existing tests:
[paste relevant tests]

Generate additional tests to improve coverage while maintaining test quality.
"""
```

### 3. Service Layer Test Template

```python
"""
Create service layer tests for [feature]:

1. Business Logic
- Core functionality
- Data transformations
- Business rules

2. Integration Points
- External services
- Database interactions
- API integrations

3. Error Handling
- Expected errors
- Edge cases
- Recovery scenarios

Current implementation:
[paste relevant code]
"""
```

## Recommended Tools

1. **Testing Tools**
- pytest
- pytest-cov
- pytest-asyncio
- pytest-mock

2. **Development Tools**
- Cursor AI
- Claude
- FastAPI TestClient
- SQLAlchemy Test Suite

3. **Coverage Tools**
- Coverage.py
- pytest-cov
- HTML coverage reports

## Implementation Example

Here's a complete example of implementing a new feature using TDD with AI assistance:

```markdown
1. Define the feature:
   "I need a user preference system that stores:
   - User settings
   - Theme preferences
   - Notification settings"

2. Generate test structure:
   "Create a complete test suite structure for user preferences"

3. Create test cases:
   "Generate comprehensive tests for:
   - Preference CRUD operations
   - Validation rules
   - API endpoints"

4. Implement with tests:
   "Guide the implementation to pass all tests"

5. Review and iterate:
   "Analyze coverage and suggest improvements"
```

This workflow ensures complete test coverage from the start and maintains code quality throughout the development process.


## Project-Specific Considerations

### FastAPI Route Testing
- Use `TestClient` for endpoint testing
- Test both synchronous and asynchronous routes
- Verify Supabase integration points
- Test authentication/authorization flows
- Validate response models match Pydantic schemas

### Supabase Testing Strategy
1. **Mock vs. Real Database**
   - Use test database for integration tests
   - Mock Supabase client for unit tests
   - Create isolated test data

2. **Authentication Testing**
   - Test JWT token validation
   - Verify role-based access
   - Test session management

3. **Data Consistency**
   - Verify triggers and RLS policies
   - Test data cascading
   - Validate foreign key constraints

### CLI Testing
- Test command-line interface functions
- Verify environment configuration handling
- Test database initialization commands
- Validate migration scripts

### Service Layer Specifics
- Test chat history management
- Verify embedding generation and storage
- Test vector search functionality
- Validate conversation context handling

### AI Integration Testing
1. **Mock AI Responses**


python
@pytest.fixture
def mock_ai_response():
return {
"content": "Test response",
"role": "assistant",
"metadata": {...}
}

  
2. **Test Conversation Flow**
- Verify context window management
- Test prompt construction
- Validate response parsing
- Test error recovery

### Common Test Fixtures

python
@pytest.fixture
async def test_db():
"""Provides isolated test database"""
# Setup test database
yield db
# Cleanup
@pytest.fixture
async def authenticated_client():
"""TestClient with authentication"""
client = TestClient(app)
# Add auth headers
return client
@pytest.fixture
def sample_conversation():
"""Creates test conversation data"""
return {
"conversation_id": "test-id",
"messages": [...]
}


### Coverage Priorities
1. **Critical Paths**
   - Authentication flows
   - Conversation management
   - Vector search operations
   - Data persistence

2. **Error Scenarios**
   - AI service unavailability
   - Database connection issues
   - Invalid authentication
   - Malformed requests

3. **Edge Cases**
   - Large conversation histories
   - Rate limiting scenarios
   - Concurrent access patterns

   These additions provide more specific guidance for your project's unique requirements, particularly around AI chat functionality, Supabase integration, and FastAPI implementation. They can be integrated into the existing document structure, either as new sections or merged into relevant existing sections.
Would you like me to suggest where specifically these sections should be inserted in the existing document?