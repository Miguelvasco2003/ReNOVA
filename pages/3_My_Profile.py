import streamlit as st
from pathlib import Path
from utils.db import (
    load_listings, save_listings, load_users, save_users,
    get_profile_photo_path, save_profile_photo, get_listing_images,
    IMAGES_DIR, BASE_DIR,
)
from utils.ui import (
    inject_css, sidebar_user, auth_gate, sidebar_nav,
    page_navbar, listing_card, housing_card, _avatar_html, sidebar_state,
)

st.set_page_config(
    page_title="My Profile – ReNOVA",
    page_icon="",
    layout="wide",
    initial_sidebar_state=sidebar_state(),
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

# ── Load data ──────────────────────────────────────────────────────────────
db           = load_listings()
all_listings = db["listings"]
my_listings  = [l for l in all_listings if l["seller_id"] == user["student_id"]]
available    = sum(1 for l in my_listings if l["status"] == "available")
reserved     = sum(1 for l in my_listings if l["status"] == "reserved")
sold         = sum(1 for l in my_listings if l["status"] == "sold")
fav_ids      = user.get("favorites", [])
fav_count    = len(fav_ids)

# ── Profile info + stats ───────────────────────────────────────────────────
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
            f'<p style="margin:2px 0;font-size:0.8rem;color:#444444;">{email}</p>'
            f'<p style="margin:2px 0;font-size:0.8rem;color:#444444;">WhatsApp: {user["whatsapp"]}</p>'
            f'</div></div>',
            unsafe_allow_html=True,
        )
        st.caption(f"Member since {user.get('created_at', '')[:10]}")

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

# ── Tab navigation (radio styled as chips, selectable via session state) ────
tab_options = [
    f"My Listings ({len(my_listings)})",
    f"Saved ({fav_count})",
]
# profile_active_tab is set by the navbar "Saved" button
default_tab_idx = st.session_state.pop("profile_active_tab", 0)

active_tab = st.radio(
    "profile_tabs",
    tab_options,
    horizontal=True,
    label_visibility="collapsed",
    index=default_tab_idx,
    key="profile_tab_radio",
)

st.write("")

# ── My Listings ────────────────────────────────────────────────────────────
if active_tab == tab_options[0]:
    if not my_listings:
        st.info("You have not posted any listings yet.")
        st.page_link("pages/2_Post_Listing.py", label="Post your first listing")
    else:
        sub_tab_labels = [
            f"All ({len(my_listings)})",
            f"Active ({available})",
            f"Reserved ({reserved})",
            f"Sold ({sold})",
        ]
        sub_tabs = st.tabs(sub_tab_labels)

        def render_manage(filtered, tab_key_suffix):
            if not filtered:
                st.caption("Nothing here.")
                return
            COLS = 3
            for row_start in range(0, len(filtered), COLS):
                cols = st.columns(COLS)
                for col_idx, lst in enumerate(filtered[row_start: row_start + COLS]):
                    with cols[col_idx]:
                        listing_card(lst, show_actions=False)

                        status_opts = ["available", "reserved", "sold"]
                        cur_idx = status_opts.index(lst.get("status", "available"))
                        new_status = st.selectbox(
                            "Status",
                            status_opts,
                            index=cur_idx,
                            key=f"status_{lst['id']}_{tab_key_suffix}",
                            format_func=lambda s: s.title(),
                        )

                        b1, b2, b3 = st.columns(3)
                        with b1:
                            if st.button("Update", key=f"upd_{lst['id']}_{tab_key_suffix}", use_container_width=True):
                                db2 = load_listings()
                                for l in db2["listings"]:
                                    if l["id"] == lst["id"]:
                                        l["status"] = new_status
                                        break
                                save_listings(db2)
                                st.success(f"Status updated to **{new_status.title()}**.")
                                st.rerun()
                        with b2:
                            if st.button("Edit", key=f"edit_{lst['id']}_{tab_key_suffix}", use_container_width=True):
                                st.session_state.edit_listing_id = lst["id"]
                                st.switch_page("pages/5_Edit_Listing.py")
                        with b3:
                            if st.button("Delete", key=f"del_{lst['id']}_{tab_key_suffix}", use_container_width=True):
                                st.session_state[f"confirm_del_{lst['id']}"] = True

                        # ── Delete confirmation ────────────────────────────
                        if st.session_state.get(f"confirm_del_{lst['id']}", False):
                            st.warning(f"Delete **{lst['title']}**? This cannot be undone.")
                            ca, cb = st.columns(2)
                            with ca:
                                if st.button("Yes, delete", key=f"yes_del_{lst['id']}_{tab_key_suffix}",
                                             type="primary", use_container_width=True):
                                    db2 = load_listings()
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
                                    st.session_state.pop(f"confirm_del_{lst['id']}", None)
                                    st.rerun()
                            with cb:
                                if st.button("Cancel", key=f"cancel_del_{lst['id']}_{tab_key_suffix}",
                                             use_container_width=True):
                                    st.session_state.pop(f"confirm_del_{lst['id']}", None)
                                    st.rerun()

        with sub_tabs[0]:
            render_manage(my_listings, "all")
        with sub_tabs[1]:
            render_manage([l for l in my_listings if l["status"] == "available"], "active")
        with sub_tabs[2]:
            render_manage([l for l in my_listings if l["status"] == "reserved"], "res")
        with sub_tabs[3]:
            render_manage([l for l in my_listings if l["status"] == "sold"], "sold")


# ── Saved listings ─────────────────────────────────────────────────────────
else:
    if not fav_ids:
        st.markdown(
            '<div style="background:#050010;border:1px dashed #2A1A5A;border-radius:12px;'
            'padding:32px;text-align:center;">'
            '<p style="color:#3A2A5A;font-size:0.95rem;margin:0 0 8px;font-weight:600;">No saved listings yet</p>'
            '<p style="color:#2A1A4A;font-size:0.82rem;margin:0;">'
            'Click the heart icon on any listing to save it here.</p>'
            '</div>',
            unsafe_allow_html=True,
        )
    else:
        fav_listings = [l for l in all_listings if l["id"] in fav_ids]
        if not fav_listings:
            st.info("Your saved listings are no longer available.")
        else:
            marketplace_favs = [
                l for l in fav_listings
                if l.get("listing_type", "marketplace") == "marketplace"
            ]
            housing_favs = [
                l for l in fav_listings
                if l.get("listing_type") == "housing"
            ]

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
