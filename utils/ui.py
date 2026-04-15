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

        /* ── Hide Streamlit chrome ── */
        #MainMenu, footer, header { visibility: hidden; }
        .block-container { padding-top: 1.5rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def show_logo(width: int = 220, tagline: bool = False):
    """Display the ReNOVA wordmark."""
    st.markdown(
        '<h1 style="font-family:\'Playfair Display\',serif;color:#FFFFFF;margin:0;font-size:3rem;">'
        'Re<span style="color:#006D77;">NOVA</span></h1>',
        unsafe_allow_html=True,
    )
    if tagline:
        st.markdown(
            '<p class="login-tagline">Give it a NOVA life.</p>',
            unsafe_allow_html=True,
        )


def show_page_header():
    """Compact logo + tagline for top of logged-in pages."""
    col_logo, col_tag = st.columns([1, 3])
    with col_logo:
        st.markdown(
            '<h2 style="font-family:\'Playfair Display\',serif;color:#FFFFFF;margin:0;">'
            'Re<span style="color:#006D77;">NOVA</span></h2>',
            unsafe_allow_html=True,
        )
    with col_tag:
        st.markdown(
            '<p class="renova-tagline" style="padding-top:1rem;">Give it a NOVA life.</p>',
            unsafe_allow_html=True,
        )
    st.divider()


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
        st.markdown(f"**{user['name'].split()[0]}** 👋")
        st.caption(f"{user['email']}")
        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
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
    icon   = CATEGORY_ICONS.get(listing.get("category", "Other"), "📦")
    status = listing.get("status", "available")
    status_label, badge_bg, badge_fg = STATUS_BADGE.get(status, STATUS_BADGE["available"])

    with st.container(border=True):
        # Image or placeholder
        img_rel  = listing.get("image_path")
        img_path = BASE_DIR / img_rel if img_rel else None
        if img_path and img_path.exists():
            st.image(str(img_path), use_container_width=True)
        else:
            st.markdown(
                f'<div class="card-img-placeholder">{icon}</div>',
                unsafe_allow_html=True,
            )

        # Title
        st.markdown(f"**{listing['title']}**")

        # Price
        if listing.get("price_type") == "offer":
            st.markdown("💬 **Make an Offer**")
        else:
            st.markdown(f"**€{float(listing.get('price', 0)):.2f}**")

        # Badges
        cond = listing.get("condition", "")
        cat  = listing.get("category", "")
        st.markdown(
            f'<span class="badge badge-{status_label}">{status_label.title()}</span>'
            f'<span class="badge badge-cat">{icon} {cat}</span>'
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
                f'💬 Contact on WhatsApp</a>',
                unsafe_allow_html=True,
            )
