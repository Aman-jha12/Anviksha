# Sample Data for Testing Anviksha

This file contains a sample CSV dataset (`west_bengal_road_tenders_sample.csv`) for testing the Anviksha application.

## Dataset Description

- **Total Records**: 50 road construction tenders
- **Time Period**: 2018-2024 (7 years)
- **Departments**: Rural Development, Public Works
- **Currency**: Indian Rupees (₹)

## Data Characteristics

### Columns Included

1. **contract_value**: Contract amount in rupees (contains some high-value anomalies)
2. **vendor_name**: Contractor/vendor names (includes some standardization variations)
3. **contract_date**: Award dates (YYYY-MM-DD format)
4. **department**: Government department
5. **description**: Tender description (all road-related)
6. **num_bidders**: Number of bidders (varies from 1-12)
7. **category**: All entries are "Road Construction"

### Intentional Anomalies for Testing

The sample data includes several anomalies to test the analysis features:

1. **Price Anomalies**:
   - Row 12: ₹25,000,000 (2018) - Very high value compared to similar projects
   - Row 25: ₹38,000,000 (2024) - Extremely high value with only 1 bidder

2. **Vendor Dominance**:
   - "ABC Construction Pvt Ltd" appears 15 times (30% of all contracts)
   - High concentration in Rural Development department

3. **Low Competition Issues**:
   - Several contracts with only 1-2 bidders and high prices
   - Row 25: 1 bidder, ₹38,000,000
   - Row 12: 2 bidders, ₹25,000,000

### Vendor Name Variations

The data includes different vendor name formats to test standardization:
- "ABC Construction Pvt Ltd"
- "XYZ Infrastructure Private Limited" 
- "West Bengal Builders Ltd"
- etc.

## How to Use

1. Start the Anviksha application:
   ```bash
   streamlit run app.py
   ```

2. Upload the sample CSV file:
   - Click "Upload CSV file" in the sidebar
   - Select `sample_data/west_bengal_road_tenders_sample.csv`

3. Click "Run Analysis" to see:
   - Inflation-adjusted values (all adjusted to 2024 prices)
   - Flagged tenders with high prices
   - Vendor dominance analysis showing ABC Construction Pvt Ltd
   - Low competition analysis
   - Detailed explanations for each anomaly

## Expected Results

After running analysis, you should see:

- **Price Anomalies**: 2-3 contracts flagged (the ₹25M and ₹38M contracts)
- **Vendor Dominance**: ABC Construction Pvt Ltd flagged for high concentration
- **Low Competition**: Several contracts with ≤2 bidders flagged
- **Visualizations**: 
  - Price distribution histogram
  - Top 10 vendors by contract count
  - Competition analysis box plots

## Notes

- Values are realistic but fictional
- Dates span 2018-2024 to demonstrate inflation adjustment
- The inflation adjustment will show that older contracts (2018-2019) get adjusted upward to 2024 prices
- Multiple departments allow testing of department-specific vendor analysis
