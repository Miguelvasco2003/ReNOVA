import streamlit as st
import uuid
from pathlib import Path
from utils.db import load_listings, save_listings, IMAGES_DIR, get_listing_images, BASE_DIR
from utils.ui import inject_css, sidebar_user, auth_gate, sidebar_nav, CATEGORIES, CONDITIONS

st.set_page_config(
    page_title="Edit Listing – ReNOVA",
    page_icon="",
    layout="centered",
    initial_sidebar_state="expanded",
)

inject_css()
auth_gate()
sidebar_user()
sidebar_nav()

user = st.session_state.user

# ── Get listing to edit ────────────────────────────────────────────────────
lid = st.session_state.get("edit_listing_id")
if not lid:
    st.error("No listing selected for editing.")
    st.page_link("pages/3_My_Profile.py", label="Back to Profile")
    st.stop()

db      = load_listings()
listing = next((l for l in db["listings"] if l["id"] == lid), None)

if not listing:
    st.error("Listing not found.")
    st.page_link("pages/3_My_Profile.py", label="Back to Profile")
    st.stop()

if listing["seller_id"] != user["student_id"]:
    st.error("You can only edit your own listings.")
    st.stop()

# ── Header ─────────────────────────────────────────────────────────────────
col_hdr, col_back = st.columns([4, 1])
with col_hdr:
    st.markdown(
        '<h2 style="font-family:\'Playfair Display\',serif;color:#E8F4F4;margin:0;">Edit Listing</h2>',
        unsafe_allow_html=True,
    )
with col_back:
    st.write("")
    if st.button("Back", key="edit_back", use_container_width=True):
        st.switch_page("pages/3_My_Profile.py")

st.divider()

# ── Show existing photos ───────────────────────────────────────────────────
existing_images = get_listing_images(listing)
remaining_images = list(existing_images)

if existing_images:
    st.markdown("**Current Photos**")
    photo_cols = st.columns(min(len(existing_images), 4))
    for i, img_rel in enumerate(existing_images):
        img_path = BASE_DIR / img_rel
        with photo_cols[i % 4]:
            if img_path.exists():
                st.image(str(img_path), use_container_width=True)
            if st.button(f"Remove photo {i+1}", key=f"rm_photo_{i}"):
                remaining_images = [p for p in remaining_images if p != img_rel]
                # Delete file
                if img_path.exists():
                    try:
                        img_path.unlink()
                    except Exception:
                        pass
                st.session_state[f"_rm_photo_{i}"] = True
    st.write("")

# ── Determine listing type ─────────────────────────────────────────────────
is_housing = listing.get("listing_type") == "housing"

# ── Edit form ─────────────────────────────────────────────────────────────
with st.form("edit_form"):
    st.subheader("Basic Info")
    title = st.text_input(
        "Title *", value=listing.get("title", ""), max_chars=80
    )
    description = st.text_area(
        "Description *",
        value=listing.get("description", ""),
        max_chars=500,
        height=120,
    )

    if not is_housing:
        c1, c2 = st.columns(2)
        with c1:
            cat_idx  = CATEGORIES.index(listing["category"]) if listing.get("category") in CATEGORIES else 0
            category = st.selectbox("Category *", CATEGORIES, index=cat_idx)
        with c2:
            cond_idx  = CONDITIONS.index(listing["condition"]) if listing.get("condition") in CONDITIONS else 0
            condition = st.selectbox("Condition *", CONDITIONS, index=cond_idx)

        st.subheader("Pricing")
        current_type = "Fixed price" if listing.get("price_type") == "fixed" else "Make an offer"
        price_type = st.radio("Pricing type", ["Fixed price", "Make an offer"], horizontal=True,
                              index=0 if current_type == "Fixed price" else 1)
        price = None
        if price_type == "Fixed price":
            price = st.number_input(
                "Price (€) *",
                min_value=0.0, max_value=10000.0, step=0.5, format="%.2f",
                value=float(listing.get("price", 0)),
            )
    else:
        location = st.text_input("Location *", value=listing.get("location", ""))
        c1, c2 = st.columns(2)
        with c1:
            rent = st.number_input("Monthly Rent (€) *", min_value=0.0, max_value=10000.0,
                                   step=10.0, format="%.0f", value=float(listing.get("price", 0)))
        with c2:
            rooms = st.number_input("Number of Rooms", min_value=1, max_value=20,
                                    value=int(listing.get("rooms", 1)))
        available_from = st.text_input("Available From", value=listing.get("available_from", ""),
                                       placeholder="e.g. June 2026")

    st.subheader("Add More Photos")
    new_uploads = st.file_uploader(
        "Upload additional photos (optional)",
        type=["jpg", "jpeg", "png", "webp"],
        accept_multiple_files=True,
    )
    if new_uploads:
        previews = st.columns(min(len(new_uploads), 4))
        for i, f in enumerate(new_uploads):
            st.session_state[f"_new_photo_{i}_bytes"] = f.getvalue()
            st.session_state[f"_new_photo_{i}_name"]  = f.name
            with previews[i % 4]:
                st.image(f, use_container_width=True)
        st.session_state["_new_photo_count"] = len(new_uploads)
    else:
        st.session_state["_new_photo_count"] = 0

    st.divider()
    submitted = st.form_submit_button("Save Changes", type="primary", use_container_width=True)

if submitted:
    if not title.strip():
        st.error("Please add a title.")
    elif not description.strip():
        st.error("Please add a description.")
    else:
        # Save new photos
        new_count = st.session_state.pop("_new_photo_count", 0)
        for i in range(new_count):
            b = st.session_state.pop(f"_new_photo_{i}_bytes", None)
            n = st.session_state.pop(f"_new_photo_{i}_name", None)
            if b and n:
                ext = Path(n).suffix.lower()
                fname = f"{uuid.uuid4().hex}{ext}"
                (IMAGES_DIR / fname).write_bytes(b)
                remaining_images.append(f"images/{fname}")

        # Update listing
        db2 = load_listings()
        for l in db2["listings"]:
            if l["id"] == lid:
                l["title"]       = title.strip()
                l["description"] = description.strip()
                l["images"]      = remaining_images
                l["image_path"]  = remaining_images[0] if remaining_images else None

                if not is_housing:
                    l["category"]   = category
                    l["condition"]  = condition
                    l["price_type"] = "fixed" if price_type == "Fixed price" else "offer"
                    l["price"]      = float(price) if price_type == "Fixed price" else 0.0
                else:
                    l["location"]       = location.strip()
                    l["price"]          = float(rent)
                    l["rooms"]          = int(rooms)
                    l["available_from"] = available_from.strip()
                break

        save_listings(db2)
        st.success("Listing updated!")
        st.page_link("pages/3_My_Profile.py", label="Back to My Profile")
