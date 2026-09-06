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
            "price_secured": 2350,  # mid-tier
            "status": "Confirmed",
            "timestamp": datetime.now() - timedelta(hours=1)
        }
    ]
    
    # Active registered farmers db simulation
    st.session_state.farmers_db = {
        "FMR8812": {"name": "Sukhdev Singh", "password": "pass", "phone": "9876543210", "rating": 4.8, "trips": 12},
        "FMR4012": {"name": "Ramesh Patidar", "password": "pass", "phone": "9441234567", "rating": 4.5, "trips": 8}
    }
    
    # Push Notifications log - cleaned from unnecessary marketing jargon
    st.session_state.push_notifications = [
        "System Status: Secure regional nodes synced.",
        "Mandi capacity monitors verified for operational queues."
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
    st.session_state.push_notifications.insert(0, f"[{timestamp}] 📢 {text}")

# ==============================================================================
# 3. INTERFACE CONFIGURATION & ADAPTIVE HIGHEST-END CORPORATE THEME INJECTION
# ==============================================================================
st.set_page_config(
    page_title="Smart Crop Procurement System",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Advanced adaptive stylesheet: perfectly integrates with both Streamlit Light and Dark modes
# Uses native CSS variables to automatically scale typography and background colors with no text-clash
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    /* Font Override */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
    }
    
    /* Hide Streamlit Native Top Bar Clutter for Enterprise Aesthetic */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Sleek Adaptive Landing Cards with Color Accents */
    .landing-card-farmer {
        background-color: var(--secondary-background-color);
        color: var(--text-color);
        border: 1px solid var(--border-color);
        border-top: 5px solid #10b981; /* Farmer Emerald Accent */
        border-radius: 12px;
        padding: 30px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        margin-bottom: 25px;
    }
    .landing-card-farmer:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 20px rgba(16, 185, 129, 0.12);
        border-color: #10b981;
    }
    
    .landing-card-admin {
        background-color: var(--secondary-background-color);
        color: var(--text-color);
        border: 1px solid var(--border-color);
        border-top: 5px solid #3b82f6; /* Admin Azure Accent */
        border-radius: 12px;
        padding: 30px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        margin-bottom: 25px;
    }
    .landing-card-admin:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 20px rgba(59, 130, 246, 0.12);
        border-color: #3b82f6;
    }
    
    /* Modern Frost-glass Status Badges */
    .status-pill {
        font-weight: 600;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 11px;
        display: inline-block;
        border: 1px solid transparent;
    }
    .pill-active {
        background-color: rgba(16, 185, 129, 0.12);
        color: #10b981;
        border-color: rgba(16, 185, 129, 0.2);
    }
    .pill-full {
        background-color: rgba(239, 68, 68, 0.12);
        color: #ef4444;
        border-color: rgba(239, 68, 68, 0.2);
    }
    .pill-pending {
        background-color: rgba(245, 158, 11, 0.12);
        color: #f59e0b;
        border-color: rgba(245, 158, 11, 0.2);
    }
    
    /* Structured UI Layout Blocks */
    .saas-card {
        background-color: var(--secondary-background-color);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.01);
    }
    
    .glass-metric {
        background-color: var(--secondary-background-color);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 2px 6px rgba(0,0,0,0.01);
    }
    
    /* Typography Overrides */
    .title-h1 {
        font-weight: 800;
        font-size: 32px;
        letter-spacing: -0.5px;
        color: var(--text-color);
    }
    
    .subtitle-p {
        font-size: 14px;
        color: var(--text-color);
        opacity: 0.75;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 4. VIEW CONTROLLER
# ==============================================================================

# ------------------------------------------------------------------------------
# 4.1 LANDING SCREEN (TWO CLEANLY ACCENTED WORKSPACE TILES)
# ------------------------------------------------------------------------------
if st.session_state.view == "landing":
    st.markdown("<br/><br/>", unsafe_allow_html=True)
    
    # Header Section
    logo_col1, logo_col2, logo_col3 = st.columns([1, 10, 1])
    with logo_col2:
        st.markdown("<h1 style='text-align: center; font-size: 36px; font-weight: 800; letter-spacing: -1px; margin-bottom: 5px;'>SMART CROP PROCUREMENT SYSTEM</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; font-size: 14px; opacity: 0.75; margin-bottom: 20px;'>Enterprise Scheduling, Dynamic FCFS Pricing & On-Site Inspection Auditing</p>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; font-size: 11px; font-weight: 700; opacity: 0.6; letter-spacing: 2px;'>SMART INDIA HACKATHON • PROBLEM STATEMENT ID: SIH26032</p>", unsafe_allow_html=True)
        st.markdown("<div style='height: 1px; background-color: var(--border-color); margin: 24px auto; width: 40%;'></div>", unsafe_allow_html=True)
    
    st.markdown("<br/>", unsafe_allow_html=True)
    
    # Side-by-Side Accent-Colored Cards
    tile_col1, space_col, tile_col2 = st.columns([4, 1, 4])
    
    with tile_col1:
        st.markdown("""
        <div class="landing-card-farmer">
            <div style="font-size: 48px; margin-bottom: 15px;">🚜</div>
            <h2 style="font-size: 20px; font-weight: 700; margin-bottom: 10px;">FARMER PORTAL</h2>
            <p style="font-size: 13px; opacity: 0.8; line-height: 1.5; margin-bottom: 25px;">
                Secure delivery slots, access real-time tiered pricing benchmarks, view paycheck estimates, and coordinate logistics prior to arrival.
            </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Access Farmer Workspace ➔", key="btn_go_farmer", use_container_width=True):
            st.session_state.role = "farmer"
            st.session_state.view = "login"
            st.rerun()
            
    with tile_col2:
        st.markdown("""
        <div class="landing-card-admin">
            <div style="font-size: 48px; margin-bottom: 15px;">🏢</div>
            <h2 style="font-size: 20px; font-weight: 700; margin-bottom: 10px;">CONTROL PANEL</h2>
            <p style="font-size: 13px; opacity: 0.8; line-height: 1.5; margin-bottom: 25px;">
                Publish procurement guidelines, verify localized price trends, execute cargo audits, and update farmer history ledgers.
            </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Access Admin Console ➔", key="btn_go_admin", use_container_width=True):
            st.session_state.role = "admin"
            st.session_state.view = "login"
            st.rerun()

    st.markdown("<br/><br/><br/>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: center; font-size: 11px; opacity: 0.5;'>Operational Environment v5.0 • Powered by Digital Public Infrastructure Specifications</div>", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 4.2 CLEAN & CENTRED SIGN-IN ENVIRONMENT (LIGHT/DARK HARMONIZED)
# ------------------------------------------------------------------------------
elif st.session_state.view == "login":
    st.markdown("<br/>", unsafe_allow_html=True)
    if st.button("⬅ Return to Role Selection", key="btn_back_home"):
        st.session_state.view = "landing"
        st.session_state.role = None
        st.rerun()
        
    st.markdown("<br/><br/>", unsafe_allow_html=True)
    login_c1, login_c2, login_c3 = st.columns([3, 4, 3])
    
    with login_c2:
        # Farmer Identity Sign-In & Onboarding Segment
        if st.session_state.role == "farmer":
            st.markdown("<h2 style='text-align: center; font-size: 24px; font-weight: 700;'>Farmer Portal Access</h2>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; opacity: 0.7; font-size: 13px; margin-bottom: 25px;'>Secure OTP-validated terminal verification</p>", unsafe_allow_html=True)
            
            auth_tab1, auth_tab2 = st.tabs(["🔐 Password & OTP login", "✍️ Secure Registration"])
            
            with auth_tab1:
                st.markdown("<br/>", unsafe_allow_html=True)
                fmr_id = st.text_input("Login ID (e.g., FMR8812)", value="FMR8812")
                fmr_pwd = st.text_input("Password", type="password", value="pass")
                
                # Collapsible Sandbox Helper
                with st.expander("🔑 Secure Sandbox Credentials"):
                    st.caption("Testing accounts pre-seeded in internal database:")
                    st.code("ID: FMR8812  | Password: pass\nID: FMR4012  | Password: pass")
                
                if fmr_id in st.session_state.farmers_db:
                    sim_otp = "8812"
                    st.markdown(f"<div style='background-color: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.2); padding: 10px; border-radius: 6px; margin-bottom: 15px; font-size: 12px; text-align: center; color: #f59e0b;'>🔐 Simulated OTP sent to registered mobile: <b>{sim_otp}</b></div>", unsafe_allow_html=True)
                    otp_input = st.text_input("Enter 4-Digit Security OTP")
                    
                    if st.button("Authenticate & Log In", use_container_width=True):
                        if fmr_pwd == "pass" and otp_input == sim_otp:
                            st.session_state.logged_in_farmer = fmr_id
                            st.session_state.view = "dashboard"
                            st.success("Session verified.")
                            st.rerun()
                        else:
                            st.error("Invalid verification credentials.")
                else:
                    st.error("Unrecognized ID. Select the Registration tab to map land records.")
                    
            with auth_tab2:
                st.markdown("<br/>", unsafe_allow_html=True)
                reg_col1, reg_col2 = st.columns(2)
                with reg_col1:
                    new_name = st.text_input("Full Name", placeholder="e.g., Sukhdev Singh")
                    new_age = st.number_input("Age", min_value=18, max_value=100, value=35)
                    new_phone = st.text_input("Mobile Phone", placeholder="e.g., 9876543210")
                with reg_col2:
                    new_loc = st.text_input("Mandi Region/Village", placeholder="e.g., Jind, Haryana")
                    new_aadhaar = st.text_input("Aadhaar Number", placeholder="XXXX-XXXX-XXXX")
                    new_crop = st.selectbox("Primary Crop", ["Paddy (Basmati)", "Wheat", "Potatoes (Jyoti)", "Cotton", "Onions"])
                
                if st.button("Verify Aadhaar Land Map", use_container_width=True):
                    if new_name and new_phone and new_aadhaar:
                        new_fid = f"FMR{random.randint(1000, 9999)}"
                        st.session_state.farmers_db[new_fid] = {
                            "name": new_name,
                            "password": "pass",
                            "phone": new_phone,
                            "rating": 5.0,
                            "trips": 0
                        }
                        st.success(f"Aadhaar verified. Account created:\n\n"
                                   f"• **Login ID:** {new_fid}\n\n"
                                   f"• **Password:** pass\n\n"
                                   f"Navigate to the OTP tab to authenticate.")
                        add_notification(f"Farmer database synced. Registration ID: {new_fid}")
                    else:
                        st.error("All identification fields are required for mapping.")
                        
        # Administrative Team Triple-Factor Authentication Block
        else:
            st.markdown("<h2 style='text-align: center; font-size: 24px; font-weight: 700;'>Control Panel Access</h2>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; opacity: 0.7; font-size: 13px; margin-bottom: 25px;'>Administrative clearances only</p>", unsafe_allow_html=True)
            
            adm_id = st.text_input("Administrator Username", value="ADMIN_SIH26")
            adm_pwd = st.text_input("Password", type="password", value="sih2026")
            adm_key = st.text_input("Secure Unique Admin Key", value="KEY-9921-X")
            
            with st.expander("🔑 Secure Sandbox Keys"):
                st.code("Admin ID: ADMIN_SIH26\nPassword: sih2026\nAdmin Key: KEY-9921-X")
                
            if st.button("Request Administrative Access", use_container_width=True):
                if adm_id == "ADMIN_SIH26" and adm_pwd == "sih2026" and adm_key == "KEY-9921-X":
                    st.session_state.admin_logged_in = True
                    st.session_state.view = "dashboard"
                    st.success("Authorization verified.")
                    st.rerun()
                else:
                    st.error("Security Key signature verification failed.")

# ------------------------------------------------------------------------------
# 4.3 MODERN DASHBOARDS (SECTIONED & STREAMLINED)
# ------------------------------------------------------------------------------
elif st.session_state.view == "dashboard":
    
    # ------------------
    # FARMER PORTAL
    # ------------------
    if st.session_state.role == "farmer":
        
        # Header Controls
        head_c1, head_c2 = st.columns([8, 2])
        with head_c1:
            st.markdown(f"<h1 style='font-size: 26px; font-weight: 800; margin: 0;'>Farmer Console</h1>", unsafe_allow_html=True)
            farmer_profile = st.session_state.farmers_db[st.session_state.logged_in_farmer]
            st.markdown(f"<p style='opacity: 0.8; font-size:14px;'>Session ID: <b>{st.session_state.logged_in_farmer}</b> | Trust Score: <b>{farmer_profile['rating']} ⭐</b></p>", unsafe_allow_html=True)
        with head_c2:
            st.markdown("<br/>", unsafe_allow_html=True)
            if st.button("🚪 Terminate Session", use_container_width=True):
                st.session_state.logged_in_farmer = None
                st.session_state.view = "landing"
                st.session_state.role = None
                st.rerun()
                
        st.write("---")
        
        # Tabs - clean structural separation
        farm_tab1, farm_tab2, farm_tab3 = st.tabs(["🔍 Browse & Reserve Slots", "📂 Active Registrations", "🔔 Push Alert Logs"])
        
        # Tab 1: Discovery & Scheduling Engine
        with farm_tab1:
            st.markdown("### Active Procurement Openings")
            st.caption("Select an active administrative buy order to secure a queue position.")
            
            # Filters
            f_col1, f_col2 = st.columns(2)
            with f_col1:
                filter_crop = st.selectbox("Filter Crop Category", ["All", "Paddy (Basmati)", "Wheat", "Potatoes (Jyoti)", "Cotton", "Onions"])
            with f_col2:
                filter_qty = st.number_input("Target Delivery Quantity (kg)", value=0)
                
            st.markdown("<br/>", unsafe_allow_html=True)
            
            # Active Orders Stream
            for order in st.session_state.buy_orders:
                if filter_crop != "All" and order["crop"] != filter_crop:
                    continue
                
                # Dynamic capacity calculations
                order_bookings = [b for b in st.session_state.bookings if b["order_id"] == order["id"] and b["status"] == "Confirmed"]
                total_booked = sum(b["qty"] for b in order_bookings)
                remaining_cap = order["target"] - total_booked
                
                # Active/Locked card render using adaptive styles
                badge_class = "pill-active" if remaining_cap > 0 else "pill-full"
                badge_text = "Active Open" if remaining_cap > 0 else "Queue Full / Locked"
                
                st.markdown(f"""
                <div class="saas-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h4 style="margin: 0; font-size: 16px; font-weight: 700;">📦 Buy Order: {order['crop']} ({order['id']})</h4>
                        <span class="status-pill {badge_class}">{badge_text}</span>
                    </div>
                    <div style="height: 1px; background-color: var(--border-color); margin: 12px 0;"></div>
                </div>
                """, unsafe_allow_html=True)
                
                info_col1, info_col2, info_col3 = st.columns([3, 3, 2])
                with info_col1:
                    st.write(f"📍 **APMC Center:** {order['location']}")
                    st.write(f"⏱ **Shift Window:** {order['time_slot']}")
                    st.write(f"📏 **Transit Distance:** **{order['distance_km']} km**")
                with info_col2:
                    if order["price_type"] == "Range":
                        st.write(f"💰 **Pricing Model:** Range (₹{order['price_min']} - ₹{order['price_max']}/qtl)")
                        estimated_tiered = calculate_tiered_price(order, total_booked)
                        st.markdown(f"<span style='color: #10b981; font-weight: 600;'>⚡ Tiered Rate Lock: ₹{estimated_tiered} / Quintal</span>", unsafe_allow_html=True)
                    else:
                        st.write(f"💰 **Pricing Model:** Fixed Cutoff (₹{order['price_min']}/qtl)")
                with info_col3:
                    st.metric("Required Quota", f"{order['target']} kg", delta=f"{remaining_cap} kg remaining")
                    
                # Action segment
                if remaining_cap > 0:
                    with st.expander(f"📝 Select Scheduling Details"):
                        book_col1, book_col2 = st.columns(2)
                        with book_col1:
                            book_qty = st.number_input("Load Weight (kg)", min_value=100, max_value=int(remaining_cap), step=100, key=f"fq_{order['id']}")
                            book_hour = st.selectbox("Preferred Arrival Time", ["06:00 AM", "07:00 AM", "08:00 AM", "09:00 AM", "10:00 AM", "11:00 AM", "12:00 PM"], key=f"fh_{order['id']}")
                        with book_col2:
                            price_secured = calculate_tiered_price(order, total_booked)
                            estimated_paycheck = int((book_qty / 100) * price_secured)
                            st.markdown(f"""
                            <div class="glass-metric">
                                <p style="margin: 0; font-size: 11px; opacity: 0.8; font-weight: 600;">ESTIMATED SETTLEMENT</p>
                                <h3 style="margin: 4px 0; font-size: 20px; color: #10b981;">₹{price_secured} <span style="font-size: 11px; opacity: 0.7;">/qtl</span></h3>
                                <p style="margin: 0; font-size: 11px; opacity: 0.7;">Total Payout Check: <b>₹{estimated_paycheck:,}</b></p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                        if st.button("Reserve Queue Position", key=f"fbtn_{order['id']}", use_container_width=True):
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
                            add_notification(f"Queue slot verified: {new_b['farmer_name']} booked {book_qty} kg of {order['crop']}")
                            st.success("Reservation confirmed.")
                            time.sleep(0.5)
                            st.rerun()
                else:
                    # ----------------------------------------------------------
                    # CLIENT-SIDE VIEW-ONLY OPTIMIZATION IN ACTION
                    # ----------------------------------------------------------
                    st.markdown("<div style='border: 1px solid rgba(239, 68, 68, 0.2); background-color: rgba(239, 68, 68, 0.05); color: #ef4444; padding: 10px; border-radius: 6px; font-size: 12px; font-weight: 600; text-align: center;'>🔒 SYSTEM OPTIMIZATION: READ-ONLY FEED LOCKED</div>", unsafe_allow_html=True)
                    st.caption("ℹ️ *This queue is fully assigned. Interactive features have been offline-locked to drop API requests and server strain to absolute zero.*")
                    
                    filled_bookings = [b for b in st.session_state.bookings if b["order_id"] == order["id"] and b["status"] == "Confirmed"]
                    if len(filled_bookings) > 0:
                        st.dataframe(
                            pd.DataFrame([
                                {"Arrival Time": b["time"], "Farmer Register": b["farmer_id"], "Verified Quantity (kg)": b["qty"], "Settled Rate (₹/Quintal)": b["price_secured"]}
                                for b in filled_bookings
                            ]), use_container_width=True
                        )
                st.markdown("<br/><hr style='border-top:1px solid var(--border-color);'/><br/>", unsafe_allow_html=True)
                
        # Tab 2: Personal Schedule & Cancellation Controls
        with farm_tab2:
            st.markdown("### Your Scheduled Departures")
            st.caption("Manage bookings or trigger cancellations to free up regional capacity.")
            
            my_reservations = [b for b in st.session_state.bookings if b["farmer_id"] == st.session_state.logged_in_farmer]
            
            if len(my_reservations) == 0:
                st.info("No active reservations detected for this profile.")
            else:
                for b in my_reservations:
                    target_order = next(o for o in st.session_state.buy_orders if o["id"] == b["order_id"])
                    
                    b_badge = "pill-active" if b["status"] == "Confirmed" else "pill-pending" if "Completed" in b["status"] else "pill-full"
                    
                    st.markdown(f"""
                    <div class="saas-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <span style="font-size: 10px; opacity: 0.7; font-weight: 700;">GATETICKET ID: {b['id']}</span>
                                <h4 style="margin: 2px 0 0 0; font-size: 15px; font-weight: 700;">🌾 {target_order['crop']} • Delivery Queue</h4>
                            </div>
                            <span class="status-pill {b_badge}">{b["status"]}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col_b1, col_b2, col_b3 = st.columns([3, 3, 2])
                    with col_b1:
                        st.write(f"⏰ **Reserved Shift:** {b['time']}")
                        st.write(f"⚖ **Target Load:** {b['qty']} kg")
                    with col_b2:
                        st.write(f"💰 **Secured Pricing:** ₹{b['price_secured']}/Quintal")
                        st.write(f"📍 **Location Center:** {target_order['location']}")
                    with col_b3:
                        if b["status"] == "Confirmed":
                            c_reason = st.text_input("Cancellation Reason", key=f"cre_{b['id']}", placeholder="Harvest delay, logistic bottleneck...")
                            if st.button("Cancel & Release Slot", key=f"cbtn_{b['id']}", use_container_width=True):
                                if c_reason:
                                    b["status"] = "Cancelled"
                                    add_notification(f"Queue Slot Released: {farmer_profile['name']} released capacity of {b['qty']} kg. Reason: {c_reason}")
                                    st.success("Slot released and SMS alert broadcasted.")
                                    time.sleep(0.5)
                                    st.rerun()
                                else:
                                    st.error("Please insert a validation reason to release the slot.")
                    st.markdown("<hr style='border-top: 1px solid var(--border-color);'/><br/>", unsafe_allow_html=True)

        # Tab 3: System logs
        with farm_tab3:
            st.markdown("### Real-Time Network Activity")
            st.caption("Active chronological logs tracing regional queue releases and center locks.")
            for log in st.session_state.push_notifications[:10]:
                st.markdown(f"""
                <div style="background-color: var(--secondary-background-color); border-left: 4px solid #10b981; border-top: 1px solid var(--border-color); border-right: 1px solid var(--border-color); border-bottom: 1px solid var(--border-color); padding: 12px 16px; border-radius: 4px; margin-bottom: 10px;">
                    <span style="font-size: 12px; font-weight: 500;">{log}</span>
                </div>
                """, unsafe_allow_html=True)
                
    # ------------------
    # ADMIN PORTAL
    # ------------------
    else:
        # Administrative Team Header
        head_a1, head_a2 = st.columns([8, 2])
        with head_a1:
            st.markdown("<h1 style='font-size: 26px; font-weight: 800; margin: 0;'>Administrative Control Panel</h1>", unsafe_allow_html=True)
            st.markdown("<p style='opacity: 0.8; font-size:14px;'>Authorized Terminal Access • System Integrity Engine Active</p>", unsafe_allow_html=True)
        with head_a2:
            st.markdown("<br/>", unsafe_allow_html=True)
            if st.button("🚪 Terminate Session", use_container_width=True):
                st.session_state.admin_logged_in = False
                st.session_state.view = "landing"
                st.session_state.role = None
                st.rerun()
                
        st.write("---")
        
        admin_tab1, admin_tab2, admin_tab3 = st.tabs(["🆕 Create Buy Order", "⚖️ Mandi Cargo Audit", "📊 Transaction Ledgers"])
        
        # Admin Tab 1: Procurement Parameter Publisher
        with admin_tab1:
            st.markdown("### Initialize New Buying Mandate")
            st.caption("Publish verified procurement specifications to the public network registries.")
            
            ord_col1, ord_col2 = st.columns(2)
            with ord_col1:
                o_crop = st.selectbox("Required Crop Category", ["Wheat", "Onions", "Paddy (Basmati)", "Cotton", "Potatoes (Jyoti)"])
                o_target = st.number_input("Target Quota Quantity (kg)", min_value=1000, max_value=100000, value=10000, step=1000)
                o_site = st.text_input("Mandi Collection Center", value="Azadpur APMC, Delhi")
                o_slot = st.selectbox("Operational Shift Window", ["Full Day (Active)", "06:00 AM - 12:00 PM", "12:00 PM - 06:00 PM"])
            with ord_col2:
                st.markdown("""
                <div class="saas-card">
                    <h5 style="margin: 0 0 10px 0; font-size: 14px; font-weight: 700;">📡 Localized Price Intelligence Engine</h5>
                    <p style="margin: 0; font-size: 12px; opacity: 0.8; line-height: 1.5;">
                        Checks regional APMC transactions and localized price points to prevent system underpricing or pricing errors.
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("Run Region-Aware Market Price Lookup", use_container_width=True):
                    with st.spinner("Executing secure regional lookup..."):
                        time.sleep(0.8)
                        
                        # Real-time state mock pricing mechanics
                        if "Delhi" in o_site:
                            avg_val = random.randint(2200, 2450)
                            region_tag = "Delhi APMC Network"
                        else:
                            avg_val = random.randint(1800, 2100)
                            region_tag = "State-Wide Baseline"
                            
                        st.info(f"📡 Found Price Suggestion for **{o_crop}** in **{region_tag}**:\n\n"
                                f"• Market Median: **₹{avg_val} / Quintal**\n\n"
                                f"• Recommended Bounds: **₹{avg_val - 150} - ₹{avg_val + 150}**")
                        
                price_type = st.selectbox("Pricing Model Mode", ["Fixed Cutoff", "Range"])
                if price_type == "Fixed Cutoff":
                    p_min = st.number_input("Standard Offer Price (₹/Quintal)", value=2100)
                    p_max = p_min
                else:
                    p_min = st.number_input("Minimum Baseline Price (₹/Quintal)", value=2000)
                    p_max = st.number_input("Maximum Cap Price (₹/Quintal)", value=2400)
                    
            if st.button("Publish Active Buy Order", use_container_width=True):
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
                add_notification(f"Administrative Order Created: {o_crop} buying mandate of {o_target} kg active.")
                st.success(f"Procurement specifications published for {new_id}.")
                time.sleep(0.5)
                st.rerun()

        # Admin Tab 2: Cargo Inspection Audit & Rating Tuning
        with admin_tab2:
            st.markdown("### Mandi Cargo Quality & Entry Audit")
            st.caption("Inspect physical cargo loads, verify weights, and grade farmer performance vectors.")
            
            pending_evals = [b for b in st.session_state.bookings if b["status"] == "Confirmed"]
            
            if len(pending_evals) == 0:
                st.info("No active scheduled arrivals are currently awaiting evaluation.")
            else:
                selected_item = st.selectbox("Select Arrived Consignment to Audit", [f"{b['id']} - {b['farmer_name']} ({b['qty']} kg of {next(o['crop'] for o in st.session_state.buy_orders if o['id'] == b['order_id'])})" for b in pending_evals])
                
                target_b_id = selected_item.split(" - ")[0]
                target_b = next(b for b in st.session_state.bookings if b["id"] == target_b_id)
                
                st.markdown(f"""
                <div class="saas-card">
                    <h5 style="margin: 0 0 10px 0; font-weight:700;">👤 Consignment Profile Information</h5>
                    <p style="margin: 0; font-size:13px;">Farmer Reference ID: <b>{target_b['farmer_id']}</b> | Name: <b>{target_b['farmer_name']}</b></p>
                    <p style="margin: 0; font-size:13px;">Declared Weight: <b>{target_b['qty']} kg</b> | Scheduled Shift: <b>{target_b['time']}</b></p>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("#### Quality Audit Scoring Parameters")
                slider_col1, slider_col2 = st.columns(2)
                with slider_col1:
                    score_q = st.slider("Quality Standard Rating (Grain moisture, impurity limits, FAQ checks)", 1, 5, 5)
                    score_a = st.slider("Load Weight Accuracy (Actual weight consistency vs. scheduled slot quantity)", 1, 5, 5)
                with slider_col2:
                    score_p = st.slider("Arrival Shift Punctuality (Timeliness within the reserved scheduling window)", 1, 5, 5)
                    
                overall_score = round((score_q + score_a + score_p) / 3, 1)
                st.metric("Aggregate Evaluation Rating Score", f"{overall_score} / 5.0 Stars")
                
                if st.button("Approve Audit & Update Profile Ledger", use_container_width=True):
                    farmer_id = target_b["farmer_id"]
                    farmer_record = st.session_state.farmers_db[farmer_id]
                    
                    p_rating = farmer_record["rating"]
                    p_trips = farmer_record["trips"]
                    
                    # Update reputation metrics via incremental moving averages
                    updated_trips = p_trips + 1
                    updated_rating = round(((p_rating * p_trips) + overall_score) / updated_trips, 2)
                    
                    st.session_state.farmers_db[farmer_id]["rating"] = updated_rating
                    st.session_state.farmers_db[farmer_id]["trips"] = updated_trips
                    target_b["status"] = "Completed & Rated"
                    
                    add_notification(f"Cargo audited: {target_b['farmer_name']} evaluated. Performance Trust updated to {updated_rating} Stars.")
                    st.success("Consignment verified and profile logs updated.")
                    time.sleep(0.5)
                    st.rerun()

        # Admin Tab 3: Transaction Ledgers & High-End Visual Tables
        with admin_tab3:
            st.markdown("### Operational Database Ledgers")
            st.caption("Active visual analytics and historical audit databases.")
            
            tot_orders = len(st.session_state.buy_orders)
            tot_slots = len([b for b in st.session_state.bookings if b["status"] == "Confirmed"])
            tot_completed = len([b for b in st.session_state.bookings if "Completed" in b["status"]])
            
            an_col1, an_col2, an_col3 = st.columns(3)
            with an_col1:
                st.metric("Total System Orders", tot_orders)
            with an_col2:
                st.metric("Active Scheduled Slots", tot_slots)
            with an_col3:
                st.metric("Verified Cargo Closures", tot_completed)
                
            st.markdown("<br/>#### Unified Ledger Database Logs", unsafe_allow_html=True)
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
