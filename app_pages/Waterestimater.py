import streamlit as st

st.set_page_config(page_title="Cuba, NM Water Estimator", page_icon="💧")

st.title("💧 Water Consumption & Cost Estimator")
st.subheader("Cuba, New Mexico")
st.write(
    "Estimate daily and monthly household water usage and calculate your expected "
    "Village of Cuba water bill."
)

st.divider()

# --- Section 1: Daily Usage Inputs ---
st.header("1. Estimate Daily Individual Usage")

col1, col2 = st.columns(2)

with col1:
    showers_per_day = st.number_input("Showers per day", min_value=0.0, value=1.0, step=0.5)
    shower_mins = st.slider("Average shower length (minutes)", 1, 30, 8)
    toilet_flushes = st.number_input("Toilet flushes per day", min_value=0, value=5, step=1)

with col2:
    faucet_mins = st.slider("Sink/faucet use per day (minutes)", 0, 30, 5)
    laundry_loads = st.number_input("Laundry loads per week", min_value=0.0, value=2.0, step=0.5)
    dishwasher_loads = st.number_input("Dishwasher loads per week", min_value=0.0, value=3.0, step=0.5)

# Standard EPA / WaterSense flow rate estimates (in gallons)
GALLONS_PER_MIN_SHOWER = 2.1
GALLONS_PER_FLUSH = 1.6
GALLONS_PER_MIN_FAUCET = 1.5
GALLONS_PER_LAUNDRY = 20.0
GALLONS_PER_DISHWASHER = 4.0

daily_gallons = (
    (showers_per_day * shower_mins * GALLONS_PER_MIN_SHOWER)
    + (toilet_flushes * GALLONS_PER_FLUSH)
    + (faucet_mins * GALLONS_PER_MIN_FAUCET)
    + ((laundry_loads * GALLONS_PER_LAUNDRY) / 7)
    + ((dishwasher_loads * GALLONS_PER_DISHWASHER) / 7)
)

monthly_gallons = daily_gallons * 30

st.divider()

# --- Section 2: Cuba, NM Rate Settings ---
st.header("2. Village of Cuba Rate Settings")
st.caption(
    "Defaults are pre-filled using New Mexico residential benchmarks (~81 gal/day average). "
    "Adjust the base fee and tier rate below to match your current Village of Cuba utility statement."
)

rate_col1, rate_col2, rate_col3 = st.columns(3)

with rate_col1:
    base_fee = st.number_input("Monthly Base Fee ($)", min_value=0.0, value=23.00, step=0.50)

with rate_col2:
    included_gallons = st.number_input(
        "Gallons Included in Base", min_value=0, value=3000, step=500
    )

with rate_col3:
    rate_per_1000 = st.number_input(
        "Rate per 1,000 Gal Over Base ($)", min_value=0.0, value=3.50, step=0.25
    )

# Calculate Cost (including Cuba's 8.0625% Gross Receipts Tax)
GRT_RATE = 0.080625  # Village of Cuba GRT

extra_gallons = max(0.0, monthly_gallons - included_gallons)
usage_charge = (extra_gallons / 1000.0) * rate_per_1000
subtotal = base_fee + usage_charge
tax = subtotal * GRT_RATE
total_monthly_cost = subtotal + tax

st.divider()

# --- Section 3: Results ---
st.header("3. Estimated Results")

res1, res2, res3 = st.columns(3)
res1.metric("Daily Usage", f"{daily_gallons:,.1f} gal")
res2.metric("Monthly Usage (30 days)", f"{monthly_gallons:,.0f} gal")
res3.metric("Est. Monthly Bill (w/ GRT)", f"${total_monthly_cost:,.2f}")

# Comparison context against NM state average (81 gal/day)
nm_avg = 81.0
diff = daily_gallons - nm_avg
if diff > 0:
    st.info(f"Your estimate is **{diff:.1f} gallons/day higher** than the New Mexico residential average (81 gal/day).")
else:
    st.success(f"Your estimate is **{abs(diff):.1f} gallons/day lower** than the New Mexico residential average (81 gal/day).")