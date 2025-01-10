# Frontend and Backend Architecture Guide

## Overview

This project uses a modern split architecture with three main components:
- A Frontend server (React-based)
- A Backend server (Python-based)
- FastAPI as the middleware/API layer

## Architecture Components

### Frontend Server
- Located in `src/frontend/`
- Built with React
- Runs on port 3000 by default
- Handles all user interface and client-side logic
- Communicates with backend via HTTP requests to FastAPI endpoints

### Backend Server
- Located in `src/backend/`
- Pure Python implementation
- Contains core business logic
- No direct HTTP exposure
- Communicates only with FastAPI layer

### FastAPI Layer
- Located in `src/api/`
- Acts as the glue between frontend and backend
- Handles all HTTP routing and request/response formatting
- Provides OpenAPI documentation automatically
- Runs on port 8000 by default

## Directory Structure

### src/frontend/
**Criteria for placing files here:**
- React components
- Frontend utilities and helpers
- CSS/SCSS styles
- Frontend assets (images, fonts, etc.)
- Client-side state management
- Frontend tests

### src/backend/
**Criteria for placing files here:**
- Core business logic
- Data models and schemas
- Database interactions
- Service layer implementations
- Backend utilities
- Pure Python implementations with no HTTP dependencies

### src/api/
**Criteria for placing files here:**
- FastAPI route definitions
- Request/response models
- API middleware
- Authentication/authorization logic
- API-specific utilities
- OpenAPI schema customizations

### src/tests/
**Criteria for placing files here:**
- Integration tests
- End-to-end tests
- Test fixtures and utilities
- API tests
- Test configuration

## Developer Workflow

### Setting Up Development Environment

1. Start the backend server:
```

## Best Practices

1. **Separation of Concerns**
   - Keep business logic in backend
   - Keep UI logic in frontend
   - Use API layer for communication only

2. **Testing**
   - Write tests before implementing features
   - Maintain high test coverage
   - Use appropriate test types for each layer

3. **Documentation**
   - Keep API documentation up to date
   - Document complex business logic
   - Include setup instructions in README

4. **Code Organization**
   - Follow directory structure guidelines
   - Use consistent naming conventions
   - Keep related files together

## Common Pitfalls

1. Mixing business logic with API routes
2. Tight coupling between frontend and backend
3. Insufficient error handling
4. Inconsistent testing approaches
5. Poor documentation maintenance

## Conclusion

This architecture provides a clean separation of concerns while maintaining flexibility and scalability. By following these guidelines, developers can efficiently contribute to the project while maintaining code quality and testability.

Remember to:
- Keep the layers separate
- Write comprehensive tests
- Document your changes
- Follow the established patterns


// ... existing content ...

## FastAPI and Supabase Integration

### Overview
FastAPI serves as the API layer that handles asynchronous communication with Supabase. This setup allows for:
- Efficient database operations using Supabase's async client
- Proper error handling and status codes
- Type-safe database interactions
- Controlled access to Supabase resources

### Supabase Client Setup

The Supabase client should be initialized as a dependency in FastAPI:

```

### Best Practices for Supabase Integration

1. **Error Handling**
   - Always wrap Supabase calls in try/except blocks
   - Map Supabase errors to appropriate HTTP status codes
   - Return meaningful error messages
   ```python
   try:
       result = await supabase.from_("table").select("*")
   except PostgrestError as e:
       raise HTTPException(status_code=500, detail=str(e))
   ```

2. **Query Optimization**
   - Use select() with specific columns instead of "*"
   - Implement pagination for large datasets
   - Use appropriate filters on the Supabase query
   ```python
   # Good practice
   await supabase.from_("users") \
       .select("id, name, email") \
       .range(0, 9)
   ```

3. **Data Validation**
   - Use Pydantic models for request/response validation
   - Validate data before sending to Supabase
   ```python
   class UserCreate(BaseModel):
       name: str
       email: EmailStr
       
   @router.post("/users")
   async def create_user(
       user: UserCreate,
       supabase: Client = Depends(get_supabase_client)
   ):
       data = user.dict()
       result = await supabase.from_("users").insert(data)
   ```

4. **Authentication**
   - Use Supabase auth in conjunction with FastAPI security
   - Implement proper role-based access control
   ```python
   @router.get("/protected")
   async def protected_route(
       supabase: Client = Depends(get_supabase_client),
       user: User = Depends(get_current_user)
   ):
       # Route logic here
   ```

### Common Supabase Operations

1. **Querying Data**
```python
# Basic select
data = await supabase.from_("table").select("*")

# Filtered select
data = await supabase.from_("table") \
    .select("column1, column2") \
    .eq("column1", value) \
    .order("column2", ascending=False)

# Joins
data = await supabase.from_("table1") \
    .select("*, table2(*)") \
    .eq("table2.foreign_key", "value")
```

2. **Modifying Data**
```python
# Insert
data = await supabase.from_("table").insert({"column": "value"})

# Update
data = await supabase.from_("table") \
    .update({"column": "new_value"}) \
    .eq("id", item_id)

# Delete
data = await supabase.from_("table").delete().eq("id", item_id)
```

3. **Real-time Subscriptions**
```python
async def handle_realtime():
    channel = supabase \
        .channel('table_changes') \
        .on('postgres_changes',
            event='*',
            schema='public',
            table='your_table',
            callback=lambda event: print(event)
        ) \
        .subscribe()
```

### Testing Supabase Integration

1. **Mocking Supabase Client**
```python
class MockSupabaseClient:
    async def from_(self, table):
        return self

    async def select(self, query):
        return {"data": [{"id": 1, "name": "test"}]}

@pytest.fixture
def mock_supabase():
    return MockSupabaseClient()

def test_get_items(mock_supabase):
    response = await client.get("/items")
    assert response.status_code == 200
```

2. **Integration Tests**
- Use a test database in Supabase
- Reset data between tests
- Test full request/response cycles

Remember to handle connection pooling and cleanup appropriately in your FastAPI application when working with Supabase.


// ... rest of existing content ...