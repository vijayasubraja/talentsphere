"""Reusable UI card components for TalentSphere.

Generates HTML components adhering to the TalentSphere dark theme design system,
including metrics cards, radial gauges, progress indicators, status badges, and section headers.
All HTML is rendered via st.html or textwrap.dedent to prevent raw code block leakage.
"""

from __future__ import annotations
import textwrap
from typing import Optional
import streamlit as st


def render_html(html_str: str) -> None:
    """Renders HTML directly into the DOM using st.html with dedent to prevent markdown code block parsing."""
    cleaned = textwrap.dedent(html_str).strip()
    if hasattr(st, "html"):
        st.html(cleaned)
    else:
        st.markdown(cleaned, unsafe_allow_html=True)


def render_metric_card(
    title: str,
    value: str,
    subtitle: Optional[str] = None,
    icon: str = "📊",
    badge_text: Optional[str] = None,
) -> None:
    """Renders an elevated dark-mode metric card with optional neon cyan pill badge."""
    badge_html = (
        f'<span style="background: #00D2FF; color: #0B0E17; font-weight: 800; font-size: 0.72rem; padding: 0.2rem 0.65rem; border-radius: 9999px; box-shadow: 0 0 10px rgba(0, 210, 255, 0.45);">{badge_text}</span>'
        if badge_text
        else ""
    )
    sub_html = (
        f'<div style="font-size: 0.82rem; color: #CBD5E1; margin-top: 0.45rem;">{subtitle}</div>'
        if subtitle
        else ""
    )
    html = f"""<div style="background: #1B2032; border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 16px; padding: 1.25rem 1.4rem; box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.07); height: 100%; display: flex; flex-direction: column; justify-content: space-between;">
<div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.45rem;">
<div style="display: flex; align-items: center; gap: 0.5rem;">
<span style="font-size: 1.25rem;">{icon}</span>
<span style="font-size: 0.84rem; font-weight: 700; color: #CBD5E1; text-transform: uppercase; letter-spacing: 0.06em;">{title}</span>
</div>
{badge_html}
</div>
<div style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 2.1rem; font-weight: 800; color: #FFFFFF; letter-spacing: -0.025em; line-height: 1.15;">
{value}
</div>
{sub_html}
</div>"""
    render_html(html)


def render_radial_gauge(
    value: int | float,
    title: str,
    subtitle: str = "",
    color_scheme: str = "pink",
) -> None:
    """Renders a semi-circle radial gauge matching the reference design (51% pink / 28% purple)."""
    val = max(0, min(100, int(value)))
    color_start = "#FF2A75" if color_scheme == "pink" else "#8A2BE2"
    color_end = "#FF5252" if color_scheme == "pink" else "#A855F7"
    glow_color = "rgba(255, 42, 117, 0.5)" if color_scheme == "pink" else "rgba(168, 85, 247, 0.5)"
    grad_id = f"radial_grad_{color_scheme}_{val}"
    # Arc circumference for R=55: ~172
    arc_offset = 172 - (val / 100) * 172

    html = f"""<div style="background: #161A29; border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 16px; padding: 1.15rem 0.9rem; text-align: center; box-shadow: 0 8px 24px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.06); height: 100%;">
<div style="position: relative; width: 140px; height: 85px; margin: 0 auto;">
<svg viewBox="0 0 140 85" width="140" height="85" style="overflow: visible;">
<defs>
<linearGradient id="{grad_id}" x1="0%" y1="0%" x2="100%" y2="0%">
<stop offset="0%" stop-color="{color_start}" />
<stop offset="100%" stop-color="{color_end}" />
</linearGradient>
</defs>
<path d="M 15 75 A 55 55 0 0 1 125 75" fill="none" stroke="#121624" stroke-width="12" stroke-linecap="round" />
<path d="M 15 75 A 55 55 0 0 1 125 75" fill="none" stroke="url(#{grad_id})" stroke-width="12" stroke-linecap="round" stroke-dasharray="172" stroke-dashoffset="{arc_offset}" style="filter: drop-shadow(0 0 6px {glow_color});" />
</svg>
<div style="position: absolute; bottom: 0; left: 0; right: 0; font-family: 'Plus Jakarta Sans', sans-serif; font-size: 1.6rem; font-weight: 800; color: #FFFFFF;">
{val}%
</div>
</div>
<div style="font-size: 0.86rem; font-weight: 700; color: #FFFFFF; margin-top: 0.4rem;">{title}</div>
<div style="font-size: 0.76rem; color: #CBD5E1; margin-top: 0.15rem; line-height: 1.35;">{subtitle}</div>
</div>"""
    render_html(html)


def render_speedometer_gauge(value: str = "304,56", label: str = "Learning Hours") -> None:
    """Renders the circular speedometer gauge matching the lower-left widget in the reference design."""
    html = f"""<div style="background: #161A29; border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 16px; padding: 1.15rem 0.9rem; text-align: center; box-shadow: 0 8px 24px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.06); height: 100%;">
<div style="position: relative; width: 140px; height: 90px; margin: 0 auto;">
<svg viewBox="0 0 140 90" width="140" height="90" style="overflow: visible;">
<defs>
<linearGradient id="speedo_grad_main" x1="0%" y1="0%" x2="100%" y2="0%">
<stop offset="0%" stop-color="#FF2A75" />
<stop offset="100%" stop-color="#FF5252" />
</linearGradient>
</defs>
<path d="M 20 80 A 50 50 0 1 1 120 80" fill="none" stroke="#121624" stroke-width="8" stroke-linecap="round" />
<path d="M 20 80 A 50 50 0 1 1 105 32" fill="none" stroke="url(#speedo_grad_main)" stroke-width="8" stroke-linecap="round" style="filter: drop-shadow(0 0 6px rgba(255,42,117,0.5));" />
<circle cx="70" cy="58" r="4" fill="#FF2A75" />
<line x1="70" y1="58" x2="94" y2="34" stroke="#FF2A75" stroke-width="2.5" stroke-linecap="round" />
</svg>
<div style="position: absolute; bottom: 2px; left: 0; right: 0; font-family: 'Plus Jakarta Sans', sans-serif; font-size: 1.22rem; font-weight: 800; color: #FFFFFF;">
{value}
</div>
</div>
<div style="font-size: 0.74rem; font-weight: 700; color: #FF2A75; text-transform: uppercase; letter-spacing: 0.05em; margin-top: 0.2rem;">
{label}
</div>
</div>"""
    render_html(html)


def render_card_thumbnail_icon(icon_type: str = "profile") -> None:
    """Renders a clean, minimalist line icon inside an elevated dark container matching the dark theme."""
    if icon_type == "profile":
        stroke_color = "#00D2FF"
        glow_color = "rgba(0, 210, 255, 0.4)"
        svg_content = """<circle cx="28" cy="18" r="9" fill="none" stroke="#00D2FF" stroke-width="2.5" stroke-linecap="round" />
<path d="M 12 46 C 12 36 20 32 28 32 C 36 32 44 36 44 46" fill="none" stroke="#00D2FF" stroke-width="2.5" stroke-linecap="round" />"""
    elif icon_type == "skills":
        stroke_color = "#00D2FF"
        glow_color = "rgba(0, 210, 255, 0.4)"
        svg_content = """<polygon points="28,10 44,19 44,37 28,46 12,37 12,19" fill="none" stroke="#00D2FF" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" />
<line x1="28" y1="10" x2="28" y2="46" stroke="#00D2FF" stroke-width="1.8" stroke-linecap="round" />
<line x1="12" y1="19" x2="44" y2="37" stroke="#00D2FF" stroke-width="1.8" stroke-linecap="round" />"""
    elif icon_type == "goals":
        stroke_color = "#FF2A75"
        glow_color = "rgba(255, 42, 117, 0.4)"
        svg_content = """<circle cx="28" cy="28" r="18" fill="none" stroke="#FF2A75" stroke-width="2.5" />
<circle cx="28" cy="28" r="10" fill="none" stroke="#FF2A75" stroke-width="2" />
<circle cx="28" cy="28" r="3" fill="#FF2A75" />
<line x1="28" y1="4" x2="28" y2="10" stroke="#FF2A75" stroke-width="2" stroke-linecap="round" />
<line x1="28" y1="46" x2="28" y2="52" stroke="#FF2A75" stroke-width="2" stroke-linecap="round" />
<line x1="4" y1="28" x2="10" y2="28" stroke="#FF2A75" stroke-width="2" stroke-linecap="round" />
<line x1="46" y1="28" x2="52" y2="28" stroke="#FF2A75" stroke-width="2" stroke-linecap="round" />"""
    else:  # career
        stroke_color = "#FF6B0B"
        glow_color = "rgba(255, 107, 11, 0.4)"
        svg_content = """<path d="M 28 8 C 36 12 40 22 40 32 L 44 38 L 38 38 L 36 44 L 28 40 L 20 44 L 18 38 L 12 38 L 16 32 C 16 22 20 12 28 8 Z" fill="none" stroke="#FF6B0B" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" />
<circle cx="28" cy="22" r="3.5" fill="#FF6B0B" />
<line x1="28" y1="40" x2="28" y2="48" stroke="#FF2A75" stroke-width="2.5" stroke-linecap="round" />"""

    html = f"""<div style="background: #1B2032; border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 16px; width: 84px; height: 84px; margin: auto; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 18px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.06); filter: drop-shadow(0 0 10px {glow_color});">
<svg viewBox="0 0 56 56" width="46" height="46">
{svg_content}
</svg>
</div>"""
    render_html(html)


def render_section_header(
    title: str,
    subtitle: Optional[str] = None,
    badge_text: Optional[str] = None,
    badge_type: str = "teal",
) -> None:
    """Renders a consistent dark-mode section header with optional subtitle and neon badge."""
    badge_html = (
        f'<span class="ts-badge ts-badge-{badge_type}" style="font-size: 14px;">{badge_text}</span>'
        if badge_text
        else ""
    )
    sub_html = (
        f'<p style="color: #CBD5E1; font-size: 16px; margin-top: 0.25rem; margin-bottom: 0.85rem; line-height: 1.5;">{subtitle}</p>'
        if subtitle
        else ""
    )
    html = f"""<div style="margin-bottom: 0.95rem; margin-top: 0.4rem;">
<div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 0.5rem;">
<h3 style="margin: 0; font-size: 21px; color: #FFFFFF; font-weight: 700; letter-spacing: -0.015em;">{title}</h3>
{badge_html}
</div>
{sub_html}
</div>"""
    render_html(html)


def render_progress_bar(
    label: str,
    percentage: int | float,
    sub_info: Optional[str] = None,
    color_scheme: str = "cyan",
) -> None:
    """Renders a smooth CSS/HTML progress bar (height: 8px, gradient fill) matching dark theme."""
    pct = max(0, min(100, int(percentage)))
    info_text = sub_info if sub_info else f"{pct}%"

    if color_scheme == "pink":
        fill_grad = "linear-gradient(90deg, #FF2A75 0%, #FF5252 100%)"
        glow = "box-shadow: 0 0 8px rgba(255, 42, 117, 0.5);"
        text_color = "#FF2A75"
    elif color_scheme == "purple":
        fill_grad = "linear-gradient(90deg, #8A2BE2 0%, #A855F7 100%)"
        glow = "box-shadow: 0 0 8px rgba(168, 85, 247, 0.5);"
        text_color = "#A855F7"
    else:
        fill_grad = "linear-gradient(90deg, #00D2FF 0%, #0072FF 100%)"
        glow = "box-shadow: 0 0 8px rgba(0, 210, 255, 0.5);"
        text_color = "#00D2FF"

    html = f"""<div style="margin: 0.45rem 0;">
<div style="display: flex; justify-content: space-between; font-size: 16px; font-weight: 600; color: #FFFFFF; margin-bottom: 0.35rem;">
<span>{label}</span>
<span style="color: {text_color}; font-weight: 700; font-size: 16px;">{info_text}</span>
</div>
<div style="height: 8px; background-color: #121624; border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 9999px; overflow: hidden;">
<div style="height: 100%; border-radius: 9999px; width: {pct}%; background: {fill_grad}; {glow} transition: width 0.4s ease;"></div>
</div>
</div>"""
    render_html(html)


def render_badge(text: str, badge_type: str = "teal") -> str:
    """Returns the HTML string for a neon pill badge."""
    return f'<span class="ts-badge ts-badge-{badge_type}">{text}</span>'


def render_demo_banner(message: str, icon: str = "ℹ️") -> None:
    """Renders a demonstration callout banner styled for dark theme."""
    html = f"""<div class="ts-demo-banner">
<span style="font-size: 1.15rem;">{icon}</span>
<div>{message}</div>
</div>"""
    render_html(html)


def render_hero_banner(
    title: str,
    subtitle: str,
    tag: str = "CAREER GROWTH PLATFORM",
    badge_icon: str = "🌱",
) -> None:
    """Renders a high-contrast dark futuristic hero banner."""
    html = f"""<div style="background: linear-gradient(135deg, #161A29 0%, #0D111D 100%); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 16px; padding: 2rem 2.25rem; margin-bottom: 1.5rem; box-shadow: 0 12px 36px rgba(0, 0, 0, 0.6), inset 0 1px 0 rgba(255, 255, 255, 0.08);">
<div style="display: inline-flex; align-items: center; gap: 0.4rem; background: rgba(0, 210, 255, 0.15); padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 700; letter-spacing: 0.06em; margin-bottom: 0.8rem; border: 1px solid rgba(0, 210, 255, 0.35); color: #00D2FF; box-shadow: 0 0 12px rgba(0, 210, 255, 0.2);">
<span>{badge_icon}</span>
<span>{tag}</span>
</div>
<h1 style="font-size: 1.85rem; margin-bottom: 0.45rem; color: #FFFFFF;">{title}</h1>
<p style="font-size: 0.98rem; max-width: 780px; margin: 0; line-height: 1.5; color: #CBD5E1;">{subtitle}</p>
</div>"""
    render_html(html)
