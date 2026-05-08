import streamlit as st
from utils.db import ensure_dirs, load_listings
from utils.auth import login_user, register_user
from utils.ui import (
    inject_css, listing_card, housing_card, sidebar_user, sidebar_nav,
    show_logo, page_navbar, CATEGORIES, CATEGORY_ICONS,
)

st.set_page_config(
    page_title="ReNOVA – Nova SBE Marketplace",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

ensure_dirs()
inject_css()

if "user" not in st.session_state:
    st.session_state.user = None


# ── Auth page ──────────────────────────────────────────────────────────────

def show_auth_page():
    st.markdown(
        """<style>
        section[data-testid="stSidebar"] { display: none !important; }
        [data-testid="stSidebarNav"]     { display: none !important; }
        .stApp { background: #000000 !important; }
        .block-container {
            padding-top: 4rem !important;
            padding-left: 0 !important;
            padding-right: 0 !important;
            max-width: 100% !important;
        }
        [data-testid="stImage"] img {
            height: auto !important;
            border-radius: 0 !important;
            object-fit: contain !important;
        }
        [data-testid="stForm"] { padding: 2rem 2.5rem !important; }
        </style>""",
        unsafe_allow_html=True,
    )

    _, col, _ = st.columns([1.5, 2, 1.5])
    with col:
        show_logo(width=600, tagline=False, description=False)

        tab_login, tab_register = st.tabs(["Login", "Create Account"])

        with tab_login:
            with st.form("login_form"):
                student_id = st.text_input("Student ID", placeholder="e.g. 12345")
                password   = st.text_input("Password", type="password")
                submitted  = st.form_submit_button("Login", use_container_width=True, type="primary")

            if submitted:
                if not student_id or not password:
                    st.error("Please fill in all fields.")
                else:
                    ok, user = login_user(student_id, password)
                    if ok:
                        st.session_state.user = user
                        st.rerun()
                    else:
                        st.error("Invalid Student ID or password.")

        with tab_register:
            with st.form("register_form"):
                r_name      = st.text_input("Full Name", placeholder="e.g. Ana Costa")
                r_id        = st.text_input("Student ID", placeholder="e.g. 12345")
                r_whatsapp  = st.text_input("WhatsApp Number", placeholder="+351 9XX XXX XXX")
                r_password  = st.text_input("Password", type="password")
                r_password2 = st.text_input("Confirm Password", type="password")
                r_submitted = st.form_submit_button("Create Account", use_container_width=True, type="primary")

            if r_submitted:
                if not all([r_name, r_id, r_whatsapp, r_password, r_password2]):
                    st.error("Please fill in all fields.")
                elif r_password != r_password2:
                    st.error("Passwords do not match.")
                else:
                    ok, msg = register_user(r_id, r_password, r_name, r_whatsapp)
                    if ok:
                        st.success(msg + " You can now log in.")
                    else:
                        st.error(msg)

        st.markdown(
            '<p style="text-align:center;font-size:0.78rem;color:#444444;margin-top:1.5rem;">'
            'Only Nova SBE student IDs are accepted.</p>',
            unsafe_allow_html=True,
        )

    _, col_count, _ = st.columns([1, 1.4, 1])
    with col_count:
        available = sum(1 for l in load_listings()["listings"] if l["status"] == "available")
        st.markdown(
            f'<p style="text-align:center;font-size:0.9rem;color:#444444;margin-top:0.5rem;">'
            f'<span style="color:#006D77;font-weight:700;font-size:1.3rem;">{available}</span>'
            f' listing{"s" if available != 1 else ""} available right now</p>',
            unsafe_allow_html=True,
        )


# ── Not logged in ──────────────────────────────────────────────────────────
if st.session_state.user is None:
    show_auth_page()
    st.stop()


# ── Logged-in layout ───────────────────────────────────────────────────────
sidebar_user()   # nav links + user info all handled inside

# ── Navbar ─────────────────────────────────────────────────────────────────
search = page_navbar(search_placeholder="Search listings…", search_key="home_search")

# ── Page title + Post button ───────────────────────────────────────────────
col_title, col_post = st.columns([5, 1])
with col_title:
    st.markdown(
        '<h2 style="font-family:\'Playfair Display\',serif;'
        'color:#E8F4F4;font-weight:900;margin:0;">Home</h2>',
        unsafe_allow_html=True,
    )
with col_post:
    if st.button("Post a Listing", type="primary", use_container_width=True, key="btn_post"):
        st.switch_page("pages/2_Post_Listing.py")

st.divider()

# ── Load all listings ──────────────────────────────────────────────────────
all_listings = load_listings()["listings"]
marketplace  = [l for l in all_listings if l.get("listing_type", "marketplace") == "marketplace"]
housing_lst  = [l for l in all_listings if l.get("listing_type") == "housing"]

# ── Category chips + sort on same row ──────────────────────────────────────
counts = {"All": sum(1 for l in marketplace if l["status"] != "sold")}
for cat in CATEGORIES:
    counts[cat] = sum(1 for l in marketplace if l["category"] == cat and l["status"] != "sold")

chips_col, sort_col = st.columns([5, 1.5])
with chips_col:
    selected_cat = st.radio(
        "category_filter",
        ["All"] + CATEGORIES,
        horizontal=True,
        label_visibility="collapsed",
        format_func=lambda x: f"All ({counts['All']})" if x == "All" else f"{x} ({counts[x]})",
    )
with sort_col:
    sort_by = st.selectbox(
        "Sort",
        ["Newest first", "Price: Low to High", "Price: High to Low"],
        label_visibility="collapsed",
        key="home_sort",
    )

st.write("")

# ── Filter marketplace listings ────────────────────────────────────────────
listings = [l for l in marketplace if l["status"] != "sold"]

if search:
    q = search.lower()
    listings = [l for l in listings if q in l["title"].lower() or q in l.get("description", "").lower()]
if selected_cat != "All":
    listings = [l for l in listings if l["category"] == selected_cat]

if sort_by == "Newest first":
    listings = sorted(listings, key=lambda x: x["created_at"], reverse=True)
elif sort_by == "Price: Low to High":
    listings = sorted(listings, key=lambda x: x.get("price", 0) if x.get("price_type") == "fixed" else 0)
else:
    listings = sorted(listings, key=lambda x: x.get("price", 0) if x.get("price_type") == "fixed" else 0, reverse=True)

# ── Results count ──────────────────────────────────────────────────────────
lc1, lc2 = st.columns([4, 1])
with lc1:
    st.markdown(
        '<h3 style="font-family:\'Playfair Display\',serif;color:#E8F4F4;margin:0;">Marketplace</h3>',
        unsafe_allow_html=True,
    )
with lc2:
    st.markdown(
        f'<div style="text-align:right;padding-top:6px;">'
        f'<span style="background:#0D0D0D;border:1px solid #1A1A1A;border-radius:999px;'
        f'padding:4px 12px;font-size:0.75rem;color:#444444;">'
        f'{len(listings)} result{"s" if len(listings) != 1 else ""}</span></div>',
        unsafe_allow_html=True,
    )

st.write("")

# ── Listings grid ──────────────────────────────────────────────────────────
if not listings:
    st.info("No listings yet — be the first to post!")
    st.page_link("pages/2_Post_Listing.py", label="Post a Listing")
else:
    COLS = 3
    for row_start in range(0, len(listings), COLS):
        cols = st.columns(COLS)
        for col_idx, listing in enumerate(listings[row_start: row_start + COLS]):
            with cols[col_idx]:
                listing_card(listing)


# ── Housing section ────────────────────────────────────────────────────────
st.markdown("<br/>", unsafe_allow_html=True)
st.divider()

# Housing header banner
st.markdown(
    '<div class="housing-section-header">'
    '<h3 style="font-family:\'Playfair Display\',serif;color:#E8F4F4;margin:0 0 4px;font-size:1.4rem;">'
    'Housing</h3>'
    '<p style="color:#6A5A8A;font-size:0.85rem;margin:0 0 12px;">'
    'Rooms and apartments shared by the Nova SBE community — find your next home near campus.</p>'
    '</div>',
    unsafe_allow_html=True,
)

post_h_col, _ = st.columns([1, 4])
with post_h_col:
    if st.button("Post a Room or Apartment", type="primary", use_container_width=True, key="btn_post_housing"):
        st.session_state.post_listing_type = "housing"
        st.switch_page("pages/2_Post_Listing.py")

st.write("")

active_housing = [l for l in housing_lst if l["status"] != "sold"]
if not active_housing:
    st.markdown(
        '<div style="background:#050010;border:1px dashed #2A1A5A;border-radius:12px;'
        'padding:24px;text-align:center;">'
        '<p style="color:#3A2A5A;font-size:0.9rem;margin:0;">'
        'No housing listings yet. Be the first to post a room!</p>'
        '</div>',
        unsafe_allow_html=True,
    )
else:
    COLS = 3
    for row_start in range(0, len(active_housing), COLS):
        cols = st.columns(COLS)
        for col_idx, listing in enumerate(active_housing[row_start: row_start + COLS]):
            with cols[col_idx]:
                housing_card(listing)
