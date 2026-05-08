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

CATEGORY_INITIALS = {
    "Furniture":   "FN",
    "Books":       "BK",
    "Electronics": "EL",
    "Clothing":    "CL",
    "Services":    "SV",
    "Other":       "OT",
}
CATEGORY_ICONS = CATEGORY_INITIALS   # backward-compat alias

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

        /* ── Pure black background matching logo ── */
        .stApp { background: #000000 !important; }
        section[data-testid="stSidebar"] {
            background: #080808 !important;
            border-right: 1px solid #1A1A1A !important;
        }
        .block-container {
            padding-top: 1.2rem !important;
            padding-bottom: 2rem !important;
        }

        /* ── Hide Streamlit chrome ── */
        #MainMenu, footer, header { visibility: hidden; }

        /* ── Make the sidebar re-open button big and visible ── */
        /* When sidebar is collapsed Streamlit shows collapsedControl */
        [data-testid="collapsedControl"] {
            position: fixed !important;
            top: 50% !important;
            left: 0 !important;
            transform: translateY(-50%) !important;
            z-index: 999 !important;
        }
        [data-testid="collapsedControl"] button {
            background: #006D77 !important;
            color: #ffffff !important;
            border: none !important;
            border-radius: 0 8px 8px 0 !important;
            width: 32px !important;
            height: 48px !important;
            font-size: 1.1rem !important;
            box-shadow: 2px 0 12px rgba(0,109,119,0.4) !important;
            cursor: pointer !important;
        }
        [data-testid="collapsedControl"] button:hover {
            background: #00838F !important;
            width: 38px !important;
        }

        /* ── Hide sidebar's own collapse button (prevent accidental close) ── */
        [data-testid="stSidebarCollapseButton"] { display: none !important; }

        /* ── Divider ── */
        hr { border-color: #1A1A1A !important; }

        /* ── Sidebar text ── */
        section[data-testid="stSidebar"] * { color: #A8C8C8 !important; }
        section[data-testid="stSidebar"] strong { color: #E8F4F4 !important; }

        /* ── Buttons ── */
        .stButton > button {
            border-radius: 8px !important;
            font-weight: 500 !important;
            font-family: 'Inter', sans-serif !important;
            background: #0D0D0D !important;
            border: 1px solid #1A1A1A !important;
            color: #A8C8C8 !important;
            transition: all 0.15s !important;
        }
        .stButton > button:hover {
            background: #181818 !important;
            border-color: #2A2A2A !important;
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
            background: #0D0D0D !important;
            border: 1px solid #1A1A1A !important;
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
        .stTextArea > div > div > textarea::placeholder { color: #3A3A3A !important; }

        /* ── Selectbox ── */
        .stSelectbox > div > div {
            background: #0D0D0D !important;
            border: 1px solid #1A1A1A !important;
            border-radius: 8px !important;
            color: #E8F4F4 !important;
        }

        /* ── Tabs ── */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0;
            border-bottom: 1px solid #1A1A1A !important;
            background: transparent !important;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 8px 20px 10px 0 !important;
            background: transparent !important;
            border: none !important;
            color: #3A3A3A !important;
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
            background: #0D0D0D !important;
            border: 1px solid #1A1A1A !important;
            border-radius: 10px !important;
            color: #A8C8C8 !important;
        }
        .streamlit-expanderContent {
            background: #080808 !important;
            border: 1px solid #1A1A1A !important;
            border-top: none !important;
        }

        /* ── Bordered containers / cards ── */
        [data-testid="stVerticalBlockBorderWrapper"] > div {
            background: #0D0D0D !important;
            border: 1px solid #1A1A1A !important;
            border-radius: 14px !important;
            transition: border-color 0.2s, transform 0.2s, box-shadow 0.2s !important;
        }
        [data-testid="stVerticalBlockBorderWrapper"] > div:hover {
            border-color: #006D77 !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 24px rgba(0,109,119,0.12) !important;
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
            background: #0D0D0D !important;
            border: 1px solid #1A1A1A !important;
            border-radius: 12px !important;
            padding: 14px 16px !important;
        }
        [data-testid="stMetricValue"] { color: #83C5BE !important; font-weight: 700 !important; }
        [data-testid="stMetricLabel"] {
            color: #3A3A3A !important;
            font-size: 0.72rem !important;
            text-transform: uppercase !important;
            letter-spacing: 0.08em !important;
        }

        /* ── Alerts ── */
        .stAlert {
            background: #050F05 !important;
            border: 1px solid #0A2A0A !important;
            border-radius: 10px !important;
            color: #6EE7B7 !important;
        }

        /* ── Radio chips (category filters) ── */
        div[data-testid="stRadio"] > div {
            display: flex !important;
            flex-wrap: wrap !important;
            gap: 6px !important;
            background: transparent !important;
        }
        div[data-testid="stRadio"] > div > label {
            background: #0D0D0D !important;
            border: 1px solid #1A1A1A !important;
            border-radius: 999px !important;
            padding: 5px 14px !important;
            cursor: pointer !important;
            font-size: 0.8rem !important;
            color: #A8C8C8 !important;
            transition: all 0.15s !important;
            margin: 0 !important;
            white-space: nowrap !important;
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
            background: #0D0D0D !important;
            border: 2px dashed #1A1A1A !important;
            border-radius: 10px !important;
        }

        /* ── Labels ── */
        label, .stTextInput label, .stSelectbox label,
        .stTextArea label, .stNumberInput label {
            color: #555555 !important;
            font-size: 0.8rem !important;
            font-weight: 500 !important;
            letter-spacing: 0.03em !important;
        }

        /* ── Forms ── */
        [data-testid="stForm"] {
            background: #0D0D0D !important;
            border: 1px solid #1A1A1A !important;
            border-radius: 16px !important;
            padding: 1.5rem !important;
        }

        /* ── Page links ── */
        [data-testid="stPageLink"] a { color: #83C5BE !important; font-weight: 500 !important; }

        /* ── Typography ── */
        h1, h2, h3 { font-family: 'Playfair Display', serif !important; color: #E8F4F4 !important; }
        p, span, div { color: #A8C8C8; }
        .stCaption, small { color: #555555 !important; }

        /* ── Card image placeholder ── */
        .card-img-placeholder {
            width: 100%;
            height: 180px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 6px;
            background: linear-gradient(135deg, #050505 0%, #0D0D0D 100%);
            border-radius: 8px 8px 0 0;
        }
        .card-img-placeholder .cat-abbr {
            font-size: 1.8rem;
            font-weight: 700;
            color: #1A1A1A;
            font-family: 'Playfair Display', serif;
        }
        .card-img-placeholder .cat-label {
            font-size: 0.6rem;
            letter-spacing: 0.16em;
            color: #222222;
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
        .badge-available { background: #001A1C; color: #83C5BE; border: 1px solid #003D3F; }
        .badge-reserved  { background: #1A1000; color: #FDE68A; border: 1px solid #3A2800; }
        .badge-sold      { background: #1A0000; color: #FCA5A5; border: 1px solid #3A0000; }
        .badge-cat       { background: #001A1C; color: #4A8A8A; }
        .badge-cond      { background: #0D0D0D; color: #444444; border: 1px solid #1A1A1A; }
        .badge-housing   { background: #0A0020; color: #B4A0FF; border: 1px solid #2A1A5A; }

        /* ── Card meta line ── */
        .card-meta {
            font-size: 0.72rem;
            color: #333333;
            margin-top: 4px;
            margin-bottom: 10px;
        }

        /* ── WhatsApp button ── */
        .wa-btn {
            display: block;
            background: #001A0D;
            color: #25D366 !important;
            text-decoration: none !important;
            text-align: center;
            padding: 9px 0;
            border-radius: 8px;
            font-size: 0.82rem;
            font-weight: 600;
            margin-top: 4px;
            border: 1px solid #0A3A1A;
            transition: all 0.15s;
        }
        .wa-btn:hover { background: #25D366; color: #000 !important; }

        /* ── Navbar saved/profile mini-buttons ── */
        .nav-action-btn {
            background: transparent !important;
            border: none !important;
            color: #555555 !important;
            font-size: 0.78rem !important;
            padding: 4px 6px !important;
            border-radius: 6px !important;
            cursor: pointer !important;
            white-space: nowrap !important;
        }
        .nav-action-btn:hover { color: #83C5BE !important; }

        /* ── Category table ── */
        .cat-table {
            width: 100%;
            border-collapse: collapse;
            border: 1px solid #1A1A1A;
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
        .cat-table tbody tr { border-top: 1px solid #1A1A1A; }
        .cat-table tbody td { padding: 9px 14px; }
        .cat-table .cat-name { color: #444444; font-size: 0.72rem; letter-spacing: 0.08em; text-transform: uppercase; }
        .cat-table .cat-count { color: #83C5BE; font-weight: 700; font-size: 0.85rem; text-align: right; }

        /* ── Housing section ── */
        .housing-section-header {
            background: linear-gradient(135deg, #000000 0%, #0A0020 100%);
            border: 1px solid #2A1A5A;
            border-radius: 14px;
            padding: 20px 24px;
            margin-bottom: 16px;
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
            'color:#83C5BE;font-size:1.1rem;margin:0.3rem 0 0;">Give it a NOVA life.</p>',
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
        f'<div style="width:{size}px;height:{size}px;border-radius:50%;background:#001A1C;'
        f'border:2px solid #006D77;display:flex;align-items:center;justify-content:center;'
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
                f'style="width:150px;display:block;margin-bottom:8px;"/>',
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
            f'<div style="font-size:0.72rem;color:#444444;">{email}</div></div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.write("")
        if st.button("Sign Out", use_container_width=True, key="sidebar_signout"):
            st.session_state.user = None
            st.rerun()


# ── Sidebar nav ────────────────────────────────────────────────────────────

def sidebar_nav():
    with st.sidebar:
        st.markdown(
            '<p style="font-size:0.65rem;letter-spacing:0.14em;color:#333333;'
            'text-transform:uppercase;margin:0.5rem 0 0.3rem;">Menu</p>',
            unsafe_allow_html=True,
        )
        st.page_link("app.py",                  label="Home")
        st.page_link("pages/1_Browse.py",        label="Browse Listings")
        st.page_link("pages/2_Post_Listing.py",  label="Post a Listing")
        st.page_link("pages/3_My_Profile.py",    label="My Profile")


# ── Page navbar ────────────────────────────────────────────────────────────

def page_navbar(
    search_placeholder: str = "Search listings…",
    search_key: str = "navbar_search",
) -> str:
    """
    Top navbar: logo | search bar | Saved button | avatar button.
    Returns the current search query.
    """
    user = st.session_state.get("user")

    col_logo, col_search, col_saved, col_profile = st.columns([1.0, 4.5, 1.0, 0.8])

    # ── Logo ───────────────────────────────────────────────────────────────
    with col_logo:
        b64 = _logo_b64()
        if b64:
            st.markdown(
                f'<img src="data:image/png;base64,{b64}" '
                f'style="height:56px;width:auto;display:block;margin-top:2px;"/>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                "<span style=\"font-family:'Playfair Display',serif;font-weight:900;"
                "color:#E8F4F4;font-size:1.3rem;\">Re<span style='color:#006D77;'>NOVA</span></span>",
                unsafe_allow_html=True,
            )

    # ── Search ─────────────────────────────────────────────────────────────
    with col_search:
        query = st.text_input(
            "",
            placeholder=search_placeholder,
            label_visibility="collapsed",
            key=search_key,
        )

    # ── Saved button ───────────────────────────────────────────────────────
    with col_saved:
        if user:
            fav_count = len(user.get("favorites", []))
            fav_label = f"Saved  ({fav_count})" if fav_count else "Saved"
            st.write("")  # align vertically
            if st.button(fav_label, key=f"nav_saved_{search_key}", use_container_width=True):
                st.session_state.profile_active_tab = 1
                st.switch_page("pages/3_My_Profile.py")

    # ── Profile avatar button ───────────────────────────────────────────────
    with col_profile:
        if user:
            st.write("")
            initials = "".join(w[0].upper() for w in user["name"].split()[:2])
            if st.button(initials, key=f"nav_profile_{search_key}", use_container_width=True):
                st.session_state.profile_active_tab = 0
                st.switch_page("pages/3_My_Profile.py")

    st.markdown(
        '<hr style="margin:6px 0 14px;border:none;border-top:1px solid #1A1A1A;"/>',
        unsafe_allow_html=True,
    )
    return query


# ── Auth gate ──────────────────────────────────────────────────────────────

def auth_gate():
    if not st.session_state.get("user"):
        st.warning("You must be logged in to view this page.")
        st.page_link("app.py", label="Go to Login")
        st.stop()


# ── Listing card ───────────────────────────────────────────────────────────

def listing_card(listing: dict, show_actions: bool = True):
    user   = st.session_state.get("user")
    cat    = listing.get("category", "Other")
    status = listing.get("status", "available")
    status_label, _, _ = STATUS_BADGE.get(status, STATUS_BADGE["available"])
    abbr   = CATEGORY_INITIALS.get(cat, "OT")
    images = get_listing_images(listing)
    lid    = listing["id"]
    is_fav = lid in user.get("favorites", []) if user else False

    with st.container(border=True):
        # Image
        if images:
            img_path = BASE_DIR / images[0]
            if img_path.exists():
                st.image(str(img_path), use_container_width=True)
            else:
                _placeholder(abbr, cat)
        else:
            _placeholder(abbr, cat)

        # Title
        st.markdown(
            f'<p style="font-size:0.9rem;font-weight:600;color:#E8F4F4;'
            f'margin:6px 0 2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">'
            f'{listing["title"]}</p>',
            unsafe_allow_html=True,
        )

        # Price
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

        # Badges
        cond = listing.get("condition", "")
        st.markdown(
            f'<div style="margin-bottom:6px;">'
            f'<span class="badge badge-{status_label}">{status_label.title()}</span>'
            f'<span class="badge badge-cat">{cat}</span>'
            f'<span class="badge badge-cond">{cond}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

        # Meta
        seller = listing.get("seller_name", "Unknown")
        date   = listing.get("created_at", "")[:10]
        st.markdown(
            f'<p class="card-meta">by {seller} · {date}</p>',
            unsafe_allow_html=True,
        )

        if not show_actions:
            return

        # Actions: View Details + heart
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

        # WhatsApp
        wa = listing.get("whatsapp", "")
        if wa and status == "available":
            clean = "".join(c for c in wa if c.isdigit() or c == "+")
            msg   = urllib.parse.quote(f"Hi! I saw your listing on ReNOVA: {listing['title']}")
            st.markdown(
                f'<a class="wa-btn" href="https://wa.me/{clean}?text={msg}" target="_blank">'
                f'Contact on WhatsApp</a>',
                unsafe_allow_html=True,
            )


# ── Housing card ───────────────────────────────────────────────────────────

def housing_card(listing: dict):
    user   = st.session_state.get("user")
    status = listing.get("status", "available")
    status_label, _, _ = STATUS_BADGE.get(status, STATUS_BADGE["available"])
    images = get_listing_images(listing)
    lid    = listing["id"]
    is_fav = lid in user.get("favorites", []) if user else False

    with st.container(border=True):
        # Image
        if images:
            img_path = BASE_DIR / images[0]
            if img_path.exists():
                st.image(str(img_path), use_container_width=True)
            else:
                _placeholder_housing()
        else:
            _placeholder_housing()

        # Location
        loc = listing.get("location", "")
        if loc:
            st.markdown(
                f'<p style="font-size:0.7rem;color:#9A80FF;letter-spacing:0.08em;'
                f'text-transform:uppercase;margin:6px 0 2px;">{loc}</p>',
                unsafe_allow_html=True,
            )

        # Title
        st.markdown(
            f'<p style="font-size:0.9rem;font-weight:600;color:#E8F4F4;'
            f'margin:0 0 2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">'
            f'{listing["title"]}</p>',
            unsafe_allow_html=True,
        )

        # Rent
        rent   = float(listing.get("price", 0))
        period = listing.get("rent_period", "month")
        st.markdown(
            f'<p style="font-size:1.05rem;font-weight:700;color:#B4A0FF;margin:0 0 4px;">'
            f'€{rent:.0f} / {period}</p>',
            unsafe_allow_html=True,
        )

        # Badges
        rooms       = listing.get("rooms", "")
        avail_from  = listing.get("available_from", "")
        badges_html = (
            f'<span class="badge badge-housing">Housing</span>'
            f'<span class="badge badge-{status_label}">{status_label.title()}</span>'
        )
        if rooms:
            badges_html += f'<span class="badge badge-cat">{rooms} room{"s" if str(rooms) != "1" else ""}</span>'
        st.markdown(f'<div style="margin-bottom:6px;">{badges_html}</div>', unsafe_allow_html=True)
        if avail_from:
            st.markdown(f'<p class="card-meta">Available from {avail_from}</p>', unsafe_allow_html=True)

        # Actions
        btn_d, btn_f = st.columns([4, 1])
        with btn_d:
            if st.button("View Details", key=f"det_{lid}", use_container_width=True):
                st.session_state.selected_listing_id = lid
                st.switch_page("pages/4_Listing_Detail.py")
        with btn_f:
            fav_symbol = "♥" if is_fav else "♡"
            if st.button(fav_symbol, key=f"fav_{lid}", help="Save"):
                if user:
                    new_favs = toggle_favorite(user["student_id"], lid)
                    st.session_state.user["favorites"] = new_favs
                    st.rerun()

        wa = listing.get("whatsapp", "")
        if wa and status == "available":
            clean = "".join(c for c in wa if c.isdigit() or c == "+")
            msg   = urllib.parse.quote(f"Hi! I saw your housing listing on ReNOVA: {listing['title']}")
            st.markdown(
                f'<a class="wa-btn" href="https://wa.me/{clean}?text={msg}" target="_blank">'
                f'Contact on WhatsApp</a>',
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
        '<div class="card-img-placeholder" style="background:linear-gradient(135deg,#000000 0%,#0A0020 100%);">'
        '<span class="cat-abbr" style="color:#2A1A5A;">HS</span>'
        '<span class="cat-label" style="color:#1A0A3A;">Housing</span>'
        '</div>',
        unsafe_allow_html=True,
    )
