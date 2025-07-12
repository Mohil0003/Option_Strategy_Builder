# Options Strategy Simulator

A comprehensive Streamlit web application for simulating and visualizing options trading strategies with interactive payoff curves.

## Features

- **Two Strategy Types:**
  - **Bull Call Spread:** A bullish strategy involving buying and selling call options
  - **Iron Condor:** A neutral strategy using both put and call spreads

- **Interactive Input Fields:**
  - Strike prices and premiums for each leg
  - Lot size configuration
  - Real-time input validation

- **Visualization:**
  - Interactive payoff curves using Plotly
  - X-axis: Spot Prices (0-5000)
  - Y-axis: Net P/L

- **Strategy Summary:**
  - Maximum Profit
  - Maximum Loss
  - Breakeven Point(s)

## Installation

1. **Clone or download the files:**
   - `app.py` - Main application file
   - `requirements.txt` - Dependencies list

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Running the App

1. **Start the Streamlit app:**
   ```bash
   streamlit run app.py
   ```

2. **Open your browser:**
   - The app will automatically open in your default browser
   - Usually at `http://localhost:8501`

## How to Use

1. **Select Strategy:** Choose between "Bull Call Spread" or "Iron Condor" from the sidebar

2. **Enter Parameters:**
   - **Bull Call Spread:**
     - Buy Call Strike & Premium
     - Sell Call Strike & Premium
   - **Iron Condor:**
     - Put Spread: Buy Put Strike/Premium, Sell Put Strike/Premium
     - Call Spread: Sell Call Strike/Premium, Buy Call Strike/Premium

3. **Set Lot Size:** Enter the number of contracts to trade

4. **Calculate:** Click "Calculate Payoff" to generate the payoff curve and summary

## Input Validation

The app includes validation to ensure:
- All premiums are positive values
- Strike prices are in ascending order
- No divide-by-zero errors

## Technical Details

- **Built with:** Streamlit, Plotly, NumPy, Pandas
- **Payoff Calculation:** Uses vectorized operations for efficiency
- **Breakeven Detection:** Linear interpolation for precise breakeven point calculation
- **Responsive Design:** Clean, modern UI with proper spacing and layout

## Profit and Loss Logic

### Bull Call Spread

- **Setup:**  
  Buy 1 Call (lower strike, pay premium), Sell 1 Call (higher strike, receive premium)

- **Net Premium Paid:**  
  Net Premium Paid = Buy Call Premium − Sell Call Premium

- **Maximum Profit:**  
  Max Profit = (Sell Call Strike − Buy Call Strike) − Net Premium Paid  
  (Occurs if spot price ≥ Sell Call Strike at expiry)

- **Maximum Loss:**  
  Max Loss = Net Premium Paid  
  (Occurs if spot price ≤ Buy Call Strike at expiry)

- **Breakeven Point:**  
  Breakeven = Buy Call Strike + Net Premium Paid

---

### Iron Condor

- **Setup:**  
  - Buy 1 Put (lowest strike, pay premium)  
  - Sell 1 Put (lower-middle strike, receive premium)  
  - Sell 1 Call (upper-middle strike, receive premium)  
  - Buy 1 Call (highest strike, pay premium)

- **Net Premium Received:**  
  \[
  \text{Net Premium Received} = (\text{Sell Put Premium} + \text{Sell Call Premium}) - (\text{Buy Put Premium} + \text{Buy Call Premium})
  \]

- **Maximum Profit:**  
  \[
  \text{Max Profit} = \text{Net Premium Received}
  \]
  (Occurs if spot price is between the two middle strikes at expiry)

- **Maximum Loss:**  
  \[
  \text{Max Loss} = (\text{Difference between adjacent strikes}) - \text{Net Premium Received}
  \]
  (Occurs if spot price is below lowest or above highest strike at expiry)

- **Breakeven Points:**  
  \[
  \text{Lower Breakeven} = \text{Lower Put Strike} + \text{Net Premium Received}
  \]
  \[
  \text{Upper Breakeven} = \text{Upper Call Strike} - \text{Net Premium Received}
  \]

## Disclaimer

This simulator is for educational purposes only. Options trading involves substantial risk and may not be suitable for all investors. Always consult with a financial advisor before making investment decisions.