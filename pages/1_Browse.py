import streamlit as st
from utils.db import load_listings
from utils.ui import (
    inject_css, listing_card, housing_card, sidebar_user, sidebar_nav,
    auth_gate, page_navbar, CATEGORIES, CATEGORY_ICONS, sidebar_state,
)

st.set_page_config(
    page_title="Browse – ReNOVA",
    page_icon="",
    layout="wide",
    initial_sidebar_state=sidebar_state(),
)

inject_css()
auth_gate()
sidebar_user()
sidebar_nav()

# ── Navbar ─────────────────────────────────────────────────────────────────
search = page_navbar(search_placeholder="Search listings…", search_key="browse_search")

st.markdown(
    '<h2 style="font-family:\'Playfair Display\',serif;color:#E8F4F4;margin:0 0 4px;">Browse Listings</h2>',
    unsafe_allow_html=True,
)
st.caption("Find what you are looking for across the Nova SBE community.")

# ── Listing type toggle ─────────────────────────────────────────────────────
listing_type = st.radio(
    "Type",
    ["Marketplace", "Housing"],
    horizontal=True,
    label_visibility="collapsed",
    key="browse_type",
)

st.write("")

all_data   = load_listings()["listings"]
is_housing = listing_type == "Housing"

if is_housing:
    pool = [l for l in all_data if l.get("listing_type") == "housing"]
else:
    pool = [l for l in all_data if l.get("listing_type", "marketplace") == "marketplace"]

# ── Filters ────────────────────────────────────────────────────────────────
with st.expander("Filters & Sort", expanded=True):
    if not is_housing:
        fc1, fc2, fc3, fc4 = st.columns([2, 1.5, 1.5, 1.5])
        with fc1:
            keyword = st.text_input("Keyword", placeholder="e.g. laptop, textbook…", key="browse_kw")
        with fc2:
            cat_opt  = ["All"] + CATEGORIES
            category = st.selectbox("Category", cat_opt, key="browse_cat")
        with fc3:
            cond_opt  = ["Any", "New", "Like New", "Good", "Fair", "Poor"]
            condition = st.selectbox("Condition", cond_opt, key="browse_cond")
        with fc4:
            status_opt    = ["Available & Reserved", "Available only", "All"]
            status_filter = st.selectbox("Status", status_opt, key="browse_status")
        sc1, sc2 = st.columns([2, 1])
        with sc1:
            price_range = st.slider("Max price (€)", 0, 2000, 2000, step=10, key="browse_price")
        with sc2:
            sort_by = st.selectbox(
                "Sort by",
                ["Newest first", "Price: Low to High", "Price: High to Low"],
                key="browse_sort",
            )
    else:
        hc1, hc2, hc3 = st.columns([2, 1.5, 1.5])
        with hc1:
            keyword = st.text_input("Keyword", placeholder="e.g. Carcavelos, studio…", key="browse_kw_h")
        with hc2:
            price_range = st.slider("Max rent / month (€)", 0, 3000, 3000, step=50, key="browse_rent")
        with hc3:
            sort_by = st.selectbox(
                "Sort by",
                ["Newest first", "Rent: Low to High", "Rent: High to Low"],
                key="browse_sort_h",
            )
        category, condition, status_filter = "All", "Any", "Available & Reserved"

# ── Apply filters ──────────────────────────────────────────────────────────
listings = pool

# Status
if status_filter == "Available only":
    listings = [l for l in listings if l["status"] == "available"]
elif status_filter == "Available & Reserved":
    listings = [l for l in listings if l["status"] in ("available", "reserved")]

if not is_housing:
    if category != "All":
        listings = [l for l in listings if l["category"] == category]
    if condition != "Any":
        listings = [l for l in listings if l.get("condition") == condition]
    listings = [
        l for l in listings
        if l.get("price_type") == "offer" or float(l.get("price", 0)) <= price_range
    ]
else:
    listings = [l for l in listings if float(l.get("price", 0)) <= price_range]

# Keyword (uses 'search' from navbar OR the expander keyword field)
active_search = search or keyword if not is_housing else search or st.session_state.get("browse_kw_h", "")
if active_search:
    q = active_search.lower()
    listings = [
        l for l in listings
        if q in l["title"].lower() or q in l.get("description", "").lower()
        or q in l.get("location", "").lower()
    ]

# Sort
if "Low to High" in sort_by:
    listings = sorted(listings, key=lambda x: float(x.get("price", 0)))
elif "High to Low" in sort_by:
    listings = sorted(listings, key=lambda x: float(x.get("price", 0)), reverse=True)
else:
    listings = sorted(listings, key=lambda x: x["created_at"], reverse=True)

# ── Results count ──────────────────────────────────────────────────────────
st.markdown("<br/>", unsafe_allow_html=True)
st.caption(f"Showing **{len(listings)}** listing(s)")

# ── Grid ──────────────────────────────────────────────────────────────────
if not listings:
    st.info("No listings match your filters.")
    st.page_link("pages/2_Post_Listing.py", label="Post a Listing")
else:
    COLS = 3
    for row_start in range(0, len(listings), COLS):
        cols = st.columns(COLS)
        for col_idx, listing in enumerate(listings[row_start: row_start + COLS]):
            with cols[col_idx]:
                if is_housing:
                    housing_card(listing)
                else:
                    listing_card(listing)
