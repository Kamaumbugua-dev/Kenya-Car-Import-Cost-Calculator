# 🚀 QUICK START GUIDE

## Get Started in 3 Minutes!

### Step 1: Install Python
If you don't have Python installed:
- **Windows**: Download from https://www.python.org/downloads/
- **Mac**: `brew install python3` or download from python.org
- **Linux**: Usually pre-installed, or `sudo apt install python3`

### Step 2: Install Dependencies
Open terminal/command prompt and run:
```bash
pip install streamlit pandas requests beautifulsoup4 openpyxl
```

### Step 3: Run the App
```bash
streamlit run car_import_calculator.py
```

That's it! The app opens automatically in your browser! 🎉

## First Time Usage

### Scenario 1: You Have a Specific Car in Mind
1. Go to "Manual Entry" tab
2. Enter: Make, Model, Year, Engine Size
3. Enter FOB price (or use auto-estimate)
4. Add shipping costs
5. Click "Calculate Total Import Cost"

### Scenario 2: You Have a KRA CRSP File
1. Click "Upload CRSP CSV File" in sidebar
2. Select your CRSP file
3. Enter Make and Model
4. Select matching vehicle from suggestions
5. Complete other details and calculate

## Example Calculation

**Toyota Harrier 2022, 2.0L Engine**

Inputs:
- FOB Value: $15,000
- Freight: $1,200
- Insurance: $300
- Engine: 2.0L

Results:
- CIF: $16,500
- Import Duty (25%): $4,125
- Excise Duty (25%): $4,125
- VAT (16%): ~$3,960
- Other Taxes: ~$537
- Service Fees: ~KES 61,000
- **TOTAL: ~KES 3,200,000**

## Tips for Accurate Results

✅ **DO:**
- Use actual FOB values from car dealers
- Include realistic shipping costs ($1000-$1500 from Japan)
- Upload CRSP database for accurate classification
- Double-check engine size (in liters, not CC)
- Add 10% buffer for contingencies

❌ **DON'T:**
- Underestimate costs to get lower results
- Forget to convert CC to liters (divide by 1000)
- Ignore the vehicle age restriction (max 3 years)
- Forget about insurance (required!)

## Common Questions

**Q: Where do I get the CRSP file?**
A: Contact KRA or your clearing agent. A sample file is included for testing.

**Q: Can I import a 5-year-old car?**
A: No. Only cars 3 years old or newer can be imported for personal use.

**Q: Are these the final costs?**
A: These are estimates. Exchange rates and fees vary. Always confirm with a clearing agent.

**Q: Should I import or buy locally?**
A: The app compares both options! Generally, you save 20-30% by importing.

## Need Help?

1. Read the full README.md
2. Check troubleshooting section
3. Consult a licensed clearing agent
4. Visit https://www.kra.go.ke for official guidelines

---

**Ready to calculate? Run the app and start planning your dream car import! 🚗✨**
