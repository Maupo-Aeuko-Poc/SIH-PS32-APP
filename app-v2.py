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
# 3. INTERFACE HEADER (HIGHLY STYLED, SLEEK & PREMIUM)
# ==========================================
st.set_page_config(page_title="Smart Crop Procurement Platform", layout="wide", initial_sidebar_state="expanded")

# Inject Google Font (Inter) and custom premium CSS overrides
st.markdown("""
<style>
    /* Import modern Inter font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global modifications */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #1e293b;
    }
    
    /* Main container styling */
    .main {
        background-color: #fcfcfd;
    }
    
    /* Section headers */
    h1 {
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        letter-spacing: -0.025em;
        color: #0f172a !important;
        margin-bottom: 0.2rem !important;
    }
    h2, h3, h4 {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        letter-spacing: -0.015em;
        color: #1e293b !important;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #f8fafc !important;
        border-right: 1px solid #e2e8f0;
    }
    
    /* Sleek Card container styling */
    .card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
    }
    
    /* Badges */
    .badge {
        display: inline-flex;
        align-items: center;
        padding: 4px 8px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .badge-success { background-color: #ecfdf5; color: #065f46; border: 1px solid #a7f3d0; }
    .badge-danger { background-color: #fef2f2; color: #991b1b; border: 1px solid #fca5a5; }
    .badge-info { background-color: #eff6ff; color: #1e40af; border: 1px solid #bfdbfe; }
    
    /* Streamlit input and button styling */
    .stButton>button {
        background-color: #0f172a !important;
        color: #ffffff !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        padding: 8px 16px !important;
        border: none !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05) !important;
        transition: background-color 0.15s ease !important;
    }
    .stButton>button:hover {
        background-color: #1e293b !important;
    }
    
    /* Secondary/outline buttons styled in stream-lit are handled cleanly */
    
    /* Custom divider */
    .divider {
        height: 1px;
        background-color: #e2e8f0;
        margin: 24px 0;
    }
    
    /* Notification Alerts styles */
    .notification-item {
        background-color: #ffffff;
        border-left: 3px solid #64748b;
        padding: 10px 14px;
        margin-bottom: 8px;
        border-radius: 4px;
        font-size: 13px;
        border-top: 1px solid #f1f5f9;
        border-right: 1px solid #f1f5f9;
        border-bottom: 1px solid #f1f5f9;
    }
    
    /* Custom Info banner */
    .info-banner {
        background-color: #f8fafc;
        border-radius: 8px;
        border: 1px dashed #cbd5e1;
        padding: 14px;
        margin-bottom: 16px;
    }
</style>
""", unsafe_allow_html=True)

# Main Title block (clean, sleek, serif/sans hybrid layout)
st.markdown("""
<div style="margin-bottom: 30px;">
    <h1 style="font-size: 2.2rem; color: #0f172a; font-weight: 800; margin: 0;">SMART CROP PROCUREMENT PLATFORM</h1>
    <p style="font-size: 0.95rem; color: #64748b; margin: 5px 0 0 0;">
        Smart India Hackathon (SIH26032) • Dynamic Queue, Slot Reservation & Trust Scoring Engine
    </p>
</div>
""", unsafe_allow_html=True)
st.markdown('<div class="divider" style="margin-top: 0; margin-bottom: 30px;"></div>', unsafe_allow_html=True)

# ==========================================
# 4. SIDEBAR - DYNAMIC LIVE SIMULATOR CONTROLS & LOGS
# ==========================================
with st.sidebar:
    st.markdown("<h3 style='margin-top: 0;'>⚙️ Prototype Hub</h3>", unsafe_allow_html=True)
    st.caption("Use this control center to monitor queue statuses, incoming notifications, and check visual properties.")
    
    st.markdown("<div class='divider' style='margin: 15px 0;'></div>", unsafe_allow_html=True)
    
    st.markdown("<h4>📡 Real-Time Alerts Feed</h4>", unsafe_allow_html=True)
    for note in st.session_state.push_notifications[:5]:
        st.markdown(f"<div class='notification-item'>{note}</div>", unsafe_allow_html=True)
        
    st.markdown("<div class='divider' style='margin: 15px 0;'></div>", unsafe_allow_html=True)
    st.markdown("<h4>⚡ Network Efficiency</h4>", unsafe_allow_html=True)
    
    # Custom styled success metrics on the sidebar
    st.markdown("""
    <div style="display: flex; flex-direction: column; gap: 8px;">
        <div style="background-color: #f0fdf4; border-radius: 8px; padding: 10px; border: 1px solid #bbf7d0; font-size: 13px; color: #166534;">
            🟢 <b>Client-Side Grid:</b> View-only state enabled for filled queues (0 server API load)
        </div>
        <div style="background-color: #f0fdf4; border-radius: 8px; padding: 10px; border: 1px solid #bbf7d0; font-size: 13px; color: #166534;">
            🟢 <b>Price Intelligence:</b> Location-aware regional web suggests active
        </div>
        <div style="background-color: #eff6ff; border-radius: 8px; padding: 10px; border: 1px solid #bfdbfe; font-size: 13px; color: #1e40af;">
            🔵 <b>Reputation Ledger:</b> Interactive rating loops operational
        </div>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 5. ROLE ROUTING (LANDING PAGE ARCHITECTURE)
# ==========================================
portal_role = st.radio("SELECT PORTAL ROLE FROM UNIVERSAL LANDING SCREEN:", ("🌾 Farmer Portal", "🏢 Administrator & Inspector Portal"), horizontal=True)

# ==========================================
# 6. FARMER PORTAL IMPLEMENTATION
# ==========================================
if portal_role == "🌾 Farmer Portal":
    st.markdown("<h2>🌾 Farmer Portal</h2>", unsafe_allow_html=True)
    
    # Mini Login / Registration Segment
    auth_tab1, auth_tab2 = st.tabs(["🔐 Secure SMS-OTP Sign In", "✍️ Account Registration"])
    
    # Keep track of logged in farmer
    if "logged_in_farmer" not in st.session_state:
        st.session_state.logged_in_farmer = None
        
    with auth_tab1:
        if st.session_state.logged_in_farmer is None:
            col1, col2 = st.columns([3, 2])
            with col1:
                fmr_id = st.text_input("Enter Farmer Login ID (e.g., FMR8812)", value="FMR8812")
                fmr_pwd = st.text_input("Enter Password", type="password", value="pass")
            with col2:
                st.markdown("""
                <div class="info-banner" style="font-size: 13px;">
                    <b>🔒 Simulated MFA Protocol:</b><br/>
                    Enter farmer ID <code>FMR8812</code> with password <code>pass</code>. 
                    A secondary OTP will generate automatically for identity verification.
                </div>
                """, unsafe_allow_html=True)
                
                if fmr_id in st.session_state.farmers_db:
                    sim_otp = "8812" # Static mock OTP
                    st.warning(f"Simulated OTP dispatched to {st.session_state.farmers_db[fmr_id]['phone']}: **{sim_otp}**")
                    otp_input = st.text_input("Enter 4-Digit SMS OTP", value="")
                    
            if st.button("Authenticate Login"):
                if fmr_id in st.session_state.farmers_db and fmr_pwd == "pass" and otp_input == sim_otp:
                    st.session_state.logged_in_farmer = fmr_id
                    st.success(f"Successfully authenticated as {st.session_state.farmers_db[fmr_id]['name']}!")
                    st.rerun()
                else:
                    st.error("Authentication failed. Please verify credentials or OTP.")
        else:
            st.markdown(f"""
            <div style="background-color: #f8fafc; border-radius: 10px; padding: 16px; border: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <div>
                    <span style="font-size: 14px; color: #64748b;">Logged in user:</span>
                    <h3 style="margin: 0; font-size: 18px;">{st.session_state.farmers_db[st.session_state.logged_in_farmer]['name']}</h3>
                    <span style="font-size: 13px; color: #475569;">ID: {st.session_state.logged_in_farmer} | Reputation: <b>{st.session_state.farmers_db[st.session_state.logged_in_farmer]['rating']} ⭐</b></span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Log Out of Session"):
                st.session_state.logged_in_farmer = None
                st.rerun()
                
    with auth_tab2:
        st.write("Complete identity check to auto-generate secure login credentials and verify state land records.")
        reg_col1, reg_col2 = st.columns(2)
        with reg_col1:
            new_name = st.text_input("Full Legal Name", placeholder="e.g., Baldev Singh")
            new_age = st.number_input("Age", min_value=18, max_value=100, value=45)
            new_phone = st.text_input("Mobile Number", placeholder="e.g., 9988776655")
        with reg_col2:
            new_loc = st.text_input("Village / District Location", placeholder="e.g., Jind, Haryana")
            new_aadhaar = st.text_input("Aadhaar Card Number (Land record mapping)", placeholder="1234-5678-9012")
            new_crop = st.selectbox("Primary Sown Crop Type", ["Paddy (Basmati)", "Wheat", "Potatoes (Jyoti)", "Cotton", "Onions"])
            
        if st.button("Complete Registration"):
            if new_name and new_phone and new_aadhaar:
                new_fid = f"FMR{random.randint(1000, 9999)}"
                st.session_state.farmers_db[new_fid] = {
                    "name": new_name,
                    "password": "pass",
                    "phone": new_phone,
                    "rating": 5.0,  # New profiles start perfectly
                    "trips": 0
                }
                st.success(f"Identity Verified! Login ID is **{new_fid}** (Password is **'pass'**). Switch tabs above to sign in.")
                add_notification(f"New Registration: {new_name} ({new_fid}) from {new_loc}")
            else:
                st.error("Please fill in all mandatory details, including Aadhaar.")

    # ------------------
    # FARMER WORKSPACE
    # ------------------
    if st.session_state.logged_in_farmer is not None:
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        st.markdown("<h3>🚜 Your Active Farmer Workspace</h3>", unsafe_allow_html=True)
        
        # 1. SMART FILTERS & ACTIVE FEED
        st.markdown("<h4>🔍 Browse Active Government Buy Orders</h4>", unsafe_allow_html=True)
        
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            filter_crop = st.selectbox("Filter Active Crops", ["All", "Paddy (Basmati)", "Wheat", "Potatoes (Jyoti)", "Cotton", "Onions"])
        with col_f2:
            filter_qty = st.number_input("Minimum Quantity Sown (kg)", value=0)
            
        # Displaying Orders inside sleek custom cards
        for order in st.session_state.buy_orders:
            if filter_crop != "All" and order["crop"] != filter_crop:
                continue
                
            # Compute current booked quantity for this order
            order_bookings = [b for b in st.session_state.bookings if b["order_id"] == order["id"] and b["status"] == "Confirmed"]
            total_booked = sum(b["qty"] for b in order_bookings)
            remaining_cap = order["target"] - total_booked
            
            # Start of sleeker card component
            st.markdown(f"""
            <div class="card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                    <h3 style="margin: 0; color: #0f172a;">📦 Buy Order: {order['crop']}</h3>
                    <span class="badge {'badge-success' if remaining_cap > 0 else 'badge-danger'}">
                        {'Capacity Active' if remaining_cap > 0 else 'Queue Locked'}
                    </span>
                </div>
            """, unsafe_allow_html=True)
            
            tile_col1, tile_col2, tile_col3 = st.columns([2, 2, 1])
            
            with tile_col1:
                st.markdown(f"""
                <div style="font-size: 14px;">
                    📍 <b>Collection Site:</b> {order['location']}<br/>
                    ⏱ <b>Operating Hours:</b> {order['time_slot']}<br/>
                    📏 <b>Transmitting Distance:</b> <b>{order['distance_km']} km</b> (Feasibility calculated)
                </div>
                """, unsafe_allow_html=True)
                
            with tile_col2:
                if order["price_type"] == "Range":
                    estimated_tiered = calculate_tiered_price(order, total_booked)
                    st.markdown(f"""
                    <div style="font-size: 14px;">
                        💰 <b>Pricing Model:</b> Tiered Range (₹{order['price_min']} - ₹{order['price_max']}/Quintal)<br/>
                        ⚡ <b>FCFS Pricing Tier:</b> <span style="color: #10b981; font-weight: 600;">Secures ₹{estimated_tiered}/quintal currently</span>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="font-size: 14px;">
                        💰 <b>Pricing Model:</b> Fixed Cutoff (₹{order['price_min']}/Quintal)<br/>
                        💡 <i>Static government floor price applies.</i>
                    </div>
                    """, unsafe_allow_html=True)
                    
            with tile_col3:
                st.metric(label="Capacity Available", value=f"{remaining_cap} kg", delta=f"{total_booked}/{order['target']} kg filled")
                
            st.markdown("</div>", unsafe_allow_html=True) # End of styled card div
            
            # Booking interaction per card
            if remaining_cap > 0:
                with st.expander(f"📝 Apply for Slot Reservation ({order['id']})"):
                    book_qty = st.number_input("Enter Quantity to Deliver (kg)", min_value=100, max_value=int(remaining_cap), step=100, key=f"qty_{order['id']}")
                    book_hour = st.selectbox("Select Preferred Drop-off Hour", ["06:00 AM", "07:00 AM", "08:00 AM", "09:00 AM", "10:00 AM", "11:00 AM", "12:00 PM"], key=f"hr_{order['id']}")
                    
                    # Instant Paycheck Estimation & Tiered Price lock
                    price_secured = calculate_tiered_price(order, total_booked)
                    estimated_paycheck = int((book_qty / 100) * price_secured)
                    
                    st.markdown(f"""
                    <div style="background-color: #f8fafc; border-radius: 8px; padding: 12px; border: 1px solid #e2e8f0; margin-bottom: 12px;">
                        🔒 <b>Secured Rate:</b> ₹{price_secured} per quintal<br/>
                        💵 <b>Estimated Payout Checklist:</b> <b style="font-size: 16px; color: #0f172a;">₹{estimated_paycheck:,}</b>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button("Confirm Booking Request", key=f"btn_{order['id']}"):
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
                        add_notification(f"Reserved: {new_booking['farmer_name']} booked {book_qty} kg of {order['crop']} for {book_hour}")
                        st.success("Reserved Successfully! Status tracked on Public Ledger.")
                        st.rerun()
            else:
                # -------------------------------------------------------------
                # CLIENT-SIDE VIEW-ONLY OPTIMIZATION CRITICAL FEATURE DEMO
                # -------------------------------------------------------------
                st.markdown("""
                <div style="background-color: #fffbeb; border-radius: 8px; border: 1px solid #fef3c7; padding: 12px; margin-bottom: 14px; font-size: 13px; color: #b45309;">
                    ℹ️ <b>Client-Side Optimization Engine:</b> Since this capacity is 100% full, the booking server is bypassed. 
                    Your interface renders this table from client-side caches to avoid unnecessary API database load.
                </div>
                """, unsafe_allow_html=True)
                
                st.dataframe(
                    pd.DataFrame([
                        {"Time": b["time"], "Farmer ID": b["farmer_id"], "Quantity (kg)": b["qty"], "Secured Price (₹/Quintal)": b["price_secured"]}
                        for b in st.session_state.bookings if b["order_id"] == order["id"] and b["status"] == "Confirmed"
                    ]),
                    use_container_width=True
                )
            st.write("")
            
        # 2. YOUR ACTIVE RESERVATIONS & CANCELLATIONS
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        st.markdown("<h4>📂 Active Time-Slot Bookings</h4>", unsafe_allow_html=True)
        my_bookings = [b for b in st.session_state.bookings if b["farmer_id"] == st.session_state.logged_in_farmer]
        
        if len(my_bookings) == 0:
            st.info("No active slot reservations found.")
        else:
            for b in my_bookings:
                target_order = next(o for o in st.session_state.buy_orders if o["id"] == b["order_id"])
                
                st.markdown(f"""
                <div style="background-color: #f8fafc; border-radius: 10px; border: 1px solid #e2e8f0; padding: 16px; margin-bottom: 12px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                        <span style="font-size: 14px; font-weight: 600; color: #475569;">Booking ID: {b['id']}</span>
                        <span class="badge badge-info">{b['status']}</span>
                    </div>
                """, unsafe_allow_html=True)
                
                b_col1, b_col2, b_col3 = st.columns([2, 2, 1])
                with b_col1:
                    st.markdown(f"🌾 **Crop Sown:** {target_order['crop']} | ⚖️ **Qty:** {b['qty']} kg")
                with b_col2:
                    st.markdown(f"⏰ **Drop-off Hour:** {b['time']} | 📍 **Site:** {target_order['location']}")
                with b_col3:
                    if b["status"] == "Confirmed":
                        cancel_reason = st.text_input("Reason for cancellation", key=f"re_{b['id']}", placeholder="e.g., Rain delayed harvest")
                        if st.button("Cancel Reservation", key=f"can_{b['id']}"):
                            if cancel_reason:
                                b["status"] = "Cancelled"
                                add_notification(f"🚨 Released: {st.session_state.farmers_db[st.session_state.logged_in_farmer]['name']} cancelled {b['qty']} kg of {target_order['crop']}. Reason: {cancel_reason}")
                                st.success("Slot released. Broadcast alerts dispatched to waiting farmers.")
                                st.rerun()
                            else:
                                st.error("Cancellation reason required.")
                st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 7. ADMINISTRATOR & INSPECTOR PORTAL
# ==========================================
else:
    st.markdown("<h2>🏢 Administrator & Inspector Portal</h2>", unsafe_allow_html=True)
    
    # Secure Login Frame
    if "admin_logged_in" not in st.session_state:
        st.session_state.admin_logged_in = False
        
    if not st.session_state.admin_logged_in:
        col_ad1, col_ad2 = st.columns([3, 2])
        with col_ad1:
            adm_id = st.text_input("Admin ID", value="ADMIN_SIH26")
            adm_pwd = st.text_input("Password", type="password", value="sih2026")
            adm_key = st.text_input("Secure Unique Admin Key", value="KEY-9921-X")
        with col_ad2:
            st.markdown("""
            <div class="info-banner" style="font-size: 13px;">
                <b>🏢 Root Admin Credentials:</b><br/>
                Admin ID: <code>ADMIN_SIH26</code><br/>
                Password: <code>sih2026</code><br/>
                Admin Key: <code>KEY-9921-X</code>
            </div>
            """, unsafe_allow_html=True)
            
        if st.button("Authenticate Admin Access"):
            if adm_id == "ADMIN_SIH26" and adm_pwd == "sih2026" and adm_key == "KEY-9921-X":
                st.session_state.admin_logged_in = True
                st.success("Authorized! Direct admin access granted.")
                st.rerun()
            else:
                st.error("Authentication failed. Check credentials and key.")
    else:
        st.markdown("""
        <div style="background-color: #f1f5f9; border-radius: 8px; padding: 10px 14px; border: 1px solid #cbd5e1; display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <span style="font-size: 13px; color: #475569;">Session status: <b>🟢 Root Authorized</b></span>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Sign Out Admin Session"):
            st.session_state.admin_logged_in = False
            st.rerun()
            
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        admin_tab1, admin_tab2, admin_tab3 = st.tabs(["🆕 Create Buy Order", "⚖️ Mandi Site Inspection", "📊 Analytics Console"])
        
        # 1. CREATE PROCUREMENT ORDER CONSOLE (WITH LOCALIZED PRICE INTELLIGENCE)
        with admin_tab1:
            st.markdown("<h3>🆕 Publish Active Buy Order</h3>", unsafe_allow_html=True)
            st.caption("Publish regional parameters, target caps, and custom pricing margins.")
            
            c_col1, c_col2 = st.columns(2)
            with c_col1:
                new_crop = st.selectbox("Required Crop Type", ["Wheat", "Onions", "Paddy (Basmati)", "Cotton", "Potatoes (Jyoti)"])
                new_target = st.number_input("Target Volume (kg)", min_value=1000, max_value=50000, value=10000, step=1000)
                new_site = st.text_input("Collection Location Site", value="Azadpur APMC, Delhi")
                new_slot = st.selectbox("Time Constraints Slabs", ["Full Day (Active)", "06:00 AM - 12:00 PM", "12:00 PM - 06:00 PM"])
            with c_col2:
                # -------------------------------------------------------------------------
                # LOCALIZED PRICE INTELLIGENCE FEATURE DEMO
                # -------------------------------------------------------------------------
                st.markdown("""
                <div style="background-color: #f8fafc; border-radius: 10px; border: 1px dashed #cbd5e1; padding: 16px; margin-bottom: 12px;">
                    <h4 style="margin-top: 0; font-size: 14px;">📡 Localized Price Intelligence Engine</h4>
                    <p style="font-size: 12px; color: #64748b; margin-bottom: 10px;">
                        Fetch dynamic localized market prices and regional baselines using smart region-aware simulated search.
                    </p>
                """, unsafe_allow_html=True)
                
                if st.button("Query Localized Market Prices"):
                    with st.spinner("Executing real-time regional web lookup..."):
                        time.sleep(1.0)
                        if "Delhi" in new_site:
                            suggested_avg = random.randint(2200, 2450)
                            region = "NCR / Delhi Mandis"
                        else:
                            suggested_avg = random.randint(1800, 2100)
                            region = "Regional Local Mandis"
                            
                        st.info(f"📡 Price intelligence results for {new_crop} at {region}:\n\n"
                                f"• Regional Average: ₹{suggested_avg}/quintal\n"
                                f"• Recommended Range: ₹{suggested_avg - 150} to ₹{suggested_avg + 150}")
                        st.session_state.suggested_price = suggested_avg
                st.markdown("</div>", unsafe_allow_html=True)
                
                price_opt = st.selectbox("Pricing Model Configuration", ["Fixed Cutoff", "Range"])
                if price_opt == "Fixed Cutoff":
                    p_min = st.number_input("Cutoff Offer Price (₹/Quintal)", value=2100)
                    p_max = p_min
                else:
                    p_min = st.number_input("Minimum Price Bound (₹/Quintal)", value=2000)
                    p_max = st.number_input("Maximum Price Bound (₹/Quintal)", value=2400)
                    
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
                add_notification(f"Order Created: Admin requested {new_target} kg of {new_crop} at {new_site}")
                st.success(f"Order {new_id} successfully dispatched and synced online!")
                st.rerun()

        # 2. ON-SITE CROP INSPECTION & REPUTATION SYSTEM
        with admin_tab2:
            st.markdown("<h3>⚖️ Mandi Site Inspector Console</h3>", unsafe_allow_html=True)
            st.caption("Evaluate physical drop-offs upon arrival to maintain system accuracy and farmer rating ledgers.")
            
            confirmed_bookings = [b for b in st.session_state.bookings if b["status"] == "Confirmed"]
            if len(confirmed_bookings) == 0:
                st.info("No active pending deliveries to evaluate today.")
            else:
                selected_b_id = st.selectbox("Select Arrived Booking to Evaluate", [f"{b['id']} - {b['farmer_name']} ({b['qty']} kg of Paddy)" for b in confirmed_bookings])
                
                # Fetch actual booking record
                booking_id = selected_b_id.split(" - ")[0]
                target_booking = next(b for b in st.session_state.bookings if b["id"] == booking_id)
                
                st.markdown(f"""
                <div style="background-color: #f8fafc; border-radius: 10px; border: 1px solid #e2e8f0; padding: 16px; margin-bottom: 16px; font-size: 14px;">
                    👤 <b>Farmer ID:</b> {target_booking['farmer_id']} | <b>Farmer Name:</b> {target_booking['farmer_name']}<br/>
                    📦 <b>Booked Crop:</b> Paddy | <b>Volume:</b> {target_booking['qty']} kg at slot <b>{target_booking['time']}</b>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("<h4>🌟 Star-Rating Quality Inspection</h4>", unsafe_allow_html=True)
                ev_col1, ev_col2 = st.columns(2)
                with ev_col1:
                    rate_quality = st.slider("1. Crop Grade (FAQ Quality Checklist)", 1, 5, 5)
                    rate_accuracy = st.slider("2. Volume Integrity (vs. reserved quantity)", 1, 5, 5)
                with ev_col2:
                    rate_punctuality = st.slider("3. Drop-off Punctuality", 1, 5, 5)
                    
                final_calc_rating = round((rate_quality + rate_accuracy + rate_punctuality) / 3, 1)
                st.metric(label="Aggregated Performance Score", value=f"{final_calc_rating} / 5.0 Stars")
                
                if st.button("Complete Cycle & Submit Rating"):
                    # Update reputation score dynamically in database
                    fid = target_booking["farmer_id"]
                    current_stats = st.session_state.farmers_db[fid]
                    
                    old_rating = current_stats["rating"]
                    old_trips = current_stats["trips"]
                    
                    new_trips = old_trips + 1
                    new_rating = round(((old_rating * old_trips) + final_calc_rating) / new_trips, 2)
                    
                    st.session_state.farmers_db[fid]["rating"] = new_rating
                    st.session_state.farmers_db[fid]["trips"] = new_trips
                    
                    # Remove booking or mark completed
                    target_booking["status"] = "Completed & Rated"
                    
                    add_notification(f"Evaluation: {target_booking['farmer_name']} rated {final_calc_rating}⭐. New profile trust: {new_rating}⭐.")
                    st.success(f"Evaluation complete! Profile updated from {old_rating}⭐ to {new_rating}⭐.")
                    st.rerun()

        # 3. ANALYTICS & REGIONAL VOLUMES
        with admin_tab3:
            st.markdown("<h3>📊 Platform Activity Analytics</h3>", unsafe_allow_html=True)
            
            total_active_orders = len(st.session_state.buy_orders)
            total_slots_booked = len([b for b in st.session_state.bookings if b["status"] == "Confirmed"])
            total_completions = len([b for b in st.session_state.bookings if "Completed" in b["status"]])
            
            stat1, stat2, stat3 = st.columns(3)
            with stat1:
                st.metric("Active Procurement Contracts", total_active_orders)
            with stat2:
                st.metric("Total Reserved Slabs", total_slots_booked)
            with stat3:
                st.metric("Completed Life-Cycles", total_completions)
                
            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
            st.markdown("<h4>📋 System Transaction Ledger</h4>", unsafe_allow_html=True)
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
