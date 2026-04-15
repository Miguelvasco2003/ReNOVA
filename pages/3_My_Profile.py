import streamlit as st
from utils.db import load_listings, save_listings, IMAGES_DIR
from utils.ui import inject_css, sidebar_user, auth_gate, show_page_header, listing_card, CATEGORY_ICONS
from pathlib import Path

st.set_page_config(
    page_title="My Profile – ReNOVA",
    page_icon="👤",
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

user = st.session_state.user

# ── Profile header ─────────────────────────────────────────────────────────
col_header, col_home = st.columns([4, 1])
with col_header:
    show_page_header()
with col_home:
    st.write("")
    if st.button("Back to Home", type="primary", use_container_width=True):
        st.switch_page("app.py")

st.divider()
st.title("My Profile")

info_col, stats_col = st.columns([2, 1])
with info_col:
    with st.container(border=True):
        st.markdown(f"### {user['name']}")
        st.markdown(f"📧 `{user['email']}`")
        st.markdown(f"💬 WhatsApp: `{user['whatsapp']}`")
        st.caption(f"Member since {user.get('created_at', '')[:10]}")

with stats_col:
    db = load_listings()
    my_listings = [l for l in db["listings"] if l["seller_id"] == user["student_id"]]
    available = sum(1 for l in my_listings if l["status"] == "available")
    reserved  = sum(1 for l in my_listings if l["status"] == "reserved")
    sold      = sum(1 for l in my_listings if l["status"] == "sold")

    with st.container(border=True):
        st.metric("Total Posted", len(my_listings))
        c1, c2, c3 = st.columns(3)
        c1.metric("Available", available)
        c2.metric("Reserved",  reserved)
        c3.metric("Sold",      sold)

st.divider()

# ── My listings management ─────────────────────────────────────────────────
st.subheader("My Listings")

if not my_listings:
    st.info("You haven't posted any listings yet.")
    st.page_link("pages/2_Post_Listing.py", label="➕ Post your first listing")
else:
    # Status filter tabs
    tab_all, tab_active, tab_reserved, tab_sold = st.tabs(
        [f"All ({len(my_listings)})",
         f"Available ({available})",
         f"Reserved ({reserved})",
         f"Sold ({sold})"]
    )

    def render_manage_listings(filtered):
        if not filtered:
            st.caption("Nothing here yet.")
            return
        COLS = 3
        for row_start in range(0, len(filtered), COLS):
            cols = st.columns(COLS)
            for col_idx, listing in enumerate(filtered[row_start : row_start + COLS]):
                with cols[col_idx]:
                    listing_card(listing)

                    # Status changer
                    status_opts = ["available", "reserved", "sold"]
                    current_idx = status_opts.index(listing.get("status", "available"))
                    new_status = st.selectbox(
                        "Status",
                        status_opts,
                        index=current_idx,
                        key=f"status_{listing['id']}",
                        format_func=lambda s: s.title(),
                    )

                    btn_col, del_col = st.columns(2)
                    with btn_col:
                        if st.button("Update", key=f"upd_{listing['id']}", use_container_width=True):
                            db2 = load_listings()
                            for l in db2["listings"]:
                                if l["id"] == listing["id"]:
                                    l["status"] = new_status
                                    break
                            save_listings(db2)
                            st.rerun()

                    with del_col:
                        if st.button("🗑 Delete", key=f"del_{listing['id']}", use_container_width=True):
                            db2 = load_listings()
                            # Remove image file if exists
                            img = listing.get("image_path")
                            if img:
                                img_file = Path(__file__).parent.parent / img
                                if img_file.exists():
                                    img_file.unlink()
                            db2["listings"] = [l for l in db2["listings"] if l["id"] != listing["id"]]
                            save_listings(db2)
                            st.rerun()

    with tab_all:
        render_manage_listings(my_listings)
    with tab_active:
        render_manage_listings([l for l in my_listings if l["status"] == "available"])
    with tab_reserved:
        render_manage_listings([l for l in my_listings if l["status"] == "reserved"])
    with tab_sold:
        render_manage_listings([l for l in my_listings if l["status"] == "sold"])
