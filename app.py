import streamlit as st
import pandas as pd
import random
import time
from datetime import datetime, timedelta

# ==========================================
# 1. INITIALIZE GLOBAL STATE (SESSION STATE)
# ==========================================
if "initialized" not in st.session_state:
    st.session_state.initialized = True
    
    # Pre-seeded active buy orders (Admin created)
    st.session_state.buy_orders = [
        {
            "id": "ORD001",
            "crop": "Paddy (Basmati)",
            "target": 5000,  # in kg
            "price_type": "Range",
            "price_min": 2200,  # per quintal (100 kg)
            "price_max": 2500,
            "location": "Azadpur APMC, Delhi",
            "time_slot": "06:00 AM - 12:00 PM",
            "distance_km": 12.4
        },
        {
            "id": "ORD002",
            "crop": "Potatoes (Jyoti)",
            "target": 8000,
            "price_type": "Fixed",
            "price_min": 1400,
            "price_max": 1400,
            "location": "Sikandra Mandi, Agra",
            "time_slot": "Full Day (Active)",
            "distance_km": 45.8
        }
    ]
    
    # Booked slots tracking
    st.session_state.bookings = [
        {
            "id": "BOK901",
            "order_id": "ORD001",
            "farmer_name": "Sukhdev Singh",
            "farmer_id": "FMR8812",
            "qty": 2000,
            "time": "08:30 AM",
            "price_secured": 2450,  # early bird premium
            "status": "Confirmed",
            "timestamp": datetime.now() - timedelta(hours=2)
        },
        {
            "id": "BOK902",
            "order_id": "ORD001",
            "farmer_name": "Ramesh Patidar",
            "farmer_id": "FMR4012",
            "qty": 1500,
            "time": "09:15 AM",
            "price_secured": 2350,  # mid tier
            "status": "Confirmed",
            "timestamp": datetime.now() - timedelta(hours=1)
        }
    ]
    
    # Active registered farmers db simulation
    st.session_state.farmers_db = {
        "FMR8812": {"name": "Sukhdev Singh", "password": "pass", "phone": "9876543210", "rating": 4.8, "trips": 12},
        "FMR4012": {"name": "Ramesh Patidar", "password": "pass", "phone": "9441234567", "rating": 4.5, "trips": 8}
    }
    
    # Push Notifications log
    st.session_state.push_notifications = [
        "System initiated: Welcome to the Smart Crop Procurement Network."
    ]

# ==========================================
# 2. HELPER FUNCTIONS
# ==========================================
def calculate_tiered_price(order, current_booked):
    """Calculates tiered pricing. Earlier bookers get premium price within range."""
    if order["price_type"] == "Fixed":
        return order["price_min"]
    
    fill_ratio = current_booked / order["target"]
    price_diff = order["price_max"] - order["price_min"]
    
    # FCFS Curve: starts at max price, drops to min price as quota fills
    tiered_price = order["price_max"] - (price_diff * fill_ratio)
    return int(max(order["price_min"], min(order["price_max"], tiered_price)))

def add_notification(text):
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.push_notifications.insert(0, f"[{timestamp}] 🔔 {text}")

# ==========================================
# 3. INTERFACE HEADER
# ==========================================
st.set_page_config(page_title="Smart Crop Procurement Prototype", layout="wide", initial_sidebar_state="expanded")

# Bold, monochrome aesthetic matching v3 spec
st.markdown("""
<style>
    .reportview-container { background: #ffffff; color: #000000; }
    h1, h2, h3 { color: #000000 !important; font-family: 'Helvetica', sans-serif; font-weight: bold; }
    .stButton>button { background-color: #000000; color: #ffffff; border-radius: 0px; border: 1px solid #000000; }
    .stButton>button:hover { background-color: #ffffff; color: #000000; }
    .css-1evm06g { border: 1px solid #000000; border-radius: 0px; padding: 20px; }
    .sidebar .sidebar-content { background: #f8f9fa; border-right: 1px solid #dee2e6; }
</style>
""", unsafe_allow_html=True)

st.title("SMART CROP PROCUREMENT & QUEUE MANAGEMENT SYSTEM")
st.caption("Smart India Hackathon (SIH26032) • Dynamic Queue & Slot Reservation Engine v1.0")
st.write("---")

# ==========================================
# 4. SIDEBAR - DYNAMIC LIVE SIMULATOR CONTROLS & LOGS
# ==========================================
with st.sidebar:
    st.header("⚙️ PROTOTYPE SIMULATOR CONTROLS")
    st.write("Use this pane to watch notifications and inspect system-level behaviors.")
    
    st.subheader("📡 Real-Time Push Alerts Feed")
    for note in st.session_state.push_notifications[:5]:
        st.caption(note)
        
    st.write("---")
    st.subheader("💡 System Optimization Status")
    st.success("✔ Client-Side Queue View-Only Listing active")
    st.success("✔ Localized Price Intelligence Online")
    st.success("✔ Zero Server API overhead for filled queues")

# ==========================================
# 5. ROLE ROUTING (LANDING PAGE ARCHITECTURE)
# ==========================================
portal_role = st.radio("SELECT YOUR ROLE AT THE UNIVERSAL LANDING SCREEN:", ("🌾 Farmer Portal", "🏢 Administrator & Inspector Portal"), horizontal=True)

# ==========================================
# 6. FARMER PORTAL IMPLEMENTATION
# ==========================================
if portal_role == "🌾 Farmer Portal":
    st.subheader("🌾 FARMER PORTAL")
    
    # Mini Login / Registration Segment
    auth_tab1, auth_tab2 = st.tabs(["🔐 Sign In via Secure OTP", "✍️ New Farmer Registration"])
    
    # Keep track of logged in farmer
    if "logged_in_farmer" not in st.session_state:
        st.session_state.logged_in_farmer = None
        
    with auth_tab1:
        if st.session_state.logged_in_farmer is None:
            col1, col2 = st.columns(2)
            with col1:
                fmr_id = st.text_input("Enter your Login ID (e.g., FMR8812)", value="FMR8812")
                fmr_pwd = st.text_input("Enter Password", type="password", value="pass")
            with col2:
                st.info("💡 SIMULATION ASSISTANCE:\n\nPassword is 'pass'. Secondary OTP is automatically simulated for verification.")
                if fmr_id in st.session_state.farmers_db:
                    sim_otp = f"8812" # Static mock OTP
                    st.warning(f"Secondary OTP Simulated & Sent to {st.session_state.farmers_db[fmr_id]['phone']}: **{sim_otp}**")
                    otp_input = st.text_input("Enter 4-Digit Mobile OTP", value="")
                    
            if st.button("Authenticate Login"):
                if fmr_id in st.session_state.farmers_db and fmr_pwd == "pass" and otp_input == sim_otp:
                    st.session_state.logged_in_farmer = fmr_id
                    st.success(f"Welcome back, {st.session_state.farmers_db[fmr_id]['name']}! (Reputation Rating: {st.session_state.farmers_db[fmr_id]['rating']} ⭐)")
                    st.rerun()
                else:
                    st.error("Invalid credentials or OTP check failed.")
        else:
            st.info(f"Logged in as **{st.session_state.farmers_db[st.session_state.logged_in_farmer]['name']}** ({st.session_state.logged_in_farmer}) | Reputation: {st.session_state.farmers_db[st.session_state.logged_in_farmer]['rating']} ⭐")
            if st.button("Sign Out"):
                st.session_state.logged_in_farmer = None
                st.rerun()
                
    with auth_tab2:
        st.write("Complete identity check to generate secure Login ID & Password.")
        reg_col1, reg_col2 = st.columns(2)
        with reg_col1:
            new_name = st.text_input("Full Name", placeholder="e.g., Baldev Singh")
            new_age = st.number_input("Age", min_value=18, max_value=100, value=45)
            new_phone = st.text_input("Mobile Number", placeholder="e.g., 9988776655")
        with reg_col2:
            new_loc = st.text_input("Location / Village", placeholder="e.g., Jind, Haryana")
            new_aadhaar = st.text_input("Aadhaar Card Number (for Auto land-record mapping)", placeholder="1234-5678-9012")
            new_crop = st.selectbox("Primary Crop Sown", ["Paddy (Basmati)", "Wheat", "Potatoes (Jyoti)", "Cotton", "Onions"])
            
        if st.button("Complete Registration"):
            if new_name and new_phone and new_aadhaar:
                new_fid = f"FMR{random.randint(1000, 9999)}"
                st.session_state.farmers_db[new_fid] = {
                    "name": new_name,
                    "password": "pass",
                    "phone": new_phone,
                    "rating": 5.0,  # Starts with perfect score
                    "trips": 0
                }
                st.success(f"Aadhaar Identity Verified! Your generated Login ID is **{new_fid}** and password is **'pass'**. Please use this to sign in.")
                add_notification(f"New Farmer Registered: {new_name} ({new_fid}) from {new_loc}")
            else:
                st.error("Please fill in all details, including Aadhaar validation.")

    # ------------------
    # FARMER WORKSPACE
    # ------------------
    if st.session_state.logged_in_farmer is not None:
        st.write("---")
        st.subheader("🚜 YOUR FARMER DASHBOARD")
        
        # 1. SMART FILTERS & ACTIVE FEED
        st.write("#### 🔍 Browse Active Government Buy Orders")
        
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            filter_crop = st.selectbox("Filter by Crop Sown", ["All", "Paddy (Basmati)", "Wheat", "Potatoes (Jyoti)", "Cotton", "Onions"])
        with col_f2:
            filter_qty = st.number_input("Minimum Quantity You Wish to Sell (kg)", value=0)
            
        # Displaying Orders as tiles
        for order in st.session_state.buy_orders:
            if filter_crop != "All" and order["crop"] != filter_crop:
                continue
                
            # Compute current booked quantity for this order
            order_bookings = [b for b in st.session_state.bookings if b["order_id"] == order["id"] and b["status"] == "Confirmed"]
            total_booked = sum(b["qty"] for b in order_bookings)
            remaining_cap = order["target"] - total_booked
            
            # Smart distance checking
            st.markdown(f"### 📦 Buy Order: {order['crop']}")
            tile_col1, tile_col2, tile_col3 = st.columns([2, 2, 1])
            
            with tile_col1:
                st.write(f"📍 **Collection Site:** {order['location']}")
                st.write(f"⏱ **Valid Window:** {order['time_slot']}")
                st.write(f"📏 **Calculated Distance:** **{order['distance_km']} km**")
                
            with tile_col2:
                if order["price_type"] == "Range":
                    st.write(f"💰 **Pricing Model:** Range (₹{order['price_min']} - ₹{order['price_max']} per Quintal)")
                    estimated_tiered = calculate_tiered_price(order, total_booked)
                    st.info(f"⚡ **Tiered FCFS Incentive:** Current early-bird rate secures you **₹{estimated_tiered}/quintal**!")
                else:
                    st.write(f"💰 **Pricing Model:** Fixed Cutoff (₹{order['price_min']}/Quintal)")
                    
            with tile_col3:
                st.metric(label="Capacity Remaining", value=f"{remaining_cap} kg", delta=f"{total_booked}/{order['target']} kg booked")
                
            # Booking interface per tile
            if remaining_cap > 0:
                with st.expander(f"📝 Reserve Slot & Book Quantity for {order['id']}"):
                    book_qty = st.number_input("Enter Quantity to Deliver (kg)", min_value=100, max_value=int(remaining_cap), step=100, key=f"qty_{order['id']}")
                    book_hour = st.selectbox("Select Preferred Drop-off Hour", ["06:00 AM", "07:00 AM", "08:00 AM", "09:00 AM", "10:00 AM", "11:00 AM", "12:00 PM"], key=f"hr_{order['id']}")
                    
                    # Instant Paycheck Estimation & Tiered Price lock
                    price_secured = calculate_tiered_price(order, total_booked)
                    # Price is per quintal (100kg)
                    estimated_paycheck = int((book_qty / 100) * price_secured)
                    
                    st.write(f"🔒 **Tiered Price Locked for your Slot:** ₹{price_secured} per quintal")
                    st.success(f"💵 **Approximate Paycheck Estimation:** **₹{estimated_paycheck:,}**")
                    
                    if st.button("Confirm Slot Reservation", key=f"btn_{order['id']}"):
                        new_booking = {
                            "id": f"BOK{random.randint(100, 999)}",
                            "order_id": order["id"],
                            "farmer_name": st.session_state.farmers_db[st.session_state.logged_in_farmer]["name"],
                            "farmer_id": st.session_state.logged_in_farmer,
                            "qty": book_qty,
                            "time": book_hour,
                            "price_secured": price_secured,
                            "status": "Confirmed",
                            "timestamp": datetime.now()
                        }
                        st.session_state.bookings.append(new_booking)
                        add_notification(f"Slot Reserved: {new_booking['farmer_name']} booked {book_qty} kg of {order['crop']} for {book_hour}")
                        st.success("Slot Booked Successfully! Check your status on the Public Queue.")
                        st.rerun()
            else:
                # -------------------------------------------------------------
                # CLIENT-SIDE VIEW-ONLY OPTIMIZATION CRITICAL FEATURE DEMO
                # -------------------------------------------------------------
                st.error("🔒 QUEUE FULL (Locked)")
                st.caption("ℹ️ *System Optimization Note: This filled queue is rendered as a lightweight, static view-only grid on your client device to prevent unnecessary API network load during peak season.*")
                
                # Show static read-only table client-side
                st.dataframe(
                    pd.DataFrame([
                        {"Time": b["time"], "Farmer ID": b["farmer_id"], "Quantity (kg)": b["qty"], "Secured Price (₹/Quintal)": b["price_secured"]}
                        for b in st.session_state.bookings if b["order_id"] == order["id"] and b["status"] == "Confirmed"
                    ])
                )
            st.write("---")
            
        # 2. YOUR ACTIVE RESERVATIONS & CANCELLATIONS
        st.write("#### 📂 Your Active Time-Slot Bookings")
        my_bookings = [b for b in st.session_state.bookings if b["farmer_id"] == st.session_state.logged_in_farmer]
        
        if len(my_bookings) == 0:
            st.write("No active slot reservations found.")
        else:
            for b in my_bookings:
                target_order = next(o for o in st.session_state.buy_orders if o["id"] == b["order_id"])
                b_col1, b_col2, b_col3 = st.columns([2, 2, 1])
                with b_col1:
                    st.markdown(f"**Booking ID: {b['id']}** ({b['status']})")
                    st.write(f"🌾 **Crop:** {target_order['crop']} | ⚖️ **Qty:** {b['qty']} kg")
                with b_col2:
                    st.write(f"⏰ **Reserved Time:** {b['time']} | 📍 **Site:** {target_order['location']}")
                    st.write(f"🔒 **Secured Rate:** ₹{b['price_secured']}/Quintal")
                with b_col3:
                    if b["status"] == "Confirmed":
                        cancel_reason = st.text_input("Reason for cancellation", key=f"re_{b['id']}", placeholder="e.g., Rain delayed harvest")
                        if st.button("Cancel Reservation", key=f"can_{b['id']}"):
                            if cancel_reason:
                                b["status"] = "Cancelled"
                                add_notification(f"🚨 Slot Cancelled! {st.session_state.farmers_db[st.session_state.logged_in_farmer]['name']} cancelled {b['qty']} kg of {target_order['crop']}. Reason: {cancel_reason}")
                                st.success("Slot cancelled and re-opened for other farmers. Push notifications broadcasted.")
                                st.rerun()
                            else:
                                st.error("Please provide a valid cancellation reason to release queue slot.")
                st.write("---")

# ==========================================
# 7. ADMINISTRATOR & INSPECTOR PORTAL
# ==========================================
else:
    st.subheader("🏢 ADMINISTRATOR & INSPECTOR PORTAL")
    
    # Secure Login Frame
    if "admin_logged_in" not in st.session_state:
        st.session_state.admin_logged_in = False
        
    if not st.session_state.admin_logged_in:
        col_ad1, col_ad2 = st.columns(2)
        with col_ad1:
            adm_id = st.text_input("Admin ID", value="ADMIN_SIH26")
            adm_pwd = st.text_input("Password", type="password", value="sih2026")
            adm_key = st.text_input("Secure Unique Admin Key", value="KEY-9921-X")
        with col_ad2:
            st.info("💡 SIMULATION ASSISTANCE:\n\nAdmin ID: `ADMIN_SIH26`\nPassword: `sih2026`\nAdmin Key: `KEY-9921-X`")
            
        if st.button("Authenticate Admin Access"):
            if adm_id == "ADMIN_SIH26" and adm_pwd == "sih2026" and adm_key == "KEY-9921-X":
                st.session_state.admin_logged_in = True
                st.success("Authorized! Direct admin access granted.")
                st.rerun()
            else:
                st.error("Admin authentication failed. Check credentials and secure key.")
    else:
        st.write("Authorized Session | Root Admin Dashboard")
        if st.button("Sign Out Admin"):
            st.session_state.admin_logged_in = False
            st.rerun()
            
        st.write("---")
        admin_tab1, admin_tab2, admin_tab3 = st.tabs(["🆕 Create Procurement Order", "⚖️ On-Site Crop Inspection", "📊 System Analytics"])
        
        # 1. CREATE PROCUREMENT ORDER CONSOLE (WITH LOCALIZED PRICE INTELLIGENCE)
        with admin_tab1:
            st.write("### 🆕 Publish Procurement Order")
            st.caption("Admins set specific slot guidelines, locations, and pricing controls.")
            
            c_col1, c_col2 = st.columns(2)
            with c_col1:
                new_crop = st.selectbox("Required Crop Type", ["Wheat", "Onions", "Paddy (Basmati)", "Cotton", "Potatoes (Jyoti)"])
                new_target = st.number_input("Target Amount (kg)", min_value=1000, max_value=50000, value=10000, step=1000)
                new_site = st.text_input("Collection Site Mandi", value="Azadpur APMC, Delhi")
                new_slot = st.selectbox("Operating Time Window", ["Full Day (Active)", "06:00 AM - 12:00 PM", "12:00 PM - 06:00 PM"])
            with c_col2:
                # -------------------------------------------------------------
                # LOCALIZED PRICE INTELLIGENCE MOCK FEATURE DEMO
                # -------------------------------------------------------------
                st.write("#### 🤖 Localized Price Intelligence Engine")
                st.write("Click below to fetch dynamic localized market price averages for the selected crop and collection region.")
                
                if st.button("Run Location-Aware Price Search"):
                    with st.spinner("Executing real-time regional web lookup..."):
                        time.sleep(1.2)  # simulate search latency
                        # Realistic mock lookup based on location and crop
                        if "Delhi" in new_site:
                            suggested_avg = random.randint(2200, 2450)
                            region = "NCR / Delhi Mandis"
                        else:
                            suggested_avg = random.randint(1800, 2100)
                            region = "Regional Local Mandis"
                            
                        st.info(f"📡 Price suggestion found for **{new_crop}** in **{region}**:\n\n"
                                f"• Local Average: **₹{suggested_avg} per quintal**\n\n"
                                f"• Recommended Range: **₹{suggested_avg - 150} to ₹{suggested_avg + 150}**")
                        st.session_state.suggested_price = suggested_avg
                
                price_opt = st.selectbox("Pricing Mode", ["Fixed Cutoff", "Range"])
                if price_opt == "Fixed Cutoff":
                    p_min = st.number_input("Cutoff Offer Price (₹ per Quintal)", value=2100)
                    p_max = p_min
                else:
                    p_min = st.number_input("Minimum Price Bound (₹ per Quintal)", value=2000)
                    p_max = st.number_input("Maximum Price Bound (₹ per Quintal)", value=2400)
                    
            if st.button("Publish Active Buy Order"):
                new_id = f"ORD00{len(st.session_state.buy_orders) + 1}"
                st.session_state.buy_orders.append({
                    "id": new_id,
                    "crop": new_crop,
                    "target": new_target,
                    "price_type": price_opt,
                    "price_min": p_min,
                    "price_max": p_max,
                    "location": new_site,
                    "time_slot": new_slot,
                    "distance_km": round(random.uniform(5, 50), 1)
                })
                add_notification(f"New Order Published: Admin created {new_crop} buy request for {new_target} kg at {new_site}")
                st.success(f"Order **{new_id}** successfully generated and pushed to active farmer feeds!")
                st.rerun()

        # 2. ON-SITE CROP INSPECTION & REPUTATION SYSTEM
        with admin_tab2:
            st.write("### ⚖️ Mandi Site Inspector Console")
            st.caption("Inspect physical loads upon arrival and rate farmer accountability to build historical profile trust.")
            
            confirmed_bookings = [b for b in st.session_state.bookings if b["status"] == "Confirmed"]
            if len(confirmed_bookings) == 0:
                st.write("No active pending deliveries to evaluate today.")
            else:
                selected_b_id = st.selectbox("Select Arrived Booking to Evaluate", [f"{b['id']} - {b['farmer_name']} ({b['qty']} kg of Paddy)" for b in confirmed_bookings])
                
                # Fetch actual booking record
                booking_id = selected_b_id.split(" - ")[0]
                target_booking = next(b for b in st.session_state.bookings if b["id"] == booking_id)
                
                st.write("---")
                st.write(f"👤 **Farmer ID:** {target_booking['farmer_id']} | **Farmer Name:** {target_booking['farmer_name']}")
                st.write(f"📦 **Booked Crop/Volume:** {target_booking['qty']} kg at slot **{target_booking['time']}**")
                
                st.write("#### 🌟 1-to-5 Star Crop Quality & Punctuality Valuation")
                ev_col1, ev_col2 = st.columns(2)
                with ev_col1:
                    rate_quality = st.slider("1. Produce Quality (Fair Average Quality Standards)", 1, 5, 5)
                    rate_accuracy = st.slider("2. Volume Accuracy (closeness to reserved quantity)", 1, 5, 5)
                with ev_col2:
                    rate_punctuality = st.slider("3. On-Time Arrival & Drop-off Punctuality", 1, 5, 5)
                    
                final_calc_rating = round((rate_quality + rate_accuracy + rate_punctuality) / 3, 1)
                st.metric(label="Calculated Evaluation Score", value=f"{final_calc_rating} / 5.0 Stars")
                
                if st.button("Submit Crop Evaluation & Complete Lifecycle"):
                    # Update reputation score dynamically in database
                    fid = target_booking["farmer_id"]
                    current_stats = st.session_state.farmers_db[fid]
                    
                    old_rating = current_stats["rating"]
                    old_trips = current_stats["trips"]
                    
                    # Calculate incremental moving average for reputation rating
                    new_trips = old_trips + 1
                    new_rating = round(((old_rating * old_trips) + final_calc_rating) / new_trips, 2)
                    
                    st.session_state.farmers_db[fid]["rating"] = new_rating
                    st.session_state.farmers_db[fid]["trips"] = new_trips
                    
                    # Remove booking or mark completed
                    target_booking["status"] = "Completed & Rated"
                    
                    add_notification(f"Lifecycle Complete: {target_booking['farmer_name']} evaluated. New Trust Rating: {new_rating} Stars.")
                    st.success(f"Evaluation submitted successfully! Farmer's profile updated from {old_rating}⭐ to {new_rating}⭐.")
                    st.rerun()

        # 3. ANALYTICS & REGIONAL VOLUMES
        with admin_tab3:
            st.write("### 📊 Operational Analytics Overview")
            
            total_active_orders = len(st.session_state.buy_orders)
            total_slots_booked = len([b for b in st.session_state.bookings if b["status"] == "Confirmed"])
            total_completions = len([b for b in st.session_state.bookings if "Completed" in b["status"]])
            
            stat1, stat2, stat3 = st.columns(3)
            with stat1:
                st.metric("Active Buy Orders", total_active_orders)
            with stat2:
                st.metric("Active Scheduled Slots", total_slots_booked)
            with stat3:
                st.metric("Total Completed Deliveries", total_completions)
                
            st.write("#### 📋 Comprehensive Platform Transaction Ledger")
            ledger_data = []
            for b in st.session_state.bookings:
                order_info = next(o for o in st.session_state.buy_orders if o["id"] == b["order_id"])
                ledger_data.append({
                    "Booking ID": b["id"],
                    "Farmer": b["farmer_name"],
                    "Crop Type": order_info["crop"],
                    "Quantity (kg)": b["qty"],
                    "Scheduled Hour": b["time"],
                    "Status": b["status"]
                })
            st.dataframe(pd.DataFrame(ledger_data), use_container_width=True)
