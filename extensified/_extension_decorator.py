import inspect
from typing import Any, Callable, TypeVar


_ExtendedClass = TypeVar("_ExtendedClass", bound=type)
"""Type of the class that is being extended (the one that is passed to `extension_on` as an argument)."""


def extension_on(extension_target: _ExtendedClass) -> Callable[[_ExtendedClass], None]:
    """
    Constructs a decorator function, which, when applied to a class, adds its methods to `extension_target`.

    Args:
        extension_target[_ExtendedClass]: The class to extend with methods defined in the decorated class (extension
        class). Must be a user-defined class (built-in types are not supported).

    Returns:
        Callable[[_ExtendedClass], None]: A decorator function that processes the extension class.

    Raises:
        TypeError: If trying to extend a built-in type.

    Example:
        >>> from extensified import extension_on
        >>> class User:
        ...     def __init__(self, name: str):
        ...         self.name = name
        ...
        >>> @extension_on(User)
        ... class UserFormattingExtension:
        ...     def as_json(self) -> dict[str, str]:
        ...         return {"name": self.name}
        ...
        ...     @property
        ...     def display_name(self) -> str:
        ...         return self.name.upper()
        ...
        >>> user = User("John")
        >>> user.as_json()
        {'name': 'John'}
        >>> user.display_name
        'JOHN'

    Notes:
        - `super()` can't be used in an extension class for now.
        - The `self` parameter in extension methods refers to instances of the target class.
        - Multiple extensions can be applied to the same target class.
        - Extension methods have access to the target instance's attributes.
    """

    def decorator(extension_class: _ExtendedClass) -> None:
        for method_name in _non_inherited_methods_names(extension_class):
            method = getattr(extension_class, method_name)
            if _is_classmethod(method):
                bound_method: classmethod[_ExtendedClass, Any, Any] = classmethod(method.__func__)
                setattr(extension_target, method_name, bound_method)
                return
            if _is_staticmethod(extension_class, method_name):
                setattr(extension_target, method_name, staticmethod(method))
                return
            setattr(extension_target, method_name, method)

    return decorator


def _non_inherited_methods_names(cls: type) -> set[str]:
    all_method_names = {
        attr
        for attr in dir(cls)
        if callable(getattr(cls, attr)) or _is_descriptor(getattr(cls, attr))
    }
    parent_classes_method_names = {
        attr
        for base in cls.__bases__
        for attr in dir(base)
        if callable(getattr(base, attr)) or _is_descriptor(getattr(base, attr))
    }
    return all_method_names - parent_classes_method_names


def _is_descriptor(obj: Any) -> bool:
    return any(hasattr(obj, attr) for attr in {"__get__", "__set__", "__delete__"})


def _is_classmethod(obj: Any) -> bool:
    return hasattr(obj, "__self__") and isinstance(obj.__self__, type)


def _is_staticmethod(cls: _ExtendedClass, method_name: str) -> bool:
    return isinstance(inspect.getattr_static(cls, method_name), staticmethod)
