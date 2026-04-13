import pytest

from frontend.pyqt.app.config.urls import API_PREFIX, BASE_URL, Endpoint, build_url


def test_build_url_static_endpoint():
    url = build_url(Endpoint.USERS_LOGIN)
    assert url == f"{BASE_URL}{API_PREFIX}/users/login"


def test_build_url_dynamic_endpoint_with_path_params():
    url = build_url(
        Endpoint.PIECE_BY_ID,
        path_params={"archive_id": 10, "piece_id": 42},
    )
    assert url == f"{BASE_URL}{API_PREFIX}/archives/10/pieces/42"


def test_build_url_missing_path_param_raises_value_error():
    with pytest.raises(
        ValueError,
        match=r"Missing path param 'piece_id' for endpoint '/archives/\{archive_id\}/pieces/\{piece_id\}'",
    ):
        build_url(Endpoint.PIECE_BY_ID, path_params={"archive_id": 10})


def test_build_url_missing_path_params_when_none_raises_value_error():
    with pytest.raises(
        ValueError,
        match=r"Missing path param 'archive_id' for endpoint '/archives/\{archive_id\}'",
    ):
        build_url(Endpoint.ARCHIVE_BY_ID)


def test_build_url_ignores_extra_path_params():
    url = build_url(
        Endpoint.ARCHIVE_BY_ID,
        path_params={"archive_id": 7, "unused": "x"},
    )
    assert url == f"{BASE_URL}{API_PREFIX}/archives/7"


def test_build_url_with_query_params():
    url = build_url(
        Endpoint.USERS_REGISTER,
        query_params={"next": "dashboard", "page": 2},
    )
    assert url == f"{BASE_URL}{API_PREFIX}/users/register?next=dashboard&page=2"


def test_build_url_filters_out_none_query_params():
    url = build_url(
        Endpoint.PREVIEW,
        query_params={"archive_id": 1, "piece_id": None, "page_number": 0},
    )
    assert url == f"{BASE_URL}{API_PREFIX}/preview/?archive_id=1&page_number=0"
    assert "piece_id=" not in url


def test_build_url_supports_sequence_query_params_with_doseq():
    url = build_url(
        Endpoint.UPLOADS_STAGING,
        query_params={"file": ["a.pdf", "b.pdf"], "overwrite": True},
    )
    assert (
        url
        == f"{BASE_URL}{API_PREFIX}/uploads/staging?file=a.pdf&file=b.pdf&overwrite=True"
    )


def test_build_url_empty_query_params_do_not_append_question_mark():
    url = build_url(Endpoint.PIECE_PRESETS, query_params={})
    assert url == f"{BASE_URL}{API_PREFIX}/presets/pieces"
    assert "?" not in url


def test_build_url_with_path_and_query_params_together():
    url = build_url(
        Endpoint.PIECE_FILES,
        path_params={"archive_id": 3, "piece_id": 9},
        query_params={"instrument": "clarinete", "take": 1},
    )
    assert (
        url
        == f"{BASE_URL}{API_PREFIX}/archives/3/pieces/9/files?instrument=clarinete&take=1"
    )


def test_build_url_preserves_trailing_slash_endpoint():
    url = build_url(Endpoint.PREVIEW)
    assert url == f"{BASE_URL}{API_PREFIX}/preview/"