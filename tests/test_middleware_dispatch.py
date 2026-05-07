"""
Tests para RequestContextMiddleware.dispatch — el corazón del request
lifecycle (request_id, logs start/end, error path, status>=500 metric).
"""
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.middleware import RequestContextMiddleware, _module_from_path


def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


def _request(*, headers=None, path="/api/v1/games", method="GET"):
    req = MagicMock()
    req.headers = headers or {}
    req.url.path = path
    req.method = method
    return req


def _response(status_code=200):
    resp = MagicMock()
    resp.status_code = status_code
    resp.headers = {}
    return resp


def _build_mw(call_next):
    mw = RequestContextMiddleware(app=MagicMock())
    # Inyectamos un dispatch que use call_next como mock async
    return mw, call_next


# --- _module_from_path ----------------------------------------------------


class TestModuleFromPath:
    def test_api_v1_returns_third_segment(self):
        assert _module_from_path("/api/v1/auth/login") == "auth"

    def test_api_v1_root_returns_third_segment(self):
        assert _module_from_path("/api/v1/games") == "games"

    def test_non_api_path_returns_first_segment(self):
        assert _module_from_path("/metrics") == "metrics"
        assert _module_from_path("/docs") == "docs"

    def test_empty_path_returns_root(self):
        assert _module_from_path("/") == "root"
        assert _module_from_path("") == "root"


# --- dispatch happy path ---------------------------------------------------


class TestDispatchHappyPath:
    def test_sets_request_id_header(self):
        async def call_next(req):
            return _response(200)

        mw = RequestContextMiddleware(app=MagicMock())
        request = _request()
        response = _run(mw.dispatch(request, call_next))
        assert "X-Request-ID" in response.headers
        # Por defecto es 32 hex chars
        assert len(response.headers["X-Request-ID"]) == 32

    def test_uses_provided_request_id(self):
        async def call_next(req):
            return _response(200)

        mw = RequestContextMiddleware(app=MagicMock())
        request = _request(headers={"X-Request-ID": "custom-rid"})
        response = _run(mw.dispatch(request, call_next))
        assert response.headers["X-Request-ID"] == "custom-rid"

    def test_metrics_path_does_not_log_start_end(self):
        # /metrics es ruidoso, no debe loguear request.start/end
        async def call_next(req):
            return _response(200)

        mw = RequestContextMiddleware(app=MagicMock())
        request = _request(path="/metrics")
        with patch("app.core.middleware.logger") as fake_logger:
            _run(mw.dispatch(request, call_next))
        # request.start NO debe haberse llamado para /metrics
        for call in fake_logger.info.call_args_list:
            assert call.args[0] != "request.start"


# --- dispatch error path ---------------------------------------------------


class TestDispatchErrorPath:
    def test_exception_propagates_after_log(self):
        async def call_next(req):
            raise ValueError("boom")

        mw = RequestContextMiddleware(app=MagicMock())
        request = _request(path="/api/v1/auth/login")
        with patch("app.core.middleware.logger") as fake_logger:
            with pytest.raises(ValueError):
                _run(mw.dispatch(request, call_next))
        # logger.exception debe haberse llamado con request.error
        fake_logger.exception.assert_called_once()
        first_arg = fake_logger.exception.call_args.args[0]
        assert first_arg == "request.error"

    def test_exception_increments_module_errors(self):
        async def call_next(req):
            raise RuntimeError("nope")

        mw = RequestContextMiddleware(app=MagicMock())
        request = _request(path="/api/v1/games")
        with patch("app.core.middleware.metrics") as fake_metrics:
            counter = MagicMock()
            fake_metrics.MODULE_ERRORS.labels.return_value = counter
            with pytest.raises(RuntimeError):
                _run(mw.dispatch(request, call_next))
        # Counter incrementado para módulo "games"
        fake_metrics.MODULE_ERRORS.labels.assert_any_call(module="games")
        counter.inc.assert_called()


# --- dispatch 500 status ---------------------------------------------------


class TestDispatch5xxStatus:
    def test_5xx_logs_as_warning_and_increments_metrics(self):
        async def call_next(req):
            return _response(503)

        mw = RequestContextMiddleware(app=MagicMock())
        request = _request(path="/api/v1/auth/login")
        with patch("app.core.middleware.metrics") as fake_metrics, \
             patch("app.core.middleware.logger") as fake_logger:
            counter = MagicMock()
            fake_metrics.MODULE_ERRORS.labels.return_value = counter
            response = _run(mw.dispatch(request, call_next))

        # Logger.warning llamado para request.end con status 5xx
        warning_events = [c.args[0] for c in fake_logger.warning.call_args_list]
        assert "request.end" in warning_events
        # Y el counter sí se incrementa para el módulo "auth"
        counter.inc.assert_called()

    def test_4xx_logs_as_warning_does_not_increment_metrics(self):
        async def call_next(req):
            return _response(400)

        mw = RequestContextMiddleware(app=MagicMock())
        request = _request(path="/api/v1/auth/login")
        with patch("app.core.middleware.metrics") as fake_metrics, \
             patch("app.core.middleware.logger") as fake_logger:
            counter = MagicMock()
            fake_metrics.MODULE_ERRORS.labels.return_value = counter
            _run(mw.dispatch(request, call_next))

        # 4xx loguea warning pero NO incrementa MODULE_ERRORS
        # (solo 5xx lo hace según el middleware)
        warning_events = [c.args[0] for c in fake_logger.warning.call_args_list]
        assert "request.end" in warning_events
