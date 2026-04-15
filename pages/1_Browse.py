import streamlit as st
from utils.db import load_listings
from utils.ui import inject_css, listing_card, sidebar_user, auth_gate, show_page_header, CATEGORIES, CATEGORY_ICONS

st.set_page_config(
    page_title="Browse – ReNOVA",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()
auth_gate()
sidebar_user()

with st.sidebar:
    st.markdown("### Navigate")
    st.page_link("app.py",                      label="🏠 Home")
    st.page_link("pages/1_Browse.py",            label="🔍 Browse Listings")
    st.page_link("pages/2_Post_Listing.py",      label="➕ Post a Listing")
    st.page_link("pages/3_My_Profile.py",        label="👤 My Profile")

show_page_header()
st.title("🔍 Browse Listings")
st.caption("Find what you're looking for across the Nova SBE community.")

# ── Filters ────────────────────────────────────────────────────────────────
with st.expander("Filters & Sort", expanded=True):
    fc1, fc2, fc3, fc4 = st.columns([2, 1.5, 1.5, 1.5])
    with fc1:
        search = st.text_input("Keyword search", placeholder="e.g. laptop, textbook…")
    with fc2:
        cat_opt  = ["All"] + CATEGORIES
        category = st.selectbox("Category", cat_opt)
    with fc3:
        cond_opt  = ["Any", "New", "Like New", "Good", "Fair", "Poor"]
        condition = st.selectbox("Condition", cond_opt)
    with fc4:
        status_opt = ["Available & Reserved", "Available only", "All"]
        status_filter = st.selectbox("Status", status_opt)

    sc1, sc2 = st.columns([2, 1])
    with sc1:
        price_range = st.slider("Max price (€)", 0, 2000, 2000, step=10)
    with sc2:
        sort_by = st.selectbox(
            "Sort by",
            ["Newest first", "Price: Low → High", "Price: High → Low"],
        )

# ── Load & filter ──────────────────────────────────────────────────────────
all_listings = load_listings()["listings"]

listings = all_listings

# Status
if status_filter == "Available only":
    listings = [l for l in listings if l["status"] == "available"]
elif status_filter == "Available & Reserved":
    listings = [l for l in listings if l["status"] in ("available", "reserved")]

# Category
if category != "All":
    listings = [l for l in listings if l["category"] == category]

# Condition
if condition != "Any":
    listings = [l for l in listings if l.get("condition") == condition]

# Keyword
if search:
    q = search.lower()
    listings = [
        l for l in listings
        if q in l["title"].lower() or q in l.get("description", "").lower()
    ]

# Price
listings = [
    l for l in listings
    if l.get("price_type") == "offer" or float(l.get("price", 0)) <= price_range
]

# Sort
if sort_by == "Newest first":
    listings = sorted(listings, key=lambda x: x["created_at"], reverse=True)
elif sort_by == "Price: Low → High":
    listings = sorted(listings, key=lambda x: float(x.get("price", 0)) if x.get("price_type") == "fixed" else 0)
else:
    listings = sorted(listings, key=lambda x: float(x.get("price", 0)) if x.get("price_type") == "fixed" else 0, reverse=True)

# ── Category chip counts ──────────────────────────────────────────────────
st.write("")
chip_cols = st.columns(len(CATEGORIES))
for i, cat in enumerate(CATEGORIES):
    count = sum(1 for l in all_listings if l["category"] == cat and l["status"] != "sold")
    with chip_cols[i]:
        icon = CATEGORY_ICONS[cat]
        label = f"{icon} **{cat}** ({count})"
        if st.button(label, use_container_width=True, key=f"chip_{cat}"):
            pass  # filter already handled above via selectbox

st.divider()
st.caption(f"Showing **{len(listings)}** listing(s)")

# ── Grid ──────────────────────────────────────────────────────────────────
if not listings:
    st.info("No listings match your filters.")
else:
    COLS = 3
    for row_start in range(0, len(listings), COLS):
        cols = st.columns(COLS)
        for col_idx, listing in enumerate(listings[row_start : row_start + COLS]):
            with cols[col_idx]:
                listing_card(listing)
