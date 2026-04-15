import streamlit as st
from pathlib import Path
import urllib.parse
import os

# Resolve BASE_DIR robustly on Windows/OneDrive paths
_THIS_FILE = os.path.abspath(__file__)          # .../utils/ui.py
_UTILS_DIR = os.path.dirname(_THIS_FILE)        # .../utils/
BASE_DIR   = Path(os.path.dirname(_UTILS_DIR))  # .../ReNOVA/
LOGO_PATH  = BASE_DIR / "images" / "logo.png"


def _logo_bytes() -> bytes | None:
    """Read logo bytes at render-time, trying multiple path strategies."""
    candidates = [
        BASE_DIR / "images" / "logo.png",
        Path(os.getcwd()) / "images" / "logo.png",
        Path("images/logo.png"),
    ]
    for p in candidates:
        try:
            return p.read_bytes()
        except Exception:
            continue
    return None

CATEGORIES = ["Books", "Electronics", "Clothing", "Services", "Other"]
CONDITIONS = ["New", "Like New", "Good", "Fair", "Poor"]

CATEGORY_ICONS = {
    "Books": "📚",
    "Electronics": "💻",
    "Clothing": "👕",
    "Services": "🔧",
    "Other": "📦",
}

STATUS_BADGE = {
    "available": ("available", "#006D77", "#FFFFFF"),
    "reserved":  ("reserved",  "#92400e", "#FEF3C7"),
    "sold":      ("sold",      "#3A0000", "#FCA5A5"),
}


def inject_css():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Inter:wght@300;400;500;600&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif !important;
        }

        /* ── Logo + tagline ── */
        .renova-logo-wrap {
            display: flex;
            align-items: center;
            gap: 1.5rem;
            padding: 1.5rem 0 1rem;
        }
        .renova-tagline {
            font-family: 'Playfair Display', serif;
            font-size: 1.15rem;
            color: #83C5BE;
            letter-spacing: 0.01em;
            margin: 0;
        }

        /* ── Login page ── */
        .login-wrap {
            text-align: center;
            padding: 2rem 0 1rem;
        }
        .login-tagline {
            font-family: 'Playfair Display', serif;
            font-size: 1.3rem;
            color: #83C5BE;
            margin: 0.5rem 0 2rem;
        }

        /* ── Listing card image placeholder ── */
        .card-img-placeholder {
            width: 100%;
            height: 170px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 3.5rem;
            background: linear-gradient(135deg, #1A1A1A, #222222);
            border-radius: 8px 8px 0 0;
        }

        /* ── Badges ── */
        .badge {
            display: inline-block;
            padding: 3px 10px;
            border-radius: 999px;
            font-size: 0.71rem;
            font-weight: 500;
            margin-right: 4px;
        }
        .badge-available { background: #003D3F; color: #83C5BE; }
        .badge-reserved  { background: #3A2A00; color: #FDE68A; }
        .badge-sold      { background: #3A0000; color: #FCA5A5; }
        .badge-cat       { background: #1A2A2A; color: #83C5BE; }
        .badge-cond      { background: #1E1E1E; color: #9CA3AF; }

        /* ── Card meta text ── */
        .card-meta {
            font-size: 0.78rem;
            color: #6B7280;
            margin-top: 4px;
        }

        /* ── WhatsApp button ── */
        .wa-btn {
            display: block;
            background: #25D366;
            color: #FFFFFF !important;
            text-decoration: none !important;
            text-align: center;
            padding: 7px 0;
            border-radius: 8px;
            font-size: 0.85rem;
            font-weight: 600;
            margin-top: 8px;
            transition: background 0.2s;
        }
        .wa-btn:hover { background: #1ebe5d; }

        /* ── Divider ── */
        hr { border-color: #2A2A2A !important; }

        /* ── Tabs ── */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0;
            border-bottom: none !important;
            background: transparent !important;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 8px 20px 8px 0;
            background: transparent !important;
            border: none !important;
            color: #4B5563;
            font-size: 0.95rem;
        }
        .stTabs [aria-selected="true"] {
            color: #006D77 !important;
        }
        .stTabs [data-baseweb="tab-highlight"],
        .stTabs [data-baseweb="tab-border"] {
            display: none !important;
        }

        /* ── Fixed image height in cards ── */
        [data-testid="stImage"] img {
            height: 180px !important;
            width: 100% !important;
            object-fit: cover !important;
            border-radius: 6px;
        }

        /* ── Buttons ── */
        .stButton > button {
            border-radius: 8px;
            font-weight: 500;
        }
        .stButton > button[kind="primary"] {
            border-radius: 999px !important;
        }

        /* ── Hide Streamlit chrome ── */
        #MainMenu, footer, header { visibility: hidden; }
        .block-container { padding-top: 1.5rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def show_logo(width: int = 220, tagline: bool = False, description: bool = False):
    """Display the ReNOVA wordmark."""
    st.markdown(
        '<h1 style="'
        'font-family:\'Playfair Display\',serif;'
        'color:#FFFFFF;'
        'margin:0 0 0.1rem;'
        'font-size:4.5rem;'
        'font-weight:700;'
        'letter-spacing:-0.02em;'
        'line-height:1;">'
        'Re<span style="color:#006D77;">NOVA</span>'
        '</h1>',
        unsafe_allow_html=True,
    )
    if tagline:
        st.markdown(
            '<p style="'
            'font-family:\'Playfair Display\',serif;'
            'font-style:italic;'
            'color:#83C5BE;'
            'font-size:1.15rem;'
            'margin:0.3rem 0 0;'
            'letter-spacing:0.01em;">'
            'Give it a NOVA life.'
            '</p>',
            unsafe_allow_html=True,
        )
    if description:
        st.markdown(
            '<p style="'
            'color:#4B5563;'
            'font-size:0.85rem;'
            'margin:0.6rem 0 0;'
            'letter-spacing:0.02em;">'
            'The Nova SBE community marketplace.'
            '</p>',
            unsafe_allow_html=True,
        )
    # Teal decorative line
    st.markdown(
        '<div style="'
        'width:48px;height:2px;'
        'background:#006D77;'
        'margin:1.2rem 0 1.4rem;'
        '"></div>',
        unsafe_allow_html=True,
    )


def show_page_header():
    """Compact logo + tagline stacked for top of logged-in pages."""
    st.markdown(
        '<h2 style="font-family:\'Playfair Display\',serif;color:#FFFFFF;margin:0 0 0.1rem;">'
        'Re<span style="color:#006D77;">NOVA</span></h2>'
        '<p style="font-family:\'Playfair Display\',serif;font-style:italic;'
        'color:#83C5BE;font-size:0.9rem;margin:0;">Give it a NOVA life.</p>',
        unsafe_allow_html=True,
    )


def sidebar_user():
    """Render user info + logout in the sidebar."""
    user = st.session_state.get("user")
    if not user:
        return
    with st.sidebar:
        st.markdown(
            '<h2 style="font-family:\'Playfair Display\',serif;color:#FFFFFF;margin:0;">'
            'Re<span style="color:#006D77;">NOVA</span></h2>',
            unsafe_allow_html=True,
        )
        st.divider()
        st.markdown(f"**{user['name'].split()[0]}**")
        st.caption(f"{user['email']}")
        st.write("")
        st.page_link("pages/3_My_Profile.py", label="My Profile", use_container_width=True)
        st.divider()
        if st.button("Logout", use_container_width=True):
            st.session_state.user = None
            st.rerun()


def auth_gate():
    """Stop rendering and show a login prompt if user is not authenticated."""
    if not st.session_state.get("user"):
        st.warning("You must be logged in to view this page.")
        st.page_link("app.py", label="← Go to Login / Home")
        st.stop()


def listing_card(listing: dict):
    """Render a listing card inside a bordered container."""
    cat    = listing.get("category", "Other")
    status = listing.get("status", "available")
    status_label, _, _ = STATUS_BADGE.get(status, STATUS_BADGE["available"])

    with st.container(border=True):
        # Image or placeholder
        img_rel  = listing.get("image_path")
        img_path = BASE_DIR / img_rel if img_rel else None
        if img_path and img_path.exists():
            st.image(str(img_path), use_container_width=True)
        else:
            st.markdown(
                f'<div class="card-img-placeholder">'
                f'<span style="font-size:0.85rem;color:#4B5563;letter-spacing:0.05em;">{cat.upper()}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

        # Title
        st.markdown(f"**{listing['title']}**")

        # Price
        if listing.get("price_type") == "offer":
            st.markdown("**Make an Offer**")
        else:
            st.markdown(f"**€{float(listing.get('price', 0)):.2f}**")

        # Badges
        cond = listing.get("condition", "")
        st.markdown(
            f'<span class="badge badge-{status_label}">{status_label.title()}</span>'
            f'<span class="badge badge-cat">{cat}</span>'
            f'<span class="badge badge-cond">{cond}</span>',
            unsafe_allow_html=True,
        )

        # Meta
        seller = listing.get("seller_name", "Unknown")
        date   = listing.get("created_at", "")[:10]
        st.markdown(f'<p class="card-meta">by {seller} · {date}</p>', unsafe_allow_html=True)

        # WhatsApp CTA
        wa = listing.get("whatsapp", "")
        if wa and status == "available":
            clean = "".join(c for c in wa if c.isdigit() or c == "+")
            msg   = urllib.parse.quote(f"Hi! I'm interested in your listing on ReNOVA: {listing['title']}")
            st.markdown(
                f'<a class="wa-btn" href="https://wa.me/{clean}?text={msg}" target="_blank">'
                f'Contact on WhatsApp</a>',
                unsafe_allow_html=True,
            )
