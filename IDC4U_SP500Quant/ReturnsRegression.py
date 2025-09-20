import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import datetime

# Expanded list of 20 tickers per sector
sp500_companies = {
    "Consumer Cyclicals": [
        "AMZN","TSLA","NKE","MCD","SBUX","HD","LOW","LULU","ROST","TJX",
        "BKNG","MAR","YUM","LEG","EXPE","ORLY","CPRI","DG","RH","BBY"
    ],
    "Financials": [
        "JPM","BAC","C","WFC","GS","MS","AXP","BLK","SCHW","PNC",
        "TFC","USB","COF","BK","FITB","STT","ICE","SPGI","AON","MMC"
    ],
    "Energy": [
        "XOM","CVX","COP","SLB","HAL","PSX","VLO","MPC","OXY","PXD",
        "KMI","EOG","NOV","APA","CPE","FANG","OKE","HES","BKR","MRO"
    ],
    "Industrials": [
        "BA","CAT","LMT","HON","DE","UPS","UNP","MMM","GD","EMR",
        "DHR","GE","ETN","ROK","PH","PCAR","XYL","CTAS","CSX","CHRW"
    ],
    "Technology": [
        "AAPL","MSFT","GOOGL","NVDA","ADBE","ORCL","INTC","CSCO","CRM","IBM",
        "QCOM","TXN","AVGO","AMD","NOW","SNPS","ANSS","ADI","MU","LRCX"
    ],
    "Healthcare": [
        "PFE","JNJ","MRNA","ABT","MRK","BMY","AMGN","GILD","BIIB","REGN",
        "VRTX","ISRG","MDT","SYK","BSX","EW","ZTS","ALXN","IQV","HUM"
    ]
}

sectors = list(sp500_companies.keys())

print("Welcome to IDC4USTOCKRECOMMENDER 🚀")
print("Choose a sector:")
for i, sec in enumerate(sectors, start=1):
    print(f"{i}. {sec}")

# User input for sector
while True:
    try:
        sector_choice = int(input("Enter the number for your chosen sector: "))
        if 1 <= sector_choice <= len(sectors):
            break
        else:
            print("Invalid choice, try again.")
    except ValueError:
        print("Please enter a valid number.")

chosen_sector = sectors[sector_choice - 1]

# User input for risk level
risk_level = input("Enter risk level (low / medium / high): ").strip().lower()
if risk_level not in ["low", "medium", "high"]:
    print("Invalid risk level, defaulting to medium.")
    risk_level = "medium"

stocks = sp500_companies[chosen_sector]

# Time period: last 6 months
end = datetime.date.today()
start = end - datetime.timedelta(days=180)

# Function to get daily returns
def get_returns(ticker):
    try:
        data = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=False)
        if data.empty:
            return None
        prices = data["Adj Close"] if "Adj Close" in data.columns else data["Close"]
        returns = prices.pct_change().dropna()
        if len(returns) < 10:
            return None
        return returns
    except Exception as e:
        print(f"Error retrieving data for {ticker}: {e}")
        return None

# Function to calculate stock score
def stock_score(ticker):
    returns = get_returns(ticker)
    if returns is None:
        return None

    X = np.arange(len(returns)).reshape(-1, 1)
    y = returns.values.reshape(-1, 1)

    model = LinearRegression()
    model.fit(X, y)
    slope = float(model.coef_[0][0])
    
    # Fix FutureWarning
    std_val = returns.std()
    volatility = float(std_val.iloc[0]) if isinstance(std_val, pd.Series) else float(std_val)

    if risk_level == "low":
        score = slope - volatility
    elif risk_level == "medium":
        score = slope
    else:  # high
        score = slope + volatility

    return score

# Function to format market cap nicely
def format_market_cap(market_cap):
    if market_cap is None:
        return "N/A"
    elif market_cap >= 1_000_000_000_000:
        return f"${market_cap/1_000_000_000_000:.2f}T"
    elif market_cap >= 1_000_000_000:
        return f"${market_cap/1_000_000_000:.2f}B"
    elif market_cap >= 1_000_000:
        return f"${market_cap/1_000_000:.2f}M"
    else:
        return f"${market_cap}"

# Calculate scores for all stocks
results = {}
for stock in stocks:
    score = stock_score(stock)
    if score is not None:
        results[stock] = score

if not results:
    print("No valid data available for your chosen sector.")
else:
    best_stock = max(results, key=results.get)
    info = yf.Ticker(best_stock).info
    name = info.get("shortName", "N/A")
    market_cap = format_market_cap(info.get("marketCap"))
    sector_info = info.get("sector", chosen_sector)
    print(f"\n✅ Best stock for sector '{sector_info}' at risk level '{risk_level}':")
    print(f"{name} ({best_stock})")
    print(f"Market Cap: {market_cap}")
