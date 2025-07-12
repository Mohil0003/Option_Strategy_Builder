import streamlit as st
import numpy as np
import plotly.graph_objects as go
import pandas as pd
from typing import Tuple, List

# Page configuration
st.set_page_config(
    page_title="Options Strategy Simulator",
    page_icon="📈",
    layout="wide"
)

# Title and description
st.title("📈 Options Strategy Simulator")
st.markdown("Simulate and visualize options strategies with interactive payoff curves.")

# Add some spacing
st.markdown("---")

def validate_inputs(premiums: List[float], strikes: List[float]) -> bool:
    """Validate that all premiums are positive and strikes are in ascending order."""
    if any(premium <= 0 for premium in premiums):
        st.error("All premiums must be positive values.")
        return False
    
    if len(strikes) > 1 and not all(strikes[i] <= strikes[i+1] for i in range(len(strikes)-1)):
        st.error("Strike prices must be in ascending order.")
        return False
    
    return True

def calculate_bull_call_spread_payoff(
    spot_prices: np.ndarray,
    buy_call_strike: float,
    buy_call_premium: float,
    sell_call_strike: float,
    sell_call_premium: float,
    lot_size: int
) -> np.ndarray:
    """Calculate payoff for Bull Call Spread strategy."""
    # Buy call payoff
    buy_call_payoff = np.maximum(spot_prices - buy_call_strike, 0) - buy_call_premium
    
    # Sell call payoff
    sell_call_payoff = sell_call_premium - np.maximum(spot_prices - sell_call_strike, 0)
    
    # Net payoff
    net_payoff = (buy_call_payoff + sell_call_payoff) * lot_size
    return net_payoff

def calculate_iron_condor_payoff(
    spot_prices: np.ndarray,
    buy_put_strike: float,
    buy_put_premium: float,
    sell_put_strike: float,
    sell_put_premium: float,
    sell_call_strike: float,
    sell_call_premium: float,
    buy_call_strike: float,
    buy_call_premium: float,
    lot_size: int
) -> np.ndarray:
    """Calculate payoff for Iron Condor strategy."""
    # Put spread payoff
    buy_put_payoff = np.maximum(buy_put_strike - spot_prices, 0) - buy_put_premium
    sell_put_payoff = sell_put_premium - np.maximum(sell_put_strike - spot_prices, 0)
    put_spread_payoff = buy_put_payoff + sell_put_payoff
    
    # Call spread payoff
    buy_call_payoff = np.maximum(spot_prices - buy_call_strike, 0) - buy_call_premium
    sell_call_payoff = sell_call_premium - np.maximum(spot_prices - sell_call_strike, 0)
    call_spread_payoff = buy_call_payoff + sell_call_payoff
    
    # Net payoff
    net_payoff = (put_spread_payoff + call_spread_payoff) * lot_size
    return net_payoff

def find_breakeven_points(payoff: np.ndarray, spot_prices: np.ndarray, tolerance: float = 0.01) -> List[float]:
    """Find breakeven points where payoff crosses zero."""
    breakeven_points = []
    
    for i in range(len(payoff) - 1):
        if (payoff[i] <= 0 and payoff[i+1] >= 0) or (payoff[i] >= 0 and payoff[i+1] <= 0):
            # Linear interpolation to find exact breakeven point
            if abs(payoff[i+1] - payoff[i]) > tolerance:
                ratio = abs(payoff[i]) / abs(payoff[i+1] - payoff[i])
                breakeven_price = spot_prices[i] + ratio * (spot_prices[i+1] - spot_prices[i])
                breakeven_points.append(round(breakeven_price, 2))
    
    return list(set(breakeven_points))  # Remove duplicates

def create_payoff_chart(spot_prices: np.ndarray, payoff: np.ndarray, strategy_name: str, currency_symbol: str) -> go.Figure:
    """Create an interactive payoff chart using Plotly."""
    fig = go.Figure()
    
    # Add payoff line with enhanced colors
    fig.add_trace(go.Scatter(
        x=spot_prices,
        y=payoff,
        mode='lines',
        name=f'{strategy_name} Payoff',
        line=dict(color='#2E86AB', width=4),
        hovertemplate='Spot Price: %{x}<br>P/L: %{y:.2f}<extra></extra>',
        fill='tonexty' if np.any(payoff > 0) else None,
        fillcolor='rgba(46, 134, 171, 0.1)'
    ))
    
    # Add zero line
    fig.add_hline(y=0, line_dash="dash", line_color="#E74C3C", opacity=0.7, line_width=2)
    
    # Update layout with enhanced styling
    fig.update_layout(
        title=dict(
            text=f'{strategy_name} Payoff Curve',
            x=0.5,
            font=dict(size=20, color='#2C3E50')
        ),
        xaxis_title=f'Spot Price ({currency_symbol})',
        yaxis_title=f'Net P/L ({currency_symbol})',
        hovermode='x unified',
        showlegend=True,
        height=600,
        margin=dict(l=60, r=60, t=100, b=60),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12, color='#2C3E50')
    )
    
    # Update axes styling
    fig.update_xaxes(
        gridcolor='rgba(128,128,128,0.2)',
        zerolinecolor='rgba(128,128,128,0.5)',
        zerolinewidth=1
    )
    fig.update_yaxes(
        gridcolor='rgba(128,128,128,0.2)',
        zerolinecolor='rgba(128,128,128,0.5)',
        zerolinewidth=1
    )
    
    return fig

def display_summary(payoff: np.ndarray, breakeven_points: List[float], currency_symbol: str):
    """Display strategy summary with max profit, max loss, and breakeven points."""
    max_profit = np.max(payoff)
    max_loss = np.min(payoff)

    st.subheader("📊 Strategy Summary")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "💰 Max Profit", 
            f"{currency_symbol}{max_profit:.2f}",
            delta_color="normal" if max_profit > 0 else "inverse"
        )

    with col2:
        st.metric(
            "📉 Max Loss", 
            f"{currency_symbol}{max_loss:.2f}",
            delta_color="inverse" if max_loss < 0 else "normal"
        )

    with col3:
        if breakeven_points:
            be_text = ", ".join([f"{currency_symbol}{be:.2f}" for be in breakeven_points])
            st.metric("⚖️ Breakeven Point(s)", be_text)
        else:
            st.metric("⚖️ Breakeven Point(s)", "None")

# Sidebar for strategy selection
st.sidebar.header("🎯 Strategy Selection")
strategy = st.sidebar.selectbox(
    "Choose Strategy",
    ["Bull Call Spread", "Iron Condor"],
    help="Select the options strategy to simulate"
)

# Set currency_symbol directly
currency_symbol = "₹"

# Add spacing
st.sidebar.markdown("---")

# Main content area
if strategy == "Bull Call Spread":
    st.header("🐂 Bull Call Spread Strategy")
    st.markdown("A bullish strategy that involves buying a call option and selling another call option with a higher strike price.")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Buy Call Leg")
        buy_call_strike = st.number_input(
            "Buy Call Strike Price",
            min_value=0.0,
            max_value=5000.0,
            value=100.0,
            step=1.0,
            help="Strike price of the call option you're buying"
        )
        buy_call_premium = st.number_input(
            "Buy Call Premium",
            min_value=0.01,
            max_value=1000.0,
            value=5.0,
            step=0.01,
            help="Premium paid for the call option"
        )
    
    with col2:
        st.subheader("📉 Sell Call Leg")
        sell_call_strike = st.number_input(
            "Sell Call Strike Price",
            min_value=0.0,
            max_value=5000.0,
            value=110.0,
            step=1.0,
            help="Strike price of the call option you're selling"
        )
        sell_call_premium = st.number_input(
            "Sell Call Premium",
            min_value=0.01,
            max_value=1000.0,
            value=2.0,
            step=0.01,
            help="Premium received for the call option"
        )
    
    # Lot size input
    st.markdown("---")
    st.subheader("📦 Position Size")
    lot_size = st.number_input(
        "Lot Size",
        min_value=1,
        max_value=1000,
        value=1,
        step=1,
        help="Number of contracts (lots) to trade"
    )
    
    # Calculate button
    st.markdown("---")
    if st.button("🚀 Calculate Payoff", type="primary", use_container_width=True):
        # Validate inputs
        if validate_inputs([buy_call_premium, sell_call_premium], [buy_call_strike, sell_call_strike]):
            # Generate spot prices
            spot_prices = np.linspace(0, 5000, 1000)
            
            # Calculate payoff
            payoff = calculate_bull_call_spread_payoff(
                spot_prices, buy_call_strike, buy_call_premium,
                sell_call_strike, sell_call_premium, lot_size
            )
            
            # Find breakeven points
            breakeven_points = find_breakeven_points(payoff, spot_prices)
            
            # Create and display chart
            st.markdown("---")
            st.subheader("📊 Payoff Visualization")
            fig = create_payoff_chart(spot_prices, payoff, "Bull Call Spread", currency_symbol)
            st.plotly_chart(fig, use_container_width=True)
            
            # Display summary
            display_summary(payoff, breakeven_points, currency_symbol)

elif strategy == "Iron Condor":
    st.header("🦅 Iron Condor Strategy")
    st.markdown("A neutral strategy that profits from low volatility by selling both a put spread and a call spread.")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📉 Put Spread")
        buy_put_strike = st.number_input(
            "Buy Put Strike Price",
            min_value=0.0,
            max_value=5000.0,
            value=90.0,
            step=1.0,
            help="Strike price of the put option you're buying"
        )
        buy_put_premium = st.number_input(
            "Buy Put Premium",
            min_value=0.01,
            max_value=1000.0,
            value=2.0,
            step=0.01,
            help="Premium paid for the put option"
        )
        sell_put_strike = st.number_input(
            "Sell Put Strike Price",
            min_value=0.0,
            max_value=5000.0,
            value=100.0,
            step=1.0,
            help="Strike price of the put option you're selling"
        )
        sell_put_premium = st.number_input(
            "Sell Put Premium",
            min_value=0.01,
            max_value=1000.0,
            value=5.0,
            step=0.01,
            help="Premium received for the put option"
        )
    
    with col2:
        st.subheader("📈 Call Spread")
        sell_call_strike = st.number_input(
            "Sell Call Strike Price",
            min_value=0.0,
            max_value=5000.0,
            value=110.0,
            step=1.0,
            help="Strike price of the call option you're selling"
        )
        sell_call_premium = st.number_input(
            "Sell Call Premium",
            min_value=0.01,
            max_value=1000.0,
            value=5.0,
            step=0.01,
            help="Premium received for the call option"
        )
        buy_call_strike = st.number_input(
            "Buy Call Strike Price",
            min_value=0.0,
            max_value=5000.0,
            value=120.0,
            step=1.0,
            help="Strike price of the call option you're buying"
        )
        buy_call_premium = st.number_input(
            "Buy Call Premium",
            min_value=0.01,
            max_value=1000.0,
            value=2.0,
            step=0.01,
            help="Premium paid for the call option"
        )
    
    # Lot size input
    st.markdown("---")
    st.subheader("📦 Position Size")
    lot_size = st.number_input(
        "Lot Size",
        min_value=1,
        max_value=1000,
        value=1,
        step=1,
        help="Number of contracts (lots) to trade"
    )
    
    # Calculate button
    st.markdown("---")
    if st.button("🚀 Calculate Payoff", type="primary", use_container_width=True):
        # Validate inputs
        if validate_inputs([buy_put_premium, sell_put_premium, sell_call_premium, buy_call_premium], 
                         [buy_put_strike, sell_put_strike, sell_call_strike, buy_call_strike]):
            # Generate spot prices
            spot_prices = np.linspace(0, 5000, 1000)
            
            # Calculate payoff
            payoff = calculate_iron_condor_payoff(
                spot_prices, buy_put_strike, buy_put_premium,
                sell_put_strike, sell_put_premium, sell_call_strike,
                sell_call_premium, buy_call_strike, buy_call_premium, lot_size
            )
            
            # Find breakeven points
            breakeven_points = find_breakeven_points(payoff, spot_prices)
            
            # Create and display chart
            st.markdown("---")
            st.subheader("📊 Payoff Visualization")
            fig = create_payoff_chart(spot_prices, payoff, "Iron Condor", currency_symbol)
            st.plotly_chart(fig, use_container_width=True)
            
            # Display summary
            display_summary(payoff, breakeven_points, currency_symbol)

# Footer
st.markdown("---")
st.markdown("**Disclaimer:** This simulator is for educational purposes only. Options trading involves substantial risk and may not be suitable for all investors.")