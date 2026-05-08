import streamlit as st
from utils.db import load_listings
from utils.ui import inject_css, auth_gate, sidebar_user, page_navbar, housing_card

st.set_page_config(
    page_title="Housing – ReNOVA",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()
auth_gate()
sidebar_user()

# ── Navbar ─────────────────────────────────────────────────────────────────
search_nav = page_navbar(
    search_placeholder="Search rooms, locations…",
    search_key="housing_nav_search",
)

# ── Header ─────────────────────────────────────────────────────────────────
col_hdr, col_btn = st.columns([4, 1])
with col_hdr:
    st.markdown(
        '<h2 style="font-family:\'Playfair Display\',serif;color:#E8F4F4;margin:0;">Housing</h2>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p style="color:#6A5A8A;font-size:0.85rem;margin:2px 0 0;">'
        'Rooms and apartments from the Nova SBE community — find your next home near campus.</p>',
        unsafe_allow_html=True,
    )
with col_btn:
    if st.button("Post a Room", type="primary", use_container_width=True, key="housing_post_btn"):
        st.session_state.post_listing_type = "housing"
        st.switch_page("pages/2_Post_Listing.py")

st.divider()

# ── Filters ────────────────────────────────────────────────────────────────
fc1, fc2, fc3 = st.columns([3, 1.5, 1.5])
with fc1:
    keyword = st.text_input(
        "Search",
        placeholder="Location, type of room…",
        label_visibility="collapsed",
        key="housing_keyword",
    )
with fc2:
    max_rent = st.number_input(
        "Max rent (€/month)",
        min_value=0, max_value=5000, value=3000, step=50,
        label_visibility="collapsed",
        key="housing_max_rent",
    )
with fc3:
    sort_by = st.selectbox(
        "Sort",
        ["Newest first", "Rent: Low to High", "Rent: High to Low"],
        label_visibility="collapsed",
        key="housing_sort",
    )

st.write("")

# ── Load & filter ──────────────────────────────────────────────────────────
all_listings = load_listings()["listings"]
listings = [
    l for l in all_listings
    if l.get("listing_type") == "housing" and l["status"] != "sold"
]

# Combine navbar search + keyword field
active_search = search_nav or keyword
if active_search:
    q = active_search.lower()
    listings = [
        l for l in listings
        if q in l["title"].lower()
        or q in l.get("description", "").lower()
        or q in l.get("location", "").lower()
    ]

listings = [l for l in listings if float(l.get("price", 0)) <= max_rent]

if sort_by == "Rent: Low to High":
    listings = sorted(listings, key=lambda x: float(x.get("price", 0)))
elif sort_by == "Rent: High to Low":
    listings = sorted(listings, key=lambda x: float(x.get("price", 0)), reverse=True)
else:
    listings = sorted(listings, key=lambda x: x["created_at"], reverse=True)

# ── Results ────────────────────────────────────────────────────────────────
rc1, rc2 = st.columns([4, 1])
with rc1:
    st.markdown(
        f'<p style="font-size:0.8rem;color:#444444;">'
        f'{len(listings)} listing{"s" if len(listings) != 1 else ""} found</p>',
        unsafe_allow_html=True,
    )

st.write("")

# ── Grid ───────────────────────────────────────────────────────────────────
if not listings:
    st.markdown(
        '<div style="background:#050010;border:1px dashed #2A1A5A;border-radius:14px;'
        'padding:40px;text-align:center;margin-top:12px;">'
        '<p style="color:#3A2A5A;font-size:1rem;font-weight:600;margin:0 0 8px;">'
        'No housing listings yet</p>'
        '<p style="color:#2A1A4A;font-size:0.82rem;margin:0;">'
        'Be the first to post a room or apartment for the Nova SBE community.</p>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.write("")
    col_cta, _ = st.columns([1, 3])
    with col_cta:
        if st.button("Post the first listing", type="primary", use_container_width=True):
            st.session_state.post_listing_type = "housing"
            st.switch_page("pages/2_Post_Listing.py")
else:
    COLS = 3
    for row_start in range(0, len(listings), COLS):
        cols = st.columns(COLS)
        for col_idx, listing in enumerate(listings[row_start: row_start + COLS]):
            with cols[col_idx]:
                housing_card(listing)
