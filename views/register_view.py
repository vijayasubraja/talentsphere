"""Registration view router for TalentSphere.

Routes registration requests to the unified dual-panel authentication page
with the Create Account tab active, eliminating duplicate screens.
"""

from __future__ import annotations
from views.login_view import render_login_page


def render_registration_page() -> None:
    """Renders the unified authentication page with the Create Account tab selected."""
    render_login_page(initial_tab="register")
