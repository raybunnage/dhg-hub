# Supabase Service Testing Guide

## AI Conversation Best Practices
Let me explain the common best practices for organizing tests in a full-stack project:

### Recommended Test Structure
The general best practice is to keep tests close to the code they're testing. For a typical full-stack project, this usually means:

### Types of Tests & Their Location

**Backend Tests** (`backend/tests/`)
- Unit tests for backend services
- API endpoint tests
- Database tests
- Backend integration tests

**Frontend Tests** (`frontend/tests/` or within component directories)
- Component unit tests
- Hook tests
- State management tests
- Frontend integration tests

**Root-level Tests** (`/tests/`)
- End-to-end (E2E) tests
- Full system integration tests
- Cross-component tests
- Import/dependency tests
- Build/deployment tests

### Recommendations
1. Move the `test_imports.py` to `backend/tests/` if it's specifically testing backend imports. Keep it in the root `tests/` folder only if it's testing project-wide imports or cross-component functionality.

2. Consider using testing frameworks that support this structure:
   - Jest for frontend (can be configured with `jest.config.js`)
   - Pytest for backend (can use `conftest.py` in different directories)
   - Cypress or Playwright for E2E tests (typically in root `tests/` or separate `e2e/` directory)

### Benefits of This Structure
- **Locality**: Tests are close to the code they're testing
- **Separation of Concerns**: Clear distinction between different types of tests
- **Scalability**: Easy to add new tests without cluttering
- **CI/CD friendly**: Easy to run specific test suites
- **Maintainability**: Clear organization makes it easier for team members to find and update tests

### Project Structure Example
```
your-project/
├── backend/
│   ├── src/
│   │   └── ...
│   └── tests/
│       └── ... (backend specific tests)
├── frontend/
│   ├── src/
│   │   └── ...
│   └── tests/
│       └── ... (frontend specific tests)
└── tests/
    └── ... (integration/e2e tests)
```

## Testing Framework Overview
This guide explains the testing techniques used in our Supabase service implementation, covering unit tests, integration tests, and advanced testing patterns.

### Testing Framework: pytest
We use pytest as our primary testing framework due to its powerful features:

- Fixture system for test setup and dependency injection
- Built-in async/await support with `@pytest.mark.asyncio`
- Rich assertion capabilities
- Plugin ecosystem

### Core Testing Concepts

#### 1. Fixtures
Fixtures are reusable setup functions that provide test data or objects:

```python
@pytest.fixture
def auth_mixin():
    mixin = AuthMixin()
    mixin.supabase = Mock()
    mixin.supabase.auth = AsyncMock()
    mixin.logger = Mock()
    return mixin
```

Key points:
- Fixtures run before each test that requests them
- They provide clean, isolated test environments
- Can be shared across multiple test files using `conftest.py`
- Can be scoped to function, class, module, or session

#### 2. Mocking
We use Python's `unittest.mock` library to create test doubles:

**Mock Types:**
- `Mock()`: General-purpose mock object
- `AsyncMock()`: For mocking async functions
- `patch()`: For temporarily replacing objects

Example:
```python
@patch('path.to.module.ClassName')
def test_something(mock_class):
    mock_class.return_value.some_method.return_value = 'expected'
    result = some_function()
    assert result == 'expected'
```

#### 3. Async Testing
For testing async functions:

```python
@pytest.mark.asyncio
async def test_async_function(auth_mixin):
    result = await auth_mixin.login('email', 'password')
    assert result is True
```

Key points:
- Use `@pytest.mark.asyncio` decorator
- Always await async functions
- Use `AsyncMock()` for mocking async methods

#### 4. Test Organization

**File Structure**
```
tests/
├── conftest.py           # Shared fixtures
├── services/
│   └── supabase/
│       ├── mixins/
│       │   ├── test_auth_mixin.py
│       │   ├── test_database_mixin.py
│       │   └── test_utils_mixin.py
│       └── test_integration.py
```

**Naming Conventions**
- Test files: `test_*.py`
- Test classes: `Test*`
- Test methods: `test_*`
- Use descriptive names indicating scenario being tested

#### 5. Error Testing
Test both success and failure scenarios:

```python
def test_login_missing_credentials(auth_mixin):
    with pytest.raises(SupabaseAuthenticationError) as exc_info:
        await auth_mixin.login("", "")
    assert "required" in str(exc_info.value)
```

Best practices:
- Test both success and failure paths
- Verify error messages and types
- Test edge cases and boundary conditions

#### 6. Property-Based Testing
Using hypothesis for generating test cases:

```python
from hypothesis import given, strategies as st

@given(st.lists(st.dictionaries(
    keys=st.text(),
    values=st.one_of(st.text(), st.integers())
)))
def test_serialization(data):
    result = serialize_data(data)
    assert isinstance(result, list)
```

#### 7. Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/services/supabase/mixins/test_auth_mixin.py

# Run with coverage report
pytest --cov=src

# Run async tests only
pytest -m asyncio
```

#### 8. Testing Tips

1. **Isolation**: Each test should be independent and not rely on the state from other tests
2. **Readability**: Tests serve as documentation - make them clear and descriptive
3. **Maintenance**: Keep tests simple and focused on a single behavior
4. **Coverage**: 
   - Aim for high coverage but focus on critical paths
   - Don't chase 100% coverage at the expense of meaningful tests
5. **Performance**: 
   - Group slow tests and run separately when needed
   - Use appropriate fixture scopes to minimize setup time
6. **Mocking**:
   - Mock external dependencies
   - Be careful not to over-mock as it can lead to brittle tests