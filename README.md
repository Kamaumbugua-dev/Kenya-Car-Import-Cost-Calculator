# Kenya-Car-Import-Cost-Calculator
A comprehensive web application built with Streamlit to help Kenyans estimate the complete cost of importing a vehicle into Kenya, including all taxes, duties, and logistics fees.


![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

##  Overview

Importing a car into Kenya involves multiple costs beyond the vehicle's purchase price. This calculator provides a transparent breakdown of all expenses, from FOB (Free On Board) price to final delivery in Nairobi, helping you make informed decisions about whether to import or buy locally.

##  Features

###  Comprehensive Cost Calculation
- **FOB Value**: Vehicle purchase price at origin
- **Shipping Costs**: Freight and insurance
- **Government Taxes**: 
  - Import Duty (25%)
  - Excise Duty (20-35% based on engine size)
  - VAT (16%)
  - Import Declaration Fee (2.25%)
  - Railway Development Levy (2%)
- **Service Fees**: 
  - Clearing agent fees
  - Port charges
  - Transport to Nairobi
  - KEBS/PVOC inspection
  - Number plates and registration

###  KRA CRSP Database Integration
- Upload and search the official Kenya Revenue Authority CRSP (Customs Reference Standard Price) database
- Real-time vehicle lookup by make and model
- View up to 50 matching results
- Supports Excel (.xlsx, .xls) and CSV formats

###  Auto-Fill from Car Listings
- Paste car links from popular sites (Be Forward, SBT Japan, etc.)
- Automatic extraction of vehicle details where possible
- Smart scraping with fallback to manual entry

###  Import vs. Local Comparison
- Side-by-side cost comparison
- Estimated local market prices
- Potential savings calculation
- Decision recommendations based on total costs

###  Export Functionality
- Download detailed cost summary as CSV
- Includes all cost breakdowns and vehicle information
- Easy to share with banks, dealers, or advisors

###  Smart Features
- Auto-estimate FOB value based on make, model, and year
- Vehicle age validation (max 8 years, recommended under 3)
- Engine-based excise duty calculation
- Real-time exchange rate consideration (USD to KES)

##  Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/kenya-car-import-calculator.git
cd kenya-car-import-calculator
```

2. **Install required packages**
```bash
pip install -r requirements.txt
```

### Requirements

Create a `requirements.txt` file with:
```
streamlit>=1.28.0
pandas>=2.0.0
requests>=2.31.0
beautifulsoup4>=4.12.0
openpyxl>=3.1.0
```

### Running the Application

```bash
streamlit run car_import_calculator.py
python -m streamlit run car_import_calculator.py
```

The app will open in your default web browser at `http://localhost:8501`

##  How to Use

### Step 1: Upload CRSP Database (Optional but Recommended)
1. Navigate to the sidebar
2. Click "Upload CRSP File"
3. Select your KRA CRSP Excel or CSV file
4. Choose the appropriate sheet
5. Use the "View CRSP Data" expander to search your database

### Step 2: Enter Vehicle Information

**Option A: Auto-fill from Link**
1. Expand "Optional: Auto-fill from Car Link"
2. Paste a car listing URL
3. Click " Search"
4. Verify and complete the auto-filled details below

**Option B: Manual Entry**
1. Enter Make (e.g., Toyota, Nissan)
2. Enter Model (e.g., Harrier, X-Trail)
3. Select Year of Manufacture
4. Input Engine Size in liters
5. Enter FOB Value (or use auto-estimate)
6. Add Freight and Insurance costs

### Step 3: Calculate & Review
1. Click " Calculate Total Import Cost"
2. Review the comprehensive breakdown:
   - Vehicle purchase cost
   - Shipping and insurance
   - Government taxes (detailed)
   - Service and logistics fees
   - Grand total in KES
3. Compare with estimated local market prices
4. Download the summary CSV for your records

##  Understanding the Costs

### Import Regulations (Kenya)
- **Maximum vehicle age**: 8 years old
- **Recommended age**: 3 years or newer for easier import
- **Right-hand drive**: Required for Kenyan roads

### Tax Structure
- **Import Duty**: 25% of CIF value
- **Excise Duty**: Varies by engine capacity
  - Up to 1500cc: 20%
  - 1501-2000cc: 25%
  - 2001-2500cc: 30%
  - Above 2500cc: 35%
- **VAT**: 16% of (CIF + Import Duty + Excise Duty)
- **IDF**: 2.25% of (CIF + Import Duty)
- **Railway Levy**: 2% of CIF

### Service Fees (Approximate)
- Clearing Agent: KES 25,000
- Transport to Nairobi: KES 15,000
- Port Charges: KES 10,000
- Inspection (KEBS/PVOC): KES 8,000
- Number Plates & Registration: KES 3,000

##  File Structure

```
kenya-car-import-calculator/
│
├── car_import_calculator.py    # Main application file
├── requirements.txt            # Python dependencies
├── README.md                   # This file
└── .gitignore                 # Git ignore file
```

##  Technical Details

### Built With
- **Streamlit**: Web application framework
- **Pandas**: Data manipulation and CRSP database handling
- **BeautifulSoup4**: Web scraping for car listings
- **Requests**: HTTP library for fetching car details

### Key Functions
- `load_crsp_file()`: Parse and standardize CRSP database
- `calculate_total_costs()`: Compute all taxes and fees
- `scrape_car_details()`: Extract vehicle info from URLs
- `search_crsp()`: Query CRSP database
- `compare_with_local_market()`: Generate buying recommendations

##  Features in Detail

### Smart Column Detection
The app intelligently handles CRSP files with:
- Extra spaces in column names
- Double quotes around headers
- Various encodings (UTF-8, Latin-1, ISO-8859-1)
- Different Excel sheet structures

### Exchange Rate
Currently uses an approximate rate of 1 USD = 129 KES. For the most accurate calculations, check current exchange rates at the Central Bank of Kenya.

##  Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Ideas for Contribution
- Real-time exchange rate API integration
- Support for more car listing websites
- Historical cost tracking
- Insurance cost estimator
- Loan calculator integration
- Multi-language support (Swahili)

##  Disclaimer

This calculator provides estimates based on current Kenya Revenue Authority regulations and standard market practices. Actual costs may vary based on:
- Exchange rate fluctuations
- Specific vehicle classifications
- Port delays or additional storage fees
- Changes in government tax policies
- Individual clearing agent fees

Always consult with a licensed customs clearing agent for official quotations and current regulations.

##  Support

For questions, issues, or suggestions:
- Open an issue on GitHub
- Contact: [Your Email]
- LinkedIn: [Your LinkedIn Profile]

##  License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

##  Acknowledgments

- Kenya Revenue Authority (KRA) for CRSP guidelines
- Streamlit community for excellent documentation
- All contributors and users who provide feedback

##  Future Enhancements

- [ ] Live exchange rate integration
- [ ] Vehicle history check integration
- [ ] Insurance calculator
- [ ] Loan/financing calculator
- [ ] Mobile app version
- [ ] SMS/WhatsApp notifications
- [ ] Multi-currency support
- [ ] PDF report generation
- [ ] User accounts for saving calculations
- [ ] Comparison across multiple vehicles

---

**Made with ❤️ for Kenyan car importers**

*Helping you make informed decisions, one calculation at a time.*
