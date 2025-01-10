from typing import Literal, Tuple, Any, Union

TableName = str
ColumnName = str
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
WhereFilter = Tuple[str, FilterOperator, Any]
ReturnType = Literal["minimal", "representation"]
InsertResult = Union[dict, list[dict]]
