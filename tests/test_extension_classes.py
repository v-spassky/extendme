from typing_extensions import Self

import pytest

from extensified import extension_on


@pytest.fixture
def user_class() -> type:
    class User:
        def __init__(self, name: str, age: int) -> None:
            self.name = name
            self.age = age

        def years_until_death(self) -> int:
            return 100 - self.age

    return User


@pytest.fixture(params=[bool, int, float, str, bytes, list, tuple, set, dict])
def builtin_class(request: pytest.FixtureRequest) -> type:
    return request.param


def test_extension_methods(user_class: type) -> None:
    @extension_on(user_class)
    class _UserMethodsExtension:
        def make_older(self, years: int) -> None:
            self.age += years  # type: ignore[attr-defined]

    user = user_class("Vasi", 25)
    user.make_older(years=1)

    assert user.age == 26


def test_extension_property_getter(user_class: type) -> None:
    @extension_on(user_class)
    class _UserPropertiesExtension:
        @property
        def display(self) -> str:
            return f"{self.name}, {self.age}"  # type: ignore[attr-defined]

        @property
        def is_adult(self) -> str:
            return self.age >= 18  # type: ignore[attr-defined]

    user = user_class("Vasi", 25)

    assert user.display == "Vasi, 25"
    assert user.is_adult is True


def test_extension_property_setter(user_class: type) -> None:
    @extension_on(user_class)
    class _UserPropertiesExtension:
        @property
        def years_until_graduation(self) -> int:
            return max(0, 22 - self.age)

        @years_until_graduation.setter
        def years_until_graduation(self, years: int) -> None:
            self.age = 22 - years

    user = user_class("Vasi", 18)

    assert user.age == 18
    assert user.years_until_graduation == 4

    user.years_until_graduation = 2

    assert user.age == 20
    assert user.years_until_graduation == 2


def test_extension_class_methods(user_class: type) -> None:
    @extension_on(user_class)
    class _UserClassmethodsExtension:
        @classmethod
        def create_adult(cls, name: str) -> Self:
            return cls(name, 18)  # type: ignore[call-arg]

    user = user_class.create_adult("Vasi")  # type: ignore[attr-defined]

    assert isinstance(user, user_class)
    assert user.name == "Vasi"  # type: ignore[attr-defined]
    assert user.age == 18  # type: ignore[attr-defined]


def test_extension_static_methods(user_class: type) -> None:
    @extension_on(user_class)
    class _UserStaticmethodsExtension:
        @staticmethod
        def validate_age(age: int) -> bool:
            return 0 <= age <= 120

    user = user_class("Vasi", 18)

    assert user.validate_age(25) is True
    assert user.validate_age(-5) is False
    assert user.validate_age(150) is False


def test_extension_method_overriding_original(user_class: type) -> None:
    @extension_on(user_class)
    class _UserStaticmethodsExtension:
        def years_until_death(self) -> int:
            return 200 - self.age  # type: ignore[attr-defined]

    user = user_class("Vasi", 18)

    assert user.years_until_death() == 200 - user.age


def test_expect_extending_builtins_to_fail(builtin_class: type) -> None:
    with pytest.raises(TypeError):

        @extension_on(builtin_class)
        class _SomeExtension:
            def dummy_method(self) -> str:
                return "Cannot add methods on built-in types 🥺"
