import streamlit as st
from utils.db import ensure_dirs, load_listings
from utils.auth import login_user, register_user
from utils.ui import (inject_css, listing_card, sidebar_user,
                      show_logo, show_page_header,
                      CATEGORIES, CATEGORY_ICONS)

st.set_page_config(
    page_title="ReNOVA – Nova SBE Marketplace",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="expanded",
)

ensure_dirs()
inject_css()

if "user" not in st.session_state:
    st.session_state.user = None


# ── Login / Register ───────────────────────────────────────────────────────

def show_auth_page():
    _, col, _ = st.columns([1, 1.4, 1])
    with col:
        # ── Wordmark + tagline ──
        show_logo(width=260, tagline=True, description=True)

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
            '<p style="text-align:center;font-size:0.78rem;color:#4B5563;margin-top:1.5rem;">'
            'Only Nova SBE student IDs are accepted.</p>',
            unsafe_allow_html=True,
        )

    # ── Available listings counter ──
    _, col_count, _ = st.columns([1, 1.4, 1])
    with col_count:
        available = sum(1 for l in load_listings()["listings"] if l["status"] == "available")
        st.markdown(
            f'<p style="text-align:center;font-size:0.9rem;color:#4B5563;margin-top:0.5rem;">'
            f'<span style="color:#006D77;font-weight:700;font-size:1.3rem;">{available}</span>'
            f' listing{"s" if available != 1 else ""} available right now</p>',
            unsafe_allow_html=True,
        )


# ── Not logged in ──────────────────────────────────────────────────────────
if st.session_state.user is None:
    show_auth_page()
    st.stop()


# ── Logged-in home ─────────────────────────────────────────────────────────
sidebar_user()

with st.sidebar:
    st.markdown("### Navigate")
    st.page_link("app.py",                  label="Home")
    st.page_link("pages/1_Browse.py",       label="Browse")
    st.page_link("pages/2_Post_Listing.py", label="Post a Listing")
    st.page_link("pages/3_My_Profile.py",   label="My Profile")

# ── Header: ReNOVA left, My Profile right ─────────────────────────────────
col_brand, col_btns = st.columns([4, 1])
with col_brand:
    show_page_header()
with col_btns:
    st.write("")
    if st.button("My Profile", use_container_width=True):
        st.switch_page("pages/3_My_Profile.py")
    if st.button("Post a Listing", type="primary", use_container_width=True):
        st.switch_page("pages/2_Post_Listing.py")

st.divider()

# ── Load listings ──────────────────────────────────────────────────────────
all_listings = load_listings()["listings"]

# ── Search + filters (left) | Category table (right) ──────────────────────
col_search, col_table = st.columns([3, 1])

with col_search:
    search = st.text_input("", placeholder="Search listings…", label_visibility="collapsed")
    fc1, fc2 = st.columns(2)
    with fc1:
        cat_options = ["All Categories"] + CATEGORIES
        category = st.selectbox("", cat_options, label_visibility="collapsed")
    with fc2:
        sort_by = st.selectbox(
            "", ["Newest first", "Price: Low → High", "Price: High → Low"],
            label_visibility="collapsed",
        )

with col_table:
    rows_html = ""
    for cat in CATEGORIES:
        count = sum(1 for l in all_listings if l["category"] == cat and l["status"] != "sold")
        rows_html += (
            f'<tr>'
            f'<td class="cat-name">{cat.upper()}</td>'
            f'<td class="cat-count">{count}</td>'
            f'</tr>'
        )
    st.markdown(
        f'<div style="margin-top:0.4rem;">'
        f'<table class="cat-table">'
        f'<thead><tr><th colspan="2">Categories</th></tr></thead>'
        f'<tbody>{rows_html}</tbody>'
        f'</table></div>',
        unsafe_allow_html=True,
    )

st.write("")

# ── Filter listings ────────────────────────────────────────────────────────
listings = [l for l in all_listings if l["status"] != "sold"]

if search:
    q = search.lower()
    listings = [l for l in listings if q in l["title"].lower() or q in l.get("description", "").lower()]
if category != "All Categories":
    listings = [l for l in listings if l["category"] == category]

if sort_by == "Newest first":
    listings = sorted(listings, key=lambda x: x["created_at"], reverse=True)
elif sort_by == "Price: Low → High":
    listings = sorted(listings, key=lambda x: x.get("price", 0) if x.get("price_type") == "fixed" else 0)
else:
    listings = sorted(listings, key=lambda x: x.get("price", 0) if x.get("price_type") == "fixed" else 0, reverse=True)

# ── Listings grid ─────────────────────────────────────────────────────────
if not listings:
    st.info("No listings yet — be the first to post!")
    st.page_link("pages/2_Post_Listing.py", label="➕ Post a Listing")
else:
    COLS = 3
    for row_start in range(0, len(listings), COLS):
        cols = st.columns(COLS)
        for col_idx, listing in enumerate(listings[row_start: row_start + COLS]):
            with cols[col_idx]:
                listing_card(listing)
