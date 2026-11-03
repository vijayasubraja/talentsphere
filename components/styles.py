"""Design system and custom CSS for TalentSphere.

Provides unified styling, color variables, cards, badges, and layout utilities
tuned for a professional SaaS employee career growth application.
"""

def get_custom_css() -> str:
    """Returns CSS rules for TalentSphere branding and layout."""
    return """
    <style>
    /* Google Fonts & Icons */
    @import url('https://fonts.googleapis.com/css2?family=Literata:wght@400;500;600;700&family=Nunito+Sans:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap');

    :root {
        --ts-navy: #0A2540;
        --ts-navy-dark: #07192C;
        --ts-navy-light: #1E3A5F;
        --ts-teal: #0D7A82;
        --ts-teal-accent: #00A896;
        --ts-teal-light: #E6F4F5;
        --ts-teal-subtle: #F0FAF9;
        --ts-bg: #F8FAFC;
        --ts-card-bg: #FFFFFF;
        --ts-border: #E2E8F0;
        --ts-border-subtle: #EDF2F7;
        --ts-text: #0F172A;
        --ts-text-muted: #64748B;
        --ts-text-light: #94A3B8;
        --ts-success: #059669;
        --ts-success-bg: #ECFDF5;
        --ts-warning: #D97706;
        --ts-warning-bg: #FFFBEB;
        --ts-info: #2563EB;
        --ts-info-bg: #EFF6FF;
        --ts-radius-sm: 8px;
        --ts-radius-md: 12px;
        --ts-radius-lg: 16px;
        --ts-shadow-sm: 0 1px 2px 0 rgba(10, 37, 64, 0.04);
        --ts-shadow: 0 4px 12px -2px rgba(10, 37, 64, 0.06), 0 2px 6px -1px rgba(10, 37, 64, 0.03);
        --ts-shadow-hover: 0 10px 25px -5px rgba(10, 37, 64, 0.1), 0 8px 10px -6px rgba(10, 37, 64, 0.04);
    }

    /* Global Typography & Background */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: var(--ts-text);
        background-color: var(--ts-bg);
    }

    div[data-testid="stAppViewContainer"] {
        background-color: var(--ts-bg) !important;
        background-image: none;
    }

    h1, h2, h3, h4, h5, h6 {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-weight: 700;
        color: var(--ts-navy);
        letter-spacing: -0.02em;
    }

    /* Header adjustments */
    header[data-testid="stHeader"] {
        background-color: transparent !important;
    }

    /* Top padding container */
    .block-container {
        padding-top: 1.8rem !important;
        padding-bottom: 3.5rem !important;
        max-width: 1400px !important;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background: #0D111D !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
    }
    
    section[data-testid="stSidebar"] .block-container {
        padding-top: 2rem !important;
        padding-left: 1.25rem !important;
        padding-right: 1.25rem !important;
    }

    /* Sidebar Navigation Radio Buttons */
    section[data-testid="stSidebar"] div[role="radiogroup"] > label {
        padding: 0.8rem 1.1rem !important;
        margin-bottom: 0.45rem !important;
        border-radius: var(--ts-radius-sm) !important;
        border: 1px solid transparent !important;
        font-weight: 600 !important;
        font-size: 1.05rem !important;
        color: var(--ts-text) !important;
        transition: all 0.2s ease-in-out !important;
        background: transparent !important;
        cursor: pointer !important;
        display: flex !important;
        align-items: center !important;
        width: 100% !important;
        box-sizing: border-box !important;
    }

    /* Completely hide radio circle indicator in sidebar */
    section[data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child,
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label > div:first-child,
    section[data-testid="stSidebar"] div[data-baseweb="radio"] > div:first-child {
        display: none !important;
        width: 0 !important;
        height: 0 !important;
        visibility: hidden !important;
        opacity: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
        background-color: var(--ts-teal-subtle) !important;
        color: var(--ts-teal) !important;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] > label[data-checked="true"],
    section[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) {
        background-color: var(--ts-teal-light) !important;
        color: var(--ts-navy) !important;
        font-weight: 700 !important;
        border-left: 4px solid var(--ts-teal) !important;
    }

    /* Primary and Secondary Buttons */
    div.stButton > button[kind="primary"], div.stButton > button[data-testid="stBaseButton-primary"] {
        background-color: var(--ts-teal) !important;
        color: #FFFFFF !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: var(--ts-radius-sm) !important;
        padding: 0.55rem 1.25rem !important;
        box-shadow: 0 2px 4px rgba(13, 122, 130, 0.2) !important;
        transition: all 0.2s ease !important;
    }

    div.stButton > button[kind="primary"]:hover, div.stButton > button[data-testid="stBaseButton-primary"]:hover {
        background-color: var(--ts-navy) !important;
        box-shadow: 0 4px 8px rgba(10, 37, 64, 0.25) !important;
        transform: translateY(-1px);
    }

    div.stButton > button[kind="secondary"], div.stButton > button[data-testid="stBaseButton-secondary"] {
        background-color: #FFFFFF !important;
        color: var(--ts-navy) !important;
        border: 1px solid var(--ts-border) !important;
        border-radius: var(--ts-radius-sm) !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }

    div.stButton > button[kind="secondary"]:hover, div.stButton > button[data-testid="stBaseButton-secondary"]:hover {
        border-color: var(--ts-teal) !important;
        color: var(--ts-teal) !important;
        background-color: var(--ts-teal-subtle) !important;
    }

    /* Cards */
    .ts-card {
        background-color: #FFFFFF;
        border: 1px solid var(--ts-border);
        border-radius: var(--ts-radius-md);
        padding: 1.35rem 1.5rem;
        box-shadow: var(--ts-shadow);
        margin-bottom: 1.25rem;
        transition: all 0.2s ease;
    }

    .ts-card:hover {
        border-color: #CBD5E1;
        box-shadow: var(--ts-shadow-hover);
    }

    .ts-card-hero {
        background: linear-gradient(135deg, #0A2540 0%, #103B64 60%, #0D7A82 100%);
        color: #FFFFFF;
        border-radius: var(--ts-radius-lg);
        padding: 2rem 2.25rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 24px -4px rgba(10, 37, 64, 0.2);
    }

    .ts-card-hero h1, .ts-card-hero h2, .ts-card-hero h3 {
        color: #FFFFFF !important;
    }

    .ts-card-hero p {
        color: #E2E8F0 !important;
    }

    /* Stat & Metric Cards */
    .ts-metric-box {
        background: #FFFFFF;
        border: 1px solid var(--ts-border);
        border-radius: var(--ts-radius-md);
        padding: 1.2rem 1.25rem;
        box-shadow: var(--ts-shadow);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        height: 100%;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    .ts-metric-box:hover {
        transform: translateY(-2px);
        box-shadow: var(--ts-shadow-hover);
        border-color: #CBD5E1;
    }

    .ts-metric-label {
        font-size: 0.82rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: var(--ts-text-muted);
        margin-bottom: 0.4rem;
        display: flex;
        align-items: center;
        gap: 0.4rem;
    }

    .ts-metric-value {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 1.85rem;
        font-weight: 800;
        color: var(--ts-navy);
        line-height: 1.2;
    }

    .ts-metric-subtitle {
        font-size: 0.82rem;
        color: var(--ts-text-muted);
        margin-top: 0.35rem;
    }

    /* Badges */
    .ts-badge {
        display: inline-flex;
        align-items: center;
        padding: 0.2rem 0.65rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.02em;
        white-space: nowrap;
    }

    .ts-badge-teal {
        background-color: var(--ts-teal-light);
        color: var(--ts-teal);
        border: 1px solid rgba(13, 122, 130, 0.2);
    }

    .ts-badge-navy {
        background-color: #E2E8F0;
        color: var(--ts-navy);
        border: 1px solid #CBD5E1;
    }

    .ts-badge-success {
        background-color: var(--ts-success-bg);
        color: var(--ts-success);
        border: 1px solid rgba(5, 150, 105, 0.2);
    }

    .ts-badge-warning {
        background-color: var(--ts-warning-bg);
        color: var(--ts-warning);
        border: 1px solid rgba(217, 119, 6, 0.2);
    }

    .ts-badge-info {
        background-color: var(--ts-info-bg);
        color: var(--ts-info);
        border: 1px solid rgba(37, 99, 235, 0.2);
    }

    /* Avatar styling */
    .ts-avatar {
        width: 72px;
        height: 72px;
        border-radius: 50%;
        background: linear-gradient(135deg, var(--ts-teal) 0%, var(--ts-navy) 100%);
        color: #FFFFFF;
        display: flex;
        align-items: center;
        justify-content: center;
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 1.5rem;
        font-weight: 700;
        box-shadow: 0 4px 10px rgba(10, 37, 64, 0.15);
        border: 3px solid #FFFFFF;
    }

    /* Custom Progress Bar Container */
    .ts-prog-wrapper {
        margin: 0.6rem 0;
    }

    .ts-prog-labels {
        display: flex;
        justify-content: space-between;
        font-size: 0.84rem;
        font-weight: 600;
        color: var(--ts-text);
        margin-bottom: 0.25rem;
    }

    .ts-prog-track {
        height: 8px;
        background-color: #E2E8F0;
        border-radius: 9999px;
        overflow: hidden;
    }

    .ts-prog-fill {
        height: 100%;
        border-radius: 9999px;
        background: linear-gradient(90deg, var(--ts-teal) 0%, var(--ts-teal-accent) 100%);
        transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
    }

    /* Activity Timeline */
    .ts-activity-row {
        display: flex;
        align-items: flex-start;
        gap: 0.85rem;
        padding: 0.8rem 0;
        border-bottom: 1px solid var(--ts-border-subtle);
    }

    .ts-activity-row:last-child {
        border-bottom: none;
        padding-bottom: 0;
    }

    .ts-activity-icon {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background-color: var(--ts-teal-light);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.1rem;
        flex-shrink: 0;
    }

    .ts-activity-content {
        flex-grow: 1;
    }

    .ts-activity-title {
        font-size: 0.9rem;
        font-weight: 600;
        color: var(--ts-text);
    }

    .ts-activity-time {
        font-size: 0.78rem;
        color: var(--ts-text-muted);
        margin-top: 0.15rem;
    }

    /* Form and Input enhancements */
    div[data-baseweb="input"], div[data-baseweb="select"], div[data-baseweb="textarea"] {
        border-radius: var(--ts-radius-sm) !important;
    }

    /* Streamlit Containers with border */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #FFFFFF !important;
        border-radius: var(--ts-radius-md) !important;
        border: 1px solid var(--ts-border) !important;
        box-shadow: var(--ts-shadow) !important;
    }

    /* Quick Action Pill Buttons */
    .ts-quick-action {
        display: block;
        padding: 0.85rem 1rem;
        background: #FFFFFF;
        border: 1px solid var(--ts-border);
        border-radius: var(--ts-radius-md);
        text-decoration: none;
        color: var(--ts-navy);
        transition: all 0.2s ease;
        margin-bottom: 0.6rem;
    }

    .ts-quick-action:hover {
        border-color: var(--ts-teal);
        background: var(--ts-teal-subtle);
        transform: translateX(3px);
    }

    /* Alert / Demo Banner */
    .ts-demo-banner {
        background-color: var(--ts-teal-light);
        border-left: 4px solid var(--ts-teal);
        border-radius: var(--ts-radius-sm);
        padding: 0.85rem 1.15rem;
        margin-bottom: 1.5rem;
        font-size: 0.88rem;
        color: var(--ts-navy);
        display: flex;
        align-items: center;
        gap: 0.6rem;
    }

    /* Clean Tabs */
    button[data-baseweb="tab"] {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.98rem !important;
        color: var(--ts-text-muted) !important;
        padding-top: 0.75rem !important;
        padding-bottom: 0.75rem !important;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        color: var(--ts-teal) !important;
        border-bottom-color: var(--ts-teal) !important;
        border-bottom-width: 3px !important;
        font-weight: 700 !important;
    }

    /* ========================================================
       iSpring LMS-Inspired Dashboard Styling
       ======================================================== */
    
    /* LMS Top Navigation Bar */
    .ts-lms-nav-container {
        background: #FFFFFF;
        border: 1px solid var(--ts-border);
        border-radius: 12px;
        padding: 0.75rem 1.25rem;
        margin-bottom: 1.25rem;
        box-shadow: 0 1px 3px rgba(10, 37, 64, 0.04);
    }

    /* Wide Dashboard Banner */
    .ts-lms-banner {
        background: linear-gradient(135deg, rgba(10, 37, 64, 0.90) 0%, rgba(13, 122, 130, 0.85) 100%),
                    url('https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&w=1600&q=80') center/cover no-repeat;
        border-radius: 14px;
        padding: 2.25rem 2.5rem;
        margin-bottom: 1.25rem;
        box-shadow: 0 6px 20px -4px rgba(10, 37, 64, 0.2);
        color: #FFFFFF;
        position: relative;
        overflow: hidden;
    }

    .ts-lms-banner-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(8px);
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        margin-bottom: 0.75rem;
        border: 1px solid rgba(255, 255, 255, 0.25);
    }

    .ts-lms-banner h1 {
        color: #FFFFFF !important;
        font-size: 2.1rem !important;
        font-weight: 800 !important;
        margin: 0 0 0.45rem 0 !important;
        letter-spacing: -0.025em !important;
    }

    .ts-lms-banner p {
        color: #E2E8F0 !important;
        font-size: 1.02rem !important;
        margin: 0 !important;
        max-width: 650px !important;
        line-height: 1.5 !important;
    }

    /* Horizontal LMS Course/Feature Content Cards */
    .ts-lms-card-wrapper {
        background: #FFFFFF;
        border: 1px solid var(--ts-border);
        border-radius: 12px;
        padding: 1.25rem 1.45rem;
        margin-bottom: 1.1rem;
        box-shadow: 0 2px 8px rgba(10, 37, 64, 0.04);
        transition: all 0.2s ease-in-out;
    }

    .ts-lms-card-wrapper:hover {
        border-color: #CBD5E1;
        box-shadow: 0 6px 18px rgba(10, 37, 64, 0.08);
        transform: translateY(-2px);
    }

    .ts-lms-tag {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 6px;
        font-size: 0.78rem;
        font-weight: 600;
        margin-right: 0.4rem;
        margin-bottom: 0.35rem;
    }

    /* ========================================================
       TalentSphere Career Growth Modern Dual-Panel Design
       ======================================================== */

    .material-symbols-outlined {
        font-family: 'Material Symbols Outlined' !important;
        font-weight: normal;
        font-style: normal;
        font-size: 20px;
        line-height: 1;
        letter-spacing: normal;
        text-transform: none;
        display: inline-block;
        white-space: nowrap;
        word-wrap: normal;
        direction: ltr;
        -webkit-font-smoothing: antialiased;
        vertical-align: middle;
    }

    /* ========================================================
       TalentSphere Simplified Clean Auth Styling
       ======================================================== */

    .material-symbols-outlined {
        font-family: 'Material Symbols Outlined' !important;
        font-weight: normal;
        font-style: normal;
        font-size: 20px;
        line-height: 1;
        letter-spacing: normal;
        text-transform: none;
        display: inline-block;
        white-space: nowrap;
        word-wrap: normal;
        direction: ltr;
        -webkit-font-smoothing: antialiased;
        vertical-align: middle;
    }

    /* Auth Page Background & Container */
    .ts-auth-body-bg {
        background-color: #F8FAFC;
    }

    /* Top Brand Bar */
    .ts-top-brand-bar {
        width: 100%;
        max-width: 960px;
        margin: 0 auto 0.75rem auto;
        display: flex;
        align-items: center;
        justify-content: flex-start;
        padding: 0 0.25rem;
    }

    .ts-brand-logo-wrap {
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }

    .ts-brand-logo-img {
        height: 38px;
        width: 38px;
        object-fit: contain;
        display: block;
        border-radius: 8px;
    }

    .ts-brand-logo-icon {
        width: 38px;
        height: 38px;
        border-radius: 10px;
        background: #2563EB;
        color: #FFFFFF;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 2px 6px rgba(37, 99, 235, 0.25);
    }

    .ts-brand-text-wrap {
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    .ts-brand-logo-text {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 1.25rem;
        font-weight: 800;
        color: #111827;
        line-height: 1.15;
        letter-spacing: -0.02em;
    }

    .ts-brand-logo-sub {
        font-family: 'Inter', sans-serif;
        font-size: 0.75rem;
        color: #64748B;
        font-weight: 500;
        letter-spacing: 0.01em;
        margin-top: 2px;
    }

    /* Left Panel - Dark Navy (#111B30) */
    .ts-left-panel {
        color: #FFFFFF;
        display: flex;
        flex-direction: column;
        justify-content: center;
        height: 100%;
    }

    .ts-left-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.45rem;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        background: rgba(37, 99, 235, 0.16);
        border: 1px solid rgba(59, 130, 246, 0.28);
        color: #93C5FD;
        font-size: 0.74rem;
        font-weight: 600;
        letter-spacing: 0.02em;
        width: fit-content;
        margin-bottom: 0.75rem;
    }

    .ts-left-badge-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: #38BDF8;
        box-shadow: 0 0 6px rgba(56, 189, 248, 0.7);
    }

    .ts-left-title {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 1.55rem;
        font-weight: 700;
        color: #FFFFFF;
        line-height: 1.3;
        letter-spacing: -0.02em;
        margin: 0 0 0.5rem 0;
    }

    .ts-left-desc {
        font-family: 'Inter', sans-serif;
        font-size: 0.88rem;
        color: #94A3B8;
        line-height: 1.55;
        margin: 0 0 1rem 0;
    }

    .ts-left-illustration-box {
        width: 100%;
        margin: 0.25rem 0 1.15rem 0;
        display: flex;
        justify-content: center;
        align-items: center;
        border-radius: 10px;
        overflow: hidden;
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 0.5rem;
    }

    .ts-left-illustration {
        width: 100%;
        max-height: 125px;
        object-fit: contain;
        display: block;
        border-radius: 6px;
    }

    .ts-left-benefits {
        display: flex;
        flex-direction: column;
        gap: 0.6rem;
    }

    .ts-benefit-item {
        display: flex;
        align-items: center;
        gap: 0.65rem;
        font-family: 'Inter', sans-serif;
        font-size: 0.85rem;
        color: #E2E8F0;
        font-weight: 500;
        line-height: 1.35;
    }

    .ts-benefit-icon {
        width: 18px;
        height: 18px;
        border-radius: 50%;
        background: rgba(37, 99, 235, 0.25);
        color: #60A5FA;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
    }

    .ts-benefit-icon .material-symbols-outlined {
        font-size: 13px !important;
        font-weight: 700 !important;
    }

    /* Right Panel - Clean White (#FFFFFF) */
    .ts-right-panel {
        display: flex;
        flex-direction: column;
        justify-content: center;
        width: 100%;
        max-width: 380px;
        margin: 0 auto;
    }

    .ts-auth-header {
        margin-bottom: 1.25rem;
    }

    .ts-auth-title {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 1.55rem;
        font-weight: 700;
        color: #111827;
        letter-spacing: -0.02em;
        margin: 0 0 0.35rem 0;
        line-height: 1.25;
    }

    .ts-auth-subtitle {
        font-family: 'Inter', sans-serif;
        font-size: 0.88rem;
        color: #64748B;
        margin: 0;
        line-height: 1.5;
    }

    /* Input Controls */
    .ts-right-panel div[data-testid="stTextInput"],
    .ts-right-panel div[data-testid="stSelectbox"] {
        margin-bottom: 0.35rem !important;
    }

    .ts-right-panel div[data-testid="stTextInput"] label,
    .ts-right-panel div[data-testid="stSelectbox"] label {
        font-family: 'Inter', sans-serif !important;
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        margin-bottom: 0.3rem !important;
        color: #111827 !important;
    }

    .ts-right-panel div[data-testid="stTextInput"] input {
        padding: 10px 14px !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.92rem !important;
        border-radius: 8px !important;
        height: 44px !important;
        border: 1px solid #CBD5E1 !important;
        background: #FFFFFF !important;
        color: #111827 !important;
        transition: all 0.15s ease-in-out !important;
    }

    .ts-right-panel div[data-testid="stTextInput"] input::placeholder {
        color: #94A3B8 !important;
    }

    .ts-right-panel div[data-testid="stTextInput"] input:focus {
        border-color: #2563EB !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.12) !important;
        outline: none !important;
    }

    .ts-right-panel div[data-testid="stSelectbox"] div[data-baseweb="select"] {
        min-height: 44px !important;
        font-size: 0.92rem !important;
        border-radius: 8px !important;
        border: 1px solid #CBD5E1 !important;
    }

    /* Password container with inline show/hide eye icon */
    .ts-password-container {
        position: relative;
        margin-bottom: 0.35rem;
    }

    .ts-password-container div[data-testid="stTextInput"] {
        margin-bottom: 0 !important;
    }

    .ts-password-container input {
        padding-right: 44px !important;
    }

    .ts-password-container div[data-testid="stCheckbox"] {
        position: absolute;
        right: 12px;
        top: 36px;
        margin: 0 !important;
        padding: 0 !important;
        height: 24px !important;
        width: 24px !important;
        z-index: 10;
        cursor: pointer;
    }

    .ts-password-container div[data-testid="stCheckbox"] label {
        margin: 0 !important;
        padding: 0 !important;
        cursor: pointer;
        display: flex !important;
        align-items: center;
        justify-content: center;
        width: 24px !important;
        height: 24px !important;
    }

    .ts-password-container div[data-testid="stCheckbox"] label div:first-child {
        opacity: 0 !important;
        position: absolute !important;
        width: 24px !important;
        height: 24px !important;
        margin: 0 !important;
        cursor: pointer !important;
    }

    .ts-password-container div[data-testid="stCheckbox"] label span {
        display: none !important;
    }

    .ts-password-container div[data-testid="stCheckbox"] label::after {
        content: 'visibility';
        font-family: 'Material Symbols Outlined' !important;
        font-size: 20px;
        line-height: 1;
        color: #94A3B8;
        transition: color 0.15s ease;
        cursor: pointer;
    }

    .ts-password-container div[data-testid="stCheckbox"]:hover label::after {
        color: #2563EB;
    }

    .ts-password-container.ts-pw-visible div[data-testid="stCheckbox"] label::after,
    .ts-password-container div[data-testid="stCheckbox"]:has(input:checked) label::after {
        content: 'visibility_off';
        color: #2563EB;
    }

    /* Remember Me & Forgot Password Row */
    .ts-remember-row {
        margin-top: 0.15rem;
        margin-bottom: 0.75rem;
    }

    .ts-remember-row div[data-testid="stCheckbox"] {
        margin: 0 !important;
    }

    .ts-remember-row div[data-testid="stCheckbox"] label span {
        font-family: 'Inter', sans-serif !important;
        font-size: 0.82rem !important;
        color: #475569 !important;
        font-weight: 500 !important;
    }

    .ts-forgot-wrap {
        text-align: right;
        padding-top: 3px;
    }

    .ts-link {
        font-family: 'Inter', sans-serif;
        color: #2563EB;
        font-size: 0.82rem;
        font-weight: 600;
        text-decoration: none;
        transition: color 0.15s ease;
    }

    .ts-link:hover {
        color: #1D4ED8;
        text-decoration: underline;
    }

    /* Primary Sign In Button */
    .ts-auth-btn-primary div.stButton > button {
        background: #2563EB !important;
        color: #FFFFFF !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.92rem !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        height: 44px !important;
        border: none !important;
        box-shadow: 0 2px 4px rgba(37, 99, 235, 0.2) !important;
        transition: all 0.15s ease-in-out !important;
        margin-top: 0.25rem !important;
    }

    .ts-auth-btn-primary div.stButton > button:hover {
        background: #1D4ED8 !important;
        box-shadow: 0 4px 8px rgba(29, 78, 216, 0.25) !important;
        transform: translateY(-1px) !important;
    }

    /* Footer Inline Link */
    .ts-auth-footer {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.35rem;
        margin-top: 1.25rem;
        font-family: 'Inter', sans-serif;
        font-size: 0.85rem;
        color: #64748B;
    }

    .ts-auth-footer .stButton {
        display: inline-flex !important;
        width: auto !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    .ts-auth-footer .stButton > button {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        color: #2563EB !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        padding: 0 !important;
        margin: 0 !important;
        height: auto !important;
        min-height: auto !important;
        text-decoration: none !important;
        cursor: pointer !important;
        line-height: inherit !important;
    }

    .ts-auth-footer .stButton > button:hover {
        color: #1D4ED8 !important;
        text-decoration: underline !important;
        background: transparent !important;
    }

    /* Rule item badges for registration password */
    .ts-rule-item {
        display: flex;
        align-items: center;
        gap: 0.45rem;
        font-size: 0.78rem;
        font-weight: 500;
    }

    .ts-rule-passed {
        color: #059669;
        font-weight: 600;
    }

    .ts-rule-pending {
        color: #94A3B8;
    }

    /* Bottom page footnote */
    .ts-page-footer {
        text-align: center;
        font-family: 'Inter', sans-serif;
        font-size: 0.75rem;
        color: #94A3B8;
        margin-top: 1rem;
    }
    </style>
    """


def get_dark_theme_css() -> str:
    """Returns the comprehensive dark-mode theme CSS rules based on the reference design."""
    return """
    <style>
    /* =========================================================================
       TALENTSPHERE FUTURISTIC DARK THEME (Inspired by Reference Design)
       Canvas: #0B0E17 · Cards: #161A29 / #1B2032 · Accents: Cyan & Neon Pink
       ========================================================================= */

    :root {
        /* Canvas & Backgrounds */
        --ts-dark-canvas: #0B0E17;
        --ts-dark-card: #161A29;
        --ts-dark-card-elevated: #1B2032;
        --ts-dark-card-inner: #121624;
        --ts-dark-sidebar: #0D111D;
        --ts-dark-border: rgba(255, 255, 255, 0.08);
        --ts-dark-border-glow: rgba(0, 210, 255, 0.35);

        /* Glowing Neon Accents */
        --ts-neon-pink: #FF2A75;
        --ts-neon-pink-light: #FF5252;
        --ts-neon-pink-glow: rgba(255, 42, 117, 0.45);
        --ts-pink-gradient: linear-gradient(135deg, #FF2A75 0%, #FF5252 100%);

        --ts-neon-cyan: #00D2FF;
        --ts-neon-cyan-dark: #0072FF;
        --ts-neon-cyan-glow: rgba(0, 210, 255, 0.45);
        --ts-cyan-gradient: linear-gradient(135deg, #00D2FF 0%, #0072FF 100%);

        --ts-neon-purple: #8A2BE2;
        --ts-neon-purple-light: #A855F7;
        --ts-neon-purple-glow: rgba(168, 85, 247, 0.4);
        --ts-purple-gradient: linear-gradient(135deg, #8A2BE2 0%, #A855F7 100%);

        --ts-neon-orange: #FF6B0B;
        --ts-orange-gradient: linear-gradient(135deg, #FF6B0B 0%, #FFA000 100%);

        /* Typography & Neutrals */
        --ts-text-primary: #FFFFFF;
        --ts-text-secondary: #CBD5E1;
        --ts-text-muted: #94A3B8;

        /* Radius & Shadows */
        --ts-radius-card: 16px;
        --ts-radius-pill: 9999px;
        --ts-glow-shadow: 0 10px 32px -4px rgba(0, 0, 0, 0.65), inset 0 1px 0 0 rgba(255, 255, 255, 0.08);
    }

    /* 1. Global Page Canvas */
    html, body, [class*="css"], [data-testid="stAppViewContainer"] {
        background: #0B0E17 !important;
        background-color: #0B0E17 !important;
        background-image: radial-gradient(circle at 50% 0%, #171E36 0%, #0B0E17 70%) !important;
        background-attachment: fixed !important;
        color: #FFFFFF !important;
    }

    /* Headings and Typography */
    h1, h2, h3, h4, h5, h6 {
        color: #FFFFFF !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em !important;
    }

    /* Full Page Width Layout */
    .main .block-container {
        max-width: 1400px !important;
        width: 100% !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }

    @media (max-width: 768px) {
        .main .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
    }

    p, span, label, div {
        color: inherit;
    }

    /* Header Bar */
    header[data-testid="stHeader"] {
        background: transparent !important;
    }

    /* 2. Sidebar Redesign (Dark Charcoal & Modern Teal/Cyan SaaS Theme) */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

    section[data-testid="stSidebar"],
    section[data-testid="stSidebar"] * {
        font-family: 'Poppins', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }

    section[data-testid="stSidebar"] {
        background: #0B0E17 !important;
        background-color: #0B0E17 !important;
        /* Token compatibility: #0D111D */
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
        box-shadow: 4px 0 24px rgba(0, 0, 0, 0.6) !important;
        min-width: 290px !important;
        max-width: 290px !important;
        width: 290px !important;
        transition: min-width 0.28s cubic-bezier(0.4, 0, 0.2, 1), max-width 0.28s cubic-bezier(0.4, 0, 0.2, 1), width 0.28s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }

    section[data-testid="stSidebar"] .block-container {
        padding-top: 1rem !important;
        padding-left: 0.95rem !important;
        padding-right: 0.95rem !important;
        padding-bottom: 2rem !important;
        max-width: 290px !important;
        box-sizing: border-box !important;
    }

    .ts-sidebar-brand {
        display: flex !important;
        align-items: center !important;
        justify-content: flex-start !important;
        gap: 0.65rem !important;
        margin: 0 0 0.85rem 0 !important;
        padding: 0 !important;
        text-align: left !important;
    }

    /* Collapse / Expand Toggle Buttons with Lucide panel-left-close & panel-left-open */
    section[data-testid="stSidebar"] div.stButton button[key="btn_sidebar_collapse"],
    section[data-testid="stSidebar"] div:has(> .ts-collapse-btn-anchor) div.stButton button,
    section[data-testid="stSidebar"] div[data-testid="column"]:last-child div.stButton button {
        background: #161A29 !important;
        border: 1px solid rgba(0, 210, 255, 0.25) !important;
        border-radius: 8px !important;
        color: transparent !important;
        font-size: 0 !important;
        padding: 0 !important;
        min-height: 38px !important;
        height: 38px !important;
        width: 100% !important;
        background-repeat: no-repeat !important;
        background-position: center !important;
        background-size: 20px 20px !important;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 24 24' fill='none' stroke='%2300D2FF' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Crect width='18' height='18' x='3' y='3' rx='2'/%3E%3Cpath d='M9 3v18'/%3E%3Cpath d='m16 15-3-3 3-3'/%3E%3C/svg%3E") !important;
        transition: all 0.2s ease !important;
        cursor: pointer !important;
    }
    section[data-testid="stSidebar"] div.stButton button[key="btn_sidebar_collapse"]:hover,
    section[data-testid="stSidebar"] div:has(> .ts-collapse-btn-anchor) div.stButton button:hover,
    section[data-testid="stSidebar"] div[data-testid="column"]:last-child div.stButton button:hover {
        background-color: rgba(0, 210, 255, 0.15) !important;
        border-color: #00D2FF !important;
        box-shadow: 0 0 10px rgba(0, 210, 255, 0.3) !important;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 24 24' fill='none' stroke='%23FFFFFF' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Crect width='18' height='18' x='3' y='3' rx='2'/%3E%3Cpath d='M9 3v18'/%3E%3Cpath d='m16 15-3-3 3-3'/%3E%3C/svg%3E") !important;
    }
    section[data-testid="stSidebar"] div.stButton button[key="btn_sidebar_collapse"] p,
    section[data-testid="stSidebar"] div:has(> .ts-collapse-btn-anchor) div.stButton button p,
    section[data-testid="stSidebar"] div[data-testid="column"]:last-child div.stButton button p {
        display: none !important;
        font-size: 0 !important;
        visibility: hidden !important;
    }

    section[data-testid="stSidebar"] div.stButton button[key="btn_sidebar_expand"],
    section[data-testid="stSidebar"] div:has(> .ts-expand-btn-anchor) div.stButton button {
        background: #161A29 !important;
        border: 1px solid rgba(0, 210, 255, 0.25) !important;
        border-radius: 8px !important;
        color: transparent !important;
        font-size: 0 !important;
        padding: 0 !important;
        min-height: 38px !important;
        height: 38px !important;
        width: 100% !important;
        background-repeat: no-repeat !important;
        background-position: center !important;
        background-size: 20px 20px !important;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 24 24' fill='none' stroke='%2300D2FF' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Crect width='18' height='18' x='3' y='3' rx='2'/%3E%3Cpath d='M9 3v18'/%3E%3Cpath d='m14 9 3 3-3 3'/%3E%3C/svg%3E") !important;
        transition: all 0.2s ease !important;
        cursor: pointer !important;
    }
    section[data-testid="stSidebar"] div.stButton button[key="btn_sidebar_expand"]:hover,
    section[data-testid="stSidebar"] div:has(> .ts-expand-btn-anchor) div.stButton button:hover {
        background-color: rgba(0, 210, 255, 0.15) !important;
        border-color: #00D2FF !important;
        box-shadow: 0 0 10px rgba(0, 210, 255, 0.3) !important;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 24 24' fill='none' stroke='%23FFFFFF' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Crect width='18' height='18' x='3' y='3' rx='2'/%3E%3Cpath d='M9 3v18'/%3E%3Cpath d='m14 9 3 3-3 3'/%3E%3C/svg%3E") !important;
    }
    section[data-testid="stSidebar"] div.stButton button[key="btn_sidebar_expand"] p,
    section[data-testid="stSidebar"] div:has(> .ts-expand-btn-anchor) div.stButton button p {
        display: none !important;
        font-size: 0 !important;
        visibility: hidden !important;
    }

    /* Sidebar Search Input (Compact dark input with teal focus glow) */
    section[data-testid="stSidebar"] div[data-testid="stTextInput"] {
        margin-bottom: 0.45rem !important;
        width: 100% !important;
    }

    section[data-testid="stSidebar"] div[data-testid="stTextInput"] input {
        background: #121624 !important;
        background-color: #121624 !important;
        border: 1px solid rgba(0, 210, 255, 0.22) !important;
        border-radius: 10px !important;
        color: #FFFFFF !important;
        font-size: 0.88rem !important;
        padding: 0.52rem 0.85rem !important;
        transition: all 0.2s ease !important;
        box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.3) !important;
        width: 100% !important;
        height: 40px !important;
    }

    section[data-testid="stSidebar"] div[data-testid="stTextInput"] input::placeholder {
        color: #64748B !important;
        font-size: 0.84rem !important;
    }

    section[data-testid="stSidebar"] div[data-testid="stTextInput"] input:focus {
        border-color: #00D2FF !important;
        box-shadow: 0 0 10px rgba(0, 210, 255, 0.25), inset 0 1px 2px rgba(0, 0, 0, 0.3) !important;
        outline: none !important;
    }

    /* Sidebar Radio Options (Identical outer box dimensions, clean SaaS styling, no decorative arrows) */
    section[data-testid="stSidebar"] div[role="radiogroup"] {
        gap: 0.35rem !important;
        display: flex !important;
        flex-direction: column !important;
        width: 100% !important;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] > div {
        width: 100% !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label,
    section[data-testid="stSidebar"] div[role="radiogroup"] > label,
    section[data-testid="stSidebar"] div[role="radiogroup"] [data-testid="stRadioOption"] {
        height: 48px !important;
        min-height: 48px !important;
        max-height: 48px !important;
        width: 100% !important;
        padding: 0 1rem !important;
        margin: 0 0 0.35rem 0 !important;
        border-radius: 10px !important;
        border: 1px solid rgba(255, 255, 255, 0.07) !important;
        border-left: 3.5px solid transparent !important;
        font-weight: 600 !important;
        font-size: 0.98rem !important;
        color: #CBD5E1 !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        background: #121624 !important;
        cursor: pointer !important;
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        box-sizing: border-box !important;
        position: relative !important;
        overflow: hidden !important;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label > div,
    section[data-testid="stSidebar"] div[role="radiogroup"] [data-testid="stRadioOption"] > div {
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        width: 100% !important;
        height: 100% !important;
        background: transparent !important;
    }

    /* Completely hide all radio circle indicators, dots and bullets */
    section[data-testid="stSidebar"] div[role="radiogroup"] [class*="e1dm8mpf4"],
    section[data-testid="stSidebar"] div[role="radiogroup"] [class*="e1dm8mpf5"],
    section[data-testid="stSidebar"] div[role="radiogroup"] label > div > div:first-child:not([data-testid="stMarkdownContainer"]):not(:has([data-testid="stMarkdownContainer"])),
    section[data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child,
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label > div:first-child,
    section[data-testid="stSidebar"] div[data-baseweb="radio"] > div:first-child,
    section[data-testid="stSidebar"] div[role="radiogroup"] label div[data-testid="stRadioCircle"],
    section[data-testid="stSidebar"] div[role="radiogroup"] label input[type="radio"],
    section[data-testid="stSidebar"] div[role="radiogroup"] input[type="radio"] {
        display: none !important;
        width: 0 !important;
        height: 0 !important;
        min-width: 0 !important;
        min-height: 0 !important;
        visibility: hidden !important;
        opacity: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
        border: none !important;
    }

    /* Lucide Outline Icons via SVG data URIs (Consistent 22px size) */
    section[data-testid="stSidebar"] div[role="radiogroup"] label::before {
        content: "" !important;
        display: inline-block !important;
        width: 22px !important;
        height: 22px !important;
        min-width: 22px !important;
        max-width: 22px !important;
        margin-right: 0.75rem !important;
        background-repeat: no-repeat !important;
        background-position: center !important;
        background-size: contain !important;
        flex-shrink: 0 !important;
        transition: opacity 0.2s ease !important;
        opacity: 0.85 !important;
        align-self: center !important;
    }

    /* 1. Dashboard: Lucide layout-dashboard */
    section[data-testid="stSidebar"] div[role="radiogroup"] > div:nth-of-type(1) label::before,
    section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input[value="0"])::before,
    section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input[value*="Dashboard"])::before,
    section[data-testid="stSidebar"] div[role="radiogroup"] > label:nth-of-type(1)::before {
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='22' height='22' viewBox='0 0 24 24' fill='none' stroke='%2394A3B8' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Crect width='7' height='9' x='3' y='3' rx='1'/%3E%3Crect width='7' height='5' x='14' y='3' rx='1'/%3E%3Crect width='7' height='9' x='14' y='12' rx='1'/%3E%3Crect width='7' height='5' x='3' y='16' rx='1'/%3E%3C/svg%3E") !important;
    }

    /* 2. Profile: Lucide user-round */
    section[data-testid="stSidebar"] div[role="radiogroup"] > div:nth-of-type(2) label::before,
    section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input[value="1"])::before,
    section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input[value*="Profile"])::before,
    section[data-testid="stSidebar"] div[role="radiogroup"] > label:nth-of-type(2)::before {
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='22' height='22' viewBox='0 0 24 24' fill='none' stroke='%2394A3B8' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='12' cy='8' r='5'/%3E%3Cpath d='M20 21a8 8 0 0 0-16 0'/%3E%3C/svg%3E") !important;
    }

    /* 3. Skills & Goals: Lucide target */
    section[data-testid="stSidebar"] div[role="radiogroup"] > div:nth-of-type(3) label::before,
    section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input[value="2"])::before,
    section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input[value*="Skills"])::before,
    section[data-testid="stSidebar"] div[role="radiogroup"] > label:nth-of-type(3)::before {
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='22' height='22' viewBox='0 0 24 24' fill='none' stroke='%2394A3B8' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='12' cy='12' r='10'/%3E%3Ccircle cx='12' cy='12' r='6'/%3E%3Ccircle cx='12' cy='12' r='2'/%3E%3C/svg%3E") !important;
    }

    /* 4. Resume Builder: Lucide file-user */
    section[data-testid="stSidebar"] div[role="radiogroup"] > div:nth-of-type(4) label::before,
    section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input[value="3"])::before,
    section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input[value*="Resume"])::before,
    section[data-testid="stSidebar"] div[role="radiogroup"] > label:nth-of-type(4)::before {
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='22' height='22' viewBox='0 0 24 24' fill='none' stroke='%2394A3B8' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M14 2v4a2 2 0 0 0 2 2h4'/%3E%3Cpath d='M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7z'/%3E%3Ccircle cx='12' cy='13' r='2'/%3E%3Cpath d='M15 18a3 3 0 0 0-6 0'/%3E%3C/svg%3E") !important;
    }

    /* 5. Career Development: Lucide trending-up */
    section[data-testid="stSidebar"] div[role="radiogroup"] > div:nth-of-type(5) label::before,
    section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input[value="4"])::before,
    section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input[value*="Career"])::before,
    section[data-testid="stSidebar"] div[role="radiogroup"] > label:nth-of-type(5)::before {
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='22' height='22' viewBox='0 0 24 24' fill='none' stroke='%2394A3B8' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='22 7 13.5 15.5 8.5 10.5 2 17'/%3E%3Cpolyline points='16 7 22 7 22 13'/%3E%3C/svg%3E") !important;
    }

    /* Active and Hover Icons switch stroke to #00D2FF */
    section[data-testid="stSidebar"] div[role="radiogroup"] label:hover::before,
    section[data-testid="stSidebar"] div[role="radiogroup"] [data-selected="true"] label::before,
    section[data-testid="stSidebar"] div[role="radiogroup"] label[data-selected="true"]::before,
    section[data-testid="stSidebar"] div[role="radiogroup"] label[data-checked="true"]::before,
    section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked)::before {
        opacity: 1 !important;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] > div:nth-of-type(1) label:hover::before,
    section[data-testid="stSidebar"] div[role="radiogroup"] > div:nth-of-type(1)[data-selected="true"] label::before,
    section[data-testid="stSidebar"] div[role="radiogroup"] label[data-checked="true"]:nth-of-type(1)::before,
    section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input[value="0"]:checked)::before,
    section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input[value*="Dashboard"]:checked)::before {
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='22' height='22' viewBox='0 0 24 24' fill='none' stroke='%2300D2FF' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Crect width='7' height='9' x='3' y='3' rx='1'/%3E%3Crect width='7' height='5' x='14' y='3' rx='1'/%3E%3Crect width='7' height='9' x='14' y='12' rx='1'/%3E%3Crect width='7' height='5' x='3' y='16' rx='1'/%3E%3C/svg%3E") !important;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] > div:nth-of-type(2) label:hover::before,
    section[data-testid="stSidebar"] div[role="radiogroup"] > div:nth-of-type(2)[data-selected="true"] label::before,
    section[data-testid="stSidebar"] div[role="radiogroup"] label[data-checked="true"]:nth-of-type(2)::before,
    section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input[value="1"]:checked)::before,
    section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input[value*="Profile"]:checked)::before {
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='22' height='22' viewBox='0 0 24 24' fill='none' stroke='%2300D2FF' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='12' cy='8' r='5'/%3E%3Cpath d='M20 21a8 8 0 0 0-16 0'/%3E%3C/svg%3E") !important;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] > div:nth-of-type(3) label:hover::before,
    section[data-testid="stSidebar"] div[role="radiogroup"] > div:nth-of-type(3)[data-selected="true"] label::before,
    section[data-testid="stSidebar"] div[role="radiogroup"] label[data-checked="true"]:nth-of-type(3)::before,
    section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input[value="2"]:checked)::before,
    section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input[value*="Skills"]:checked)::before {
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='22' height='22' viewBox='0 0 24 24' fill='none' stroke='%2300D2FF' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='12' cy='12' r='10'/%3E%3Ccircle cx='12' cy='12' r='6'/%3E%3Ccircle cx='12' cy='12' r='2'/%3E%3C/svg%3E") !important;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] > div:nth-of-type(4) label:hover::before,
    section[data-testid="stSidebar"] div[role="radiogroup"] > div:nth-of-type(4)[data-selected="true"] label::before,
    section[data-testid="stSidebar"] div[role="radiogroup"] label[data-checked="true"]:nth-of-type(4)::before,
    section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input[value="3"]:checked)::before,
    section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input[value*="Resume"]:checked)::before {
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='22' height='22' viewBox='0 0 24 24' fill='none' stroke='%2300D2FF' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M14 2v4a2 2 0 0 0 2 2h4'/%3E%3Cpath d='M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7z'/%3E%3Ccircle cx='12' cy='13' r='2'/%3E%3Cpath d='M15 18a3 3 0 0 0-6 0'/%3E%3C/svg%3E") !important;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] > div:nth-of-type(5) label:hover::before,
    section[data-testid="stSidebar"] div[role="radiogroup"] > div:nth-of-type(5)[data-selected="true"] label::before,
    section[data-testid="stSidebar"] div[role="radiogroup"] label[data-checked="true"]:nth-of-type(5)::before,
    section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input[value="4"]:checked)::before,
    section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input[value*="Career"]:checked)::before {
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='22' height='22' viewBox='0 0 24 24' fill='none' stroke='%2300D2FF' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='22 7 13.5 15.5 8.5 10.5 2 17'/%3E%3Cpolyline points='16 7 22 7 22 13'/%3E%3C/svg%3E") !important;
    }

    /* Completely remove decorative arrows and chevrons inside navigation buttons */
    section[data-testid="stSidebar"] div[role="radiogroup"] label::after {
        display: none !important;
        content: none !important;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label p,
    section[data-testid="stSidebar"] div[role="radiogroup"] label span,
    section[data-testid="stSidebar"] div[role="radiogroup"] label [data-testid="stMarkdownContainer"] p {
        color: #CBD5E1 !important;
        font-size: 1.05rem !important;
        font-weight: 600 !important;
        letter-spacing: -0.01em !important;
        line-height: 1 !important;
        margin: 0 !important;
        padding: 0 !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        display: flex !important;
        align-items: center !important;
        transition: color 0.2s ease !important;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
        background: #161A29 !important;
        border-color: rgba(0, 210, 255, 0.3) !important;
        transform: translateX(2px) !important;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label:hover p,
    section[data-testid="stSidebar"] div[role="radiogroup"] label:hover span {
        color: #FFFFFF !important;
    }

    /* Active Nav Item with Subtle Teal Highlight & Slim Cyan Left Border */
    section[data-testid="stSidebar"] div[role="radiogroup"] div[data-selected="true"] label,
    section[data-testid="stSidebar"] div[role="radiogroup"] label[data-selected="true"],
    section[data-testid="stSidebar"] div[role="radiogroup"] label[data-checked="true"],
    section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
        background: linear-gradient(90deg, rgba(0, 210, 255, 0.18) 0%, rgba(13, 122, 130, 0.12) 100%) !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        border: 1px solid rgba(0, 210, 255, 0.35) !important;
        border-left: 3.5px solid #00D2FF !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.35), inset 0 1px 0 rgba(255, 255, 255, 0.08) !important;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label[data-selected="true"] p,
    section[data-testid="stSidebar"] div[role="radiogroup"] label[data-checked="true"] p,
    section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) p,
    section[data-testid="stSidebar"] div[role="radiogroup"] label[data-selected="true"] span,
    section[data-testid="stSidebar"] div[role="radiogroup"] label[data-checked="true"] span,
    section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) span,
    section[data-testid="stSidebar"] div[role="radiogroup"] label[data-selected="true"] [data-testid="stMarkdownContainer"] p,
    section[data-testid="stSidebar"] div[role="radiogroup"] label[data-checked="true"] [data-testid="stMarkdownContainer"] p,
    section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) [data-testid="stMarkdownContainer"] p {
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }

    /* View Profile Action Button */
    section[data-testid="stSidebar"] div.stButton button[key="btn_sidebar_view_profile"],
    section[data-testid="stSidebar"] div:has(> .ts-view-profile-anchor) div.stButton button {
        background: linear-gradient(90deg, rgba(0, 210, 255, 0.15) 0%, rgba(13, 122, 130, 0.15) 100%) !important;
        border: 1px solid rgba(0, 210, 255, 0.35) !important;
        border-radius: 8px !important;
        color: #00D2FF !important;
        font-size: 0.86rem !important;
        font-weight: 700 !important;
        padding: 0.45rem 0.75rem !important;
        min-height: 38px !important;
        height: 38px !important;
        margin-bottom: 0.45rem !important;
        width: 100% !important;
        transition: all 0.2s ease !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    section[data-testid="stSidebar"] div.stButton button[key="btn_sidebar_view_profile"]:hover,
    section[data-testid="stSidebar"] div:has(> .ts-view-profile-anchor) div.stButton button:hover {
        background: rgba(0, 210, 255, 0.25) !important;
        border-color: #00D2FF !important;
        color: #FFFFFF !important;
        box-shadow: 0 0 12px rgba(0, 210, 255, 0.3) !important;
        transform: translateY(-1px) !important;
    }

    /* Modern Logout Button with Coral/Red Accent */
    section[data-testid="stSidebar"] div.stButton button[key="btn_sidebar_signout"] {
        background: rgba(255, 42, 117, 0.12) !important;
        border: 1px solid rgba(244, 63, 94, 0.45) !important;
        border-radius: 10px !important;
        color: #FDA4AF !important;
        font-size: 0.82rem !important;
        font-weight: 600 !important;
        padding: 0.45rem 0.65rem !important;
        min-height: 36px !important;
        height: 36px !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.25) !important;
    }
    section[data-testid="stSidebar"] div.stButton button[key="btn_sidebar_signout"]:hover {
        background: rgba(244, 63, 94, 0.22) !important;
        border-color: #F43F5E !important;
        color: #FFFFFF !important;
        box-shadow: 0 0 12px rgba(244, 63, 94, 0.3) !important;
        transform: translateY(-1px) !important;
    }

    /* Reset Data Button (Neutral Charcoal with Cyan Hover) */
    section[data-testid="stSidebar"] div.stButton button[key="btn_sidebar_reset"] {
        background: #161A29 !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 10px !important;
        color: #CBD5E1 !important;
        font-size: 0.82rem !important;
        font-weight: 600 !important;
        padding: 0.45rem 0.65rem !important;
        min-height: 36px !important;
        height: 36px !important;
        transition: all 0.2s ease !important;
    }
    section[data-testid="stSidebar"] div.stButton button[key="btn_sidebar_reset"]:hover {
        border-color: #00D2FF !important;
        color: #00D2FF !important;
        background: rgba(0, 210, 255, 0.10) !important;
    }

    /* Sidebar Popover (Account Settings - Clean, No Overlapping Text, and Lucide Settings Icon) */
    section[data-testid="stSidebar"] div[data-testid="stPopover"] {
        margin-bottom: 0.65rem !important;
        width: 100% !important;
    }

    section[data-testid="stSidebar"] div[data-testid="stPopover"] > button {
        background: #161A29 !important;
        border: 1px solid rgba(0, 210, 255, 0.22) !important;
        color: #CBD5E1 !important;
        border-radius: 8px !important;
        font-size: 0.84rem !important;
        font-weight: 600 !important;
        padding: 0.45rem 0.85rem !important;
        min-height: 38px !important;
        height: 38px !important;
        transition: all 0.2s ease !important;
        display: flex !important;
        align-items: center !important;
        justify-content: flex-start !important;
        gap: 0.5rem !important;
        width: 100% !important;
        box-sizing: border-box !important;
    }

    section[data-testid="stSidebar"] div[data-testid="stPopover"] > button::before {
        content: "" !important;
        display: inline-block !important;
        width: 18px !important;
        height: 18px !important;
        min-width: 18px !important;
        background-repeat: no-repeat !important;
        background-position: center !important;
        background-size: contain !important;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 24 24' fill='none' stroke='%2300D2FF' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z'/%3E%3Ccircle cx='12' cy='12' r='3'/%3E%3C/svg%3E") !important;
        flex-shrink: 0 !important;
    }

    section[data-testid="stSidebar"] div[data-testid="stPopover"] > button [data-testid="stMarkdownContainer"] {
        flex: 1 !important;
        text-align: left !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }

    section[data-testid="stSidebar"] div[data-testid="stPopover"] > button svg,
    section[data-testid="stSidebar"] div[data-testid="stPopover"] > button [data-testid="stIconMaterial"],
    section[data-testid="stSidebar"] div[data-testid="stPopover"] > button span[class*="material"] {
        margin-left: auto !important;
        flex-shrink: 0 !important;
        width: 18px !important;
        height: 18px !important;
        color: #00D2FF !important;
    }

    section[data-testid="stSidebar"] div[data-testid="stPopover"] > button:hover {
        border-color: #00D2FF !important;
        color: #FFFFFF !important;
        box-shadow: 0 0 10px rgba(0, 210, 255, 0.25) !important;
    }

    /* Mobile Responsive Drawer Safeguards */
    @media (max-width: 768px) {
        section[data-testid="stSidebar"] {
            box-shadow: 0 0 32px rgba(0, 0, 0, 0.85) !important;
            max-width: 85vw !important;
        }
    }

    /* 3. Elevated Cards & Containers */
    div[data-testid="stVerticalBlockBorderWrapper"],
    .ts-card,
    .ts-lms-card-wrapper {
        background: #161A29 !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important;
        box-shadow: 0 12px 32px -4px rgba(0, 0, 0, 0.6), inset 0 1px 0 0 rgba(255, 255, 255, 0.08) !important;
        color: #FFFFFF !important;
    }

    /* Hover elevation for cards */
    .ts-card:hover,
    .ts-lms-card-wrapper:hover {
        border-color: rgba(0, 210, 255, 0.3) !important;
        box-shadow: 0 14px 40px -4px rgba(0, 0, 0, 0.75), 0 0 16px rgba(0, 210, 255, 0.15) !important;
        transform: translateY(-2px) !important;
    }

    /* 4. Top Navigation Bar (Reference Design Center Nav) */
    .ts-top-nav-bar {
        background: #161A29 !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important;
        padding: 0.75rem 1.4rem !important;
        margin-bottom: 1.25rem !important;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.45), inset 0 1px 0 rgba(255, 255, 255, 0.08) !important;
    }

    .ts-nav-link-active {
        color: #00D2FF !important;
        font-weight: 700 !important;
        border-bottom: 2px solid #00D2FF !important;
        text-shadow: 0 0 10px rgba(0, 210, 255, 0.5) !important;
        padding-bottom: 4px !important;
    }

    /* Wide Dashboard Banner */
    .ts-lms-banner {
        background: linear-gradient(135deg, rgba(22, 26, 41, 0.95) 0%, rgba(13, 17, 29, 0.98) 100%),
                    radial-gradient(circle at 85% 20%, rgba(255, 42, 117, 0.22) 0%, transparent 55%) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important;
        padding: 2.25rem 2.5rem !important;
        box-shadow: 0 12px 36px rgba(0, 0, 0, 0.6), inset 0 1px 0 rgba(255, 255, 255, 0.1) !important;
        color: #FFFFFF !important;
    }

    .ts-lms-banner-badge {
        background: rgba(0, 210, 255, 0.15) !important;
        border: 1px solid rgba(0, 210, 255, 0.35) !important;
        color: #00D2FF !important;
        box-shadow: 0 0 12px rgba(0, 210, 255, 0.2) !important;
    }

    /* 5. Metrics & Stat Cards (Top Cards in Reference Image) */
    .ts-metric-box {
        background: #1B2032 !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important;
        padding: 1.25rem 1.4rem !important;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.07) !important;
    }

    .ts-metric-label {
        color: #CBD5E1 !important;
        font-size: 0.82rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.06em !important;
    }

    .ts-metric-value {
        color: #FFFFFF !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-size: 2rem !important;
        font-weight: 800 !important;
        letter-spacing: -0.02em !important;
    }

    .ts-metric-subtitle {
        color: #94A3B8 !important;
        font-size: 0.82rem !important;
        font-weight: 500 !important;
    }

    /* 6. Neon Badges & Pill Tags (Vibrant Cyan, Pink, Purple) */
    .ts-badge {
        display: inline-flex;
        align-items: center;
        padding: 0.22rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.76rem;
        font-weight: 700;
        letter-spacing: 0.02em;
    }

    .ts-badge-teal, .ts-badge-cyan {
        background: #00D2FF !important;
        color: #0B0E17 !important;
        box-shadow: 0 0 12px rgba(0, 210, 255, 0.45) !important;
        border: none !important;
    }

    .ts-badge-pink {
        background: rgba(255, 42, 117, 0.2) !important;
        color: #FF2A75 !important;
        border: 1px solid rgba(255, 42, 117, 0.45) !important;
        box-shadow: 0 0 12px rgba(255, 42, 117, 0.3) !important;
    }

    .ts-badge-purple {
        background: rgba(138, 43, 226, 0.2) !important;
        color: #A855F7 !important;
        border: 1px solid rgba(138, 43, 226, 0.4) !important;
        box-shadow: 0 0 12px rgba(168, 85, 247, 0.3) !important;
    }

    .ts-badge-navy {
        background: #1B2032 !important;
        color: #CBD5E1 !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
    }

    .ts-badge-success {
        background: rgba(0, 210, 255, 0.15) !important;
        color: #00D2FF !important;
        border: 1px solid rgba(0, 210, 255, 0.3) !important;
    }

    .ts-badge-warning {
        background: rgba(255, 107, 11, 0.2) !important;
        color: #FF6B0B !important;
        border: 1px solid rgba(255, 107, 11, 0.4) !important;
    }

    .ts-badge-info {
        background: rgba(0, 114, 255, 0.2) !important;
        color: #00D2FF !important;
        border: 1px solid rgba(0, 114, 255, 0.4) !important;
    }

    .ts-lms-tag {
        display: inline-block;
        padding: 0.25rem 0.65rem;
        border-radius: 8px;
        font-size: 0.78rem;
        font-weight: 700;
        background: #1B2032 !important;
        color: #00D2FF !important;
        border: 1px solid rgba(0, 210, 255, 0.25) !important;
        margin-right: 0.4rem;
        margin-bottom: 0.35rem;
    }

    /* Code Elements & Markdown Preformatted Tags in Dark Theme (Never render as white popovers) */
    pre, code, kbd, samp,
    div[data-testid="stCodeBlock"],
    .stCodeBlock,
    div.stCode {
        background: #121624 !important;
        background-color: #121624 !important;
        color: #00D2FF !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 12px !important;
        box-shadow: none !important;
    }

    /* Popovers, Tooltips & Floating Containers in Dark Theme */
    div[data-testid="stPopoverBody"],
    div[data-testid="stTooltipContent"],
    div[data-baseweb="popover"],
    div[data-baseweb="tooltip"] {
        background: #1B2032 !important;
        background-color: #1B2032 !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 14px !important;
        box-shadow: 0 12px 32px rgba(0, 0, 0, 0.7) !important;
    }

    /* 7. Action Buttons (Clean Pink-to-Magenta Gradient Background #FF2A75, White Text, Rounded Corners, Glow) */
    div.stButton > button,
    div[data-testid="stButton"] button,
    div.stButton > button[kind="primary"],
    div.stButton > button[data-testid="stBaseButton-primary"],
    div[data-testid="stButton"] button[kind="primary"],
    button[data-testid="stBaseButton-primary"],
    div.stButton > button[kind="secondary"],
    div.stButton > button[data-testid="stBaseButton-secondary"],
    div[data-testid="stButton"] button[kind="secondary"] {
        border-radius: 12px !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 700 !important;
        transition: all 0.2s ease-in-out !important;
    }

    div.stButton > button[kind="primary"],
    div.stButton > button[data-testid="stBaseButton-primary"],
    div[data-testid="stButton"] button[kind="primary"],
    div[data-testid="stButton"] button[data-testid="stBaseButton-primary"],
    button[data-testid="stBaseButton-primary"] {
        background: linear-gradient(135deg, #FF2A75 0%, #FF5252 100%) !important;
        background-color: #FF2A75 !important;
        color: #FFFFFF !important;
        border: none !important;
        font-size: 0.92rem !important;
        padding: 0.6rem 1.4rem !important;
        box-shadow: 0 4px 18px rgba(255, 42, 117, 0.45) !important;
    }

    div.stButton > button[kind="primary"]:hover,
    div[data-testid="stButton"] button[kind="primary"]:hover,
    button[data-testid="stBaseButton-primary"]:hover {
        background: linear-gradient(135deg, #FF5252 0%, #FF2A75 100%) !important;
        box-shadow: 0 6px 26px rgba(255, 42, 117, 0.65) !important;
        transform: translateY(-2px) !important;
    }

    div.stButton > button[kind="secondary"],
    div.stButton > button[data-testid="stBaseButton-secondary"],
    div[data-testid="stButton"] button[kind="secondary"],
    div[data-testid="stButton"] button[data-testid="stBaseButton-secondary"] {
        background: #1B2032 !important;
        background-color: #1B2032 !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        font-size: 0.88rem !important;
        padding: 0.55rem 1.25rem !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
    }

    div.stButton > button[kind="secondary"]:hover,
    div[data-testid="stButton"] button[kind="secondary"]:hover {
        border-color: #00D2FF !important;
        color: #00D2FF !important;
        box-shadow: 0 0 14px rgba(0, 210, 255, 0.3) !important;
        transform: translateY(-1px) !important;
    }

    /* 8. Progress Bars (Neon Cyan-to-Purple Glow Fills) */
    .ts-prog-track {
        height: 9px !important;
        background-color: #121624 !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        border-radius: 9999px !important;
        overflow: hidden !important;
    }

    .ts-prog-fill {
        height: 100% !important;
        border-radius: 9999px !important;
        background: linear-gradient(90deg, #00D2FF 0%, #0072FF 50%, #8A2BE2 100%) !important;
        box-shadow: 0 0 10px rgba(0, 210, 255, 0.45) !important;
    }

    .ts-prog-labels {
        color: #FFFFFF !important;
        font-size: 0.85rem !important;
        font-weight: 600 !important;
    }

    /* Streamlit Native Progress Bar */
    div[data-testid="stProgress"] > div > div > div > div {
        background: linear-gradient(90deg, #00D2FF 0%, #8A2BE2 100%) !important;
        box-shadow: 0 0 12px rgba(0, 210, 255, 0.4) !important;
    }

    div[data-testid="stProgress"] > div > div {
        background-color: #121624 !important;
    }

    /* Form Labels, Questions & Field Labels (Bright High-Contrast White & Light Gray) */
    div[data-testid="stWidgetLabel"],
    label[data-testid="stWidgetLabel"],
    div[data-testid="stWidgetLabel"] label,
    div[data-testid="stWidgetLabel"] p,
    div[data-testid="stWidgetLabel"] span,
    div[data-testid="stWidgetLabel"] div,
    .stTextInput label,
    .stTextInput label p,
    .stTextArea label,
    .stTextArea label p,
    .stSelectbox label,
    .stSelectbox label p,
    .stNumberInput label,
    .stNumberInput label p,
    .stDateInput label,
    .stDateInput label p,
    .stSlider label,
    .stSlider label p,
    .stRadio label,
    .stRadio label p,
    .stCheckbox label,
    .stCheckbox label p,
    .stFileUploader label,
    .stFileUploader label p,
    .stMultiSelect label,
    .stMultiSelect label p,
    form label,
    form label p,
    div[data-testid="stForm"] label,
    div[data-testid="stForm"] label p {
        color: #FFFFFF !important;
        font-weight: 600 !important;
        font-size: 0.94rem !important;
        opacity: 1 !important;
        letter-spacing: 0.01em !important;
    }

    /* Paragraphs and Descriptions in Containers */
    div[data-testid="stMarkdownContainer"] p {
        color: #E2E8F0 !important;
    }

    div[data-testid="stCaptionContainer"],
    div[data-testid="stCaptionContainer"] p,
    small,
    .stCaption {
        color: #CBD5E1 !important;
    }

    /* Slider questions, tick marks & values */
    div[data-testid="stSlider"] label,
    div[data-testid="stSlider"] label p {
        color: #FFFFFF !important;
        font-size: 0.94rem !important;
        font-weight: 600 !important;
    }

    div[data-testid="stSlider"] div[data-testid="stTickBarMin"],
    div[data-testid="stSlider"] div[data-testid="stTickBarMax"],
    div[data-testid="stSlider"] div[data-testid="stThumbValue"] {
        color: #E2E8F0 !important;
        font-weight: 600 !important;
    }

    /* 9. Tabs (Clearly Visible Inactive & Glowing Cyan Active Indicator) */
    div[data-testid="stTabs"] button[role="tab"],
    button[data-baseweb="tab"] {
        color: #E2E8F0 !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        padding: 0.65rem 1.1rem !important;
        border-bottom: 2px solid transparent !important;
        background: transparent !important;
        opacity: 0.9 !important;
    }

    div[data-testid="stTabs"] button[role="tab"] p,
    div[data-testid="stTabs"] button[role="tab"] span,
    div[data-testid="stTabs"] button[role="tab"] div,
    button[data-baseweb="tab"] p,
    button[data-baseweb="tab"] span,
    button[data-baseweb="tab"] div {
        color: #E2E8F0 !important;
        font-weight: 600 !important;
    }

    div[data-testid="stTabs"] button[role="tab"]:hover,
    div[data-testid="stTabs"] button[role="tab"]:hover p,
    button[data-baseweb="tab"]:hover,
    button[data-baseweb="tab"]:hover p {
        color: #FFFFFF !important;
        opacity: 1 !important;
    }

    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"],
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #00D2FF !important;
        border-bottom: 2px solid #00D2FF !important;
        text-shadow: 0 0 10px rgba(0, 210, 255, 0.5) !important;
        font-weight: 700 !important;
        opacity: 1 !important;
    }

    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] p,
    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] span,
    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] div,
    button[data-baseweb="tab"][aria-selected="true"] p,
    button[data-baseweb="tab"][aria-selected="true"] span,
    button[data-baseweb="tab"][aria-selected="true"] div {
        color: #00D2FF !important;
        font-weight: 700 !important;
        text-shadow: 0 0 10px rgba(0, 210, 255, 0.5) !important;
    }

    /* 10. Form Inputs, Selectboxes, Textareas: Dark Text on Clean White Background */
    div[data-baseweb="input"],
    div[data-baseweb="input"] > div,
    div[data-baseweb="input"] input,
    div[data-baseweb="textarea"],
    div[data-baseweb="textarea"] textarea,
    div[data-testid="stTextInput"] input,
    div[data-testid="stTextArea"] textarea,
    div[data-testid="stNumberInput"] input,
    div[data-testid="stDateInput"] input {
        background-color: #FFFFFF !important;
        background: #FFFFFF !important;
        color: #0F172A !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 8px !important;
        font-size: 0.92rem !important;
        font-weight: 500 !important;
    }

    div[data-baseweb="input"] input::placeholder,
    div[data-baseweb="textarea"] textarea::placeholder,
    input::placeholder,
    textarea::placeholder {
        color: #64748B !important;
        opacity: 1 !important;
    }

    div[data-baseweb="input"]:focus-within,
    div[data-baseweb="input"] input:focus,
    div[data-baseweb="textarea"]:focus-within,
    div[data-baseweb="textarea"] textarea:focus,
    div[data-baseweb="select"]:focus-within {
        border-color: #00D2FF !important;
        box-shadow: 0 0 0 2px rgba(0, 210, 255, 0.45) !important;
        outline: none !important;
    }

    /* Selectboxes: Clean White Background with Dark Text */
    div[data-baseweb="select"],
    div[data-baseweb="select"] > div,
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div,
    div[data-baseweb="select"] div[role="combobox"] {
        background-color: #FFFFFF !important;
        background: #FFFFFF !important;
        color: #0F172A !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 8px !important;
    }

    div[data-baseweb="select"] *,
    div[data-testid="stSelectbox"] div[data-baseweb="select"] * {
        color: #0F172A !important;
    }

    div[data-baseweb="select"] svg {
        fill: #475569 !important;
    }

    /* Selectbox Dropdown Options */
    div[data-baseweb="popover"] div[role="listbox"],
    div[data-baseweb="menu"],
    ul[role="listbox"] {
        background-color: #FFFFFF !important;
        background: #FFFFFF !important;
        color: #0F172A !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 8px !important;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3) !important;
    }

    li[role="option"] {
        color: #0F172A !important;
        background: #FFFFFF !important;
    }

    li[role="option"]:hover,
    li[role="option"][aria-selected="true"] {
        background-color: #F1F5F9 !important;
        color: #0072FF !important;
        font-weight: 600 !important;
    }

    div[data-testid="stNumberInput"] button {
        background-color: #F1F5F9 !important;
        color: #0F172A !important;
        border: 1px solid #CBD5E1 !important;
    }

    div[data-testid="stNumberInput"] button:hover {
        background-color: #E2E8F0 !important;
        color: #0072FF !important;
    }

    /* Slider Handle with Glow */
    div[data-baseweb="slider"] div[role="slider"] {
        background-color: #00D2FF !important;
        box-shadow: 0 0 12px rgba(0, 210, 255, 0.6) !important;
        border: 2px solid #FFFFFF !important;
    }

    /* 11. Circular/Radial Gauge Visual Component (from Reference Design) */
    .ts-radial-card {
        background: #161A29;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 1.25rem 1rem;
        text-align: center;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
        position: relative;
    }

    .ts-radial-title {
        font-size: 0.82rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #CBD5E1;
        margin-top: 0.6rem;
    }

    .ts-radial-sub {
        font-size: 0.74rem;
        color: #94A3B8;
        margin-top: 0.2rem;
    }

    /* 12. Toggle Panel Card (Reference Design Center Widget) */
    .ts-toggle-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.75rem 0.2rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    }

    .ts-toggle-row:last-child {
        border-bottom: none;
    }

    .ts-toggle-label {
        font-size: 0.86rem;
        font-weight: 600;
        color: #FFFFFF;
    }

    .ts-toggle-desc {
        font-size: 0.74rem;
        color: #CBD5E1;
    }

    .ts-toggle-switch-active {
        width: 36px;
        height: 20px;
        background: #00D2FF;
        border-radius: 9999px;
        position: relative;
        box-shadow: 0 0 10px rgba(0, 210, 255, 0.5);
    }

    .ts-toggle-switch-active::after {
        content: '';
        position: absolute;
        top: 2px;
        right: 2px;
        width: 16px;
        height: 16px;
        background: #0B0E17;
        border-radius: 50%;
    }

    /* Radio Filter Pills */
    div[data-testid="stRadio"] > div {
        background: #121624 !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 12px !important;
        padding: 4px !important;
    }

    div[data-testid="stRadio"] label {
        color: #CBD5E1 !important;
        font-weight: 600 !important;
        padding: 0.35rem 0.85rem !important;
        border-radius: 8px !important;
    }

    div[data-testid="stRadio"] label[data-checked="true"] {
        background: #1B2032 !important;
        color: #00D2FF !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.4) !important;
    }

    /* Demo / Alert Banner */
    .ts-demo-banner {
        background: #161A29 !important;
        border-left: 3px solid #00D2FF !important;
        border-radius: 12px !important;
        padding: 0.95rem 1.25rem !important;
        margin-bottom: 1.5rem !important;
        color: #FFFFFF !important;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4) !important;
        border-top: 1px solid rgba(255, 255, 255, 0.06) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.06) !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.06) !important;
    }

    /* Avatar Glow */
    /* Toast Notifications & Popups (High Contrast Dark Theme) */
    div[data-testid="stToastContainer"] {
        position: fixed !important;
        top: 1.5rem !important;
        right: 1.5rem !important;
        z-index: 999999 !important;
        display: flex !important;
        flex-direction: column !important;
        gap: 0.75rem !important;
        max-width: 440px !important;
    }

    div[data-testid="stToast"],
    div.stToast {
        background-color: #252530 !important;
        color: #FFFFFF !important;
        border: 1px solid #454553 !important;
        border-radius: 10px !important;
        box-shadow: 0 10px 28px rgba(0, 0, 0, 0.65), 0 2px 8px rgba(0, 0, 0, 0.4) !important;
        padding: 0.85rem 1.15rem !important;
        min-width: 300px !important;
        max-width: 440px !important;
        word-wrap: break-word !important;
        overflow-wrap: break-word !important;
    }

    div[data-testid="stToast"] p,
    div[data-testid="stToastText"],
    div[data-testid="stToastText"] p,
    div.stToast p {
        color: #FFFFFF !important;
        font-size: 0.92rem !important;
        font-weight: 600 !important;
        line-height: 1.45 !important;
        margin: 0 !important;
        word-break: break-word !important;
        white-space: normal !important;
    }

    div[data-testid="stToast"] span,
    div[data-testid="stToast"] small {
        color: #D1D1DC !important;
    }

    div[data-testid="stToastDynamicIcon"],
    div[data-testid="stToast"] svg {
        color: #60A5FA !important;
        fill: #60A5FA !important;
        flex-shrink: 0 !important;
    }

    div[data-testid="stToast"] button,
    div.stToast button {
        color: #D1D1DC !important;
        background: transparent !important;
        border: none !important;
        padding: 2px !important;
        min-height: auto !important;
        height: auto !important;
        box-shadow: none !important;
        opacity: 0.85 !important;
        cursor: pointer !important;
    }
    div[data-testid="stToast"] button:hover,
    div.stToast button:hover {
        color: #FFFFFF !important;
        opacity: 1 !important;
        background: rgba(255, 255, 255, 0.12) !important;
    }
    </style>
    """


