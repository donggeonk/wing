import { useState, useRef, useEffect } from 'react';
import { Send, Trash2, Shield, Activity, Sparkles, ChevronDown, Cpu, Wallet, TrendingUp, TrendingDown, DollarSign, PieChart, RefreshCw } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { 
  sendMessage, 
  resetChat, 
  getPortfolio, 
  getPortfolioHistory 
} from './api';
import type { PortfolioData, PortfolioHistoryPoint } from './api';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

const LLM_MODELS = [
  { id: 'gpt-5', name: 'GPT-5', provider: 'OpenAI' },
  { id: 'gemini-3-pro', name: 'Gemini 3 Pro', provider: 'Google' },
  { id: 'claude-4.5-sonnet', name: 'Claude 4.5 Sonnet', provider: 'Anthropic' },
];

const BROKERAGES = [
  { id: 'alpaca', name: 'Alpaca' },
  { id: 'robinhood', name: 'Robinhood' },
  { id: 'webull', name: 'Webull' },
  { id: 'coinbase', name: 'Coinbase' },
];

const TIME_PERIODS = ['1D', '1W', '1M', '3M', '1Y', 'ALL'];

function App() {
  // Chat State
  const [messages, setMessages] = useState<Message[]>([
    { role: 'assistant', content: "**Welcome to OASIS.** \n\nI can analyze your portfolio, research market trends, and execute trades. Try:\n\n* \"Buy 5 shares of AAPL\"\n* \"What's my buying power?\"\n* \"How is TSLA performing?\"" }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedModel, setSelectedModel] = useState(LLM_MODELS[0]);
  const [selectedBrokerage, setSelectedBrokerage] = useState(BROKERAGES[0]);
  const [isModelDropdownOpen, setIsModelDropdownOpen] = useState(false);
  const [isBrokerageDropdownOpen, setIsBrokerageDropdownOpen] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Portfolio State
  const [portfolio, setPortfolio] = useState<PortfolioData | null>(null);
  const [portfolioHistory, setPortfolioHistory] = useState<PortfolioHistoryPoint[]>([]);
  const [selectedPeriod, setSelectedPeriod] = useState('1M');
  const [totalPL, setTotalPL] = useState(0);
  const [totalPLPct, setTotalPLPct] = useState(0);
  const [isLoadingPortfolio, setIsLoadingPortfolio] = useState(true);

  // Fetch portfolio data on mount
  useEffect(() => {
    fetchPortfolioData();
  }, []);

  // Fetch history when period changes
  useEffect(() => {
    fetchPortfolioHistory();
  }, [selectedPeriod]);

  const fetchPortfolioData = async () => {
    setIsLoadingPortfolio(true);
    const data = await getPortfolio();
    if (data) {
      setPortfolio(data);
    }
    setIsLoadingPortfolio(false);
  };

  const fetchPortfolioHistory = async () => {
    const timeframe = selectedPeriod === '1D' ? '5Min' : '1D';
    const data = await getPortfolioHistory(selectedPeriod, timeframe);
    if (data.success) {
      setPortfolioHistory(data.data);
      setTotalPL(data.total_pl);
      setTotalPLPct(data.total_pl_pct);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    const handleClickOutside = () => {
      setIsModelDropdownOpen(false);
      setIsBrokerageDropdownOpen(false);
    };
    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, []);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = input;
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setIsLoading(true);

    try {
      const data = await sendMessage(userMessage);
      if (data.success) {
        setMessages(prev => [...prev, { role: 'assistant', content: data.response }]);
        // Refresh portfolio after potential trade
        fetchPortfolioData();
        fetchPortfolioHistory();
      } else {
        setMessages(prev => [...prev, { role: 'assistant', content: `⚠️ **Error:** ${data.error}` }]);
      }
    } catch (error) {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, I encountered a network error.' }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = async () => {
    if (confirm('Clear conversation history?')) {
      await resetChat();
      setMessages([{ role: 'assistant', content: 'History cleared. Ready for new trades.' }]);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(value);
  };

  const formatPercent = (value: number) => {
    const sign = value >= 0 ? '+' : '';
    return `${sign}${(value * 100).toFixed(2)}%`;
  };

  const formatChartTime = (timestamp: number) => {
    const date = new Date(timestamp * 1000);
    if (selectedPeriod === '1D') {
      return date.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
    }
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  const isPositive = totalPL >= 0;

  return (
    <div className="flex h-screen bg-rh-black text-rh-text font-sans">
      
      {/* ========== LEFT SIDE: Portfolio Dashboard ========== */}
      <div className="flex-1 flex flex-col border-r border-gray-800">
        
        {/* Header */}
        <header className="h-16 px-6 flex items-center justify-between border-b border-gray-800 bg-rh-black/90 backdrop-blur-md">
          <div className="flex items-center gap-4">
            <span className="font-bold text-xl tracking-tight">OASIS</span>
            
            {/* Brokerage Dropdown */}
            <div className="relative">
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  setIsBrokerageDropdownOpen(!isBrokerageDropdownOpen);
                }}
                className="flex items-center gap-2 px-3 py-1.5 bg-rh-gray hover:bg-rh-hover border border-gray-700 rounded-full text-sm transition-all"
              >
                <Wallet size={14} className="text-rh-subtext" />
                <span>{selectedBrokerage.name}</span>
                <ChevronDown size={14} className={`text-rh-subtext transition-transform ${isBrokerageDropdownOpen ? 'rotate-180' : ''}`} />
              </button>

              {isBrokerageDropdownOpen && (
                <div className="absolute top-full left-0 mt-2 w-48 bg-rh-gray border border-gray-700 rounded-xl shadow-2xl overflow-hidden z-50">
                  <div className="px-3 py-2 border-b border-gray-700">
                    <span className="text-[10px] uppercase tracking-wider text-rh-subtext font-bold">Select Brokerage</span>
                  </div>
                  {BROKERAGES.map((brokerage) => (
                    <button
                      key={brokerage.id}
                      onClick={(e) => {
                        e.stopPropagation();
                        setSelectedBrokerage(brokerage);
                        setIsBrokerageDropdownOpen(false);
                      }}
                      className={`w-full flex items-center gap-3 px-3 py-2.5 hover:bg-rh-hover transition-colors text-left ${
                        selectedBrokerage.id === brokerage.id ? 'bg-rh-green/10 text-rh-green' : ''
                      }`}
                    >
                      <span className="text-sm font-medium">{brokerage.name}</span>
                      {selectedBrokerage.id === brokerage.id && <span className="ml-auto text-rh-green">✓</span>}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className={`flex items-center gap-2 text-xs font-medium px-3 py-1 rounded-full border ${
              isPositive 
                ? 'text-rh-green bg-rh-green/10 border-rh-green/20' 
                : 'text-rh-red bg-rh-red/10 border-rh-red/20'
            }`}>
              <span className="relative flex h-2 w-2">
                <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${isPositive ? 'bg-rh-green' : 'bg-rh-red'}`}></span>
                <span className={`relative inline-flex rounded-full h-2 w-2 ${isPositive ? 'bg-rh-green' : 'bg-rh-red'}`}></span>
              </span>
              Market Open
            </div>
            <button onClick={() => { fetchPortfolioData(); fetchPortfolioHistory(); }} className="p-2 text-rh-subtext hover:text-white hover:bg-rh-gray rounded-full transition-all">
              <RefreshCw size={16} />
            </button>
          </div>
        </header>

        {/* Portfolio Value & Chart */}
        <div className="flex-1 overflow-y-auto p-6">
          {isLoadingPortfolio ? (
            <div className="flex items-center justify-center h-64">
              <Activity className="w-8 h-8 text-rh-green animate-spin" />
            </div>
          ) : (
            <>
              {/* Portfolio Value */}
              <div className="mb-6">
                <h1 className="text-4xl font-bold mb-1">
                  {portfolio ? formatCurrency(portfolio.total_equity) : '$0.00'}
                </h1>
                <div className={`flex items-center gap-2 text-lg ${isPositive ? 'text-rh-green' : 'text-rh-red'}`}>
                  {isPositive ? <TrendingUp size={20} /> : <TrendingDown size={20} />}
                  <span>{formatCurrency(Math.abs(totalPL))}</span>
                  <span>({formatPercent(totalPLPct)})</span>
                  <span className="text-rh-subtext text-sm ml-2">{selectedPeriod}</span>
                </div>
              </div>

              {/* Chart */}
              <div className="h-72 mb-4">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={portfolioHistory}>
                    <defs>
                      <linearGradient id="colorEquity" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor={isPositive ? '#00c805' : '#ff3b30'} stopOpacity={0.3}/>
                        <stop offset="95%" stopColor={isPositive ? '#00c805' : '#ff3b30'} stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <XAxis 
                      dataKey="timestamp" 
                      tickFormatter={formatChartTime}
                      axisLine={false}
                      tickLine={false}
                      tick={{ fill: '#8e9196', fontSize: 11 }}
                      minTickGap={50}
                    />
                    <YAxis 
                      domain={['dataMin - 100', 'dataMax + 100']}
                      axisLine={false}
                      tickLine={false}
                      tick={{ fill: '#8e9196', fontSize: 11 }}
                      tickFormatter={(val) => `$${(val/1000).toFixed(0)}k`}
                      width={60}
                    />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: '#1e2124', 
                        border: '1px solid #40414F',
                        borderRadius: '12px',
                        padding: '12px'
                      }}
                      labelFormatter={(val) => formatChartTime(val as number)}
                      formatter={(value: number) => [formatCurrency(value), 'Portfolio Value']}
                    />
                    <Area 
                      type="monotone" 
                      dataKey="equity" 
                      stroke={isPositive ? '#00c805' : '#ff3b30'} 
                      strokeWidth={2}
                      fill="url(#colorEquity)"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>

              {/* Time Period Selector */}
              <div className="flex gap-2 mb-8">
                {TIME_PERIODS.map((period) => (
                  <button
                    key={period}
                    onClick={() => setSelectedPeriod(period)}
                    className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${
                      selectedPeriod === period
                        ? 'bg-rh-green text-black'
                        : 'bg-rh-gray text-rh-subtext hover:bg-rh-hover hover:text-white'
                    }`}
                  >
                    {period}
                  </button>
                ))}
              </div>

              {/* Portfolio Stats Cards */}
              <div className="grid grid-cols-3 gap-4 mb-8">
                <div className="bg-rh-gray rounded-2xl p-4 border border-gray-800">
                  <div className="flex items-center gap-2 text-rh-subtext text-xs uppercase tracking-wider mb-2">
                    <DollarSign size={14} />
                    <span>Cash</span>
                  </div>
                  <p className="text-xl font-bold">{portfolio ? formatCurrency(portfolio.cash) : '$0.00'}</p>
                </div>
                <div className="bg-rh-gray rounded-2xl p-4 border border-gray-800">
                  <div className="flex items-center gap-2 text-rh-subtext text-xs uppercase tracking-wider mb-2">
                    <TrendingUp size={14} />
                    <span>Buying Power</span>
                  </div>
                  <p className="text-xl font-bold">{portfolio ? formatCurrency(portfolio.buying_power) : '$0.00'}</p>
                </div>
                <div className="bg-rh-gray rounded-2xl p-4 border border-gray-800">
                  <div className="flex items-center gap-2 text-rh-subtext text-xs uppercase tracking-wider mb-2">
                    <PieChart size={14} />
                    <span>Positions</span>
                  </div>
                  <p className="text-xl font-bold">{portfolio?.total_positions || 0}</p>
                </div>
              </div>

              {/* Positions List */}
              <div>
                <h2 className="text-lg font-bold mb-4">Positions</h2>
                {portfolio?.positions && portfolio.positions.length > 0 ? (
                  <div className="space-y-2">
                    {portfolio.positions.map((position) => (
                      <div key={position.symbol} className="flex items-center justify-between bg-rh-gray rounded-xl p-4 border border-gray-800 hover:bg-rh-hover transition-colors">
                        <div>
                          <p className="font-bold">{position.symbol}</p>
                          <p className="text-sm text-rh-subtext">{position.qty} shares @ {formatCurrency(position.avg_entry_price)}</p>
                        </div>
                        <div className="text-right">
                          <p className="font-bold">{formatCurrency(position.market_value)}</p>
                          <p className={`text-sm ${position.unrealized_pl >= 0 ? 'text-rh-green' : 'text-rh-red'}`}>
                            {formatCurrency(position.unrealized_pl)} ({(position.unrealized_plpc * 100).toFixed(2)}%)
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8 text-rh-subtext">
                    <p>No positions yet</p>
                    <p className="text-sm mt-1">Ask OASIS to buy some stocks!</p>
                  </div>
                )}
              </div>
            </>
          )}
        </div>
      </div>

      {/* ========== RIGHT SIDE: Chat Panel ========== */}
      <div className="w-[400px] flex flex-col bg-rh-black">
        
        {/* Chat Header */}
        <div className="h-16 px-4 flex items-center justify-between border-b border-gray-800">
          <div className="flex items-center gap-2">
            <Sparkles size={18} className="text-rh-green" />
            <span className="font-bold">OASIS Copilot</span>
          </div>
          <button 
            onClick={handleReset}
            className="p-2 text-rh-subtext hover:text-rh-red hover:bg-rh-red/10 rounded-full transition-all"
            title="Reset Chat"
          >
            <Trash2 size={16} />
          </button>
        </div>

        {/* Chat Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((msg, idx) => (
            <div 
              key={idx} 
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div 
                className={`max-w-[90%] px-4 py-2 ${
                  msg.role === 'user' 
                    ? 'bg-rh-green text-black rounded-2xl rounded-tr-sm' 
                    : 'bg-rh-gray text-rh-text rounded-2xl rounded-tl-sm border border-gray-800'
                }`}
              >
                <div className={`prose prose-sm max-w-none leading-relaxed ${
                  msg.role === 'user' ? 'prose-p:text-black' : 'prose-invert prose-p:text-gray-200 prose-strong:text-white'
                }`}>
                  <ReactMarkdown>{msg.content}</ReactMarkdown>
                </div>
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-rh-gray px-4 py-2 rounded-2xl rounded-tl-sm border border-gray-800 flex items-center gap-2">
                <Activity className="w-4 h-4 text-rh-green animate-spin" />
                <span className="text-sm text-rh-subtext">Thinking...</span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Chat Input */}
        <div className="p-4 border-t border-gray-800">
          {/* Model Selector */}
          <div className="flex justify-start mb-3">
            <div className="relative">
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  setIsModelDropdownOpen(!isModelDropdownOpen);
                }}
                className="flex items-center gap-2 px-3 py-1.5 bg-rh-gray hover:bg-rh-hover border border-gray-700 rounded-full text-xs transition-all"
              >
                <Cpu size={12} className="text-rh-green" />
                <span className="font-medium">{selectedModel.name}</span>
                <ChevronDown size={12} className={`text-rh-subtext transition-transform ${isModelDropdownOpen ? 'rotate-180' : ''}`} />
              </button>

              {isModelDropdownOpen && (
                <div className="absolute bottom-full left-0 mb-2 w-52 bg-rh-gray border border-gray-700 rounded-xl shadow-2xl overflow-hidden z-50">
                  <div className="px-3 py-2 border-b border-gray-700">
                    <span className="text-[10px] uppercase tracking-wider text-rh-subtext font-bold">Select AI Model</span>
                  </div>
                  {LLM_MODELS.map((model) => (
                    <button
                      key={model.id}
                      onClick={(e) => {
                        e.stopPropagation();
                        setSelectedModel(model);
                        setIsModelDropdownOpen(false);
                      }}
                      className={`w-full flex items-center justify-between px-3 py-2.5 hover:bg-rh-hover transition-colors text-left ${
                        selectedModel.id === model.id ? 'bg-rh-green/10' : ''
                      }`}
                    >
                      <div className="flex flex-col">
                        <span className={`text-sm font-medium ${selectedModel.id === model.id ? 'text-rh-green' : ''}`}>{model.name}</span>
                        <span className="text-[10px] text-rh-subtext">{model.provider}</span>
                      </div>
                      {selectedModel.id === model.id && <span className="text-rh-green">✓</span>}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Input Box */}
          <div className="flex items-center gap-2 bg-rh-gray rounded-full border border-gray-700 focus-within:border-rh-green focus-within:ring-1 focus-within:ring-rh-green transition-all">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask about stocks..."
              className="flex-1 bg-transparent text-white placeholder-rh-subtext px-4 py-3 rounded-full focus:outline-none text-sm"
            />
            <button
              onClick={handleSend}
              disabled={!input.trim() || isLoading}
              className="mr-1 p-2 bg-rh-green text-black rounded-full hover:bg-rh-greenHover disabled:opacity-50 disabled:cursor-not-allowed transition-transform active:scale-95"
            >
              <Send size={16} strokeWidth={2.5} />
            </button>
          </div>

          {/* Footer */}
          <div className="flex justify-center gap-4 mt-3 text-[9px] text-rh-subtext uppercase tracking-widest">
            <span className="flex items-center gap-1"><Shield size={8} /> Secure</span>
            <span>Paper Trading</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;