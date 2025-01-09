from typing import Dict, Any, Literal, NewType, Union, List
from dataclasses import dataclass

# Supabase-specific types
TableName = NewType("TableName", str)
ColumnName = NewType("ColumnName", str)
FilterOperator = Literal[
    "eq",
    "neq",
    "gt",
    "gte",
    "lt",
    "lte",
    "like",
    "ilike",
    "is",
    "in",
    "contains",
    "contained_by",
    "text_search",
]


# Simplified return types
@dataclass
class InsertResult:
    """Result of an insert operation."""

    count: int
    data: List[Dict[str, Any]]  # More generic than ResponseRecord
