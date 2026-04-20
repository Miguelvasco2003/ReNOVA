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
    "Books":       "📚",
    "Electronics": "💻",
    "Clothing":    "👕",
    "Services":    "🔧",
    "Other":       "📦",
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
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Inter:wght@300;400;500;600;700&display=swap');

        /* ── Base ── */
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif !important;
        }

        /* ── App background ── */
        .stApp {
            background: #0C1A1A !important;
        }
        section[data-testid="stSidebar"] {
            background: #111F1F !important;
            border-right: 1px solid #1E3232 !important;
        }
        .block-container {
            padding-top: 1.8rem !important;
            padding-bottom: 2rem !important;
        }

        /* ── Hide Streamlit chrome ── */
        #MainMenu, footer, header { visibility: hidden; }

        /* ── Divider ── */
        hr { border-color: #1E3232 !important; }

        /* ── Sidebar text ── */
        section[data-testid="stSidebar"] * {
            color: #A8C8C8 !important;
        }
        section[data-testid="stSidebar"] strong {
            color: #E8F4F4 !important;
        }

        /* ── Buttons ── */
        .stButton > button {
            border-radius: 8px !important;
            font-weight: 500 !important;
            font-family: 'Inter', sans-serif !important;
            background: #162424 !important;
            border: 1px solid #1E3232 !important;
            color: #A8C8C8 !important;
            transition: all 0.15s !important;
        }
        .stButton > button:hover {
            background: #1E3232 !important;
            border-color: #2A4A4A !important;
            color: #E8F4F4 !important;
        }
        .stButton > button[kind="primary"] {
            background: #006D77 !important;
            border: none !important;
            color: #FFFFFF !important;
            border-radius: 999px !important;
            font-weight: 600 !important;
            padding: 0.45rem 1.4rem !important;
        }
        .stButton > button[kind="primary"]:hover {
            background: #00838F !important;
            box-shadow: 0 4px 14px rgba(0,109,119,0.4) !important;
            transform: translateY(-1px) !important;
        }

        /* ── Inputs ── */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea,
        .stNumberInput > div > div > input {
            background: #111F1F !important;
            border: 1px solid #1E3232 !important;
            border-radius: 8px !important;
            color: #E8F4F4 !important;
            font-family: 'Inter', sans-serif !important;
        }
        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus {
            border-color: #006D77 !important;
            box-shadow: 0 0 0 3px rgba(0,109,119,0.15) !important;
        }
        .stTextInput > div > div > input::placeholder,
        .stTextArea > div > div > textarea::placeholder {
            color: #3A5A5A !important;
        }

        /* ── Selectbox ── */
        .stSelectbox > div > div {
            background: #111F1F !important;
            border: 1px solid #1E3232 !important;
            border-radius: 8px !important;
            color: #E8F4F4 !important;
        }

        /* ── Slider ── */
        .stSlider [data-baseweb="slider"] [data-testid="stThumbValue"] {
            color: #83C5BE !important;
        }
        .stSlider [role="slider"] {
            background: #006D77 !important;
        }

        /* ── Tabs ── */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0;
            border-bottom: 1px solid #1E3232 !important;
            background: transparent !important;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 8px 20px 10px 0 !important;
            background: transparent !important;
            border: none !important;
            color: #3A5A5A !important;
            font-size: 0.9rem !important;
            font-family: 'Inter', sans-serif !important;
            font-weight: 500 !important;
            border-bottom: 2px solid transparent !important;
            margin-bottom: -1px !important;
        }
        .stTabs [aria-selected="true"] {
            color: #83C5BE !important;
            border-bottom-color: #006D77 !important;
        }
        .stTabs [data-baseweb="tab-highlight"],
        .stTabs [data-baseweb="tab-border"] { display: none !important; }

        /* ── Expander ── */
        .streamlit-expanderHeader {
            background: #111F1F !important;
            border: 1px solid #1E3232 !important;
            border-radius: 10px !important;
            color: #A8C8C8 !important;
        }
        .streamlit-expanderContent {
            background: #0F1E1E !important;
            border: 1px solid #1E3232 !important;
            border-top: none !important;
        }

        /* ── Containers / cards ── */
        [data-testid="stVerticalBlockBorderWrapper"] > div {
            background: #0F2020 !important;
            border: 1px solid #1E3232 !important;
            border-radius: 14px !important;
            transition: border-color 0.2s, transform 0.2s, box-shadow 0.2s !important;
        }
        [data-testid="stVerticalBlockBorderWrapper"] > div:hover {
            border-color: #004D55 !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 24px rgba(0,0,0,0.35) !important;
        }

        /* ── Metrics ── */
        [data-testid="stMetric"] {
            background: #0F2020 !important;
            border: 1px solid #1E3232 !important;
            border-radius: 12px !important;
            padding: 14px 16px !important;
        }
        [data-testid="stMetricValue"] {
            color: #83C5BE !important;
            font-weight: 700 !important;
        }
        [data-testid="stMetricLabel"] {
            color: #4A6A6A !important;
            font-size: 0.72rem !important;
            text-transform: uppercase !important;
            letter-spacing: 0.08em !important;
        }

        /* ── Alerts / Info ── */
        .stAlert {
            background: #0A2A1A !important;
            border: 1px solid #1A4A2A !important;
            border-radius: 10px !important;
            color: #6EE7B7 !important;
        }

        /* ── Fixed image height in cards ── */
        [data-testid="stImage"] img {
            height: 180px !important;
            width: 100% !important;
            object-fit: cover !important;
            border-radius: 8px 8px 0 0 !important;
        }

        /* ── Radio ── */
        .stRadio > div {
            background: transparent !important;
        }
        .stRadio [data-baseweb="radio"] {
            color: #A8C8C8 !important;
        }

        /* ── File uploader ── */
        [data-testid="stFileUploader"] {
            background: #111F1F !important;
            border: 2px dashed #1E3232 !important;
            border-radius: 10px !important;
        }

        /* ── Labels ── */
        label, .stTextInput label, .stSelectbox label,
        .stTextArea label, .stNumberInput label {
            color: #7A9A9A !important;
            font-size: 0.8rem !important;
            font-weight: 500 !important;
            letter-spacing: 0.03em !important;
        }

        /* ── Form submit ── */
        [data-testid="stForm"] {
            background: #0F2020 !important;
            border: 1px solid #1E3232 !important;
            border-radius: 16px !important;
            padding: 1.5rem !important;
        }

        /* ── Page link ── */
        [data-testid="stPageLink"] a {
            color: #83C5BE !important;
            font-weight: 500 !important;
        }

        /* ── Subheader / title ── */
        h1, h2, h3 {
            font-family: 'Playfair Display', serif !important;
            color: #E8F4F4 !important;
        }
        p, span, div {
            color: #A8C8C8;
        }

        /* ── Caption ── */
        .stCaption, small {
            color: #4A6A6A !important;
        }

        /* ── Card image placeholder ── */
        .card-img-placeholder {
            width: 100%;
            height: 170px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 8px;
            background: linear-gradient(135deg, #0A1818 0%, #162424 100%);
            border-radius: 8px 8px 0 0;
        }
        .card-img-placeholder .cat-emoji { font-size: 2.4rem; }
        .card-img-placeholder .cat-label {
            font-size: 0.65rem;
            letter-spacing: 0.12em;
            color: #3A5A5A;
            text-transform: uppercase;
        }

        /* ── Badges ── */
        .badge {
            display: inline-block;
            padding: 3px 10px;
            border-radius: 999px;
            font-size: 0.68rem;
            font-weight: 500;
            margin-right: 4px;
            letter-spacing: 0.02em;
        }
        .badge-available { background: #003D3F; color: #83C5BE; }
        .badge-reserved  { background: #3A2800; color: #FDE68A; }
        .badge-sold      { background: #3A0000; color: #FCA5A5; }
        .badge-cat       { background: #0F2A2A; color: #6BB8B8; }
        .badge-cond      { background: #1A2A2A; color: #4A6A6A; }

        /* ── Card meta ── */
        .card-meta {
            font-size: 0.72rem;
            color: #3A5A5A;
            margin-top: 4px;
            margin-bottom: 10px;
        }

        /* ── WhatsApp button ── */
        .wa-btn {
            display: block;
            background: #1A4A3A;
            color: #25D366 !important;
            text-decoration: none !important;
            text-align: center;
            padding: 8px 0;
            border-radius: 8px;
            font-size: 0.8rem;
            font-weight: 600;
            margin-top: 8px;
            border: 1px solid #1e5a40;
            transition: all 0.15s;
        }
        .wa-btn:hover { background: #25D366; color: #fff !important; }

        /* ── Category table ── */
        .cat-table {
            width: 100%;
            border-collapse: collapse;
            border: 1.5px solid #1E3232;
            border-radius: 12px;
            overflow: hidden;
        }
        .cat-table thead tr { background: #006D77; }
        .cat-table thead th {
            padding: 8px 14px;
            color: #fff;
            font-size: 0.68rem;
            letter-spacing: 0.12em;
            font-weight: 600;
            text-align: left;
            text-transform: uppercase;
        }
        .cat-table tbody tr { border-top: 1px solid #1E3232; }
        .cat-table tbody td { padding: 9px 14px; }
        .cat-table .cat-name {
            color: #4A6A6A;
            font-size: 0.72rem;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }
        .cat-table .cat-count {
            color: #83C5BE;
            font-weight: 700;
            font-size: 0.85rem;
            text-align: right;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def show_logo(width: int = 220, tagline: bool = False, description: bool = False):
    """Display the ReNOVA wordmark."""
    st.markdown(
        '<h1 style="'
        "font-family:'Playfair Display',serif;"
        "color:#E8F4F4;"
        "margin:0 0 0.1rem;"
        "font-size:4rem;"
        "font-weight:900;"
        "letter-spacing:-0.03em;"
        'line-height:1;">'
        'Re<span style="color:#006D77;">NOVA</span>'
        '</h1>',
        unsafe_allow_html=True,
    )
    if tagline:
        st.markdown(
            '<p style="'
            "font-family:'Playfair Display',serif;"
            "font-style:italic;"
            "color:#83C5BE;"
            "font-size:1.1rem;"
            "margin:0.3rem 0 0;"
            'letter-spacing:0.01em;">'
            "Give it a NOVA life."
            "</p>",
            unsafe_allow_html=True,
        )
    if description:
        st.markdown(
            '<p style="'
            "color:#4A6A6A;"
            "font-size:0.8rem;"
            "margin:0.5rem 0 0;"
            'letter-spacing:0.04em;">'
            "The Nova SBE community marketplace."
            "</p>",
            unsafe_allow_html=True,
        )
    st.markdown(
        '<div style="'
        "width:36px;height:2px;"
        "background:#006D77;"
        'margin:1.1rem 0 1.3rem;">'
        "</div>",
        unsafe_allow_html=True,
    )


def show_page_header():
    """Compact logo + tagline for top of logged-in pages."""
    st.markdown(
        "<h2 style=\"font-family:'Playfair Display',serif;color:#E8F4F4;margin:0 0 0.1rem;font-weight:900;\">"
        'Re<span style="color:#006D77;">NOVA</span></h2>'
        "<p style=\"font-family:'Playfair Display',serif;font-style:italic;"
        'color:#83C5BE;font-size:0.88rem;margin:0;\">Give it a NOVA life.</p>',
        unsafe_allow_html=True,
    )


def sidebar_user():
    """Render user info + logout in the sidebar."""
    user = st.session_state.get("user")
    if not user:
        return
    with st.sidebar:
        st.markdown(
            "<h2 style=\"font-family:'Playfair Display',serif;color:#E8F4F4;margin:0;font-weight:900;\">"
            'Re<span style="color:#006D77;">NOVA</span></h2>'
            '<p style="font-size:0.6rem;letter-spacing:0.18em;color:#3A5A5A;margin:3px 0 0;text-transform:uppercase;">Nova SBE Marketplace</p>',
            unsafe_allow_html=True,
        )
        st.divider()

        # Avatar with initials
        initials = "".join(w[0].upper() for w in user["name"].split()[:2])
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">'
            f'<div style="width:36px;height:36px;border-radius:50%;background:#004D55;'
            f'display:flex;align-items:center;justify-content:center;'
            f'font-weight:700;font-size:0.82rem;color:#83C5BE;flex-shrink:0;">{initials}</div>'
            f'<div><div style="font-size:0.85rem;font-weight:600;color:#E8F4F4;">{user["name"].split()[0]}</div>'
            f'<div style="font-size:0.72rem;color:#4A6A6A;">{user["email"]}</div></div>'
            f"</div>",
            unsafe_allow_html=True,
        )
        st.write("")
        st.page_link("pages/3_My_Profile.py", label="My Profile", use_container_width=True)
        st.divider()
        if st.button("Sign Out", use_container_width=True):
            st.session_state.user = None
            st.rerun()


def auth_gate():
    """Stop rendering and show a login prompt if user is not authenticated."""
    if not st.session_state.get("user"):
        st.warning("You must be logged in to view this page.")
        st.page_link("app.py", label="← Go to Login / Home")
        st.stop()


def listing_card(listing: dict):
    """Render a polished listing card inside a bordered container."""
    cat    = listing.get("category", "Other")
    status = listing.get("status", "available")
    status_label, _, _ = STATUS_BADGE.get(status, STATUS_BADGE["available"])
    icon   = CATEGORY_ICONS.get(cat, "📦")

    with st.container(border=True):
        # Image or placeholder
        img_rel  = listing.get("image_path")
        img_path = BASE_DIR / img_rel if img_rel else None
        if img_path and img_path.exists():
            st.image(str(img_path), use_container_width=True)
        else:
            st.markdown(
                f'<div class="card-img-placeholder">'
                f'<span class="cat-emoji">{icon}</span>'
                f'<span class="cat-label">{cat}</span>'
                f"</div>",
                unsafe_allow_html=True,
            )

        # Title
        st.markdown(
            f'<p style="font-size:0.9rem;font-weight:600;color:#E8F4F4;'
            f'margin:0 0 4px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">'
            f"{listing['title']}</p>",
            unsafe_allow_html=True,
        )

        # Price
        if listing.get("price_type") == "offer":
            st.markdown(
                '<p style="font-size:0.85rem;font-weight:700;color:#F59E0B;margin:0 0 8px;">Make an Offer</p>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<p style="font-size:1.05rem;font-weight:700;color:#83C5BE;margin:0 0 8px;">'
                f'€{float(listing.get("price", 0)):.2f}</p>',
                unsafe_allow_html=True,
            )

        # Badges
        cond = listing.get("condition", "")
        st.markdown(
            f'<div style="margin-bottom:8px;">'
            f'<span class="badge badge-{status_label}">{status_label.title()}</span>'
            f'<span class="badge badge-cat">{cat}</span>'
            f'<span class="badge badge-cond">{cond}</span>'
            f"</div>",
            unsafe_allow_html=True,
        )

        # Meta
        seller = listing.get("seller_name", "Unknown")
        date   = listing.get("created_at", "")[:10]
        st.markdown(
            f'<p class="card-meta">by {seller} · {date}</p>',
            unsafe_allow_html=True,
        )

        # WhatsApp CTA
        wa = listing.get("whatsapp", "")
        if wa and status == "available":
            clean = "".join(c for c in wa if c.isdigit() or c == "+")
            msg   = urllib.parse.quote(
                f"Hi! I'm interested in your listing on ReNOVA: {listing['title']}"
            )
            st.markdown(
                f'<a class="wa-btn" href="https://wa.me/{clean}?text={msg}" target="_blank">'
                f"💬 Contact on WhatsApp</a>",
                unsafe_allow_html=True,
            )
