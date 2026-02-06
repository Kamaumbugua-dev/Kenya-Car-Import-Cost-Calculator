

import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import io

# Page configuration
st.set_page_config(
    page_title="Kenya Car Import Calculator",
    page_icon="🚗",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .info-box {
        background-color: #e8f4f8;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'crsp_data' not in st.session_state:
    st.session_state.crsp_data = None
if 'selected_car' not in st.session_state:
    st.session_state.selected_car = None
if 'scraped_data' not in st.session_state:
    st.session_state.scraped_data = None

# Helper Functions
def load_crsp_file(df):
    """Load and parse the KRA CRSP file from a dataframe"""
    try:
        # Standardize column names - remove extra spaces and quotes
        df.columns = df.columns.str.strip().str.replace('"', '').str.replace(r'\s+', ' ', regex=True).str.upper()
        
        # Debug: show what columns we found
        st.info(f"Found columns: {', '.join(df.columns.tolist())}")
        
        # Check for required columns (case-insensitive)
        has_make = any('MAKE' in col.upper() for col in df.columns)
        has_model = any('MODEL' in col.upper() and 'NUMBER' not in col.upper() for col in df.columns)
        
        if has_make and has_model:
            # Rename to standard names for easier access
            column_mapping = {}
            for col in df.columns:
                if col.upper() == 'MAKE':
                    column_mapping[col] = 'MAKE'
                elif col.upper() == 'MODEL' and 'NUMBER' not in col.upper():
                    column_mapping[col] = 'MODEL'
            
            df = df.rename(columns=column_mapping)
            return df
        else:
            st.error(f"CRSP file must contain 'Make' and 'Model' columns. Found: {', '.join(df.columns.tolist())}")
            return None
    except Exception as e:
        st.error(f"Error loading CRSP file: {str(e)}")
        return None

def scrape_car_details(url):
    """
    Attempt to scrape car details from URL
    This is a simplified version - actual scraping depends on the website
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # This is simplified - would need specific selectors for each website
        car_data = {
            'make': '',
            'model': '',
            'year': None,
            'engine_size': None,
            'fob_value': None
        }
        
        # Try to extract from common patterns
        text = soup.get_text().lower()
        
        # Extract year (4 digits between 2010-2025)
        year_match = re.search(r'(20[1-2][0-9])', text)
        if year_match:
            car_data['year'] = int(year_match.group(1))
        
        # Extract price (various formats)
        price_patterns = [
            r'\$[\d,]+',
            r'usd[\s:]*[\d,]+',
            r'fob[\s:]*[\d,]+',
        ]
        for pattern in price_patterns:
            price_match = re.search(pattern, text, re.IGNORECASE)
            if price_match:
                price_str = re.sub(r'[^\d]', '', price_match.group())
                if price_str:
                    car_data['fob_value'] = int(price_str)
                    break
        
        return car_data
        
    except Exception as e:
        st.error(f"Error scraping URL: {str(e)}")
        return None

def search_crsp(make, model, crsp_data):
    """Search CRSP database for matching vehicles"""
    if crsp_data is None:
        return []
    
    # Convert to uppercase for matching
    make = make.upper().strip()
    model = model.upper().strip()
    
    # Filter data
    results = crsp_data[
        (crsp_data['MAKE'].str.upper().str.contains(make, na=False)) &
        (crsp_data['MODEL'].str.upper().str.contains(model, na=False))
    ]
    
    return results.to_dict('records')

def extract_engine_size(model_str):
    """Extract engine size from model string"""
    # Look for patterns like 2.0, 3.0TFSI, etc.
    match = re.search(r'(\d+\.?\d*)\s*[LT]?', str(model_str), re.IGNORECASE)
    if match:
        return float(match.group(1))
    return None

def calculate_customs_duty(cif_value, vehicle_age):
    """
    Calculate customs duty based on vehicle age
    - Under 3 years: 25% of CIF
    - Over 3 years: Not allowed for general use (diplomatic/special cases only)
    """
    if vehicle_age > 8:
        return 0, " Vehicles over 8 years old cannot be imported into Kenya"
    elif vehicle_age <= 7:
        return cif_value * 0.25, None
    else:
        return 0, " Only vehicles 3 years old or newer can be imported"

def calculate_excise_duty(cif_value, engine_size):
    """
    Calculate excise duty based on engine capacity
    - Up to 1500cc: 20%
    - 1501cc to 2000cc: 25%
    - 2001cc to 2500cc: 30%
    - Above 2500cc: 35%
    """
    if engine_size <= 1.5:
        rate = 0.20
    elif engine_size <= 2.0:
        rate = 0.25
    elif engine_size <= 2.5:
        rate = 0.30
    else:
        rate = 0.35
    
    return (cif_value * rate), rate * 100

def calculate_vat(cif_value, customs_duty, excise_duty):
    """Calculate VAT at 16% of (CIF + Customs Duty + Excise Duty)"""
    taxable_value = cif_value + customs_duty + excise_duty
    return taxable_value * 0.16

def calculate_idf(cif_value, customs_duty):
    """Calculate Import Declaration Fee at 2.25% of (CIF + Customs Duty)"""
    return (cif_value + customs_duty) * 0.0225

def calculate_rail_levy(cif_value):
    """Calculate Railway Development Levy at 2% of CIF"""
    return cif_value * 0.02

def estimate_car_value(year, make, model):
    """
    Estimate FOB value based on car details
    This is a simplified estimation - actual values vary
    """
    current_year = datetime.now().year
    age = current_year - year
    
    # Base values by make (simplified)
    base_values = {
        'TOYOTA': 25000,
        'NISSAN': 20000,
        'HONDA': 22000,
        'MAZDA': 18000,
        'SUBARU': 23000,
        'AUDI': 35000,
        'BMW': 40000,
        'MERCEDES': 45000,
        'VOLKSWAGEN': 28000,
    }
    
    base_value = base_values.get(make.upper(), 20000)
    
    # Depreciation: 15% per year
    depreciation_rate = 0.15
    estimated_value = base_value * ((1 - depreciation_rate) ** age)
    
    return max(estimated_value, 5000)  # Minimum value

def calculate_total_costs(fob_value, freight_cost, insurance_cost, vehicle_age, engine_size):
    """Calculate all import costs"""
    
    # CIF = Cost + Insurance + Freight
    cif_value = fob_value + insurance_cost + freight_cost
    
    # Statutory Taxes
    customs_duty, warning = calculate_customs_duty(cif_value, vehicle_age)
    if warning:
        return None, warning
    
    excise_duty, excise_rate = calculate_excise_duty(cif_value, engine_size)
    vat = calculate_vat(cif_value, customs_duty, excise_duty)
    idf = calculate_idf(cif_value, customs_duty)
    rail_levy = calculate_rail_levy(cif_value)
    
    # Other Fees
    clearing_agent_fee = 25000  # KES
    transport_to_nairobi = 15000  # KES
    port_charges = 10000  # KES
    inspection_fee = 8000  # KES (KEBS, PVOC)
    number_plate = 3000  # KES
    
    # Total statutory taxes (in USD, converted to KES)
    exchange_rate = 129  # USD to KES (approximate)
    total_statutory_taxes = customs_duty + excise_duty + vat + idf + rail_levy
    
    # Other fees in KES
    total_other_fees = (clearing_agent_fee + transport_to_nairobi + 
                        port_charges + inspection_fee + number_plate)
    
    # Grand total in KES
    grand_total_kes = (cif_value * exchange_rate) + (total_statutory_taxes * exchange_rate) + total_other_fees
    
    return {
        'fob_value': fob_value,
        'freight_cost': freight_cost,
        'insurance_cost': insurance_cost,
        'cif_value': cif_value,
        'customs_duty': customs_duty,
        'excise_duty': excise_duty,
        'excise_rate': excise_rate,
        'vat': vat,
        'idf': idf,
        'rail_levy': rail_levy,
        'total_statutory_taxes': total_statutory_taxes,
        'clearing_agent_fee': clearing_agent_fee,
        'transport_to_nairobi': transport_to_nairobi,
        'port_charges': port_charges,
        'inspection_fee': inspection_fee,
        'number_plate': number_plate,
        'total_other_fees': total_other_fees,
        'grand_total_kes': grand_total_kes,
        'exchange_rate': exchange_rate
    }, None

def display_cost_breakdown(costs):
    """Display comprehensive cost breakdown"""
    
    st.markdown('<div class="section-header"> Complete Cost Breakdown</div>', unsafe_allow_html=True)
    
    # Vehicle Cost (FOB)
    st.markdown("###  Vehicle Purchase Cost (FOB)")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("FOB Value", f"${costs['fob_value']:,.2f}")
    with col2:
        st.metric("In Kenyan Shillings", f"KES {costs['fob_value'] * costs['exchange_rate']:,.2f}")
    
    st.markdown("""
    <div class="info-box">
    <b>What is FOB?</b><br>
    FOB (Free On Board) is the price of the car at the port of origin (e.g., Japan, UK). 
    This is what you pay to the seller before shipping costs.
    </div>
    """, unsafe_allow_html=True)
    
    # Shipping Costs
    st.markdown("###  Shipping & Insurance")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Freight Cost", f"${costs['freight_cost']:,.2f}")
    with col2:
        st.metric("Insurance", f"${costs['insurance_cost']:,.2f}")
    with col3:
        st.metric("**CIF Value**", f"${costs['cif_value']:,.2f}")
    
    st.markdown("""
    <div class="info-box">
    <b>Understanding CIF:</b><br>
    CIF (Cost, Insurance, Freight) = FOB + Freight + Insurance. This is the total landed cost 
    at Mombasa port and forms the basis for calculating customs taxes.
    </div>
    """, unsafe_allow_html=True)
    
    # Statutory Taxes
    st.markdown("###  Government Taxes (Statutory)")
    
    tax_data = {
        'Tax Type': [
            'Import Duty (25%)',
            f'Excise Duty ({costs["excise_rate"]}%)',
            'VAT (16%)',
            'IDF (2.25%)',
            'Railway Levy (2%)'
        ],
        'Amount (USD)': [
            f"${costs['customs_duty']:,.2f}",
            f"${costs['excise_duty']:,.2f}",
            f"${costs['vat']:,.2f}",
            f"${costs['idf']:,.2f}",
            f"${costs['rail_levy']:,.2f}"
        ],
        'Amount (KES)': [
            f"KES {costs['customs_duty'] * costs['exchange_rate']:,.2f}",
            f"KES {costs['excise_duty'] * costs['exchange_rate']:,.2f}",
            f"KES {costs['vat'] * costs['exchange_rate']:,.2f}",
            f"KES {costs['idf'] * costs['exchange_rate']:,.2f}",
            f"KES {costs['rail_levy'] * costs['exchange_rate']:,.2f}"
        ],
        'How It\'s Calculated': [
            '25% of CIF value',
            f'{costs["excise_rate"]}% of CIF (based on engine size)',
            '16% of (CIF + Import Duty + Excise Duty)',
            '2.25% of (CIF + Import Duty)',
            '2% of CIF value'
        ]
    }
    
    st.dataframe(pd.DataFrame(tax_data), use_container_width=True, hide_index=True)
    
    st.metric("**Total Statutory Taxes**", 
              f"KES {costs['total_statutory_taxes'] * costs['exchange_rate']:,.2f}",
              delta=f"${costs['total_statutory_taxes']:,.2f}")
    
    st.markdown("""
    <div class="info-box">
    <b>Tax Breakdown Explained:</b><br>
    • <b>Import Duty:</b> Standard 25% charged on all imported vehicles under 3 years old<br>
    • <b>Excise Duty:</b> Varies by engine size (larger engines = higher tax) to discourage gas guzzlers<br>
    • <b>VAT:</b> 16% consumption tax on the total value including other duties<br>
    • <b>IDF:</b> Import Declaration Fee for processing your import documentation<br>
    • <b>Railway Levy:</b> Infrastructure development levy
    </div>
    """, unsafe_allow_html=True)
    
    # Other Fees
    st.markdown("###  Service & Logistics Fees")
    
    fees_data = {
        'Fee Type': [
            'Clearing Agent',
            'Transport to Nairobi',
            'Port Charges',
            'Inspection (KEBS/PVOC)',
            'Number Plates & Registration'
        ],
        'Amount (KES)': [
            f"KES {costs['clearing_agent_fee']:,.2f}",
            f"KES {costs['transport_to_nairobi']:,.2f}",
            f"KES {costs['port_charges']:,.2f}",
            f"KES {costs['inspection_fee']:,.2f}",
            f"KES {costs['number_plate']:,.2f}"
        ],
        'Purpose': [
            'Professional to handle customs clearance',
            'Truck transport from Mombasa to Nairobi',
            'Port storage and handling fees',
            'Safety and compliance certification',
            'KRA registration and plates'
        ]
    }
    
    st.dataframe(pd.DataFrame(fees_data), use_container_width=True, hide_index=True)
    
    st.metric("**Total Other Fees**", f"KES {costs['total_other_fees']:,.2f}")
    
    # Grand Total
    st.markdown("### TOTAL COST TO YOUR DOORSTEP")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Vehicle Cost (CIF)", 
                  f"KES {costs['cif_value'] * costs['exchange_rate']:,.2f}")
    with col2:
        st.metric("All Taxes & Duties", 
                  f"KES {costs['total_statutory_taxes'] * costs['exchange_rate']:,.2f}")
    with col3:
        st.metric("Service Fees", 
                  f"KES {costs['total_other_fees']:,.2f}")
    
    st.markdown("---")
    st.markdown(f"###  **GRAND TOTAL: KES {costs['grand_total_kes']:,.2f}**")
    st.markdown(f"#### (Approximately ${costs['grand_total_kes'] / costs['exchange_rate']:,.2f} USD)")

def compare_with_local_market(total_cost, make, model, year):
    """Compare import cost with local car yard prices"""
    
    st.markdown('<div class="section-header"> Should You Import or Buy Locally?</div>', unsafe_allow_html=True)
    
    # Estimated local market price (simplified - would need real data)
    # Typically 20-40% markup from import cost
    estimated_local_price = total_cost * 1.30
    potential_savings = estimated_local_price - total_cost
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("####  Importing Cost")
        st.metric("Total Cost", f"KES {total_cost:,.2f}")
        st.markdown("""
        **Advantages:**
        -  Know the exact car history
        -  Choose specific specifications
        -  Direct from source (Japan/UK)
        -  Potential cost savings
        
        **Challenges:**
        -  Takes 4-8 weeks to arrive
        -  Paperwork and customs process
        -  Pay upfront before seeing car
        -  Exchange rate risk
        """)
    
    with col2:
        st.markdown("####  Local Car Yard Price (Estimated)")
        st.metric("Estimated Price", f"KES {estimated_local_price:,.2f}")
        st.markdown("""
        **Advantages:**
        -  Immediate availability
        -  Test drive before buying
        -  No import hassle
        -  Local warranty options
        
        **Challenges:**
        -  Higher markup (20-40%)
        -  Unknown history sometimes
        -  May have been used locally
        """)
    
    if potential_savings > 0:
        savings_percentage = (potential_savings / estimated_local_price) * 100
        st.markdown(f"""
        <div class="success-box">
        <h4> Recommendation: IMPORT</h4>
        You could potentially save <b>KES {potential_savings:,.2f}</b> ({savings_percentage:.1f}%) by importing!
        <br><br>
        This saving can cover:
        - First year insurance
        - Comprehensive service package
        - Quality accessories and upgrades
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="warning-box">
        <h4> Recommendation: Consider Local Purchase</h4>
        The convenience and immediate availability of buying locally might outweigh 
        the relatively small cost difference. Plus, you avoid import risks and delays.
        </div>
        """, unsafe_allow_html=True)

# Main App
def main():
    st.markdown('<div class="main-header">🚗 Kenya Car Import Cost Calculator</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
    <h4>Welcome! </h4>
    This calculator helps you understand the complete cost of importing a car to Kenya, 
    including all taxes, duties, and fees from purchase to your doorstep in Nairobi.
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar for CRSP Upload
    with st.sidebar:
        st.markdown("###  KRA CRSP Database")
        st.markdown("""
        Upload your KRA CRSP (Customs Reference Standard Price) file 
        to get accurate tax classifications.
        """)
        
        uploaded_file = st.file_uploader(
            "Upload CRSP File",
            type=['xlsx', 'xls', 'csv']
        )
        
        if uploaded_file is not None:
            # Check file type and process accordingly
            if uploaded_file.name.endswith(('.xlsx', '.xls')):
                # Read all sheets
                excel_file = pd.ExcelFile(uploaded_file)
            
                # Let user select a sheet
                sheet_name = st.selectbox("Select sheet", excel_file.sheet_names)
                excel_sheet = pd.read_excel(uploaded_file, sheet_name=sheet_name)
            
                crsp_data = load_crsp_file(excel_sheet)
                if crsp_data is not None:
                    st.session_state.crsp_data = crsp_data
                    st.success(f" Loaded {len(crsp_data):,} vehicles from CRSP")
                    
                    # Show sample and search
                    with st.expander(" View CRSP Data", expanded=False):
                        # Add search functionality
                        st.markdown("** Search CRSP Database**")
                        search_make = st.text_input("Search by Make", key="sidebar_search_make")
                        search_model = st.text_input("Search by Model", key="sidebar_search_model")
                        
                        if search_make or search_model:
                            # Filter the dataframe
                            filtered_df = crsp_data.copy()
                            if search_make:
                                filtered_df = filtered_df[
                                    filtered_df['MAKE'].str.upper().str.contains(search_make.upper(), na=False)
                                ]
                            if search_model:
                                filtered_df = filtered_df[
                                    filtered_df['MODEL'].str.upper().str.contains(search_model.upper(), na=False)
                                ]
                            
                            if len(filtered_df) > 0:
                                st.success(f"Found {len(filtered_df)} matches")
                                st.dataframe(filtered_df.head(50), use_container_width=True)
                            else:
                                st.warning("No matches found")
                        else:
                            st.info("Enter Make or Model to search")
                            st.markdown("**Sample Data (first 20 rows):**")
                            st.dataframe(crsp_data.head(20), use_container_width=True)
                        
                        # Show total count and columns
                        st.markdown(f"**Total vehicles in database:** {len(crsp_data):,}")
                        st.markdown(f"**Columns:** {', '.join(crsp_data.columns.tolist())}")
            
            elif uploaded_file.name.endswith('.csv'):
                # Handle CSV files with different encodings
                try:
                    uploaded_file.seek(0)
                    csv_data = pd.read_csv(uploaded_file, encoding='utf-8')
                except UnicodeDecodeError:
                    try:
                        uploaded_file.seek(0)
                        csv_data = pd.read_csv(uploaded_file, encoding='latin-1')
                    except:
                        uploaded_file.seek(0)
                        csv_data = pd.read_csv(uploaded_file, encoding='iso-8859-1')
                
                crsp_data = load_crsp_file(csv_data)
                if crsp_data is not None:
                    st.session_state.crsp_data = crsp_data
                    st.success(f" Loaded {len(crsp_data):,} vehicles from CRSP")
                    
                    # Show sample and search
                    with st.expander(" View CRSP Data", expanded=False):
                        # Add search functionality
                        st.markdown("** Search CRSP Database**")
                        search_make = st.text_input("Search by Make", key="sidebar_search_make_csv")
                        search_model = st.text_input("Search by Model", key="sidebar_search_model_csv")
                        
                        if search_make or search_model:
                            # Filter the dataframe
                            filtered_df = crsp_data.copy()
                            if search_make:
                                filtered_df = filtered_df[
                                    filtered_df['MAKE'].str.upper().str.contains(search_make.upper(), na=False)
                                ]
                            if search_model:
                                filtered_df = filtered_df[
                                    filtered_df['MODEL'].str.upper().str.contains(search_model.upper(), na=False)
                                ]
                            
                            if len(filtered_df) > 0:
                                st.success(f"Found {len(filtered_df)} matches")
                                st.dataframe(filtered_df.head(50), use_container_width=True)
                            else:
                                st.warning("No matches found")
                        else:
                            st.info("Enter Make or Model to search")
                            st.markdown("**Sample Data (first 20 rows):**")
                            st.dataframe(crsp_data.head(20), use_container_width=True)
                        
                        # Show total count and columns
                        st.markdown(f"**Total vehicles in database:** {len(crsp_data):,}")
                        st.markdown(f"**Columns:** {', '.join(crsp_data.columns.tolist())}")
            
            else:
                st.error("Please upload a valid Excel (.xlsx, .xls) or CSV file")
        else:
            st.info(" Upload your CRSP file to enable vehicle lookup")
        
        st.markdown("---")
        st.markdown("###  About")
        st.markdown("""
        **Exchange Rate:** 1 USD = 129 KES (approx.)
        
        **Vehicle Age Limit:** 
        - Max 3 years for general import
        - Max 8 years old overall
        
        **Contact:** For assistance with 
        imports, consult a licensed 
        clearing agent.
        """)
    
    # Main Input Section - Single unified form
    st.markdown("###  Enter Vehicle Information")
    
    # Link search section at the top
    with st.expander(" Optional: Auto-fill from Car Link", expanded=False):
        col1, col2 = st.columns([3, 1])
        with col1:
            car_link = st.text_input(
                "Paste car link (e.g., from Be Forward, SBT Japan, etc.)", 
                placeholder="https://www.beforward.jp/...",
                key="car_link_input"
            )
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)  # Spacing
            search_button = st.button(" Search", type="primary", use_container_width=True)
        
        if search_button and car_link:
            with st.spinner(" Searching car details..."):
                scraped_data = scrape_car_details(car_link)
                if scraped_data:
                    st.session_state.scraped_data = scraped_data
                    st.success(" Found some car details! The form below has been updated.")
                    st.rerun()  # Refresh to show updated form
                else:
                    st.warning(" Could not automatically extract car details. Please enter manually below.")
        
        st.markdown("""
        <div class="info-box">
        <b>Note:</b> Link scraping works best for popular sites like Be Forward and SBT Japan. 
        For best accuracy, manually verify the details below.
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Main form - Pre-fill with scraped data if available
    default_make = st.session_state.scraped_data.get('make', '') if st.session_state.scraped_data else ''
    default_model = st.session_state.scraped_data.get('model', '') if st.session_state.scraped_data else ''
    default_year = st.session_state.scraped_data.get('year', 2019) if st.session_state.scraped_data else 2019
    default_fob = st.session_state.scraped_data.get('fob_value', 15000) if st.session_state.scraped_data else 15000
    col1, col2, col3 = st.columns(3)
        
    with col1:
            make = st.text_input("Make (e.g., Toyota, Nissan)", value=default_make, key="make_input").upper()
    with col2:
            model = st.text_input("Model (e.g., Harrier, X-Trail)", value=default_model, key="model_input")
    with col3:
            year = st.number_input("Year of Manufacture", 
                                   min_value=2015, 
                                   max_value=datetime.now().year, 
                                   value=default_year,
                                   key="year_input")
        
        # Search CRSP if database loaded
    if st.session_state.crsp_data is not None and make and model:
            st.markdown("####  CRSP Database Matches")
            matches = search_crsp(make, model, st.session_state.crsp_data)
            
            if matches:
                st.success(f"Found {len(matches)} matching vehicles in CRSP")
                
                match_options = []
                for idx, match in enumerate(matches[:10]):  # Limit to 10
                    label = f"{match.get('MAKE', 'N/A')} {match.get('MODEL', 'N/A')}"
                    if 'MODEL NUMBER' in match or 'MODEL  NUMBER' in match:
                        model_num = match.get('MODEL NUMBER') or match.get('MODEL  NUMBER')
                        label += f" - {model_num}"
                    match_options.append(label)
                
                selected_match = st.selectbox("Select your vehicle from CRSP:", 
                                              ["None"] + match_options)
                
                if selected_match != "None":
                    idx = match_options.index(selected_match)
                    st.session_state.selected_car = matches[idx]
                    st.success(" Vehicle selected from CRSP database")
            else:
                st.warning("No exact matches found in CRSP. You can still proceed with manual entry.")
        
    st.markdown("---")
        
    col1, col2 = st.columns(2)
        
    with col1:
            engine_size = st.number_input("Engine Size (in Liters, e.g., 2.0)", 
                                          min_value=0.5, 
                                          max_value=6.0, 
                                          value=2.0, 
                                          step=0.1)
            
            fob_value = st.number_input("FOB Value (USD) - Price at origin", 
                                        min_value=1000, 
                                        max_value=200000, 
                                        value=default_fob, 
                                        step=500)
        
    with col2:
            freight_cost = st.number_input("Freight Cost (USD) - Shipping", 
                                           min_value=500, 
                                           max_value=5000, 
                                           value=1200, 
                                           step=100)
            
            insurance_cost = st.number_input("Insurance Cost (USD)", 
                                            min_value=100, 
                                            max_value=2000, 
                                            value=300, 
                                            step=50)
        
        # Auto-estimate option
    if st.checkbox(" Auto-estimate FOB value based on year and make"):
            if make and year:
                estimated_fob = estimate_car_value(year, make, model)
                st.info(f"Estimated FOB Value: ${estimated_fob:,.2f}")
                fob_value = estimated_fob
        
    st.markdown("---")
        
        # Calculate button
    if st.button(" Calculate Total Import Cost", type="primary", use_container_width=True):
            if not make or not model:
                st.error("Please enter at least Make and Model")
            else:
                vehicle_age = datetime.now().year - year
                
                with st.spinner("Calculating all costs..."):
                    costs, warning = calculate_total_costs(
                        fob_value, 
                        freight_cost, 
                        insurance_cost, 
                        vehicle_age, 
                        engine_size
                    )
                    
                    if warning:
                        st.error(warning)
                    else:
                        # Display results
                        st.success(" Calculation Complete!")
                    # Save summary data to session_state
                    st.session_state.summary_data = {
                        "make": make,
                        "model": model,
                        "year": year,
                        "engine_size": engine_size,
                        "costs": costs
                                                    }

                        
                        
                        # Summary at top
                    st.markdown(f"""
                        ###  Vehicle Summary
                        **{make} {model} ({year})**  
                        Engine: {engine_size}L | Age: {vehicle_age} years
                        """)
                        
                        # Cost breakdown
                    display_cost_breakdown(costs)
                        
                        # Comparison
                    st.markdown("---")
                    compare_with_local_market(
                            costs['grand_total_kes'], 
                            make, 
                            model, 
                            year
                        )
                        
                        # Additional Tips
                    st.markdown("---")
                    st.markdown('<div class="section-header"> Important Tips</div>', 
                                   unsafe_allow_html=True)
                        
                    col1, col2 = st.columns(2)
                        
                    with col1:
                            st.markdown("""
                            **Before Importing:**
                            - ✓ Verify car history (accidents, floods)
                            - ✓ Confirm all documents are genuine
                            - ✓ Use reputable dealers/agents
                            - ✓ Budget extra 10% for contingencies
                            - ✓ Check current exchange rates
                            """)
                        
                    with col2:
                            st.markdown("""
                            **Timeline:**
                            -  Shipping: 3-6 weeks
                            -  Customs clearance: 3-7 days
                            -  Transport to Nairobi: 1-2 days
                            -  Registration: 2-5 days
                            - **Total: ~6-8 weeks**
                            """)
                        
                        # ------------------ DOWNLOAD SUMMARY ------------------

                    summary_data = {
                        "Item": [
                            "Vehicle",
                            "Year",
                            "Engine Size (L)",
                            "FOB Value (USD)",
                            "CIF Value (USD)",
                            "Total Statutory Taxes (USD)",
                            "Other Fees (KES)",
                            "Exchange Rate (USD → KES)",
                            "GRAND TOTAL (KES)"
                        ],
                        "Value": [
                            f"{make} {model}",
                            year,
                            engine_size,
                            f"{costs['fob_value']:,.2f}",
                            f"{costs['cif_value']:,.2f}",
                            f"{costs['total_statutory_taxes']:,.2f}",
                            f"{costs['total_other_fees']:,.2f}",
                            costs['exchange_rate'],
                            f"{costs['grand_total_kes']:,.2f}"
                        ]
                    }

                    summary_df = pd.DataFrame(summary_data)

                    summary_csv = summary_df.to_csv(index=False)

                    st.markdown("---")
                    st.download_button(
                        label=" Download Summary",
                        data=summary_csv,
                        file_name=f"{make}_{model}_{year}_import_summary.csv",
                        mime="text/csv"
                    )


if __name__ == "__main__":
    main()
