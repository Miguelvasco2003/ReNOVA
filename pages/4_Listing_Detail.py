import urllib.parse
import streamlit as st
from utils.db import load_listings, get_listing_images, toggle_favorite, BASE_DIR
from utils.ui import inject_css, auth_gate, sidebar_user, sidebar_nav, sidebar_state

st.set_page_config(
    page_title="Listing – ReNOVA",
    page_icon="",
    layout="wide",
    initial_sidebar_state=sidebar_state(),
)

inject_css()
auth_gate()
sidebar_user()
sidebar_nav()

user = st.session_state.user

# ── Get listing ────────────────────────────────────────────────────────────
lid = st.session_state.get("selected_listing_id")
if not lid:
    st.error("No listing selected.")
    st.page_link("app.py", label="Back to Home")
    st.stop()

db       = load_listings()
listing  = next((l for l in db["listings"] if l["id"] == lid), None)

if not listing:
    st.error("Listing not found.")
    st.page_link("app.py", label="Back to Home")
    st.stop()

# ── Back button ────────────────────────────────────────────────────────────
if st.button("Back", key="detail_back"):
    st.switch_page("app.py")

st.markdown("<br/>", unsafe_allow_html=True)

# ── Layout ─────────────────────────────────────────────────────────────────
col_img, col_info = st.columns([1.4, 1])

images = get_listing_images(listing)

with col_img:
    if images:
        valid = [p for p in images if (BASE_DIR / p).exists()]
        if valid:
            # Show first image large
            st.image(str(BASE_DIR / valid[0]), use_container_width=True)
            # Thumbnails if multiple
            if len(valid) > 1:
                st.write("")
                thumb_cols = st.columns(min(len(valid), 5))
                for i, img_path in enumerate(valid[:5]):
                    with thumb_cols[i]:
                        st.image(str(BASE_DIR / img_path), use_container_width=True)
        else:
            st.markdown(
                '<div style="height:340px;background:#0A1818;border-radius:12px;'
                'display:flex;align-items:center;justify-content:center;">'
                '<span style="color:#2A4A4A;font-size:0.8rem;letter-spacing:0.1em;">NO PHOTO</span></div>',
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            '<div style="height:340px;background:#0A1818;border-radius:12px;'
            'display:flex;align-items:center;justify-content:center;">'
            '<span style="color:#2A4A4A;font-size:0.8rem;letter-spacing:0.1em;">NO PHOTO</span></div>',
            unsafe_allow_html=True,
        )

with col_info:
    is_housing = listing.get("listing_type") == "housing"

    # ── Status badge ───────────────────────────────────────────────────────
    status = listing.get("status", "available")
    badge_colors = {
        "available": ("#003D3F", "#83C5BE"),
        "reserved":  ("#3A2800", "#FDE68A"),
        "sold":      ("#3A0000", "#FCA5A5"),
    }
    bg, fg = badge_colors.get(status, badge_colors["available"])
    st.markdown(
        f'<span style="background:{bg};color:{fg};padding:4px 14px;border-radius:999px;'
        f'font-size:0.72rem;font-weight:600;letter-spacing:0.06em;">'
        f'{status.upper()}</span>',
        unsafe_allow_html=True,
    )
    st.markdown("<br/>", unsafe_allow_html=True)

    # ── Title ──────────────────────────────────────────────────────────────
    st.markdown(
        f'<h2 style="font-family:\'Playfair Display\',serif;color:#E8F4F4;'
        f'margin:0 0 8px;font-size:1.6rem;font-weight:900;">{listing["title"]}</h2>',
        unsafe_allow_html=True,
    )

    # ── Price ──────────────────────────────────────────────────────────────
    if is_housing:
        rent    = float(listing.get("price", 0))
        period  = listing.get("rent_period", "month")
        price_html = (
            f'<p style="font-size:1.6rem;font-weight:700;color:#B4A0FF;margin:0 0 12px;">'
            f'€{rent:.0f} <span style="font-size:0.9rem;color:#6A5A8A;">/ {period}</span></p>'
        )
    elif listing.get("price_type") == "offer":
        price_html = (
            '<p style="font-size:1.4rem;font-weight:700;color:#F59E0B;margin:0 0 12px;">Make an Offer</p>'
        )
    else:
        price = float(listing.get("price", 0))
        price_html = (
            f'<p style="font-size:1.6rem;font-weight:700;color:#83C5BE;margin:0 0 12px;">'
            f'€{price:.2f}</p>'
        )
    st.markdown(price_html, unsafe_allow_html=True)

    # ── Details grid ───────────────────────────────────────────────────────
    detail_rows = []
    if not is_housing:
        detail_rows.append(("Category",  listing.get("category", "")))
        detail_rows.append(("Condition", listing.get("condition", "")))
    else:
        detail_rows.append(("Location",  listing.get("location", "")))
        if listing.get("rooms"):
            detail_rows.append(("Rooms",    str(listing["rooms"])))
        if listing.get("available_from"):
            detail_rows.append(("Available from", listing["available_from"]))

    for label, val in detail_rows:
        if val:
            c1, c2 = st.columns([1, 2])
            c1.markdown(
                f'<span style="font-size:0.72rem;color:#3A5A5A;text-transform:uppercase;'
                f'letter-spacing:0.08em;">{label}</span>',
                unsafe_allow_html=True,
            )
            c2.markdown(
                f'<span style="font-size:0.82rem;color:#A8C8C8;font-weight:500;">{val}</span>',
                unsafe_allow_html=True,
            )

    st.markdown("<br/>", unsafe_allow_html=True)

    # ── Description ────────────────────────────────────────────────────────
    desc = listing.get("description", "")
    if desc:
        st.markdown(
            '<p style="font-size:0.72rem;color:#3A5A5A;text-transform:uppercase;'
            'letter-spacing:0.08em;margin-bottom:4px;">Description</p>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<p style="font-size:0.9rem;color:#A8C8C8;line-height:1.6;">{desc}</p>',
            unsafe_allow_html=True,
        )
        st.markdown("<br/>", unsafe_allow_html=True)

    # ── Seller ─────────────────────────────────────────────────────────────
    seller = listing.get("seller_name", "Unknown")
    date   = listing.get("created_at", "")[:10]
    st.markdown(
        f'<div style="background:#111F1F;border:1px solid #1E3232;border-radius:10px;padding:12px 16px;margin-bottom:12px;">'
        f'<p style="font-size:0.72rem;color:#3A5A5A;margin:0 0 4px;text-transform:uppercase;letter-spacing:0.08em;">Seller</p>'
        f'<p style="font-size:0.9rem;color:#E8F4F4;font-weight:600;margin:0;">{seller}</p>'
        f'<p style="font-size:0.72rem;color:#4A6A6A;margin:0;">Posted {date}</p>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── Contact button ─────────────────────────────────────────────────────
    wa = listing.get("whatsapp", "")
    if wa and status == "available":
        clean = "".join(c for c in wa if c.isdigit() or c == "+")
        msg   = urllib.parse.quote(
            f"Hi! I saw your listing on ReNOVA: {listing['title']}"
        )
        st.markdown(
            f'<a class="wa-btn" href="https://wa.me/{clean}?text={msg}" target="_blank" '
            f'style="font-size:0.95rem;padding:12px 0;border-radius:10px;">'
            f'Contact Seller on WhatsApp</a>',
            unsafe_allow_html=True,
        )

    st.markdown("<br/>", unsafe_allow_html=True)

    # ── Favorite button ────────────────────────────────────────────────────
    is_fav     = lid in user.get("favorites", [])
    fav_label  = "Remove from Saved" if is_fav else "Save Listing"
    if st.button(fav_label, key="detail_fav", use_container_width=True):
        new_favs = toggle_favorite(user["student_id"], lid)
        st.session_state.user["favorites"] = new_favs
        st.rerun()

    # ── Edit (own listing) ─────────────────────────────────────────────────
    if listing.get("seller_id") == user["student_id"]:
        st.markdown("<br/>", unsafe_allow_html=True)
        if st.button("Edit This Listing", key="detail_edit", use_container_width=True):
            st.session_state.edit_listing_id = lid
            st.switch_page("pages/5_Edit_Listing.py")
