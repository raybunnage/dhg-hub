import pytest
from unittest.mock import Mock, AsyncMock
from dhg.db.uni_document_types import UniDocumentTypes


class TestUniDocumentTypes:
    @pytest.fixture
    def doc_types(self):
        """Create UniDocumentTypes instance with mocked client."""
        mock_client = Mock()
        return UniDocumentTypes(supabase_client=mock_client)

    @pytest.mark.asyncio
    async def test_get_document_type(self, doc_types):
        """Test getting a single document type."""
        # Setup mock response
        mock_response = Mock()
        mock_response.data = [{"id": "123", "name": "Test Type"}]

        # Setup mock chain
        mock_execute = AsyncMock(return_value=mock_response)
        mock_eq = Mock()
        mock_eq.execute = mock_execute

        mock_select = Mock()
        mock_select.eq = Mock(return_value=mock_eq)

        mock_from = Mock()
        mock_from.select = Mock(return_value=mock_select)

        doc_types.client.from_ = Mock(return_value=mock_from)

        # Execute test
        result = await doc_types.get_document_type("123")

        # Assert results
        assert result == {"id": "123", "name": "Test Type"}
        doc_types.client.from_.assert_called_once_with("uni_document_types")
