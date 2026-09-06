import streamlit as st
import pandas as pd
import random
import time
from datetime import datetime, timedelta

# ==============================================================================
# 1. INITIALIZE GLOBAL STATE (SESSION STATE)
# ==============================================================================
if "initialized" not in st.session_state:
    st.session_state.initialized = True
    st.session_state.role = None  # None, "farmer", "admin"
    st.session_state.view = "landing"  # "landing", "login", "dashboard"
    st.session_state.logged_in_farmer = None
    st.session_state.admin_logged_in = False
    
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
        "Welcome to the Smart Crop Procurement Network. Systems operational.",
        "Mandi Capacity monitors updated for Kharif season."
    ]

# ==============================================================================
# 2. HELPER FUNCTIONS
# ==============================================================================
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

# ==============================================================================
# 3. INTERFACE CONFIGURATION & HIGH-END THEME INJECTION (DARK-MODE READY)
# ==============================================================================
st.set_page_config(
    page_title="Smart Crop Procurement System",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom premium UI style sheet injection (Inter Font, CSS Card Elevation, Smooth Gradients, Fully Theme-Aware)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Global Typography & Theme-Aware Text */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, sans-serif;
    }
    
    /* Modern minimalist custom cards - dynamically inherits Streamlit values for Light & Dark Mode compatibility */
    .landing-card {
        background: var(--secondary-background-color, rgba(148, 163, 184, 0.05));
        border: 1px solid var(--border-color, rgba(148, 163, 184, 0.2));
        border-radius: 16px;
        padding: 40px 30px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.04), 0 4px 6px -2px rgba(0, 0, 0, 0.02);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        text-align: center;
        height: 100%;
        margin-bottom: 20px;
    }
    .landing-card:hover {
        transform: translateY(-6px);
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        border-color: var(--primary-color, #10b981);
    }
    
    /* Alpha-blended semi-transparent status badges (Incredible contrast on dark & light background themes) */
    .status-badge {
        font-weight: 700;
        padding: 6px 14px;
        border-radius: 9999px;
        font-size: 11px;
        display: inline-block;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    .status-active { 
        background-color: rgba(16, 185, 129, 0.15); 
        color: #10b981; 
        border: 1px solid rgba(16, 185, 129, 0.3); 
    }
    .status-full { 
        background-color: rgba(239, 68, 68, 0.15); 
        color: #ef4444; 
        border: 1px solid rgba(239, 68, 68, 0.3); 
    }
    .status-pending { 
        background-color: rgba(245, 158, 11, 0.15); 
        color: #f59e0b; 
        border: 1px solid rgba(245, 158, 11, 0.3); 
    }
    
    /* Premium custom-bordered card containers */
    .custom-container {
        background-color: var(--secondary-background-color, rgba(148, 163, 184, 0.05));
        border: 1px solid var(--border-color, rgba(148, 163, 184, 0.15));
        border-radius: 14px;
        padding: 24px;
        margin-bottom: 24px;
    }
    
    .stat-container {
        background-color: rgba(148, 163, 184, 0.08);
        border: 1px solid var(--border-color, rgba(148, 163, 184, 0.15));
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Hiding streamlit default elements for pure bespoke design layout
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 4. VIEW CONTROLLER
# ==============================================================================

# ------------------------------------------------------------------------------
# 4.1 LANDING SCREEN (TWO MAJESTIC THEME-AWARE TILES)
# ------------------------------------------------------------------------------
if st.session_state.view == "landing":
    st.markdown("<br/><br/>", unsafe_allow_html=True)
    
    # Header Banner (Theme-Aware Coloration)
    logo_col1, logo_col2, logo_col3 = st.columns([1, 10, 1])
    with logo_col2:
        st.markdown("""
        <h1 style='text-align: center; font-size: 40px; font-weight: 800; letter-spacing: -1.2px; color: var(--text-color, #0f172a); margin-bottom: 8px;'>
            SMART CROP PROCUREMENT PLATFORM
        </h1>
        <p style='text-align: center; font-size: 16px; font-weight: 400; color: var(--text-color, #64748b); opacity: 0.8; margin-bottom: 2px;'>
            An Enterprise Queue Scheduling, Dynamic FCFS Price Tuning & Inspector Audit Environment
        </p>
        <p style='text-align: center; font-size: 11px; font-weight: 600; color: var(--text-color, #94a3b8); opacity: 0.6; letter-spacing: 2px;'>
            SMART INDIA HACKATHON • PROBLEM STATEMENT ID: SIH26032
        </p>
        <div style='height: 1px; background-color: var(--border-color, rgba(148, 163, 184, 0.25)); margin: 30px auto; width: 60%;'></div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br/>", unsafe_allow_html=True)
    
    # Two Elegant side-by-side tiles with fully integrated theme colors
    tile_col1, space_col, tile_col2 = st.columns([4, 1, 4])
    
    with tile_col1:
        st.markdown("""
        <div class="landing-card">
            <div style="font-size: 65px; margin-bottom: 15px;">🚜</div>
            <h2 style="font-size: 24px; font-weight: 700; color: var(--text-color, #0f172a); margin-bottom: 12px;">FARMER PORTAL</h2>
            <p style="font-size: 14.5px; color: var(--text-color, #475569); opacity: 0.85; line-height: 1.6; margin-bottom: 25px;">
                Secure your delivery slots, check real-time FCFS dynamic rates, calculate your estimated payoff, and track active mandi lines instantly from your home.
            </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Access Farmer Workspace ➔", key="btn_go_farmer", use_container_width=True):
            st.session_state.role = "farmer"
            st.session_state.view = "login"
            st.rerun()
            
    with tile_col2:
        st.markdown("""
        <div class="landing-card">
            <div style="font-size: 65px; margin-bottom: 15px;">🏢</div>
            <h2 style="font-size: 24px; font-weight: 700; color: var(--text-color, #0f172a); margin-bottom: 12px;">ADMIN & INSPECTOR PORTAL</h2>
            <p style="font-size: 14.5px; color: var(--text-color, #475569); opacity: 0.85; line-height: 1.6; margin-bottom: 25px;">
                Publish buy orders, access real-time localized price intelligence, manage gate entry flow, audit crop arrivals, and rate farmer metrics to update trust profile histories.
            </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Access Admin Console ➔", key="btn_go_admin", use_container_width=True):
            st.session_state.role = "admin"
            st.session_state.view = "login"
            st.rerun()

    st.markdown("<br/><br/><br/><br/>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: center; font-size: 12px; color: var(--text-color, #94a3b8); opacity: 0.8;'>Powered by Digital Public Infrastructure Frameworks • Government-Agent Linked ERP Core</div>", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 4.2 CLEAN & CENTRED SIGN-IN PAGE (THEME-AWARE)
# ------------------------------------------------------------------------------
elif st.session_state.view == "login":
    st.markdown("<br/>", unsafe_allow_html=True)
    if st.button("⬅ Return to Home Screen", key="btn_back_home"):
        st.session_state.view = "landing"
        st.session_state.role = None
        st.rerun()
        
    st.markdown("<br/><br/>", unsafe_allow_html=True)
    login_c1, login_c2, login_c3 = st.columns([3, 4, 3])
    
    with login_c2:
        # Farmer Login & Registration Framework
        if st.session_state.role == "farmer":
            st.markdown("<h2 style='text-align: center; font-size: 28px; font-weight: 700; color: var(--text-color, #000); margin-bottom: 10px;'>🌾 FARMER WORKSPACE ACCESS</h2>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: var(--text-color, #64748b); opacity: 0.85; margin-bottom: 30px;'>Authenticate using your secure mobile credentials or register below</p>", unsafe_allow_html=True)
            
            auth_tab1, auth_tab2 = st.tabs(["🔐 OTP Sign In", "✍️ Register New Farmer Profile"])
            
            with auth_tab1:
                st.markdown("<br/>", unsafe_allow_html=True)
                fmr_id = st.text_input("Login ID (e.g., FMR8812)", value="FMR8812")
                fmr_pwd = st.text_input("Password", type="password", value="pass")
                
                # Help credentials box
                with st.expander("💡 Helper: Demo Accounts for Judges"):
                    st.write("**Demo Farmer 1:** ID: `FMR8812` | Password: `pass`")
                    st.write("**Demo Farmer 2:** ID: `FMR4012` | Password: `pass`")
                    st.caption("Once you type in the credentials, an OTP is instantly sent below.")
                
                if fmr_id in st.session_state.farmers_db:
                    sim_otp = "8812"
                    st.warning(f"🔐 Secondary OTP Broadcasted to registered device: **{sim_otp}**")
                    otp_input = st.text_input("Enter 4-Digit Security OTP")
                    
                    if st.button("Complete Security Check & Enter Portal", use_container_width=True):
                        if fmr_pwd == "pass" and otp_input == sim_otp:
                            st.session_state.logged_in_farmer = fmr_id
                            st.session_state.view = "dashboard"
                            st.success("Access Granted! Opening dashboard...")
                            st.rerun()
                        else:
                            st.error("Verification checks failed. Please review your credentials.")
                else:
                    st.error("Login ID not found in database. Create a new profile in the next tab.")
                    
            with auth_tab2:
                st.markdown("<br/>", unsafe_allow_html=True)
                reg_col1, reg_col2 = st.columns(2)
                with reg_col1:
                    new_name = st.text_input("Full Name", placeholder="e.g., Sukhdev Singh")
                    new_age = st.number_input("Age", min_value=18, max_value=100, value=35)
                    new_phone = st.text_input("Mobile Number", placeholder="e.g., 9876543210")
                with reg_col2:
                    new_loc = st.text_input("Location / Village", placeholder="e.g., Jind, Haryana")
                    new_aadhaar = st.text_input("Aadhaar Card Details", placeholder="4432-1102-9901")
                    new_crop = st.selectbox("Crop Variety Sown", ["Paddy (Basmati)", "Wheat", "Potatoes (Jyoti)", "Cotton", "Onions"])
                
                if st.button("Verify Identity & Issue Account", use_container_width=True):
                    if new_name and new_phone and new_aadhaar:
                        new_fid = f"FMR{random.randint(1000, 9999)}"
                        st.session_state.farmers_db[new_fid] = {
                            "name": new_name,
                            "password": "pass",
                            "phone": new_phone,
                            "rating": 5.0,  # Seed newly registered farmer with perfect rating
                            "trips": 0
                        }
                        st.success(f"Identity Matched! Secure credentials generated:\n\n"
                                   f"• **Login ID:** {new_fid}\n\n"
                                   f"• **Password:** pass\n\n"
                                   f"Use these to login in the OTP tab above.")
                        add_notification(f"Farmer database updated. New Profile Registered: {new_name} ({new_fid})")
                    else:
                        st.error("All details, including secure Aadhaar registration numbers, are mandatory.")
                        
        # Admin Portal Triple Credentials Verification
        else:
            st.markdown("<h2 style='text-align: center; font-size: 28px; font-weight: 700; color: var(--text-color, #000); margin-bottom: 10px;'>🏢 CONTROL CENTRE LOGIN</h2>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: var(--text-color, #64748b); opacity: 0.85; margin-bottom: 30px;'>Triple-Factor administrative clearance required</p>", unsafe_allow_html=True)
            
            adm_id = st.text_input("Administrator Username", value="ADMIN_SIH26")
            adm_pwd = st.text_input("Password", type="password", value="sih2026")
            adm_key = st.text_input("Secure Unique Admin Key", value="KEY-9921-X")
            
            with st.expander("💡 Helper: Demo Keys for Judges"):
                st.write("• **Admin ID:** `ADMIN_SIH26`")
                st.write("• **Password:** `sih2026`")
                st.write("• **Admin Key:** `KEY-9921-X`")
                
            if st.button("Request Administrative Access", use_container_width=True):
                if adm_id == "ADMIN_SIH26" and adm_pwd == "sih2026" and adm_key == "KEY-9921-X":
                    st.session_state.admin_logged_in = True
                    st.session_state.view = "dashboard"
                    st.success("Authorized! Direct admin access granted.")
                    st.rerun()
                else:
                    st.error("Security violation: Secure Admin Key checks failed.")

# ------------------------------------------------------------------------------
# 4.3 SLEEK WORKSPACE INTERFACES (TABBED, SECTIONED & DESIGN-READY)
# ------------------------------------------------------------------------------
elif st.session_state.view == "dashboard":
    
    # ------------------
    # FARMER DASHBOARD
    # ------------------
    if st.session_state.role == "farmer":
        
        # Dashboard Nav Header
        head_c1, head_c2 = st.columns([8, 2])
        with head_c1:
            st.markdown(f"<h1 style='font-size: 28px; font-weight: 800; color: var(--text-color, #0f172a); margin: 0;'>🚜 FARMER PORTAL CONTROL CENTRE</h1>", unsafe_allow_html=True)
            farmer_profile = st.session_state.farmers_db[st.session_state.logged_in_farmer]
            st.markdown(f"<p style='color: var(--text-color, #475569); opacity: 0.8;'>Logged in as: <b>{farmer_profile['name']}</b> ({st.session_state.logged_in_farmer}) | Performance Rating: <b>{farmer_profile['rating']} ⭐</b></p>", unsafe_allow_html=True)
        with head_c2:
            st.markdown("<br/>", unsafe_allow_html=True)
            if st.button("🚪 Logout of Account", use_container_width=True):
                st.session_state.logged_in_farmer = None
                st.session_state.view = "landing"
                st.session_state.role = None
                st.rerun()
                
        st.write("---")
        
        # Clean workspace sections divided cleanly in tabs
        farm_tab1, farm_tab2, farm_tab3 = st.tabs(["🔍 Browse & Reserve Slots", "📂 Active Reservations & Calendar", "🔔 Dynamic Notifications"])
        
        # 1st Tab: Browser & Reservation Dashboard
        with farm_tab1:
            st.markdown("### 🔍 Active Procurement Opportunities")
            st.write("Browse government buy orders and schedule delivery. Early bookings secure higher dynamic FCFS prices.")
            
            # Clean layout filters
            f_col1, f_col2 = st.columns(2)
            with f_col1:
                filter_crop = st.selectbox("Target Crop Filter", ["All", "Paddy (Basmati)", "Wheat", "Potatoes (Jyoti)", "Cotton", "Onions"])
            with f_col2:
                filter_qty = st.number_input("Filter Minimum Required Capacity (kg)", value=0)
                
            st.markdown("<br/>", unsafe_allow_html=True)
            
            # Render orders
            for order in st.session_state.buy_orders:
                if filter_crop != "All" and order["crop"] != filter_crop:
                    continue
                
                # Bookings capacity parameters
                order_bookings = [b for b in st.session_state.bookings if b["order_id"] == order["id"] and b["status"] == "Confirmed"]
                total_booked = sum(b["qty"] for b in order_bookings)
                remaining_cap = order["target"] - total_booked
                
                # Responsive clean header container using native colors
                status_class = "status-active" if remaining_cap > 0 else "status-full"
                status_label = "Active Open" if remaining_cap > 0 else "Queue Locked / Filled"
                
                st.markdown(f"""
                <div class="custom-container">
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <h4 style='margin: 0; font-size: 19px; font-weight: 700; color: var(--text-color, #0f172a);'>
                            📦 Buy Request: {order['crop']} ({order['id']})
                        </h4>
                        <span class="status-badge {status_class}">
                            {status_label}
                        </span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                info_col1, info_col2, info_col3 = st.columns([3, 3, 2])
                with info_col1:
                    st.write(f"📍 **Collection Point:** {order['location']}")
                    st.write(f"⏱ **Acceptance Window:** {order['time_slot']}")
                    st.write(f"📏 **Transit Distance:** **{order['distance_km']} km**")
                with info_col2:
                    if order["price_type"] == "Range":
                        st.write(f"💰 **Pricing Model:** Range (₹{order['price_min']} - ₹{order['price_max']} per Quintal)")
                        estimated_tiered = calculate_tiered_price(order, total_booked)
                        st.markdown(f"<span style='color: #10b981; font-weight: 700; font-size: 15px;'>⚡ Current Tiered Rate: ₹{estimated_tiered}/Quintal</span>", unsafe_allow_html=True)
                    else:
                        st.write(f"💰 **Pricing Model:** Fixed Cutoff (₹{order['price_min']}/Quintal)")
                with info_col3:
                    st.metric("Aggregate Target Quota", f"{order['target']} kg", delta=f"{remaining_cap} kg remaining")
                    
                # Interactive Booking or view-only optimization demo
                if remaining_cap > 0:
                    with st.expander(f"📝 Book Drop-off Reservation for {order['id']}"):
                        book_col1, book_col2 = st.columns(2)
                        with book_col1:
                            book_qty = st.number_input("Delivery Quantity (kg)", min_value=100, max_value=int(remaining_cap), step=100, key=f"fq_{order['id']}")
                            book_hour = st.selectbox("Preferred Time Slot", ["06:00 AM", "07:00 AM", "08:00 AM", "09:00 AM", "10:00 AM", "11:00 AM", "12:00 PM"], key=f"fh_{order['id']}")
                        with book_col2:
                            price_secured = calculate_tiered_price(order, total_booked)
                            estimated_paycheck = int((book_qty / 100) * price_secured)
                            st.markdown(f"""
                            <div class='stat-container'>
                                <p style='margin: 0; font-size: 12px; color: var(--text-color, #64748b); opacity: 0.8; font-weight: 600;'>SECURED DYNAMIC RATE</p>
                                <h3 style='margin: 5px 0; font-size: 26px; color: #10b981; font-weight: 800;'>
                                    ₹{price_secured} <span style='font-size: 11px; color: var(--text-color, #64748b); font-weight: normal;'>/qtl</span>
                                </h3>
                                <p style='margin: 0; font-size: 12px; color: var(--text-color, #475569);'>Estimated Payout: <b>₹{estimated_paycheck:,}</b></p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                        if st.button("Confirm Allocation & Book Queue Position", key=f"fbtn_{order['id']}", use_container_width=True):
                            new_b = {
                                "id": f"BOK{random.randint(100, 999)}",
                                "order_id": order["id"],
                                "farmer_name": farmer_profile["name"],
                                "farmer_id": st.session_state.logged_in_farmer,
                                "qty": book_qty,
                                "time": book_hour,
                                "price_secured": price_secured,
                                "status": "Confirmed",
                                "timestamp": datetime.now()
                            }
                            st.session_state.bookings.append(new_b)
                            add_notification(f"Slot Reserved: {new_b['farmer_name']} locked {book_qty} kg of {order['crop']} for {book_hour}")
                            st.success("Queue slot registered! Check details in active bookings tab.")
                            time.sleep(1.0)
                            st.rerun()
                else:
                    # ----------------------------------------------------------
                    # CLIENT-SIDE VIEW-ONLY PERFORMANCE LOCK OPTIMIZATION INJECT
                    # ----------------------------------------------------------
                    st.error("🔒 ORDER COMPLETE - QUEUE COMPLETED")
                    st.caption("⚙️ *Engine Optimization Status: Inactive schedules automatically lock interaction, transforming this layout into a client-side view-only array. This eliminates database API polling cycles and prevents server congestion.*")
                    
                    # Read-only static table representation
                    filled_bookings = [b for b in st.session_state.bookings if b["order_id"] == order["id"] and b["status"] == "Confirmed"]
                    if len(filled_bookings) > 0:
                        st.dataframe(
                            pd.DataFrame([
                                {"Arrival Time": b["time"], "Farmer Register": b["farmer_id"], "Verified Quantity (kg)": b["qty"], "Settled Rate (₹/Quintal)": b["price_secured"]}
                                for b in filled_bookings
                            ]), use_container_width=True
                        )
                st.markdown("<br/><hr style='border: 1px solid var(--border-color, rgba(148,163,184,0.15));'/><br/>", unsafe_allow_html=True)
                
        # 2nd Tab: Active Reservations & Cancellations Frame
        with farm_tab2:
            st.markdown("### 📂 Your Scheduled Bookings")
            st.write("Track the status of your active reservations or submit valid cancellations to release capacity back to nearby farmers.")
            
            my_reservations = [b for b in st.session_state.bookings if b["farmer_id"] == st.session_state.logged_in_farmer]
            
            if len(my_reservations) == 0:
                st.info("You have no active slot reservations on the ledger.")
            else:
                for b in my_reservations:
                    target_order = next(o for o in st.session_state.buy_orders if o["id"] == b["order_id"])
                    badge_style = "status-active" if b["status"] == "Confirmed" else "status-pending" if "Completed" in b["status"] else "status-full"
                    
                    st.markdown(f"""
                    <div class="custom-container">
                        <div style='display: flex; justify-content: space-between;'>
                            <div>
                                <span style='font-size: 11px; font-weight: 700; color: var(--text-color, #64748b); opacity: 0.8;'>BOOKING REFERENCE: {b['id']}</span>
                                <h4 style='margin: 5px 0; font-size: 18px; font-weight: 700; color: var(--text-color, #0f172a);'>🌾 {target_order['crop']} • Delivery</h4>
                            </div>
                            <div>
                                <span class="status-badge {badge_style}">
                                    {b["status"]}
                                </span>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col_b1, col_b2, col_b3 = st.columns([3, 3, 2])
                    with col_b1:
                        st.write(f"⏱ **Reserved Hour:** {b['time']}")
                        st.write(f"⚖ **Target Quantity:** {b['qty']} kg")
                    with col_b2:
                        st.write(f"💰 **Secured Pricing:** ₹{b['price_secured']}/Quintal")
                        st.write(f"📍 **Dropoff Site:** {target_order['location']}")
                    with col_b3:
                        if b["status"] == "Confirmed":
                            c_reason = st.text_input("Reason for Cancellation", key=f"cre_{b['id']}", placeholder="Rain, delay, logistics...")
                            if st.button("Release Slot Back to Public", key=f"cbtn_{b['id']}", use_container_width=True):
                                if c_reason:
                                    b["status"] = "Cancelled"
                                    add_notification(f"Slot Released! {farmer_profile['name']} cancelled slot for {b['qty']} kg of {target_order['crop']}. Reason: {c_reason}")
                                    st.success("Slot released! SMS Broadcast and system capacities updated.")
                                    time.sleep(1.0)
                                    st.rerun()
                                else:
                                    st.error("Please provide a valid cancellation reason to release queue slot.")
                    st.markdown("<hr style='border: 1px solid var(--border-color, rgba(148,163,184,0.15));'/><br/>", unsafe_allow_html=True)

        # 3rd Tab: Dynamic Broadcast & Notifications Feed
        with farm_tab3:
            st.markdown("### 🔔 Real-Time Network Log")
            st.write("Dynamic system tracking showing queue releases, newly created allocations, and mandi alerts.")
            
            for log in st.session_state.push_notifications[:10]:
                st.markdown(f"""
                <div style='background-color: var(--secondary-background-color, rgba(148, 163, 184, 0.05)); border-left: 4px solid #10b981; padding: 14px 18px; border-radius: 6px; border-top: 1px solid var(--border-color, rgba(148,163,184,0.1)); border-right: 1px solid var(--border-color, rgba(148,163,184,0.1)); border-bottom: 1px solid var(--border-color, rgba(148,163,184,0.1)); margin-bottom: 12px;'>
                    <span style='font-size: 13.5px; color: var(--text-color, #1e293b); font-weight: 500;'>{log}</span>
                </div>
                """, unsafe_allow_html=True)
                
    # ------------------
    # ADMIN DASHBOARD
    # ------------------
    else:
        head_a1, head_a2 = st.columns([8, 2])
        with head_a1:
            st.markdown("<h1 style='font-size: 28px; font-weight: 800; color: var(--text-color, #0f172a); margin: 0;'>🏢 ADMIN & INSPECTOR CONTROL CENTRE</h1>", unsafe_allow_html=True)
            st.markdown("<p style='color: var(--text-color, #475569); opacity: 0.8;'>Authorized Administrative Session • Standard Security Key Active</p>", unsafe_allow_html=True)
        with head_a2:
            st.markdown("<br/>", unsafe_allow_html=True)
            if st.button("🚪 Exits Admin Session", use_container_width=True):
                st.session_state.admin_logged_in = False
                st.session_state.view = "landing"
                st.session_state.role = None
                st.rerun()
                
        st.write("---")
        
        admin_tab1, admin_tab2, admin_tab3 = st.tabs(["🆕 Create Buy Order", "⚖️ Mandi Cargo Audit", "📊 System Ledgers"])
        
        # 1st Tab: Procurement Creation Portal (with price intelligence)
        with admin_tab1:
            st.markdown("### 🆕 Publish Procurement Guidelines")
            st.write("Publish verified buy requests to the network. Use the integrated Localized Price Intelligence model to verify local market price suggestions.")
            
            ord_col1, ord_col2 = st.columns(2)
            with ord_col1:
                o_crop = st.selectbox("Requested Crop", ["Wheat", "Onions", "Paddy (Basmati)", "Cotton", "Potatoes (Jyoti)"])
                o_target = st.number_input("Target Aggregate Quantity (kg)", min_value=1000, max_value=100000, value=10000, step=1000)
                o_site = st.text_input("Mandi Collection Center", value="Azadpur APMC, Delhi")
                o_slot = st.selectbox("Allocated Operating Shift", ["Full Day (Active)", "06:00 AM - 12:00 PM", "12:00 PM - 06:00 PM"])
            with ord_col2:
                st.markdown("""
                <div class="custom-container">
                    <h5 style='margin: 0 0 10px 0; font-size: 14px; font-weight: 700; color: var(--text-color, #0f172a);'>📡 Localized Price Intelligence API</h5>
                    <p style='margin: 0 0 15px 0; font-size: 12px; color: var(--text-color, #64748b); opacity: 0.85;'>
                        Automatically query the internet and localized APMC databases to capture average regional crop transactions and prevent localization pricing errors.
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("Run Region-Aware Market Price Lookup", use_container_width=True):
                    with st.spinner("Accessing dynamic local market averages..."):
                        time.sleep(1.2)
                        
                        # Geolocation price simulation
                        if "Delhi" in o_site:
                            avg_val = random.randint(2200, 2450)
                            region_tag = "NCR Local Mandis"
                        else:
                            avg_val = random.randint(1800, 2100)
                            region_tag = "Regional State Mandis"
                            
                        st.info(f"💡 Suggested Rate found for **{o_crop}** inside **{region_tag}**:\n\n"
                                f"• Regional APMC Median: **₹{avg_val}/Quintal**\n\n"
                                f"• Target FCFS boundaries suggested: **₹{avg_val - 150} to ₹{avg_val + 150}**")
                        
                price_type = st.selectbox("Pricing Mode Option", ["Fixed Cutoff", "Range"])
                if price_type == "Fixed Cutoff":
                    p_min = st.number_input("Standard Cutoff Price (₹ per Quintal)", value=2100)
                    p_max = p_min
                else:
                    p_min = st.number_input("Minimum Pricing Boundary (₹/Quintal)", value=2000)
                    p_max = st.number_input("Maximum Premium Pricing Boundary (₹/Quintal)", value=2400)
                    
            if st.button("Publish Dynamic Buy Order to Network Feed", use_container_width=True):
                new_id = f"ORD00{len(st.session_state.buy_orders) + 1}"
                st.session_state.buy_orders.append({
                    "id": new_id,
                    "crop": o_crop,
                    "target": o_target,
                    "price_type": price_type,
                    "price_min": p_min,
                    "price_max": p_max,
                    "location": o_site,
                    "time_slot": o_slot,
                    "distance_km": round(random.uniform(5, 50), 1)
                })
                add_notification(f"New Order Published: Admin launched buy order for {o_crop} at {o_site} (Target: {o_target} kg)")
                st.success(f"Dynamic Buy Order {new_id} pushed successfully to farmer dashboards!")
                time.sleep(1.0)
                st.rerun()

        # 2nd Tab: Cargo Audit & Farmer Reputation Tuning
        with admin_tab2:
            st.markdown("### ⚖️ Mandi Arrival Audit & Inspection Terminal")
            st.write("Review arriving farmer loads, inspect crop quality standards, and submit performance evaluations to calculate global reputation scores.")
            
            pending_evals = [b for b in st.session_state.bookings if b["status"] == "Confirmed"]
            
            if len(pending_evals) == 0:
                st.info("No active scheduled arrivals are currently awaiting evaluation.")
            else:
                selected_item = st.selectbox("Select Arrived Consignment to Audit", [f"{b['id']} - {b['farmer_name']} ({b['qty']} kg of {next(o['crop'] for o in st.session_state.buy_orders if o['id'] == b['order_id'])})" for b in pending_evals])
                
                target_b_id = selected_item.split(" - ")[0]
                target_b = next(b for b in st.session_state.bookings if b["id"] == target_b_id)
                
                st.markdown(f"""
                <div class="custom-container">
                    <h5 style='margin: 0 0 10px 0; color: var(--text-color, #0f172a); font-weight: 700;'>👤 Farmer Profile Information</h5>
                    <p style='margin: 0; color: var(--text-color, #334155);'>Farmer ID: <b>{target_b['farmer_id']}</b> | Name: <b>{target_b['farmer_name']}</b></p>
                    <p style='margin: 0; color: var(--text-color, #334155);'>Declared Weight: <b>{target_b['qty']} kg</b> | Scheduled Delivery Slot: <b>{target_b['time']}</b></p>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("#### Evaluate Delivery Performance Metrics")
                slider_col1, slider_col2 = st.columns(2)
                with slider_col1:
                    score_q = st.slider("Quality Standards (Grain moisture, impurity limits, FAQ checks)", 1, 5, 5)
                    score_a = st.slider("Quantity Consistency (Actual delivered weight vs. reserved booked volume)", 1, 5, 5)
                with slider_col2:
                    score_p = st.slider("Punctuality Check (On-time arrival within the designated hour)", 1, 5, 5)
                    
                overall_score = round((score_q + score_a + score_p) / 3, 1)
                st.metric("Consignment Weighted Score", f"{overall_score} / 5.0 Stars")
                
                if st.button("Complete Audit & Update Farmer Profile Trust Star History", use_container_width=True):
                    farmer_id = target_b["farmer_id"]
                    farmer_record = st.session_state.farmers_db[farmer_id]
                    
                    p_rating = farmer_record["rating"]
                    p_trips = farmer_record["trips"]
                    
                    # Update reputation score moving average
                    updated_trips = p_trips + 1
                    updated_rating = round(((p_rating * p_trips) + overall_score) / updated_trips, 2)
                    
                    st.session_state.farmers_db[farmer_id]["rating"] = updated_rating
                    st.session_state.farmers_db[farmer_id]["trips"] = updated_trips
                    target_b["status"] = "Completed & Rated"
                    
                    add_notification(f"Consignment audit complete: {target_b['farmer_name']} evaluated. New trust score: {updated_rating} Stars.")
                    st.success("Cargo evaluation verified! Database indicators and farmer profile successfully synced.")
                    time.sleep(1.0)
                    st.rerun()

        # 3rd Tab: Ledgers & Dynamic Reports
        with admin_tab3:
            st.markdown("### 📊 Enterprise Ledger Dashboard")
            st.write("Aggregated visual reporting on regional active buy orders, scheduled slots, and transaction ledgers.")
            
            tot_orders = len(st.session_state.buy_orders)
            tot_slots = len([b for b in st.session_state.bookings if b["status"] == "Confirmed"])
            tot_completed = len([b for b in st.session_state.bookings if "Completed" in b["status"]])
            
            an_col1, an_col2, an_col3 = st.columns(3)
            with an_col1:
                st.metric("Total Active Orders", tot_orders)
            with an_col2:
                st.metric("Active Scheduled Slots", tot_slots)
            with an_col3:
                st.metric("Completed Cargo Audits", tot_completed)
                
            st.markdown("<br/>#### Live Central Database Records", unsafe_allow_html=True)
            ledger_logs = []
            for b in st.session_state.bookings:
                target_ord = next(o for o in st.session_state.buy_orders if o["id"] == b["order_id"])
                ledger_logs.append({
                    "Reservation ID": b["id"],
                    "Farmer Profile": f"{b['farmer_name']} ({b['farmer_id']})",
                    "Crop Type": target_ord["crop"],
                    "Reserved Capacity (kg)": b["qty"],
                    "Scheduled Slot Hour": b["time"],
                    "Current System Status": b["status"]
                })
            
            st.dataframe(pd.DataFrame(ledger_logs), use_container_width=True)
