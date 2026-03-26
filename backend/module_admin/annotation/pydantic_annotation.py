import inspect
from typing import Type, TypeVar

from fastapi import Query
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


def as_query(cls: Type[T]) -> Type[T]:
    """
    Decorator that adds an `as_query` class method to a Pydantic model.
    The `as_query` method can be used with `Depends` to parse query parameters.
    """

    # We need to construct the signature dynamically
    parameters = []
    # model_fields contains all fields including inherited ones
    for name, field in cls.model_fields.items():
        # Handle default values
        default = Query(default=... if field.is_required() else field.default)
        if field.default_factory:
            default = Query(default_factory=field.default_factory)

        # Add parameter with correct type annotation
        # Use field.alias if present, otherwise name
        # In Pydantic v2, alias might be None if not explicitly set,
        # even if alias_generator is present?
        # Actually field.alias usually holds the alias if set.
        # If alias_generator is used, we might need to check serialization_alias or validation_alias.
        # But for simplicity, let's try field.alias or name.
        param_name = field.alias if field.alias else name

        parameters.append(
            inspect.Parameter(
                name=param_name,
                kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                default=default,
                annotation=field.annotation,
            )
        )

    async def as_query_dependency(**kwargs):
        # kwargs keys will be the alias names (e.g. userName)
        # Pydantic model init expects field names (e.g. user_name) OR aliases if populated_by_name is True?
        # With alias_generator, we typically initialize with aliases if ConfigDict(populate_by_name=True) is set?
        # Or usually Pydantic accepts aliases in __init__.
        return cls(**kwargs)

    # Replace signature of the dependency function
    as_query_dependency.__signature__ = inspect.Signature(parameters)

    # Attach to class
    cls.as_query = as_query_dependency
    return cls
