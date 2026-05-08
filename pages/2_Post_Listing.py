import streamlit as st
import uuid
from datetime import datetime
from pathlib import Path
from utils.db import load_listings, save_listings, IMAGES_DIR
from utils.ui import inject_css, sidebar_user, auth_gate, sidebar_nav, CATEGORIES, CONDITIONS

st.set_page_config(
    page_title="Post a Listing – ReNOVA",
    page_icon="",
    layout="centered",
    initial_sidebar_state="expanded",
)

inject_css()
auth_gate()
sidebar_user()
sidebar_nav()

user = st.session_state.user

col_header, col_home = st.columns([4, 1])
with col_header:
    st.markdown(
        '<h2 style="font-family:\'Playfair Display\',serif;color:#E8F4F4;margin:0;">Post a Listing</h2>',
        unsafe_allow_html=True,
    )
with col_home:
    st.write("")
    if st.button("Back to Home", key="btn_home_top", type="primary", use_container_width=True):
        st.switch_page("app.py")

st.divider()

# ── Listing type selector ──────────────────────────────────────────────────
st.markdown("**What are you posting?**")
listing_type = st.radio(
    "listing_type_sel",
    ["Marketplace Item", "Housing / Room"],
    horizontal=True,
    label_visibility="collapsed",
    key="post_type",
)
is_housing = listing_type == "Housing / Room"
st.caption(
    "List a second-hand item, service or product."
    if not is_housing
    else "List a room or apartment for rent near Nova SBE."
)

st.divider()

# ── Form ──────────────────────────────────────────────────────────────────
with st.form("post_form", clear_on_submit=False):
    st.subheader("Basic Info")
    title = st.text_input(
        "Title *", max_chars=80,
        placeholder="MacBook Air M2 – 8GB / 256GB" if not is_housing else "Double room in Carcavelos apartment",
    )
    description = st.text_area(
        "Description *",
        max_chars=500,
        height=120,
        placeholder="Describe the item, condition, what is included…"
        if not is_housing else "Describe the room, flat, amenities, house rules…",
    )

    if not is_housing:
        c1, c2 = st.columns(2)
        with c1:
            category  = st.selectbox("Category *", CATEGORIES)
        with c2:
            condition = st.selectbox("Condition *", CONDITIONS)

        st.subheader("Pricing")
        price_type = st.radio("Pricing type", ["Fixed price", "Make an offer"], horizontal=True)
        price = None
        if price_type == "Fixed price":
            price = st.number_input("Price (€) *", min_value=0.0, max_value=10000.0,
                                    step=0.5, format="%.2f")
    else:
        location = st.text_input("Location *", placeholder="e.g. Carcavelos, Cascais, Lisboa")
        c1, c2, c3 = st.columns(3)
        with c1:
            rent = st.number_input("Monthly Rent (€) *", min_value=0.0, max_value=5000.0,
                                   step=10.0, format="%.0f")
        with c2:
            rooms = st.number_input("Number of Rooms", min_value=1, max_value=20, value=1)
        with c3:
            available_from = st.text_input("Available From", placeholder="e.g. June 2026")

    # ── Photos ──────────────────────────────────────────────────────────────
    st.subheader("Photos (optional)")
    uploaded_files = st.file_uploader(
        "Upload photos",
        type=["jpg", "jpeg", "png", "webp"],
        accept_multiple_files=True,
    )

    # Stash bytes inside form before submission clears the uploader
    if uploaded_files:
        st.session_state["_upload_files"] = [
            {"bytes": f.getvalue(), "name": f.name} for f in uploaded_files
        ]
        preview_cols = st.columns(min(len(uploaded_files), 4))
        for i, f in enumerate(uploaded_files[:4]):
            with preview_cols[i]:
                st.image(f, use_container_width=True)
    else:
        st.session_state.pop("_upload_files", None)

    st.divider()
    submitted = st.form_submit_button("Post Listing", type="primary", use_container_width=True)

if submitted:
    if not title.strip():
        st.error("Please add a title.")
    elif not description.strip():
        st.error("Please add a description.")
    elif is_housing and not locals().get("location", "").strip():
        st.error("Please add a location.")
    elif not is_housing and price_type == "Fixed price" and price == 0.0:
        st.warning("Are you sure the price is €0.00? You can also choose 'Make an offer'.")
        st.stop()
    else:
        # ── Save photos ────────────────────────────────────────────────────
        upload_data = st.session_state.pop("_upload_files", [])
        image_paths = []
        for f in upload_data:
            ext      = Path(f["name"]).suffix.lower()
            filename = f"{uuid.uuid4().hex}{ext}"
            (IMAGES_DIR / filename).write_bytes(f["bytes"])
            image_paths.append(f"images/{filename}")

        # ── Build listing ──────────────────────────────────────────────────
        listing: dict = {
            "id":           uuid.uuid4().hex,
            "title":        title.strip(),
            "description":  description.strip(),
            "seller_id":    user["student_id"],
            "seller_name":  user["name"],
            "whatsapp":     user["whatsapp"],
            "status":       "available",
            "images":       image_paths,
            "image_path":   image_paths[0] if image_paths else None,
            "created_at":   datetime.now().isoformat(),
            "listing_type": "housing" if is_housing else "marketplace",
        }

        if not is_housing:
            listing.update({
                "category":   category,
                "condition":  condition,
                "price":      float(price) if price_type == "Fixed price" else 0.0,
                "price_type": "fixed" if price_type == "Fixed price" else "offer",
            })
        else:
            listing.update({
                "location":       location.strip(),
                "price":          float(rent),
                "rent_period":    "month",
                "rooms":          int(rooms),
                "available_from": available_from.strip(),
                "price_type":     "fixed",
                "category":       "Housing",
                "condition":      "",
            })

        db = load_listings()
        db["listings"].append(listing)
        save_listings(db)

        st.success("Your listing has been posted!")
        st.balloons()
        col1, col2 = st.columns(2)
        with col1:
            st.page_link("app.py", label="Back to Home", use_container_width=True)
        with col2:
            st.page_link("pages/3_My_Profile.py", label="View My Listings", use_container_width=True)
