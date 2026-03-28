from server.core.crypto.context_cache import (
    clear_ckks_context_cache,
    get_cached_ckks_context,
)


def test_get_cached_ckks_context_reuses_same_object():
    clear_ckks_context_cache()

    context1 = get_cached_ckks_context(
        "CKKS",
        16384,
        (60, 30, 30, 60),
        1073741824.0,
    )
    context2 = get_cached_ckks_context(
        "CKKS",
        16384,
        (60, 30, 30, 60),
        1073741824.0,
    )

    assert context1 is context2