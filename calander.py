import streamlit as st
import holidays
import pycountry
from datetime import datetime, timedelta

st.set_page_config(layout="wide")

# --- STYLE ---
st.markdown("""
<style>
html, body, [class*="css"] {
    font-size: 10px !important;
    background-color: #ffffff;
    color: #000000;
}
.cell {
    text-align: center;
    padding: 2px;
    border: 1px solid #d0d0d0;
    height: 26px;
    display: flex;
    align-items: center;
    justify-content: center;
}
.date {
    background-color: #f5f5f5;
    font-weight: 600;
}
.holiday {
    background-color: #ff4d4d;
    color: white;
    font-weight: 600;
}
.header {
    background-color: #e9ecef;
    border: 1px solid #d0d0d0;
    height: 36px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

st.title("RMA Holiday Calendar")

# --- DEFAULT ---
default_map = {
    "USD": "US", "GBP": "GB", "AUD": "AU", "CAD": "CA",
    "CHF": "CH", "CZK": "CZ", "DKK": "DK", "SEK": "SE",
    "NOK": "NO", "RON": "RO", "PLN": "PL",
    "EUR-DE": "DE", "EUR-IT": "IT", "EUR-FR": "FR"
}

# --- STATE ---
if "all_countries" not in st.session_state:
    st.session_state.all_countries = default_map.copy()

if "selected_currencies" not in st.session_state:
    st.session_state.selected_currencies = list(default_map.keys())

if "days" not in st.session_state:
    st.session_state.days = 15

# --- RESET ---
if st.sidebar.button("🔄 Reset App"):
    st.session_state.all_countries = default_map.copy()
    st.session_state.selected_currencies = list(default_map.keys())
    st.session_state.days = 15
    st.rerun()

# --- MULTISELECT ---
selected = st.sidebar.multiselect(
    "Select Currencies",
    options=list(st.session_state.all_countries.keys()),
    default=st.session_state.selected_currencies
)

st.session_state.selected_currencies = selected

# --- ADD COUNTRY (UNLIMITED) ---
st.sidebar.markdown("---")
st.sidebar.header("Add Country")

country_input = st.sidebar.text_input("Country name")

if st.sidebar.button("Add Country"):
    try:
        c = pycountry.countries.search_fuzzy(country_input)[0]
        code = c.alpha_2
        name = c.name[:3].upper()  # simple label

        # Add to master list
        st.session_state.all_countries[name] = code

        # Auto select it
        st.session_state.selected_currencies.append(name)

        st.rerun()
    except:
        st.sidebar.error("Country not found")

# --- FLAG ---
def flag(code):
    return f"https://flagcdn.com/w40/{code.lower()}.png"

# --- ACTIVE COUNTRIES ---
active = {
    k: st.session_state.all_countries[k]
    for k in st.session_state.selected_currencies
}

# --- DATES ---
start = datetime.today()
dates = [start + timedelta(days=i) for i in range(st.session_state.days)]

# --- HOLIDAYS ---
holiday_data = {}
for code in active.values():
    try:
        holiday_data[code] = holidays.CountryHoliday(code)
    except:
        holiday_data[code] = {}

# --- HEADER ---
cols = st.columns(len(active) + 1)

cols[0].markdown('<div class="header">Date</div>', unsafe_allow_html=True)

for i, (cur, code) in enumerate(active.items()):
    cols[i + 1].markdown(f"""
    <div class="header">
        <img src="{flag(code)}" width="16">
        <div>{cur}</div>
    </div>
    """, unsafe_allow_html=True)

# --- TABLE ---
for d in dates:
    cols = st.columns(len(active) + 1)

    cols[0].markdown(
        f'<div class="cell date">{d.strftime("%d-%b")}</div>',
        unsafe_allow_html=True
    )

    for i, code in enumerate(active.values()):
        h = holiday_data[code].get(d.date(), "")

        if h:
            cell = f'<div class="cell holiday">{h}</div>'
        else:
            cell = '<div class="cell"></div>'

        cols[i + 1].markdown(cell, unsafe_allow_html=True)

# --- LOAD MORE ---
if st.button("Load next 15 days"):
    st.session_state.days += 15
    st.rerun()