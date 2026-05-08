import streamlit as st
import base64
from pathlib import Path
from utils.db import (
    load_listings, save_listings, load_users, save_users,
    get_profile_photo_path, save_profile_photo, IMAGES_DIR, BASE_DIR,
)
from utils.ui import (
    inject_css, sidebar_user, auth_gate, sidebar_nav,
    page_navbar, listing_card, housing_card, _avatar_html,
)

st.set_page_config(
    page_title="My Profile – ReNOVA",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()
auth_gate()
sidebar_user()
sidebar_nav()

user = st.session_state.user

# ── Navbar ─────────────────────────────────────────────────────────────────
page_navbar(search_key="profile_search")

# ── Header ─────────────────────────────────────────────────────────────────
col_hdr, col_home = st.columns([4, 1])
with col_hdr:
    st.markdown(
        '<h2 style="font-family:\'Playfair Display\',serif;color:#E8F4F4;margin:0;">My Profile</h2>',
        unsafe_allow_html=True,
    )
with col_home:
    st.write("")
    if st.button("Back to Home", type="primary", use_container_width=True, key="profile_home"):
        st.switch_page("app.py")

st.divider()

# ── Profile info + stats ───────────────────────────────────────────────────
db           = load_listings()
all_listings = db["listings"]
my_listings  = [l for l in all_listings if l["seller_id"] == user["student_id"]]
available    = sum(1 for l in my_listings if l["status"] == "available")
reserved     = sum(1 for l in my_listings if l["status"] == "reserved")
sold         = sum(1 for l in my_listings if l["status"] == "sold")

info_col, stats_col = st.columns([2, 1])

with info_col:
    with st.container(border=True):
        avatar_html = _avatar_html(user["student_id"], user["name"], size=64)
        email = user.get("email", f"{user['student_id']}@novasbe.pt")
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:16px;margin-bottom:10px;">'
            f'{avatar_html}'
            f'<div>'
            f'<h3 style="margin:0;color:#E8F4F4;">{user["name"]}</h3>'
            f'<p style="margin:2px 0;font-size:0.8rem;color:#4A6A6A;">{email}</p>'
            f'<p style="margin:2px 0;font-size:0.8rem;color:#4A6A6A;">WhatsApp: {user["whatsapp"]}</p>'
            f'</div></div>',
            unsafe_allow_html=True,
        )
        st.caption(f"Member since {user.get('created_at', '')[:10]}")

        # ── Profile photo upload ──────────────────────────────────────────
        with st.expander("Change Profile Photo"):
            new_photo = st.file_uploader(
                "Upload a new profile photo",
                type=["jpg", "jpeg", "png", "webp"],
                key="profile_photo_upload",
            )
            if new_photo is not None:
                st.session_state["_profile_photo_bytes"] = new_photo.getvalue()
                st.session_state["_profile_photo_name"]  = new_photo.name
                st.image(new_photo, width=120, caption="Preview")

            if st.button("Save Photo", key="save_photo_btn"):
                b = st.session_state.pop("_profile_photo_bytes", None)
                n = st.session_state.pop("_profile_photo_name", None)
                if b and n:
                    ext = Path(n).suffix.lower()
                    save_profile_photo(user["student_id"], ext, b)
                    # Reload user in session state
                    users_db = load_users()
                    st.session_state.user = users_db["users"][user["student_id"]]
                    st.success("Profile photo updated!")
                    st.rerun()
                else:
                    st.warning("Please upload a photo first.")

with stats_col:
    with st.container(border=True):
        st.metric("Total Posted", len(my_listings))
        c1, c2, c3 = st.columns(3)
        c1.metric("Active",   available)
        c2.metric("Reserved", reserved)
        c3.metric("Sold",     sold)

st.divider()

# ── Tabs ───────────────────────────────────────────────────────────────────
fav_ids    = user.get("favorites", [])
fav_count  = len(fav_ids)
tab_my, tab_favs = st.tabs([
    f"My Listings ({len(my_listings)})",
    f"Saved ({fav_count})",
])


# ── My Listings tab ────────────────────────────────────────────────────────
with tab_my:
    if not my_listings:
        st.info("You have not posted any listings yet.")
        st.page_link("pages/2_Post_Listing.py", label="Post your first listing")
    else:
        sub_tabs = st.tabs([
            f"All ({len(my_listings)})",
            f"Active ({available})",
            f"Reserved ({reserved})",
            f"Sold ({sold})",
        ])

        def render_manage(filtered):
            if not filtered:
                st.caption("Nothing here.")
                return
            COLS = 3
            for row_start in range(0, len(filtered), COLS):
                cols = st.columns(COLS)
                for col_idx, lst in enumerate(filtered[row_start: row_start + COLS]):
                    with cols[col_idx]:
                        # Show card without default action buttons (we add custom ones)
                        listing_card(lst, show_actions=False)

                        # ── Status changer ────────────────────────────────
                        status_opts = ["available", "reserved", "sold"]
                        cur_idx = status_opts.index(lst.get("status", "available"))
                        new_status = st.selectbox(
                            "Status",
                            status_opts,
                            index=cur_idx,
                            key=f"status_{lst['id']}",
                            format_func=lambda s: s.title(),
                        )

                        # ── Action buttons ────────────────────────────────
                        b1, b2, b3 = st.columns(3)
                        with b1:
                            if st.button("Update", key=f"upd_{lst['id']}", use_container_width=True):
                                db2 = load_listings()
                                for l in db2["listings"]:
                                    if l["id"] == lst["id"]:
                                        l["status"] = new_status
                                        break
                                save_listings(db2)
                                st.rerun()
                        with b2:
                            if st.button("Edit", key=f"edit_{lst['id']}", use_container_width=True):
                                st.session_state.edit_listing_id = lst["id"]
                                st.switch_page("pages/5_Edit_Listing.py")
                        with b3:
                            if st.button("Delete", key=f"del_{lst['id']}", use_container_width=True):
                                db2 = load_listings()
                                # Remove image files
                                from utils.db import get_listing_images
                                for img_rel in get_listing_images(lst):
                                    img_file = BASE_DIR / img_rel
                                    if img_file.exists():
                                        try:
                                            img_file.unlink()
                                        except Exception:
                                            pass
                                db2["listings"] = [
                                    l for l in db2["listings"] if l["id"] != lst["id"]
                                ]
                                save_listings(db2)
                                st.rerun()

        with sub_tabs[0]:
            render_manage(my_listings)
        with sub_tabs[1]:
            render_manage([l for l in my_listings if l["status"] == "available"])
        with sub_tabs[2]:
            render_manage([l for l in my_listings if l["status"] == "reserved"])
        with sub_tabs[3]:
            render_manage([l for l in my_listings if l["status"] == "sold"])


# ── Saved / Favorites tab ──────────────────────────────────────────────────
with tab_favs:
    if not fav_ids:
        st.info("You have not saved any listings yet. Click the heart icon on a listing to save it.")
    else:
        fav_listings = [l for l in all_listings if l["id"] in fav_ids]
        if not fav_listings:
            st.info("Your saved listings are no longer available.")
        else:
            marketplace_favs = [l for l in fav_listings if l.get("listing_type", "marketplace") == "marketplace"]
            housing_favs     = [l for l in fav_listings if l.get("listing_type") == "housing"]

            if marketplace_favs:
                st.markdown(
                    '<h4 style="color:#E8F4F4;margin-bottom:12px;">Marketplace</h4>',
                    unsafe_allow_html=True,
                )
                COLS = 3
                for row_start in range(0, len(marketplace_favs), COLS):
                    cols = st.columns(COLS)
                    for col_idx, lst in enumerate(marketplace_favs[row_start: row_start + COLS]):
                        with cols[col_idx]:
                            listing_card(lst)

            if housing_favs:
                st.markdown(
                    '<h4 style="color:#E8F4F4;margin:16px 0 12px;">Housing</h4>',
                    unsafe_allow_html=True,
                )
                COLS = 3
                for row_start in range(0, len(housing_favs), COLS):
                    cols = st.columns(COLS)
                    for col_idx, lst in enumerate(housing_favs[row_start: row_start + COLS]):
                        with cols[col_idx]:
                            housing_card(lst)
