import typing

from fastapi import FastAPI


class DependencyMocker:
    def __init__(
        self, app: FastAPI, overrides: typing.Mapping[typing.Callable, any]
    ) -> None:
        self.overrides = overrides
        self._app = app
        self._old_overrides = {}

    def __enter__(self):
        def get_dep(dep):
            return lambda: dep

        for dep, new_dep in self.overrides.items():
            if dep in self._app.dependency_overrides:
                # Save existing overrides
                self._old_overrides[dep] = self._app.dependency_overrides[dep]

            self._app.dependency_overrides[dep] = get_dep(new_dep)
        return self

    def __exit__(self, *args: typing.Any) -> None:
        for dep in self.overrides.keys():
            if dep in self._old_overrides:
                # Restore previous overrides
                self._app.dependency_overrides[dep] = self._old_overrides.pop(dep)
            else:
                # Just delete the entry
                del self._app.dependency_overrides[dep]
