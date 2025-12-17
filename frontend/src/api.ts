import axios from 'axios';

const API_URL = 'http://localhost:8000/api';

// ============ INTERFACES ============

export interface ChatResponse {
  response: string;
  success: boolean;
  error?: string;
}

export interface Position {
  symbol: string;
  qty: number;
  market_value: number;
  cost_basis: number;
  unrealized_pl: number;
  unrealized_plpc: number;
  current_price: number;
  avg_entry_price: number;
}

export interface PortfolioData {
  total_equity: number;
  cash: number;
  buying_power: number;
  positions: Position[];
  total_positions: number;
  total_unrealized_pl: number;
  cash_percentage: number;
  invested_percentage: number;
  success: boolean;
}

export interface PortfolioHistoryPoint {
  timestamp: number;
  equity: number;
  profit_loss: number;
  profit_loss_pct: number;
}

export interface PortfolioHistoryResponse {
  success: boolean;
  period: string;
  timeframe: string;
  data: PortfolioHistoryPoint[];
  base_value: number;
  total_pl: number;
  total_pl_pct: number;
  error?: string;
}

// ============ API FUNCTIONS ============

export const sendMessage = async (message: string): Promise<ChatResponse> => {
  try {
    const res = await axios.post(`${API_URL}/chat`, { message });
    return res.data;
  } catch (error) {
    console.error('API Error:', error);
    return {
      response: '',
      success: false,
      error: 'Failed to connect to server'
    };
  }
};

export const resetChat = async () => {
  try {
    await axios.post(`${API_URL}/chat/reset`);
  } catch (error) {
    console.error('Reset Error:', error);
  }
};

export const getPortfolio = async (): Promise<PortfolioData | null> => {
  try {
    const res = await axios.get(`${API_URL}/portfolio`);
    return res.data;
  } catch (error) {
    console.error('Portfolio Error:', error);
    return null;
  }
};

export const getPortfolioHistory = async (
  period: string = '1M',
  timeframe: string = '1D'
): Promise<PortfolioHistoryResponse> => {
  try {
    const res = await axios.get(`${API_URL}/portfolio/history`, {
      params: { period, timeframe }
    });
    return res.data;
  } catch (error) {
    console.error('Portfolio History Error:', error);
    return {
      success: false,
      period,
      timeframe,
      data: [],
      base_value: 0,
      total_pl: 0,
      total_pl_pct: 0,
      error: 'Failed to fetch portfolio history'
    };
  }
};