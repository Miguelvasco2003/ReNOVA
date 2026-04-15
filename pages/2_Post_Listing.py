import streamlit as st
import uuid
from datetime import datetime
from pathlib import Path
from PIL import Image
from utils.db import load_listings, save_listings, IMAGES_DIR
from utils.ui import inject_css, sidebar_user, auth_gate, show_page_header, CATEGORIES, CONDITIONS

st.set_page_config(
    page_title="Post a Listing – ReNOVA",
    page_icon="➕",
    layout="centered",
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

user = st.session_state.user

col_header, col_home = st.columns([4, 1])
with col_header:
    show_page_header()
with col_home:
    st.write("")
    if st.button("Back to Home", key="btn_home_top", type="primary", use_container_width=True):
        st.switch_page("app.py")

st.divider()
st.title("Post a Listing")
st.caption("Fill in the details below. Your WhatsApp number from your profile will be shown to buyers.")

with st.form("post_form", clear_on_submit=True):
    st.subheader("Basic Info")
    title = st.text_input("Title *", max_chars=80, placeholder="e.g. MacBook Air M2 – 8GB / 256GB")
    description = st.text_area(
        "Description *",
        max_chars=500,
        height=120,
        placeholder="Describe the item: condition details, reason for selling, what's included…",
    )

    c1, c2 = st.columns(2)
    with c1:
        category = st.selectbox("Category *", CATEGORIES)
    with c2:
        condition = st.selectbox("Condition *", CONDITIONS)

    st.subheader("Pricing")
    price_type = st.radio("Pricing type", ["Fixed price", "Make an offer"], horizontal=True)
    price = None
    if price_type == "Fixed price":
        price = st.number_input("Price (€) *", min_value=0.0, max_value=10000.0, step=0.5, format="%.2f")

    st.subheader("Photo (optional)")
    uploaded = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png", "webp"])

    if uploaded:
        st.image(uploaded, caption="Preview", width=280)

    st.divider()
    submitted = st.form_submit_button("🚀 Post Listing", type="primary", use_container_width=True)

if submitted:
    if not title.strip():
        st.error("Please add a title.")
    elif not description.strip():
        st.error("Please add a description.")
    elif price_type == "Fixed price" and price == 0.0:
        st.warning("Are you sure the price is €0.00? You can also choose 'Make an offer'.")
        st.stop()
    else:
        # Save image
        image_path = None
        if uploaded:
            ext = Path(uploaded.name).suffix.lower()
            filename = f"{uuid.uuid4().hex}{ext}"
            save_path = IMAGES_DIR / filename
            img = Image.open(uploaded)
            img.save(save_path)
            image_path = f"images/{filename}"

        # Build listing
        listing = {
            "id": uuid.uuid4().hex,
            "title": title.strip(),
            "description": description.strip(),
            "price": float(price) if price_type == "Fixed price" else 0.0,
            "price_type": "fixed" if price_type == "Fixed price" else "offer",
            "category": category,
            "condition": condition,
            "seller_id": user["student_id"],
            "seller_name": user["name"],
            "whatsapp": user["whatsapp"],
            "status": "available",
            "image_path": image_path,
            "created_at": datetime.now().isoformat(),
        }

        db = load_listings()
        db["listings"].append(listing)
        save_listings(db)

        st.success("Your listing has been posted!")
        st.balloons()
        col1, col2 = st.columns(2)
        with col1:
            st.page_link("app.py", label="← Back to Home", use_container_width=True)
        with col2:
            st.page_link("pages/3_My_Profile.py", label="View My Listings →", use_container_width=True)
