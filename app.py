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
        show_logo(width=260, tagline=True)

        st.write("")

        # ── Category pills ──
        cat_html = "".join(
            f'<span style="display:inline-block;padding:4px 14px;margin:0 6px 6px 0;'
            f'border:1px solid #2A2A2A;border-radius:999px;font-size:0.78rem;'
            f'color:#83C5BE;letter-spacing:0.04em;">{cat}</span>'
            for cat in CATEGORIES
        )
        st.markdown(f'<div style="margin-bottom:1rem;">{cat_html}</div>', unsafe_allow_html=True)

        # ── Available listings counter ──
        all_listings = load_listings()["listings"]
        available = sum(1 for l in all_listings if l["status"] == "available")
        st.markdown(
            f'<p style="font-size:0.85rem;color:#4B5563;margin-bottom:1.5rem;">'
            f'<span style="color:#006D77;font-weight:600;">{available}</span>'
            f' listing{"s" if available != 1 else ""} available right now</p>',
            unsafe_allow_html=True,
        )

        st.divider()

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


# ── Not logged in ──────────────────────────────────────────────────────────
if st.session_state.user is None:
    show_auth_page()
    st.stop()


# ── Logged-in home ─────────────────────────────────────────────────────────
sidebar_user()

with st.sidebar:
    st.markdown("### Navigate")
    st.page_link("app.py",                 label="🏠 Home")
    st.page_link("pages/1_Browse.py",      label="🔍 Browse")
    st.page_link("pages/2_Post_Listing.py",label="➕ Post a Listing")
    st.page_link("pages/3_My_Profile.py",  label="👤 My Profile")

show_page_header()

# ── Search + filter bar ────────────────────────────────────────────────────
c1, c2, c3 = st.columns([3, 1.5, 1.5])
with c1:
    search = st.text_input("", placeholder="🔍  Search listings…", label_visibility="collapsed")
with c2:
    cat_options = ["All Categories"] + CATEGORIES
    category = st.selectbox("", cat_options, label_visibility="collapsed")
with c3:
    sort_by = st.selectbox(
        "", ["Newest first", "Price: Low → High", "Price: High → Low"],
        label_visibility="collapsed",
    )

# ── Load & filter ──────────────────────────────────────────────────────────
all_listings = load_listings()["listings"]
listings = [l for l in all_listings if l["status"] != "sold"]

if search:
    q = search.lower()
    listings = [
        l for l in listings
        if q in l["title"].lower() or q in l.get("description", "").lower()
    ]
if category != "All Categories":
    listings = [l for l in listings if l["category"] == category]

if sort_by == "Newest first":
    listings = sorted(listings, key=lambda x: x["created_at"], reverse=True)
elif sort_by == "Price: Low → High":
    listings = sorted(listings, key=lambda x: x.get("price", 0) if x.get("price_type") == "fixed" else 0)
else:
    listings = sorted(listings, key=lambda x: x.get("price", 0) if x.get("price_type") == "fixed" else 0, reverse=True)

# ── Stats strip ───────────────────────────────────────────────────────────
total  = len(all_listings)
active = sum(1 for l in all_listings if l["status"] == "available")
res    = sum(1 for l in all_listings if l["status"] == "reserved")

m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Listings", total)
m2.metric("Available",      active)
m3.metric("Reserved",       res)
m4.metric("Showing",        len(listings))

st.divider()

# ── Category chips ────────────────────────────────────────────────────────
chip_cols = st.columns(len(CATEGORIES))
for i, (cat, icon) in enumerate(CATEGORY_ICONS.items()):
    count = sum(1 for l in all_listings if l["category"] == cat and l["status"] != "sold")
    with chip_cols[i]:
        st.button(f"{icon} {cat} ({count})", use_container_width=True, key=f"chip_{cat}")

st.write("")

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
