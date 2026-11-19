"""
ShopImpact — Conscious Shopping Dashboard
Log a planned purchase, see its estimated CO₂ footprint instantly,
track your month, earn badges and discover greener alternatives.

Run locally:  streamlit run app.py
"""

from datetime import date

import pandas as pd
import streamlit as st

import logic
import turtle_art

st.set_page_config(page_title="ShopImpact", page_icon="🌿", layout="wide")

# ---------------------------------------------------------------------------
# SESSION STATE — the list of purchases lives here while the app is open
# ---------------------------------------------------------------------------
defaults = {
    "purchases": [],          # list of dicts (see logic.make_purchase)
    "known_badges": [],       # badges already earned, to spot new ones
    "new_badge": None,        # badge earned on the latest action
    "last_message": None,     # feedback after logging
    "last_tip": None,         # random eco tip after logging
    "quote": logic.random_quote(),
    "uploaded_id": None,
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ---------------------------------------------------------------------------
# STYLING — earthy palette, large readable fonts
# ---------------------------------------------------------------------------
def inject_css(high_contrast):
    if high_contrast:
        palette = """
        --bg:#FFFFFF; --surface:#FFFFFF; --ink:#000000; --muted:#000000;
        --moss:#003D1A; --sage:#003D1A; --river:#00315C; --bark:#000000;
        --line:#000000; --tag-bg:#FFFFFF;
        """
    else:
        palette = """
        --bg:#E9ECDD; --surface:#F7F8F2; --ink:#1F2A22; --muted:#55604F;
        --moss:#2F5D3A; --sage:#8DB38B; --river:#3E7C98; --bark:#6B4F3A;
        --line:#C9D0B8; --tag-bg:#FBFCF6;
        """
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:wght@400;700&family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700;12..96,800&display=swap');
        :root {{ {palette} }}
        html, body, [class*="css"], .stMarkdown, p, label, input, textarea, select, li {{
            font-family: 'Atkinson Hyperlegible', system-ui, sans-serif;
        }}
        .stApp {{ background: var(--bg); color: var(--ink); }}
        .stApp p, .stApp li, .stApp label {{ font-size: 1.08rem; }}
        h1, h2, h3, h4 {{ font-family: 'Bricolage Grotesque', sans-serif !important;
                          color: var(--moss) !important; letter-spacing: -0.01em; }}
        h1 {{ font-size: 3.1rem !important; font-weight: 800 !important; margin-bottom: 0 !important; }}
        section[data-testid="stSidebar"] {{ background: var(--surface); border-right: 1px solid var(--line); }}
        div[data-testid="stVerticalBlockBorderWrapper"] {{ background: var(--surface);
            border-color: var(--line) !important; border-radius: 14px; }}
        div[data-testid="stMetricValue"], div[data-testid="stMetricValue"] * {{ font-family: 'Bricolage Grotesque', sans-serif;
            font-size: 2.3rem; font-weight: 700; color: var(--moss); }}
        div[data-testid="stMetricLabel"] p {{ font-size: 1rem; color: var(--muted); }}
        .stButton > button, .stDownloadButton > button {{
            border-radius: 999px; font-size: 1.05rem; padding: 0.45rem 1.3rem;
            border: 2px solid var(--moss); color: var(--moss); background: transparent; }}
        .stButton > button[kind="primary"] {{ background: var(--moss); color: #FFFFFF; }}
        .stButton > button:focus-visible {{ outline: 3px solid var(--river); outline-offset: 2px; }}
        .subtitle {{ font-size: 1.25rem; color: var(--muted); margin: 0.2rem 0 1.2rem; max-width: 60ch; }}

        /* the CO₂ "price tag" — the live preview */
        .co2-tag {{ position: relative; background: var(--tag-bg); border: 2px dashed var(--bark);
            border-radius: 10px 22px 22px 10px; padding: 1rem 1.2rem 1rem 2.6rem; }}
        .co2-tag::before {{ content: ""; position: absolute; left: 0.9rem; top: 50%;
            width: 0.8rem; height: 0.8rem; margin-top: -0.4rem; border-radius: 50%;
            border: 2px solid var(--bark); background: var(--bg); }}
        .co2-tag .kg {{ font-family: 'Bricolage Grotesque', sans-serif; font-size: 2.6rem;
            font-weight: 800; line-height: 1; }}
        .co2-tag .level {{ display: inline-block; margin-left: 0.6rem; padding: 0.15rem 0.7rem;
            border-radius: 999px; font-weight: 700; font-size: 0.95rem; color: #FFFFFF; vertical-align: middle; }}
        .co2-tag .note {{ color: var(--muted); margin-top: 0.4rem; font-size: 1rem; }}
        .lvl-Low {{ background: #2F5D3A; }} .lvl-Medium {{ background: #A07A1E; }} .lvl-High {{ background: #B5543C; }}

        .badge {{ display: flex; gap: 0.7rem; align-items: center; padding: 0.45rem 0; }}
        .badge .icon {{ font-size: 1.7rem; width: 2.2rem; text-align: center; }}
        .badge .name {{ font-weight: 700; color: var(--ink); }}
        .badge .why {{ font-size: 0.93rem; color: var(--muted); }}
        .badge.locked {{ opacity: 0.42; filter: grayscale(1); }}
        .tip {{ border-left: 4px solid var(--river); padding: 0.5rem 0.9rem; background: var(--surface);
                border-radius: 0 10px 10px 0; margin-top: 0.6rem; }}
        .quote {{ font-style: italic; color: var(--ink); }}
        .quote-by {{ color: var(--muted); font-size: 0.95rem; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------
def purchases_df(purchases):
    """List of dicts -> pandas DataFrame for tables and charts."""
    if not purchases:
        return pd.DataFrame(columns=["date", "product_type", "brand", "price",
                                     "co2_kg", "eco_choice", "ethical_brand"])
    df = pd.DataFrame(purchases)
    df["date"] = pd.to_datetime(df["date"])
    return df


def refresh_badges(month_key, goal):
    """Check badge rules and remember any badge earned for the first time."""
    current = logic.earned_badges(st.session_state.purchases, month_key, goal)
    fresh = [b for b in current if b not in st.session_state.known_badges]
    if fresh:
        st.session_state.new_badge = fresh[-1]
        st.session_state.known_badges.extend(fresh)
    return current


def load_csv(file):
    """Rebuild purchases from a CSV the user downloaded earlier."""
    df = pd.read_csv(file)
    needed = {"date", "product_type", "brand", "price"}
    if not needed.issubset(df.columns):
        st.sidebar.error("That file is missing date, product_type, brand or price columns.")
        return
    loaded = []
    for _, row in df.iterrows():
        if row["product_type"] in logic.PRODUCTS:
            loaded.append(logic.make_purchase(row["product_type"], float(row["price"]),
                                              str(row["brand"]), logic.to_date(row["date"])))
    st.session_state.purchases = loaded
    st.sidebar.success(f"Loaded {len(loaded)} purchases.")


# ---------------------------------------------------------------------------
# SIDEBAR — settings, data, motivation
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("Settings")
    goal = st.slider("Monthly CO₂ goal (kg)", min_value=10, max_value=300, value=80, step=5,
                     help="Badges like Low Impact Shopper use this goal.")
    high_contrast = st.toggle("High-contrast mode", help="Stronger colours for easier reading.")
    show_tips = st.checkbox("Show an eco tip after each purchase", value=True)

    st.header("Your data")
    st.caption("Purchases stay while this tab is open. Download them to keep them.")
    if st.button("Load 15 sample purchases", width="stretch"):
        st.session_state.purchases = logic.sample_purchases()
        st.session_state.known_badges, st.session_state.new_badge = [], None
        st.session_state.last_message = "Sample purchases loaded — explore the dashboard."

    if st.session_state.purchases:
        export = purchases_df(st.session_state.purchases).copy()
        export["date"] = export["date"].dt.strftime("%Y-%m-%d")
        st.download_button("Download my purchases (CSV)", export.to_csv(index=False),
                           file_name="shopimpact_purchases.csv", mime="text/csv",
                           width="stretch")

    upload = st.file_uploader("Load a saved CSV", type="csv")
    if upload is not None and st.session_state.uploaded_id != upload.file_id:
        st.session_state.uploaded_id = upload.file_id
        load_csv(upload)

    if st.button("Undo last purchase", width="stretch", disabled=not st.session_state.purchases):
        st.session_state.purchases.pop()
    if st.button("Clear all purchases", width="stretch", disabled=not st.session_state.purchases):
        st.session_state.purchases = []
        st.session_state.known_badges, st.session_state.new_badge = [], None

    st.header("Today's thought")
    quote, author = st.session_state.quote
    st.markdown(f'<p class="quote">“{quote}”</p><p class="quote-by">{author}</p>',
                unsafe_allow_html=True)
    if st.button("Another quote"):
        st.session_state.quote = logic.random_quote()
        st.rerun()

inject_css(high_contrast)

# ---------------------------------------------------------------------------
# HEADER
# ---------------------------------------------------------------------------
st.title("ShopImpact")
st.markdown('<p class="subtitle">See the hidden carbon cost of what you buy — before you buy it — '
            'and find greener swaps along the way.</p>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# TOP: LOG A PURCHASE (with live preview)
# ---------------------------------------------------------------------------
with st.container(border=True):
    st.subheader("Log a planned purchase")
    c1, c2, c3, c4 = st.columns([2.2, 1.6, 1.2, 1.2])
    product_type = c1.selectbox(
        "Product type", list(logic.PRODUCTS.keys()),
        format_func=lambda p: f"{logic.PRODUCTS[p]['emoji']}  {p}",
    )
    brand = c2.text_input("Brand", placeholder="e.g. Zara, Doodlage, Cashify")
    price = c3.number_input("Price (₹)", min_value=0.0, value=999.0, step=100.0)
    purchase_date = c4.date_input("Date", value=date.today(), max_value=date.today())

    # live estimate — updates as soon as any input changes
    preview_kg = logic.calculate_impact(product_type, price, brand)
    level = logic.impact_level(preview_kg)
    eq = logic.everyday_equivalents(preview_kg)
    ethical_note = " Ethical brand: estimate lowered by 15%." if logic.is_ethical_brand(brand) else ""

    left, right = st.columns([1.3, 1])
    with left:
        st.markdown(
            f"""<div class="co2-tag" aria-live="polite">
                <span class="kg">{preview_kg:.1f} kg CO₂e</span>
                <span class="level lvl-{level}">{level} impact</span>
                <div class="note">About the same as driving {eq['km_driven']} km in a petrol car.{ethical_note}</div>
            </div>""",
            unsafe_allow_html=True,
        )
        st.write("")
        log_clicked = st.button("Log purchase", type="primary", disabled=price <= 0)
    with right:
        info = logic.PRODUCTS[product_type]
        title = "You're already choosing well" if info["eco"] else "Greener options to consider"
        st.markdown(f"**{title}**")
        for alt in info["alternatives"]:
            st.markdown(f"- {alt}")

# handle the click BEFORE drawing the dashboard, so totals update immediately
if log_clicked:
    new = logic.make_purchase(product_type, price, brand, purchase_date)
    st.session_state.purchases.append(new)
    st.session_state.last_message = logic.feedback_message(new)
    st.session_state.last_tip = logic.random_tip() if show_tips else None

if st.session_state.last_message:
    st.success(st.session_state.last_message)
    if st.session_state.last_tip:
        st.markdown(f'<div class="tip">💡 Did you know? {st.session_state.last_tip}</div>',
                    unsafe_allow_html=True)
    st.session_state.last_message, st.session_state.last_tip = None, None

# ---------------------------------------------------------------------------
# MAIN AREA: DASHBOARD (centre) + TURTLE & BADGES (side)
# ---------------------------------------------------------------------------
purchases = st.session_state.purchases
df = purchases_df(purchases)

this_month = logic.month_key(date.today())
months = sorted({logic.month_key(p["date"]) for p in purchases} | {this_month}, reverse=True)

dash, side = st.columns([2.3, 1], gap="large")

with dash:
    head_l, head_r = st.columns([2, 1])
    head_l.subheader("Your monthly dashboard")
    selected = head_r.selectbox(
        "Month", months, label_visibility="collapsed",
        format_func=lambda k: pd.to_datetime(k + "-01").strftime("%B %Y"),
    )
    summary = logic.monthly_summary(purchases, selected)
    badges_now = refresh_badges(selected, goal)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Spent", f"₹{summary['spend']:,.0f}")
    m2.metric("CO₂ footprint", f"{summary['co2']:.1f} kg")
    m3.metric("Purchases", summary["count"])
    m4.metric("Green choices", f"{summary['green_share']:.0%}")

    used = summary["co2"] / goal if goal else 0
    status = logic.goal_status(summary["co2"], goal)
    status_text = {
        "good": "Comfortably under your goal.",
        "close": "Getting close to your goal — a few green swaps will keep you under.",
        "over": "Over your goal this month. Next month is a fresh start.",
    }[status]
    st.progress(min(used, 1.0), text=f"{summary['co2']:.1f} of {goal} kg goal used. {status_text}")

    if purchases:
        saved = logic.co2_saved_vs_conventional(purchases)
        if saved > 0:
            st.caption(f"Your green swaps have avoided about {saved:.1f} kg CO₂ compared with the regular options.")

    month_df = df[df["date"].dt.strftime("%Y-%m") == selected] if not df.empty else df
    if month_df.empty:
        st.info("No purchases this month yet. Log one above, or load the sample purchases from the sidebar.")
    else:
        tab1, tab2, tab3, tab4 = st.tabs(["By product type", "Day by day", "Month by month", "All purchases"])
        with tab1:
            by_type = (month_df.groupby("product_type", as_index=False)["co2_kg"].sum()
                       .sort_values("co2_kg", ascending=False))
            st.bar_chart(by_type, x="product_type", y="co2_kg", color="#2F5D3A",
                         x_label="Product type", y_label="kg CO₂e", horizontal=True)
        with tab2:
            daily = month_df.groupby(month_df["date"].dt.date)["co2_kg"].sum().cumsum().reset_index()
            daily.columns = ["Day", "Running total (kg CO₂e)"]
            st.line_chart(daily, x="Day", y="Running total (kg CO₂e)", color="#3E7C98")
        with tab3:
            monthly = df.groupby(df["date"].dt.strftime("%Y-%m")).agg(
                co2=("co2_kg", "sum"), spend=("price", "sum")).reset_index()
            monthly.columns = ["Month", "kg CO₂e", "Spent (₹)"]
            st.bar_chart(monthly, x="Month", y="kg CO₂e", color="#6B4F3A")
            st.dataframe(monthly, hide_index=True, width="stretch")
        with tab4:
            table = df.sort_values("date", ascending=False).copy()
            table["date"] = table["date"].dt.date
            table["green"] = table["eco_choice"] | table["ethical_brand"]
            st.dataframe(
                table[["date", "product_type", "brand", "price", "co2_kg", "green"]],
                hide_index=True, width="stretch",
                column_config={
                    "date": "Date", "product_type": "Product type", "brand": "Brand",
                    "price": st.column_config.NumberColumn("Price", format="₹%.0f"),
                    "co2_kg": st.column_config.NumberColumn("CO₂ (kg)", format="%.1f"),
                    "green": st.column_config.CheckboxColumn("Green choice"),
                },
            )

with side:
    with st.container(border=True):
        st.subheader("Turtle corner")
        view = st.radio("Drawing", ["Auto", "Footprint", "Leaf", "Badge"], horizontal=True,
                        label_visibility="collapsed")
        last = purchases[-1] if purchases else None

        if view == "Auto":
            if st.session_state.new_badge:
                view = "Badge"
            elif last and logic.is_green_purchase(last):
                view = "Leaf"
            elif purchases:
                view = "Footprint"
            else:
                view = "Sprout"

        if view == "Badge" and (st.session_state.new_badge or badges_now):
            name = st.session_state.new_badge or badges_now[-1]
            svg, alt = turtle_art.draw_badge(name), f"Medal for {name}"
            caption = f"New badge: {name}! 🎉" if st.session_state.new_badge else "Your latest badge"
        elif view == "Leaf":
            svg, alt = turtle_art.draw_leaf(), "A green leaf"
            caption = "A leaf for every green choice."
        elif view == "Footprint" or (view == "Badge" and purchases):
            svg, alt = turtle_art.draw_footprint(summary["co2"], status), "Your monthly footprint"
            caption = "Green = under goal, yellow = close, red = over."
        else:
            svg, alt = turtle_art.draw_sprout(), "A seedling"
            caption = "Your first purchase plants the seed."

        st.markdown(turtle_art.svg_to_img_tag(svg, alt), unsafe_allow_html=True)
        st.caption(caption)
        st.session_state.new_badge = None

    with st.container(border=True):
        st.subheader("Badges")
        rows = []
        for name, (icon, why) in logic.BADGES.items():
            locked = "" if name in badges_now else " locked"
            rows.append(f'<div class="badge{locked}"><div class="icon">{icon}</div>'
                        f'<div><div class="name">{name}</div><div class="why">{why}</div></div></div>')
        st.markdown("".join(rows), unsafe_allow_html=True)
        month_name = pd.to_datetime(selected + "-01").strftime("%B %Y")
        st.caption(f"{len(badges_now)} of {len(logic.BADGES)} earned for {month_name}.")

st.divider()
st.caption("CO₂ figures are simplified estimates (price × product multiplier) to compare choices, "
           "not exact measurements. Made with Python, Streamlit and turtle-style graphics.")
