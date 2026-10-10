import pytest


class RelogioFalso:
    def __init__(self):
        self.agora = 1000.0
        self.esperas: list[float] = []

    def __call__(self) -> float:
        return self.agora

    async def dormir(self, segundos: float) -> None:
        self.esperas.append(segundos)
        self.agora += segundos


@pytest.fixture
def relogio() -> RelogioFalso:
    return RelogioFalso()


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"
