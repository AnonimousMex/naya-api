"""
Lightweight helpers to enrich Sentry with breadcrumbs and business events
without repeating the same boilerplate in every controller.

Usage:
    from app.core import sentry_events as sentry

    # Context that only matters if an error fires later in the request:
    sentry.breadcrumb("auth", "login.attempt", email_domain="naya.local")

    # Business event that shows up as an info-level Issue in Sentry:
    sentry.track(
        "user.registered",
        level="info",
        category="onboarding",
        tags={"role": "PATIENT"},
        extras={"user_id": str(user.id)},
    )

Design:
- These helpers never break the request if Sentry is disabled (no-op).
- No PII leaks: full emails are not stored, only the domain or the user_id.
- `tags` are for filtering/grouping in Sentry; `extras` are extra context
  that shows on the Issue but does not affect grouping.
"""
from __future__ import annotations

from typing import Any, Mapping, Optional

import sentry_sdk


def breadcrumb(
    category: str,
    message: str,
    *,
    level: str = "info",
    data: Optional[Mapping[str, Any]] = None,
) -> None:
    """
    Drop a breadcrumb on the current Sentry scope.
    It only surfaces if a Sentry event (error or warning) is reported later
    in the same request — useful for reconstructing what happened before
    the failure.
    """
    try:
        sentry_sdk.add_breadcrumb(
            category=category,
            message=message,
            level=level,
            data=dict(data) if data else None,
        )
    except Exception:  # noqa: BLE001 — observability must never break the app
        pass


def track(
    message: str,
    *,
    level: str = "info",
    category: Optional[str] = None,
    tags: Optional[Mapping[str, str]] = None,
    extras: Optional[Mapping[str, Any]] = None,
) -> None:
    """
    Capture a business event on Sentry as a standalone Issue at the given
    level. Unlike `breadcrumb`, this ALWAYS creates an event — even when
    no error happened.

    Use sparingly — events count against the Sentry quota. Reserve it for
    rare and important milestones (registration, patient-therapist
    connection, etc).
    """
    try:
        with sentry_sdk.new_scope() as scope:
            if category:
                scope.set_tag("category", category)
            for k, v in (tags or {}).items():
                scope.set_tag(k, v)
            for k, v in (extras or {}).items():
                scope.set_extra(k, v)
            sentry_sdk.capture_message(message, level=level)
    except Exception:  # noqa: BLE001
        pass


def set_user(
    *,
    user_id: Optional[str] = None,
    role: Optional[str] = None,
    email_domain: Optional[str] = None,
) -> None:
    """
    Set the active user for Sentry. Call early in each authenticated
    request so any event raised within the scope carries this user.
    The full email (PII) is never stored — only the domain when needed.
    """
    try:
        payload: dict = {}
        if user_id:
            payload["id"] = user_id
        if role:
            payload["user_type"] = role
        if email_domain:
            payload["email_domain"] = email_domain
        if payload:
            sentry_sdk.set_user(payload)
    except Exception:  # noqa: BLE001
        pass
