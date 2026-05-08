import base64
import urllib.parse
import os
from pathlib import Path

import streamlit as st

from utils.db import (
    BASE_DIR,
    get_listing_images,
    get_profile_photo_path,
    toggle_favorite,
    load_users,
    save_users,
)

# ── Constants ──────────────────────────────────────────────────────────────

CATEGORIES = ["Furniture", "Books", "Electronics", "Clothing", "Services", "Other"]
CONDITIONS  = ["New", "Like New", "Good", "Fair", "Poor"]

# Short initials shown in placeholder cards (no emojis)
CATEGORY_INITIALS = {
    "Furniture":   "FN",
    "Books":       "BK",
    "Electronics": "EL",
    "Clothing":    "CL",
    "Services":    "SV",
    "Other":       "OT",
}

# Keep this dict for any code that imports CATEGORY_ICONS — values are now
# plain text abbreviations instead of emoji characters.
CATEGORY_ICONS = CATEGORY_INITIALS

STATUS_BADGE = {
    "available": ("available", "#006D77", "#FFFFFF"),
    "reserved":  ("reserved",  "#92400e", "#FEF3C7"),
    "sold":      ("sold",      "#3A0000", "#FCA5A5"),
}


# ── CSS ────────────────────────────────────────────────────────────────────

def inject_css():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Inter:wght@300;400;500;600;700&display=swap');

        /* ── Base ── */
        html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

        /* ── App background ── */
        .stApp { background: #0C1A1A !important; }
        section[data-testid="stSidebar"] {
            background: #111F1F !important;
            border-right: 1px solid #1E3232 !important;
        }
        .block-container {
            padding-top: 1.4rem !important;
            padding-bottom: 2rem !important;
        }

        /* ── Hide Streamlit chrome ── */
        #MainMenu, footer, header { visibility: hidden; }

        /* ── Divider ── */
        hr { border-color: #1E3232 !important; }

        /* ── Sidebar text ── */
        section[data-testid="stSidebar"] * { color: #A8C8C8 !important; }
        section[data-testid="stSidebar"] strong { color: #E8F4F4 !important; }

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
        .stTextArea > div > div > textarea::placeholder { color: #3A5A5A !important; }

        /* ── Selectbox ── */
        .stSelectbox > div > div {
            background: #111F1F !important;
            border: 1px solid #1E3232 !important;
            border-radius: 8px !important;
            color: #E8F4F4 !important;
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

        /* ── Bordered containers / cards ── */
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

        /* ── Card images (scoped to bordered containers only) ── */
        [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stImage"] img {
            height: 180px !important;
            width: 100% !important;
            object-fit: cover !important;
            border-radius: 8px 8px 0 0 !important;
        }

        /* ── Metrics ── */
        [data-testid="stMetric"] {
            background: #0F2020 !important;
            border: 1px solid #1E3232 !important;
            border-radius: 12px !important;
            padding: 14px 16px !important;
        }
        [data-testid="stMetricValue"] { color: #83C5BE !important; font-weight: 700 !important; }
        [data-testid="stMetricLabel"] {
            color: #4A6A6A !important;
            font-size: 0.72rem !important;
            text-transform: uppercase !important;
            letter-spacing: 0.08em !important;
        }

        /* ── Alerts ── */
        .stAlert {
            background: #0A2A1A !important;
            border: 1px solid #1A4A2A !important;
            border-radius: 10px !important;
            color: #6EE7B7 !important;
        }

        /* ── Radio chips ── */
        div[data-testid="stRadio"] > div {
            display: flex !important;
            flex-wrap: wrap !important;
            gap: 8px !important;
            background: transparent !important;
        }
        div[data-testid="stRadio"] > div > label {
            background: #162424 !important;
            border: 1px solid #1E3232 !important;
            border-radius: 999px !important;
            padding: 6px 16px !important;
            cursor: pointer !important;
            font-size: 0.82rem !important;
            color: #A8C8C8 !important;
            transition: all 0.15s !important;
            margin: 0 !important;
        }
        div[data-testid="stRadio"] > div > label:hover {
            border-color: #006D77 !important;
            color: #E8F4F4 !important;
        }
        div[data-testid="stRadio"] > div > label:has(input:checked) {
            background: #006D77 !important;
            border-color: #006D77 !important;
            color: #FFFFFF !important;
            font-weight: 600 !important;
        }
        div[data-testid="stRadio"] > div > label > div:first-child { display: none !important; }

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

        /* ── Forms ── */
        [data-testid="stForm"] {
            background: #0F2020 !important;
            border: 1px solid #1E3232 !important;
            border-radius: 16px !important;
            padding: 1.5rem !important;
        }

        /* ── Page links ── */
        [data-testid="stPageLink"] a { color: #83C5BE !important; font-weight: 500 !important; }

        /* ── Typography ── */
        h1, h2, h3 { font-family: 'Playfair Display', serif !important; color: #E8F4F4 !important; }
        p, span, div { color: #A8C8C8; }
        .stCaption, small { color: #4A6A6A !important; }

        /* ── Card image placeholder ── */
        .card-img-placeholder {
            width: 100%;
            height: 180px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 6px;
            background: linear-gradient(135deg, #0A1818 0%, #162424 100%);
            border-radius: 8px 8px 0 0;
        }
        .card-img-placeholder .cat-abbr {
            font-size: 1.8rem;
            font-weight: 700;
            color: #1E3A3A;
            font-family: 'Playfair Display', serif;
        }
        .card-img-placeholder .cat-label {
            font-size: 0.6rem;
            letter-spacing: 0.16em;
            color: #2A4A4A;
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
        .badge-housing   { background: #1A0A3A; color: #B4A0FF; border: 1px solid #2A1A5A; }

        /* ── Card meta line ── */
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
            margin-top: 4px;
            border: 1px solid #1e5a40;
            transition: all 0.15s;
        }
        .wa-btn:hover { background: #25D366; color: #fff !important; }

        /* ── Housing card banner ── */
        .housing-badge-row { margin-bottom: 6px; }

        /* ── Navbar row ── */
        .renova-navbar {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 8px 0 12px;
            border-bottom: 1px solid #1E3232;
            margin-bottom: 16px;
        }

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


# ── Logo helpers ───────────────────────────────────────────────────────────

def _logo_b64() -> str | None:
    p = BASE_DIR / "images" / "logo.png"
    if p.exists():
        return base64.b64encode(p.read_bytes()).decode()
    return None


def show_logo(width: int = 300, tagline: bool = False, description: bool = False):
    logo_path = BASE_DIR / "images" / "logo.png"
    if logo_path.exists():
        st.image(str(logo_path), use_container_width=True)
    else:
        st.markdown(
            '<h1 style="font-family:\'Playfair Display\',serif;color:#E8F4F4;'
            'margin:0;font-size:4rem;font-weight:900;letter-spacing:-0.03em;line-height:1;">'
            'Re<span style="color:#006D77;">NOVA</span></h1>',
            unsafe_allow_html=True,
        )
    if tagline:
        st.markdown(
            '<p style="font-family:\'Playfair Display\',serif;font-style:italic;'
            'color:#83C5BE;font-size:1.1rem;margin:0.3rem 0 0;letter-spacing:0.01em;">'
            "Give it a NOVA life.</p>",
            unsafe_allow_html=True,
        )


def show_page_header():
    st.markdown(
        "<h2 style=\"font-family:'Playfair Display',serif;color:#E8F4F4;"
        "margin:0 0 0.1rem;font-weight:900;\">"
        'Re<span style="color:#006D77;">NOVA</span></h2>'
        "<p style=\"font-family:'Playfair Display',serif;font-style:italic;"
        'color:#83C5BE;font-size:0.88rem;margin:0;\">Give it a NOVA life.</p>',
        unsafe_allow_html=True,
    )


# ── Avatar helper ──────────────────────────────────────────────────────────

def _avatar_html(student_id: str, name: str, size: int = 36) -> str:
    photo = get_profile_photo_path(student_id)
    if photo:
        b64  = base64.b64encode(photo.read_bytes()).decode()
        ext  = photo.suffix.lstrip(".")
        if ext == "jpg":
            ext = "jpeg"
        return (
            f'<div style="width:{size}px;height:{size}px;border-radius:50%;'
            f'overflow:hidden;flex-shrink:0;border:2px solid #006D77;">'
            f'<img src="data:image/{ext};base64,{b64}" '
            f'style="width:100%;height:100%;object-fit:cover;display:block;"/></div>'
        )
    initials = "".join(w[0].upper() for w in name.split()[:2])
    fs = max(10, int(size * 0.32))
    return (
        f'<div style="width:{size}px;height:{size}px;border-radius:50%;background:#004D55;'
        f'display:flex;align-items:center;justify-content:center;'
        f'font-weight:700;font-size:{fs}px;color:#83C5BE;flex-shrink:0;">{initials}</div>'
    )


# ── Sidebar ────────────────────────────────────────────────────────────────

def sidebar_user():
    user = st.session_state.get("user")
    if not user:
        return
    with st.sidebar:
        b64 = _logo_b64()
        if b64:
            st.markdown(
                f'<img src="data:image/png;base64,{b64}" '
                f'style="width:140px;display:block;margin-bottom:8px;"/>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                "<h3 style=\"font-family:'Playfair Display',serif;color:#E8F4F4;margin:0;\">"
                'Re<span style="color:#006D77;">NOVA</span></h3>',
                unsafe_allow_html=True,
            )

        st.divider()

        avatar = _avatar_html(user["student_id"], user["name"], size=38)
        email  = user.get("email", f"{user['student_id']}@novasbe.pt")
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">'
            f'{avatar}'
            f'<div><div style="font-size:0.85rem;font-weight:600;color:#E8F4F4;">'
            f'{user["name"].split()[0]}</div>'
            f'<div style="font-size:0.72rem;color:#4A6A6A;">{email}</div></div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.write("")
        if st.button("Sign Out", use_container_width=True, key="sidebar_signout"):
            st.session_state.user = None
            st.rerun()


# ── Page navbar (top header row) ───────────────────────────────────────────

def page_navbar(search_placeholder: str = "Search listings…", search_key: str = "navbar_search"):
    """
    Render the top navbar: logo | search bar | favorites count | profile avatar.
    Returns the current search query string.
    """
    user = st.session_state.get("user")
    col_logo, col_search, col_actions = st.columns([1, 4, 1.2])

    with col_logo:
        b64 = _logo_b64()
        if b64:
            st.markdown(
                f'<img src="data:image/png;base64,{b64}" '
                f'style="height:42px;width:auto;display:block;margin-top:4px;"/>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                "<span style=\"font-family:'Playfair Display',serif;font-weight:900;"
                "color:#E8F4F4;font-size:1.3rem;\">Re<span style='color:#006D77;'>NOVA</span></span>",
                unsafe_allow_html=True,
            )

    with col_search:
        query = st.text_input(
            "",
            placeholder=search_placeholder,
            label_visibility="collapsed",
            key=search_key,
        )

    with col_actions:
        if user:
            fav_count = len(user.get("favorites", []))
            fav_label  = f"Saved ({fav_count})" if fav_count else "Saved"
            avatar_html = _avatar_html(user["student_id"], user["name"], size=30)

            st.markdown(
                f'<div style="display:flex;align-items:center;gap:8px;padding-top:6px;">'
                f'<a href="/3_My_Profile" style="text-decoration:none;">'
                f'<span style="font-size:0.75rem;color:#4A6A6A;">{fav_label}</span></a>'
                f'<a href="/3_My_Profile" style="text-decoration:none;">{avatar_html}</a>'
                f'</div>',
                unsafe_allow_html=True,
            )
        else:
            query = ""

    st.markdown('<hr style="margin:8px 0 16px;border-color:#1E3232;"/>', unsafe_allow_html=True)
    return query


# ── Auth gate ──────────────────────────────────────────────────────────────

def auth_gate():
    if not st.session_state.get("user"):
        st.warning("You must be logged in to view this page.")
        st.page_link("app.py", label="Go to Login")
        st.stop()


# ── Sidebar nav links ──────────────────────────────────────────────────────

def sidebar_nav():
    with st.sidebar:
        st.markdown(
            '<p style="font-size:0.65rem;letter-spacing:0.14em;color:#3A5A5A;'
            'text-transform:uppercase;margin:0.5rem 0 0.3rem;">Menu</p>',
            unsafe_allow_html=True,
        )
        st.page_link("app.py",                  label="Home")
        st.page_link("pages/1_Browse.py",        label="Browse Listings")
        st.page_link("pages/2_Post_Listing.py",  label="Post a Listing")
        st.page_link("pages/3_My_Profile.py",    label="My Profile")


# ── Listing card ───────────────────────────────────────────────────────────

def listing_card(listing: dict, show_actions: bool = True):
    """
    Render a marketplace listing card.
    show_actions: show View Details + WhatsApp + Favorites.
    """
    user   = st.session_state.get("user")
    cat    = listing.get("category", "Other")
    status = listing.get("status", "available")
    status_label, _, _ = STATUS_BADGE.get(status, STATUS_BADGE["available"])
    abbr   = CATEGORY_INITIALS.get(cat, "OT")
    images = get_listing_images(listing)
    lid    = listing["id"]

    is_fav = False
    if user:
        is_fav = lid in user.get("favorites", [])

    with st.container(border=True):
        # ── Image ──────────────────────────────────────────────────────────
        if images:
            img_path = BASE_DIR / images[0]
            if img_path.exists():
                st.image(str(img_path), use_container_width=True)
            else:
                _placeholder(abbr, cat)
        else:
            _placeholder(abbr, cat)

        # ── Title ──────────────────────────────────────────────────────────
        st.markdown(
            f'<p style="font-size:0.9rem;font-weight:600;color:#E8F4F4;'
            f'margin:6px 0 2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">'
            f'{listing["title"]}</p>',
            unsafe_allow_html=True,
        )

        # ── Price ──────────────────────────────────────────────────────────
        if listing.get("price_type") == "offer":
            st.markdown(
                '<p style="font-size:0.85rem;font-weight:700;color:#F59E0B;margin:0 0 6px;">Make an Offer</p>',
                unsafe_allow_html=True,
            )
        else:
            price = float(listing.get("price", 0))
            st.markdown(
                f'<p style="font-size:1.05rem;font-weight:700;color:#83C5BE;margin:0 0 6px;">'
                f'€{price:.2f}</p>',
                unsafe_allow_html=True,
            )

        # ── Badges ─────────────────────────────────────────────────────────
        cond = listing.get("condition", "")
        st.markdown(
            f'<div style="margin-bottom:6px;">'
            f'<span class="badge badge-{status_label}">{status_label.title()}</span>'
            f'<span class="badge badge-cat">{cat}</span>'
            f'<span class="badge badge-cond">{cond}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

        # ── Meta ───────────────────────────────────────────────────────────
        seller = listing.get("seller_name", "Unknown")
        date   = listing.get("created_at", "")[:10]
        st.markdown(
            f'<p class="card-meta">by {seller} · {date}</p>',
            unsafe_allow_html=True,
        )

        if not show_actions:
            return

        # ── Actions ────────────────────────────────────────────────────────
        btn_detail, btn_fav = st.columns([4, 1])
        with btn_detail:
            if st.button("View Details", key=f"det_{lid}", use_container_width=True):
                st.session_state.selected_listing_id = lid
                st.switch_page("pages/4_Listing_Detail.py")
        with btn_fav:
            fav_symbol = "♥" if is_fav else "♡"
            if st.button(fav_symbol, key=f"fav_{lid}", help="Save to favorites"):
                if user:
                    new_favs = toggle_favorite(user["student_id"], lid)
                    st.session_state.user["favorites"] = new_favs
                    st.rerun()

        # ── WhatsApp ───────────────────────────────────────────────────────
        wa = listing.get("whatsapp", "")
        if wa and status == "available":
            clean = "".join(c for c in wa if c.isdigit() or c == "+")
            msg   = urllib.parse.quote(
                f"Hi! I saw your listing on ReNOVA: {listing['title']}"
            )
            st.markdown(
                f'<a class="wa-btn" href="https://wa.me/{clean}?text={msg}" target="_blank">'
                f"Contact on WhatsApp</a>",
                unsafe_allow_html=True,
            )


# ── Housing card ───────────────────────────────────────────────────────────

def housing_card(listing: dict):
    """Render a housing listing card with rent-focused layout."""
    user   = st.session_state.get("user")
    status = listing.get("status", "available")
    status_label, _, _ = STATUS_BADGE.get(status, STATUS_BADGE["available"])
    images = get_listing_images(listing)
    lid    = listing["id"]
    is_fav = lid in user.get("favorites", []) if user else False

    with st.container(border=True):
        # ── Image ──────────────────────────────────────────────────────────
        if images:
            img_path = BASE_DIR / images[0]
            if img_path.exists():
                st.image(str(img_path), use_container_width=True)
            else:
                _placeholder_housing()
        else:
            _placeholder_housing()

        # ── Location ───────────────────────────────────────────────────────
        loc = listing.get("location", "")
        if loc:
            st.markdown(
                f'<p style="font-size:0.72rem;color:#83C5BE;letter-spacing:0.06em;'
                f'text-transform:uppercase;margin:6px 0 2px;">{loc}</p>',
                unsafe_allow_html=True,
            )

        # ── Title ──────────────────────────────────────────────────────────
        st.markdown(
            f'<p style="font-size:0.9rem;font-weight:600;color:#E8F4F4;'
            f'margin:0 0 2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">'
            f'{listing["title"]}</p>',
            unsafe_allow_html=True,
        )

        # ── Rent ───────────────────────────────────────────────────────────
        rent = float(listing.get("price", 0))
        period = listing.get("rent_period", "month")
        st.markdown(
            f'<p style="font-size:1.05rem;font-weight:700;color:#B4A0FF;margin:0 0 4px;">'
            f'€{rent:.0f} / {period}</p>',
            unsafe_allow_html=True,
        )

        # ── Badges ─────────────────────────────────────────────────────────
        rooms = listing.get("rooms", "")
        avail_from = listing.get("available_from", "")
        badges_html = (
            f'<span class="badge badge-housing">Housing</span>'
            f'<span class="badge badge-{status_label}">{status_label.title()}</span>'
        )
        if rooms:
            badges_html += f'<span class="badge badge-cat">{rooms} room{"s" if str(rooms) != "1" else ""}</span>'
        st.markdown(f'<div style="margin-bottom:6px;">{badges_html}</div>', unsafe_allow_html=True)

        if avail_from:
            st.markdown(
                f'<p class="card-meta">Available from {avail_from}</p>',
                unsafe_allow_html=True,
            )

        # ── Actions ────────────────────────────────────────────────────────
        btn_detail, btn_fav = st.columns([4, 1])
        with btn_detail:
            if st.button("View Details", key=f"det_{lid}", use_container_width=True):
                st.session_state.selected_listing_id = lid
                st.switch_page("pages/4_Listing_Detail.py")
        with btn_fav:
            fav_symbol = "♥" if is_fav else "♡"
            if st.button(fav_symbol, key=f"fav_{lid}", help="Save"):
                if user:
                    new_favs = toggle_favorite(user["student_id"], lid)
                    st.session_state.user["favorites"] = new_favs
                    st.rerun()

        wa = listing.get("whatsapp", "")
        if wa and status == "available":
            clean = "".join(c for c in wa if c.isdigit() or c == "+")
            msg   = urllib.parse.quote(
                f"Hi! I saw your housing listing on ReNOVA: {listing['title']}"
            )
            st.markdown(
                f'<a class="wa-btn" href="https://wa.me/{clean}?text={msg}" target="_blank">'
                f"Contact on WhatsApp</a>",
                unsafe_allow_html=True,
            )


# ── Placeholder helpers ────────────────────────────────────────────────────

def _placeholder(abbr: str, cat: str):
    st.markdown(
        f'<div class="card-img-placeholder">'
        f'<span class="cat-abbr">{abbr}</span>'
        f'<span class="cat-label">{cat}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )


def _placeholder_housing():
    st.markdown(
        '<div class="card-img-placeholder">'
        '<span class="cat-abbr" style="color:#2A1A5A;">HS</span>'
        '<span class="cat-label">Housing</span>'
        '</div>',
        unsafe_allow_html=True,
    )
