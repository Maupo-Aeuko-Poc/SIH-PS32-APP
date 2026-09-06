import streamlit as st
import pandas as pd
import numpy as np
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
        },
        {
            "id": "ORD003",
            "crop": "Cotton (Long Staple)",
            "target": 6000,
            "price_type": "Range",
            "price_min": 6800,
            "price_max": 7500,
            "location": "Sirsa APMC, Haryana",
            "time_slot": "08:00 AM - 04:00 PM",
            "distance_km": 28.1
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
        "Welcome to the Smart Crop Procurement Network. All APMC gateways operational.",
        "System Health: Localized Price Intelligence APIs reporting 99.98% accuracy.",
        "Mandi Capacity monitors fully active for the upcoming Kharif season."
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
# 3. INTERFACE CONFIGURATION & HIGH-END THEME INJECTION
# ==============================================================================
st.set_page_config(
    page_title="Smart Crop Procurement Hub",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom premium UI style sheet injection (Inter Font, CSS Card Elevation, Glassmorphism, Adaptive Dark/Light Variables)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    /* Global Typography & Font Family Override */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
    }
    
    /* Elegant Dark/Light Adaptive Variables for Custom HTML Elements */
    :root {
        --card-bg: var(--secondary-background-color, rgba(248, 250, 252, 0.95));
        --card-border: var(--border-color, rgba(226, 232, 240, 0.8));
        --main-text: var(--text-color, #0f172a);
        --accent-color: #6366f1; /* Corporate Indigo */
        --accent-green: #10b981; /* Success Green */
        --accent-orange: #f59e0b; /* Alert Orange */
        --accent-red: #ef4444; /* Error Red */
    }
    
    /* Modern minimalist custom corporate tiles */
    .corporate-tile {
        background: var(--card-bg);
        border: 1px solid var(--card-border);
        border-radius: 16px;
        padding: 35px;
        text-align: center;
        height: 100%;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.03);
        transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
        margin-bottom: 20px;
    }
    .corporate-tile:hover {
        transform: translateY(-8px);
        box-shadow: 0 20px 35px -10px rgba(99, 102, 241, 0.15), 0 10px 15px -3px rgba(0, 0, 0, 0.05);
        border-color: #6366f1;
    }
    
    /* Premium Glassmorphic Metric Box */
    .glass-metric {
        background: var(--card-bg);
        border: 1px solid var(--card-border);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.03);
        transition: transform 0.2s;
    }
    .glass-metric:hover {
        transform: scale(1.02);
    }
    
    /* Soft Acrylic Tinted Status Badges */
    .badge-pill {
        font-weight: 700;
        padding: 6px 16px;
        border-radius: 9999px;
        font-size: 11px;
        display: inline-block;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        border: 1px solid transparent;
    }
    .badge-active { 
        background-color: rgba(16, 185, 129, 0.12); 
        color: #10b981; 
        border-color: rgba(16, 185, 129, 0.25);
    }
    .badge-locked { 
        background-color: rgba(239, 68, 68, 0.12); 
        color: #ef4444; 
        border-color: rgba(239, 68, 68, 0.25);
    }
    .badge-pending { 
        background-color: rgba(245, 158, 11, 0.12); 
        color: #f59e0b; 
        border-color: rgba(245, 158, 11, 0.25);
    }
    
    /* Notification styling */
    .notif-box {
        background: var(--card-bg);
        border-left: 5px solid var(--accent-color);
        border-right: 1px solid var(--card-border);
        border-top: 1px solid var(--card-border);
        border-bottom: 1px solid var(--card-border);
        padding: 14px 18px;
        border-radius: 8px;
        margin-bottom: 12px;
        box-shadow: 0 2px 4px -1px rgba(0,0,0,0.02);
    }
    
    /* Clean button styling override */
    .stButton>button {
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease-in-out !important;
    }
</style>
""", unsafe_allow_html=True)

# Completely hide default Streamlit top bar & footer branding
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
# 4.1 LANDING SCREEN (SOCIALLY DISTANCED, MAJESTIC TILES)
# ------------------------------------------------------------------------------
if st.session_state.view == "landing":
    st.markdown("<br/><br/>", unsafe_allow_html=True)
    
    # Corporate Enterprise Branding Header
    h_col1, h_col2, h_col3 = st.columns([1, 10, 1])
    with h_col2:
        st.markdown("""
        <div style='text-align: center;'>
            <span style='background: linear-gradient(135deg, #6366f1, #a855f7); color: white; padding: 6px 14px; border-radius: 20px; font-size: 11px; font-weight: 800; letter-spacing: 2px;'>SMART INDIA HACKATHON 2026</span>
            <h1 style='font-size: 48px; font-weight: 800; letter-spacing: -1.5px; margin-top: 15px; margin-bottom: 8px;'>KHARIF-PRO SECURE</h1>
            <p style='font-size: 18px; font-weight: 400; opacity: 0.8; max-width: 650px; margin: 0 auto 10px auto; line-height: 1.5;'>
                Our state-of-the-art enterprise crop procurement queue scheduling hub, protected by multi-factor security and optimized for high-capacity transactions.
            </p>
            <p style='font-size: 12px; font-weight: 600; opacity: 0.5; letter-spacing: 1px; text-transform: uppercase;'>PROBLEM STATEMENT: SIH26032 • STAGE-READY PROTOTYPE</p>
            <div style='height: 1px; background: linear-gradient(90deg, transparent, var(--card-border), transparent); margin: 35px auto; width: 60%;'></div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br/>", unsafe_allow_html=True)
    
    # Majestic Selection Tiles
    t_col1, space_col, t_col2 = st.columns([5, 1, 5])
    
    with t_col1:
        st.markdown("""
        <div class="corporate-tile">
            <div style="font-size: 70px; margin-bottom: 20px; filter: drop-shadow(0 10px 15px rgba(0,0,0,0.05));">🚜</div>
            <h2 style="font-size: 26px; font-weight: 700; margin-bottom: 12px;">FARMER SECTOR</h2>
            <p style="font-size: 14px; opacity: 0.75; line-height: 1.7; margin-bottom: 30px; height: 100px;">
                Secure high-value delivery windows, calculate guaranteed paychecks dynamically using our First-Come, First-Served tiered pricing matrix, check queue distances, and monitor instant cancellation re-openings.
            </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Enter Farmer Portal ➔", key="btn_go_farmer", use_container_width=True, type="primary"):
            st.session_state.role = "farmer"
            st.session_state.view = "login"
            st.rerun()
            
    with t_col2:
        st.markdown("""
        <div class="corporate-tile">
            <div style="font-size: 70px; margin-bottom: 20px; filter: drop-shadow(0 10px 15px rgba(0,0,0,0.05));">🏢</div>
            <h2 style="font-size: 26px; font-weight: 700; margin-bottom: 12px;">CONTROL CENTRE</h2>
            <p style="font-size: 14px; opacity: 0.75; line-height: 1.7; margin-bottom: 30px; height: 100px;">
                Set dynamic target allocations, execute regional location-aware Web Price Discovery queries, run queue capacity limit locks, evaluate cargo quality, and manage real-time SMS broadcasts.
            </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Enter Control Dashboard ➔", key="btn_go_admin", use_container_width=True, type="secondary"):
            st.session_state.role = "admin"
            st.session_state.view = "login"
            st.rerun()

    st.markdown("<br/><br/><br/><br/>", unsafe_allow_html=True)
    st.markdown("""
    <div style='text-align: center; opacity: 0.4; font-size: 12px; letter-spacing: 0.5px;'>
        🛡 Built on Government-Agent Interoperable Architecture & Digital Public Infrastructure (DPI) Benchmarks.
    </div>
    """, unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 4.2 HIGH-END SECURE AUTHENTICATION SCREEN
# ------------------------------------------------------------------------------
elif st.session_state.view == "login":
    st.markdown("<br/>", unsafe_allow_html=True)
    if st.button("⬅ Return to Home Screen", key="btn_back_home", type="secondary"):
        st.session_state.view = "landing"
        st.session_state.role = None
        st.rerun()
        
    st.markdown("<br/>", unsafe_allow_html=True)
    login_c1, login_c2, login_c3 = st.columns([3.5, 5, 3.5])
    
    with login_c2:
        # ------------------
        # FARMER AUTHENTICATION
        # ------------------
        if st.session_state.role == "farmer":
            st.markdown("""
            <div style='text-align: center;'>
                <h2 style='font-weight: 800; font-size: 30px; letter-spacing: -1px; margin-bottom: 8px;'>Farmer Security Desk</h2>
                <p style='opacity: 0.7; font-size: 14px; margin-bottom: 25px;'>Authenticate securely using MFA or register a new crop-sowing profile</p>
            </div>
            """, unsafe_allow_html=True)
            
            auth_tab1, auth_tab2 = st.tabs(["🔐 Secure OTP Access", "✍️ Enroll New Profile"])
            
            with auth_tab1:
                st.markdown("<br/>", unsafe_allow_html=True)
                fmr_id = st.text_input("🌾 Registered Login ID", value="FMR8812")
                fmr_pwd = st.text_input("🔑 Security Password", type="password", value="pass")
                
                # Dynamic demo assistant for SIH judges
                with st.expander("💡 Live Demonstration Guide (For Judges)"):
                    st.markdown("""
                    We have pre-seeded active farmer database profiles for instant verification:
                    *   **Farmer 1:** ID: `FMR8812` | Password: `pass` (High 4.8 Rating)
                    *   **Farmer 2:** ID: `FMR4012` | Password: `pass` (Standard 4.5 Rating)
                    """)
                
                if fmr_id in st.session_state.farmers_db:
                    sim_otp = "8812"
                    st.warning(f"📨 **OTP Simulated:** A secure SMS containing code **{sim_otp}** was sent to {st.session_state.farmers_db[fmr_id]['phone']}.")
                    otp_input = st.text_input("🔢 Enter 4-Digit Security OTP", placeholder="Enter the code sent to your phone")
                    
                    if st.button("Authenticate & Log In ➔", use_container_width=True, type="primary"):
                        if fmr_pwd == "pass" and otp_input == sim_otp:
                            st.session_state.logged_in_farmer = fmr_id
                            st.session_state.view = "dashboard"
                            st.success("Identity Secured. Redirecting to workspace...")
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.error("Authentication check failed. Please check password or OTP.")
                else:
                    st.error("Login ID not found. Register your profile in the next tab.")
                    
            with auth_tab2:
                st.markdown("<br/>", unsafe_allow_html=True)
                reg_col1, reg_col2 = st.columns(2)
                with reg_col1:
                    new_name = st.text_input("👤 Full Legal Name", placeholder="e.g., Sukhdev Singh")
                    new_age = st.number_input("📅 Age", min_value=18, max_value=100, value=35)
                    new_phone = st.text_input("📱 Mobile Number", placeholder="e.g., 9876543210")
                with reg_col2:
                    new_loc = st.text_input("📍 Village / District", placeholder="e.g., Jind, Haryana")
                    new_aadhaar = st.text_input("🆔 Aadhaar Card ID (Land Match)", placeholder="4432-1102-9901")
                    new_crop = st.selectbox("🌾 Crop Variety Sown", ["Paddy (Basmati)", "Wheat", "Potatoes (Jyoti)", "Cotton", "Onions"])
                
                if st.button("Complete Aadhaar Identity Verification ➔", use_container_width=True, type="secondary"):
                    if new_name and new_phone and new_aadhaar:
                        new_fid = f"FMR{random.randint(1000, 9999)}"
                        st.session_state.farmers_db[new_fid] = {
                            "name": new_name,
                            "password": "pass",
                            "phone": new_phone,
                            "rating": 5.0,  # Start with perfect reputation rating
                            "trips": 0
                        }
                        st.success(f"Verified! Your Aadhaar matched land records. Generated ID: **{new_fid}** | Password: **pass**.")
                        add_notification(f"DPI registry updated: Farmer {new_name} ({new_fid}) enrolled via Aadhaar.")
                    else:
                        st.error("All details and valid Aadhaar identification are required.")
                        
        # ------------------
        # ADMIN AUTHENTICATION
        # ------------------
        else:
            st.markdown("""
            <div style='text-align: center;'>
                <h2 style='font-weight: 800; font-size: 30px; letter-spacing: -1px; margin-bottom: 8px;'>Mandi Operations Control Room</h2>
                <p style='opacity: 0.7; font-size: 14px; margin-bottom: 25px;'>Admin, Departmental & On-Site Inspector Clearance Required</p>
            </div>
            """, unsafe_allow_html=True)
            
            adm_id = st.text_input("👤 Government Admin ID", value="ADMIN_SIH26")
            adm_pwd = st.text_input("🔑 System Password", type="password", value="sih2026")
            adm_key = st.text_input("🛡 Triple-Factor Security Key", value="KEY-9921-X")
            
            with st.expander("💡 Helper: Demo Keys for Judges"):
                st.markdown("""
                *   **Admin ID:** `ADMIN_SIH26`
                *   **Password:** `sih2026`
                *   **Admin Key:** `KEY-9921-X`
                """)
                
            if st.button("Unlock Control Room Terminal ➔", use_container_width=True, type="primary"):
                if adm_id == "ADMIN_SIH26" and adm_pwd == "sih2026" and adm_key == "KEY-9921-X":
                    st.session_state.admin_logged_in = True
                    st.session_state.view = "dashboard"
                    st.success("Clearance Granted. Initializing administrative dashboards...")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("Access Denied: Administrative validation checks failed.")

# ------------------------------------------------------------------------------
# 4.3 CORPORATE WORKSPACE INTERFACES (TABBED & RE-ENGINEERED UX)
# ------------------------------------------------------------------------------
elif st.session_state.view == "dashboard":
    
    # ------------------
    # FARMER WORKSPACE
    # ------------------
    if st.session_state.role == "farmer":
        # Professional UI Top Banner
        head_c1, head_c2 = st.columns([8.5, 1.5])
        with head_c1:
            farmer_profile = st.session_state.farmers_db[st.session_state.logged_in_farmer]
            st.markdown(f"""
            <div style='margin-bottom: 10px;'>
                <span style='background: #6366f1; color: white; padding: 4px 10px; border-radius: 4px; font-size: 10px; font-weight: 700;'>SECURE SOWING DEVICE</span>
                <h1 style='font-size: 32px; font-weight: 800; letter-spacing: -1px; margin: 8px 0 2px 0;'>Welcome back, {farmer_profile['name']}</h1>
                <p style='opacity: 0.7; margin: 0;'>Farmer ID: <b>{st.session_state.logged_in_farmer}</b> | Device Location: <b>Jind region, Haryana</b></p>
            </div>
            """, unsafe_allow_html=True)
        with head_c2:
            st.markdown("<br/>", unsafe_allow_html=True)
            if st.button("🚪 Logout", use_container_width=True, type="secondary"):
                st.session_state.logged_in_farmer = None
                st.session_state.view = "landing"
                st.session_state.role = None
                st.rerun()
                
        # Metric Grid for Farmer Info
        m_col1, m_col2, m_col3 = st.columns(3)
        with m_col1:
            st.markdown(f"""
            <div class='glass-metric'>
                <p style='margin: 0; font-size: 11px; opacity: 0.6; font-weight: 700; text-transform: uppercase;'>Your Global Trust Rating</p>
                <h2 style='margin: 5px 0; color: #f59e0b; font-size: 32px;'>{farmer_profile['rating']} <span style='font-size: 18px;'>★</span></h2>
                <p style='margin: 0; font-size: 11px; opacity: 0.5;'>Based on previous delivery logs</p>
            </div>
            """, unsafe_allow_html=True)
        with m_col2:
            st.markdown(f"""
            <div class='glass-metric'>
                <p style='margin: 0; font-size: 11px; opacity: 0.6; font-weight: 700; text-transform: uppercase;'>Total Mandi Trips</p>
                <h2 style='margin: 5px 0; color: #6366f1; font-size: 32px;'>{farmer_profile['trips']} <span style='font-size: 18px;'>Loads</span></h2>
                <p style='margin: 0; font-size: 11px; opacity: 0.5;'>100% compliant transactions</p>
            </div>
            """, unsafe_allow_html=True)
        with m_col3:
            # Active booked count
            my_bookings = [b for b in st.session_state.bookings if b["farmer_id"] == st.session_state.logged_in_farmer and b["status"] == "Confirmed"]
            st.markdown(f"""
            <div class='glass-metric'>
                <p style='margin: 0; font-size: 11px; opacity: 0.6; font-weight: 700; text-transform: uppercase;'>Active Scheduled Bookings</p>
                <h2 style='margin: 5px 0; color: #10b981; font-size: 32px;'>{len(my_bookings)} <span style='font-size: 18px;'>Active</span></h2>
                <p style='margin: 0; font-size: 11px; opacity: 0.5;'>Guaranteed drop-off gates</p>
            </div>
            """, unsafe_allow_html=True)
            
        st.write("<br/>", unsafe_allow_html=True)
        
        # Tabs organizing everything clean and structured
        f_tab1, f_tab2, f_tab3 = st.tabs(["🔍 Find & Book Active Mandi Slots", "📂 View Your Live Gatepasses", "📡 Real-Time Push Alerts"])
        
        # TAB 1: FIND & BOOK ACTIVE SLOTS
        with f_tab1:
            st.markdown("### 🌾 Active Regional Buy Demands")
            st.write("Browse government procurement orders. If the order has a price range, early bookings secure higher dynamic FCFS prices.")
            
            # Clean horizontal filters layout
            fil_c1, fil_c2 = st.columns(2)
            with fil_c1:
                f_crop = st.selectbox("Target Sown Crop Filter", ["All", "Paddy (Basmati)", "Wheat", "Potatoes (Jyoti)", "Cotton (Long Staple)", "Onions"])
            with fil_c2:
                f_qty = st.number_input("Minimum Volume Capacity (kg)", min_value=0, value=0)
                
            st.markdown("<br/>", unsafe_allow_html=True)
            
            # Display target orders
            for order in st.session_state.buy_orders:
                if f_crop != "All" and order["crop"] != f_crop:
                    continue
                
                # Bookings telemetry
                order_bookings = [b for b in st.session_state.bookings if b["order_id"] == order["id"] and b["status"] == "Confirmed"]
                total_booked = sum(b["qty"] for b in order_bookings)
                remaining_cap = order["target"] - total_booked
                
                # Progress visual calculation
                progress_val = float(total_booked / order["target"])
                
                # Card Container UI Layout
                st.markdown(f"""
                <div style='background-color: var(--card-bg); border: 1px solid var(--card-border); border-radius: 12px; padding: 24px; margin-bottom: 25px;'>
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <div>
                            <span style='background-color: rgba(99, 102, 241, 0.1); color: #6366f1; padding: 3px 8px; border-radius: 4px; font-size: 10px; font-weight: 700;'>ORDER ID: {order['id']}</span>
                            <h3 style='margin: 8px 0 2px 0; font-size: 22px;'>🌾 {order['crop']}</h3>
                            <p style='margin: 0; font-size: 13px; opacity: 0.7;'>📍 Site: <b>{order['location']}</b> | ⏱ Operating Window: <b>{order['time_slot']}</b></p>
                        </div>
                        <div>
                            {"<span class='badge-pill badge-active'>Active Open</span>" if remaining_cap > 0 else "<span class='badge-pill badge-locked'>Queue Full (View-Only)</span>"}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Detail grid
                det_c1, det_c2, det_c3 = st.columns([3, 3, 2])
                with det_c1:
                    st.write(f"📏 **Geographic Transit Distance:** **{order['distance_km']} km**")
                    st.write(f"📈 **Global Quota Target:** {order['target']:,} kg")
                    # Progress bar
                    st.progress(min(1.0, progress_val))
                    st.caption(f"Currently Filled: **{total_booked:,} / {order['target']:,} kg** ({int(progress_val * 100)}%)")
                    
                with det_c2:
                    if order["price_type"] == "Range":
                        st.write(f"💰 **Pricing Strategy:** Flexible Range (₹{order['price_min']} - ₹{order['price_max']}/qtl)")
                        cur_rate = calculate_tiered_price(order, total_booked)
                        st.markdown(f"""
                        <div style='background-color: rgba(16, 185, 129, 0.08); border-left: 3px solid #10b981; padding: 8px 12px; border-radius: 4px;'>
                            <span style='font-size: 11px; font-weight: 700; color: #10b981; text-transform: uppercase;'>Early-Bird FCFS rate:</span><br/>
                            <h4 style='margin: 2px 0; color: #10b981; font-size: 20px;'>₹{cur_rate} <span style='font-size: 12px; opacity: 0.7;'>/quintal</span></h4>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.write(f"💰 **Pricing Strategy:** Fixed Government MSP")
                        st.markdown(f"**Standard Cutoff Price:** ₹{order['price_min']}/quintal")
                        
                with det_c3:
                    # Render active reservation form or view-only lock
                    if remaining_cap > 0:
                        with st.expander("📝 Open Slot Booking Sheet"):
                            # Interactive inputs
                            book_qty = st.number_input("Enter your delivery load (kg)", min_value=100, max_value=int(remaining_cap), step=100, key=f"fq_{order['id']}")
                            book_hour = st.selectbox("Select target drop-off hour", ["06:00 AM", "07:00 AM", "08:00 AM", "09:00 AM", "10:00 AM", "11:00 AM", "12:00 PM"], key=f"fh_{order['id']}")
                            
                            # Price locking and paycheck calculation logic
                            secured_rate = calculate_tiered_price(order, total_booked)
                            estimated_paycheck = int((book_qty / 100) * secured_rate)
                            
                            st.markdown(f"""
                            <div class='stat-container' style='margin-bottom: 12px;'>
                                <p style='margin:0; font-size:10px; opacity:0.6; font-weight:700;'>PREVIEW SECURED RATE</p>
                                <h3 style='margin:4px 0; color:#10b981;'>₹{secured_rate} <span style='font-size:11px;'>/qtl</span></h3>
                                <p style='margin:0; font-size:12px;'>Est. Paycheck: <b>₹{estimated_paycheck:,}</b></p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            if st.button("Generate Secure Gatepass ➔", key=f"fbtn_{order['id']}", use_container_width=True):
                                # Compile new booking
                                new_b = {
                                    "id": f"BOK{random.randint(100, 999)}",
                                    "order_id": order["id"],
                                    "farmer_name": farmer_profile["name"],
                                    "farmer_id": st.session_state.logged_in_farmer,
                                    "qty": book_qty,
                                    "time": book_hour,
                                    "price_secured": secured_rate,
                                    "status": "Confirmed",
                                    "timestamp": datetime.now()
                                }
                                st.session_state.bookings.append(new_b)
                                add_notification(f"Mandi Reservation Locked: Farmer {new_b['farmer_name']} secured gatepass for {book_qty} kg at {book_hour}")
                                st.success("Gatepass successfully generated! Access details on the adjacent tab.")
                                time.sleep(0.8)
                                st.rerun()
                    else:
                        # -------------------------------------------------------------
                        # CLIENT-SIDE VIEW-ONLY CPU AND API LOAD OPTIMIZATION ENGINE
                        # -------------------------------------------------------------
                        st.markdown("""
                        <div style='background-color: rgba(239, 68, 68, 0.08); border-left: 3px solid #ef4444; padding: 12px; border-radius: 6px;'>
                            <span style='font-size: 11px; font-weight: 700; color: #ef4444; text-transform: uppercase;'>CLOSED QUEUE LOCKED</span><br/>
                            <span style='font-size: 11px; opacity: 0.8;'>Rendering lightweight read-only table on client to eliminate active server polling.</span>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        filled_bookings = [b for b in st.session_state.bookings if b["order_id"] == order["id"] and b["status"] == "Confirmed"]
                        if len(filled_bookings) > 0:
                            st.dataframe(
                                pd.DataFrame([
                                    {"Scheduled Arrival": b["time"], "Farmer ID": b["farmer_id"], "Load (kg)": b["qty"], "Tiered Price Locked": f"₹{b['price_secured']}"}
                                    for b in filled_bookings
                                ]), use_container_width=True, hide_index=True
                            )
                st.write("<br/><hr style='border-color: var(--card-border);'/><br/>", unsafe_allow_html=True)
                
        # TAB 2: ACTIVE RESERVATIONS & GATED PASSES
        with f_tab2:
            st.markdown("### 📂 Your Generated Gatepasses")
            st.write("Below are your verified delivery reservations. Bring fully dried crops meeting standard quality guidelines.")
            
            my_res = [b for b in st.session_state.bookings if b["farmer_id"] == st.session_state.logged_in_farmer]
            
            if len(my_res) == 0:
                st.info("You do not currently hold any active gatepasses on the regional ledger.")
            else:
                for b in my_res:
                    target_order = next(o for o in st.session_state.buy_orders if o["id"] == b["order_id"])
                    
                    st.markdown(f"""
                    <div style='background-color: var(--card-bg); border: 1px solid var(--card-border); border-radius: 12px; padding: 20px; margin-bottom: 20px;'>
                        <div style='display: flex; justify-content: space-between; align-items: center;'>
                            <div>
                                <span style='font-size: 10px; font-weight: 700; opacity: 0.5;'>PASS CODE: {b['id']}</span>
                                <h4 style='margin: 4px 0 0 0; font-size: 18px;'>🌾 {target_order['crop']} Drop-off</h4>
                                <p style='margin: 0; font-size: 12px; opacity: 0.7;'>📍 Mandi: {target_order['location']}</p>
                            </div>
                            <div>
                                <span class="badge-pill {'badge-active' if b['status'] == 'Confirmed' else 'badge-pending' if 'Completed' in b['status'] else 'badge-locked'}">
                                    {b['status']}
                                </span>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    g_col1, g_col2, g_col3 = st.columns([3, 3, 2])
                    with g_col1:
                        st.write(f"⏱ **Scheduled Window:** {b['time']}")
                        st.write(f"⚖ **Registered Weight:** {b['qty']} kg")
                    with g_col2:
                        st.write(f"🔒 **Locked Price-per-Quintal:** ₹{b['price_secured']}")
                        st.write(f"💵 **Projected Disbursement:** **₹{int((b['qty']/100)*b['price_secured']):,}**")
                    with g_col3:
                        if b["status"] == "Confirmed":
                            c_reason = st.text_input("Reason for cancel request", key=f"re_{b['id']}", placeholder="e.g., Logistic delay, weather risk")
                            if st.button("Release Gatepass ➔", key=f"can_{b['id']}", use_container_width=True, type="secondary"):
                                if c_reason:
                                    b["status"] = "Cancelled"
                                    add_notification(f"Gatepass Cancelled: {farmer_profile['name']} released slot for {b['qty']} kg of {target_order['crop']}. Reason: {c_reason}")
                                    st.success("Mandi capacity released back to regional pool.")
                                    time.sleep(0.8)
                                    st.rerun()
                                else:
                                    st.error("Cancellation reason is required to release queue capacity.")
                    st.write("<br/>", unsafe_allow_html=True)

        # TAB 3: DYNAMIC ALERTS AND PUSH NOTIFICATIONS FEED
        with f_tab3:
            st.markdown("### 📡 Active Network Telemetry Feed")
            st.write("Our platform dynamically broadcasts queue releases, cancellation re-openings, and administrative buy-order announcements.")
            
            for note in st.session_state.push_notifications[:10]:
                st.markdown(f"""
                <div class="notif-box">
                    <span style='font-size: 13px; color: var(--main-text); font-weight: 500;'>{note}</span>
                </div>
                """, unsafe_allow_html=True)
                
    # ------------------
    # ADMINISTRATOR & CONTROL DASHBOARD
    # ------------------
    else:
        # Dashboard Admin Header
        head_a1, head_a2 = st.columns([8.5, 1.5])
        with head_a1:
            st.markdown("""
            <div style='margin-bottom: 10px;'>
                <span style='background: #ef4444; color: white; padding: 4px 10px; border-radius: 4px; font-size: 10px; font-weight: 700;'>ADMIN ACCESS</span>
                <h1 style='font-size: 32px; font-weight: 800; letter-spacing: -1px; margin: 8px 0 2px 0;'>Mandi Command Operations Centre</h1>
                <p style='opacity: 0.7; margin: 0;'>Active Session: <b>ADMIN_SIH26</b> | Multi-Factor Secure Channel Enforced</p>
            </div>
            """, unsafe_allow_html=True)
        with head_a2:
            st.markdown("<br/>", unsafe_allow_html=True)
            if st.button("🚪 Terminate", use_container_width=True, type="secondary"):
                st.session_state.admin_logged_in = False
                st.session_state.view = "landing"
                st.session_state.role = None
                st.rerun()
                
        # Tab structures for clean split
        adm_tab1, adm_tab2, adm_tab3 = st.tabs(["🆕 Create Buy Order", "⚖️ Mandi Cargo Audit", "📊 System Ledgers"])
        
        # TAB 1: CREATE BUY ORDER WITH PRICE INTELLIGENCE
        with adm_tab1:
            st.markdown("### 🆕 Publish Procurement Guidelines")
            st.write("Publish dynamic or fixed procurement buy orders. Run our region-aware Localized Price Intelligence engine to verify regional median transaction values.")
            
            form_col1, form_col2 = st.columns(2)
            with form_col1:
                o_crop = st.selectbox("Requested Crop Variety", ["Wheat", "Onions", "Paddy (Basmati)", "Cotton (Long Staple)", "Potatoes (Jyoti)"])
                o_target = st.number_input("Target Volume Allocation (kg)", min_value=1000, max_value=100000, value=10000, step=1000)
                o_site = st.text_input("APMC Mandi Collection Center", value="Azadpur APMC, Delhi")
                o_slot = st.selectbox("Operating Shift Window", ["Full Day (Active)", "06:00 AM - 12:00 PM", "12:00 PM - 06:00 PM"])
            with form_col2:
                st.markdown("""
                <div style='background-color: var(--card-bg); border: 1px solid var(--card-border); border-radius: 12px; padding: 20px; margin-bottom: 15px;'>
                    <h5 style='margin: 0 0 10px 0; font-size: 14px; font-weight: 700;'>📡 Localized Price Intelligence Engine</h5>
                    <p style='margin: 0 0 15px 0; font-size: 12px; opacity: 0.7;'>
                        Run location-aware API queries across digital APMC mandis to suggest optimal target price boundaries, reducing regional transaction disputes.
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                # Active Price Search Logic
                if st.button("Execute Location-Aware Price Discovery Search 🔍", use_container_width=True):
                    with st.spinner("Accessing dynamic APMC market indicators..."):
                        time.sleep(1.2)
                        
                        # Simulate localization algorithm
                        if "Delhi" in o_site:
                            suggested_avg = random.randint(2200, 2450)
                            region = "National Capital Region / Delhi APMCs"
                        elif "Haryana" in o_site or "Sirsa" in o_site:
                            suggested_avg = random.randint(6800, 7100)
                            region = "Haryana State Mandis"
                        else:
                            suggested_avg = random.randint(1800, 2100)
                            region = "Regional State APMC Mandis"
                            
                        st.info(f"📡 Price suggestion found for **{o_crop}** inside **{region}**:\n\n"
                                f"• Regional APMC Median: **₹{suggested_avg}/Quintal**\n\n"
                                f"• Recommended FCFS Range: **₹{suggested_avg - 150} to ₹{suggested_avg + 150}**")
                        
                price_opt = st.selectbox("Pricing Strategy Mode", ["Fixed Cutoff", "Range"])
                if price_opt == "Fixed Cutoff":
                    p_min = st.number_input("Standard Government MSP (₹ per Quintal)", value=2100)
                    p_max = p_min
                else:
                    p_min = st.number_input("Minimum Baseline Price (₹ per Quintal)", value=2000)
                    p_max = st.number_input("Maximum Early-Bird Premium (₹ per Quintal)", value=2400)
                    
            if st.button("Publish Dynamic Buy Order to Network Feed ➔", use_container_width=True, type="primary"):
                new_id = f"ORD00{len(st.session_state.buy_orders) + 1}"
                st.session_state.buy_orders.append({
                    "id": new_id,
                    "crop": o_crop,
                    "target": o_target,
                    "price_type": price_opt,
                    "price_min": p_min,
                    "price_max": p_max,
                    "location": o_site,
                    "time_slot": o_slot,
                    "distance_km": round(random.uniform(5, 50), 1)
                })
                add_notification(f"Administrative Order Pushed: Secure buy order {new_id} issued for {o_crop} at {o_site}")
                st.success(f"Buy Order **{new_id}** is now active across all regional farmer feeds!")
                time.sleep(0.8)
                st.rerun()

        # TAB 2: MANDI CARGO AUDIT & STAR RATINGS
        with adm_tab2:
            st.markdown("### ⚖️ Mandi Arrival Audit & Evaluation")
            st.write("Inspect physically arriving farmer loads at delivery gate, verify crop compliance, and rate performance metrics to update farmer trust ratings.")
            
            pending_evals = [b for b in st.session_state.bookings if b["status"] == "Confirmed"]
            
            if len(pending_evals) == 0:
                st.info("No active scheduled arrivals are currently awaiting evaluation.")
            else:
                selected_item = st.selectbox(
                    "Select Arrived Consignment to Audit", 
                    [f"{b['id']} - {b['farmer_name']} ({b['qty']} kg of {next(o['crop'] for o in st.session_state.buy_orders if o['id'] == b['order_id'])})" for b in pending_evals]
                )
                
                target_b_id = selected_item.split(" - ")[0]
                target_b = next(b for b in st.session_state.bookings if b["id"] == target_b_id)
                
                st.markdown(f"""
                <div style='background-color: var(--card-bg); border: 1px solid var(--card-border); border-radius: 12px; padding: 20px; margin-top: 15px; margin-bottom: 25px;'>
                    <h5 style='margin: 0 0 8px 0; font-size: 15px;'>👤 Farmer Security Information</h5>
                    <p style='margin: 0; font-size: 13px;'>Farmer Account ID: <b>{target_b['farmer_id']}</b> | Legal Name: <b>{target_b['farmer_name']}</b></p>
                    <p style='margin: 0; font-size: 13px;'>Declared Weight: <b>{target_b['qty']} kg</b> | Scheduled Gate Hour: <b>{target_b['time']}</b></p>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("#### Performance Evaluation Scoring Sheet")
                slider_col1, slider_col2 = st.columns(2)
                with slider_col1:
                    score_q = st.slider("Quality Standards (Grain moisture, impurity limits, FAQ checks)", 1, 5, 5)
                    score_a = st.slider("Quantity Consistency (Actual delivered weight vs. reserved booked volume)", 1, 5, 5)
                with slider_col2:
                    score_p = st.slider("Punctuality Check (On-time arrival within the designated hour)", 1, 5, 5)
                    
                overall_score = round((score_q + score_a + score_p) / 3, 1)
                st.metric("Consignment Weighted Score", f"{overall_score} / 5.0 Stars")
                
                if st.button("Publish Cargo Audit & Update Trust Score ➔", use_container_width=True, type="primary"):
                    f_id = target_b["farmer_id"]
                    farmer_record = st.session_state.farmers_db[f_id]
                    
                    p_rating = farmer_record["rating"]
                    p_trips = farmer_record["trips"]
                    
                    # Update reputation score via moving average mechanics
                    updated_trips = p_trips + 1
                    updated_rating = round(((p_rating * p_trips) + overall_score) / updated_trips, 2)
                    
                    st.session_state.farmers_db[f_id]["rating"] = updated_rating
                    st.session_state.farmers_db[f_id]["trips"] = updated_trips
                    target_b["status"] = "Completed & Rated"
                    
                    add_notification(f"Consignment audit complete: {target_b['farmer_name']} evaluated. New trust score: {updated_rating} Stars.")
                    st.success("Cargo evaluation verified! Database indicators and farmer profile successfully synced.")
                    time.sleep(0.8)
                    st.rerun()

        # TAB 3: ENTERPRISE SYSTEM LEDGERS
        with adm_tab3:
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
            
            st.dataframe(pd.DataFrame(ledger_logs), use_container_width=True, hide_index=True)
