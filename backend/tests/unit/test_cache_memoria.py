from app.cache.memory import CacheMemoria


def test_item_vale_ate_ttl_e_expira_depois(relogio):
    cache = CacheMemoria(ttl_segundos=3600, relogio=relogio)
    cache.guardar(("4214805", "2024-01"), [])

    relogio.agora += 3599
    assert cache.obter(("4214805", "2024-01")) == []

    relogio.agora += 1
    assert cache.obter(("4214805", "2024-01")) is None


def test_estatisticas_contam_hits_misses_e_itens_validos(relogio):
    cache = CacheMemoria(ttl_segundos=3600, relogio=relogio)
    cache.obter(("4214805", "2024-01"))
    cache.guardar(("4214805", "2024-01"), [])
    cache.obter(("4214805", "2024-01"))
    cache.obter(("4214805", "2024-01"))
    relogio.agora += 1800
    cache.guardar(("4202404", "2024-01"), [])
    relogio.agora += 1800

    assert (cache.hits, cache.misses, cache.itens) == (2, 1, 1)
