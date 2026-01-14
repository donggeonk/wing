# Trading Agent MVP

A full-stack trading dashboard with an AI-powered chat assistant for portfolio analysis.

Product Demo: https://youtu.be/eZDtmIYLHvk
CLI Demo: https://youtu.be/YvyS0EDiCX8


## 🚀 Features

- **Real-time Stock Charts**: Interactive candlestick charts using TradingView's lightweight-charts
- **Ticker Selection**: Dropdown to select from popular stock symbols
- **AI Chat Assistant**: GPT-powered portfolio assistant that provides insights on your holdings
- **Account Overview**: View Alpaca account balance, positions, and portfolio value
- **Historical Data**: Analyze price movements with historical market data

## 🛠 Tech Stack

### Frontend
- **React 18** with **TypeScript**
- **Vite** for fast development and building
- **lightweight-charts** for professional stock charts
- **Axios** for API communication

### Backend
- **Python 3.10+**
- **FastAPI** for high-performance API
- **Alpaca API** for market data and account information
- **OpenAI GPT-4** for intelligent chat responses

## 📋 Prerequisites

- Python 3.10 or higher
- Node.js 18 or higher
- Alpaca API account (paper trading)
- OpenAI API key

## 🔧 Setup Instructions

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd oasis
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env and add your API keys:
# - ALPACA_API_KEY
# - ALPACA_SECRET_KEY
# - OPENAI_API_KEY
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install
```

## 🚀 Running the Application

### Start Backend (Terminal 1)
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python main.py
```
Backend will run on `http://localhost:8000`

### Start Frontend (Terminal 2)
```bash
cd frontend
npm run dev
```
Frontend will run on `http://localhost:3000`

## 📚 API Documentation

Once the backend is running, view the interactive API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🔑 Environment Variables

### Backend (.env)
```
ALPACA_API_KEY=your_alpaca_api_key_here
ALPACA_SECRET_KEY=your_alpaca_secret_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

## 📖 API Endpoints

- `GET /account` - Get Alpaca account information
- `GET /positions` - Get current portfolio positions
- `GET /price-data?symbol=AAPL&days=30` - Get historical price data
- `POST /chat` - Chat with AI portfolio assistant

## 💬 Chat Assistant

The chat assistant:
- Fetches real-time portfolio data from Alpaca
- Includes recent price movements in context
- Uses GPT-4 to provide clear, factual explanations
- Does NOT provide financial advice or predictions

## 🎨 UI Features

- Dark theme optimized for financial data
- Responsive design for desktop and mobile
- Real-time chart updates
- Smooth animations and transitions

## 📝 Future Enhancements

- [ ] Trade execution functionality
- [ ] Multi-timeframe charts
- [ ] Technical indicators
- [ ] Portfolio analytics dashboard
- [ ] Watchlist management
- [ ] Price alerts
- [ ] Authentication and user accounts

## ⚠️ Disclaimer

This is a demo application using paper trading. Do not use with real money without proper testing and risk management.
