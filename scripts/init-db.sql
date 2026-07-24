-- Stock Market Dashboard - Database Initialization Script
-- PostgreSQL 16+ compatible

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create schemas for each service
CREATE SCHEMA IF NOT EXISTS auth;
CREATE SCHEMA IF NOT EXISTS users;
CREATE SCHEMA IF NOT EXISTS market_data;
CREATE SCHEMA IF NOT EXISTS watchlists;
CREATE SCHEMA IF NOT EXISTS portfolio;
CREATE SCHEMA IF NOT EXISTS trading;
CREATE SCHEMA IF NOT EXISTS alerts;
CREATE SCHEMA IF NOT EXISTS notifications;
CREATE SCHEMA IF NOT EXISTS news;
CREATE SCHEMA IF NOT EXISTS reports;

-- Set search path
SET search_path TO auth, users, market_data, watchlists, portfolio, trading, alerts, notifications, news, reports, public;

-- ============================================
-- AUTH SCHEMA - Authentication tables
-- ============================================

CREATE TABLE IF NOT EXISTS auth.users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    role VARCHAR(20) NOT NULL DEFAULT 'user' CHECK (role IN ('guest', 'user', 'premium', 'admin')),
    status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'suspended', 'deleted')),
    email_verified BOOLEAN NOT NULL DEFAULT FALSE,
    phone VARCHAR(20),
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_auth_users_username ON auth.users(username);
CREATE INDEX IF NOT EXISTS idx_auth_users_email ON auth.users(email);
CREATE INDEX IF NOT EXISTS idx_auth_users_role ON auth.users(role);
CREATE INDEX IF NOT EXISTS idx_auth_users_status ON auth.users(status);

-- Refresh tokens
CREATE TABLE IF NOT EXISTS auth.refresh_tokens (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    token TEXT NOT NULL UNIQUE,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    revoked BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_auth_refresh_tokens_token ON auth.refresh_tokens(token);
CREATE INDEX IF NOT EXISTS idx_auth_refresh_tokens_user_id ON auth.refresh_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_auth_refresh_tokens_expires ON auth.refresh_tokens(expires_at);

-- Sessions
CREATE TABLE IF NOT EXISTS auth.sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    session_token TEXT NOT NULL UNIQUE,
    ip_address VARCHAR(45),
    user_agent TEXT,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_auth_sessions_token ON auth.sessions(session_token);
CREATE INDEX IF NOT EXISTS idx_auth_sessions_user_id ON auth.sessions(user_id);

-- ============================================
-- USERS SCHEMA - User profiles and preferences
-- ============================================

CREATE TABLE IF NOT EXISTS users.profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL UNIQUE REFERENCES auth.users(id) ON DELETE CASCADE,
    display_name VARCHAR(100),
    bio TEXT,
    avatar_url TEXT,
    date_of_birth DATE,
    gender VARCHAR(20),
    country VARCHAR(100),
    city VARCHAR(100),
    timezone VARCHAR(50) NOT NULL DEFAULT 'UTC',
    language VARCHAR(10) NOT NULL DEFAULT 'en',
    currency VARCHAR(3) NOT NULL DEFAULT 'INR',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_users_profiles_user_id ON users.profiles(user_id);

-- User preferences
CREATE TABLE IF NOT EXISTS users.preferences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL UNIQUE REFERENCES auth.users(id) ON DELETE CASCADE,
    theme VARCHAR(20) NOT NULL DEFAULT 'dark' CHECK (theme IN ('light', 'dark', 'system')),
    chart_theme VARCHAR(20) NOT NULL DEFAULT 'dark',
    chart_type VARCHAR(20) NOT NULL DEFAULT 'candlestick' CHECK (chart_type IN ('line', 'candlestick', 'bar', 'area')),
    default_timeframe VARCHAR(10) NOT NULL DEFAULT '1D',
    show_grid BOOLEAN NOT NULL DEFAULT TRUE,
    show_indicators BOOLEAN NOT NULL DEFAULT TRUE,
    notification_email BOOLEAN NOT NULL DEFAULT TRUE,
    notification_push BOOLEAN NOT NULL DEFAULT TRUE,
    notification_sms BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_users_preferences_user_id ON users.preferences(user_id);

-- ============================================
-- MARKET_DATA SCHEMA - Market data tables
-- ============================================

-- Symbols master data
CREATE TABLE IF NOT EXISTS market_data.symbols (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol VARCHAR(20) NOT NULL,
    exchange VARCHAR(10) NOT NULL CHECK (exchange IN ('NSE', 'BSE', 'NFO', 'BFO', 'MCX')),
    symbol_type VARCHAR(20) NOT NULL CHECK (symbol_type IN ('stock', 'index', 'future', 'option', 'commodity', 'forex', 'crypto')),
    company_name VARCHAR(255) NOT NULL,
    sector VARCHAR(100),
    industry VARCHAR(100),
    market_cap DECIMAL(20, 2),
    isin VARCHAR(20),
    face_value DECIMAL(10, 2),
    listing_date DATE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_market_data_symbols_unique ON market_data.symbols(symbol, exchange);
CREATE INDEX IF NOT EXISTS idx_market_data_symbols_exchange ON market_data.symbols(exchange);
CREATE INDEX IF NOT EXISTS idx_market_data_symbols_sector ON market_data.symbols(sector);
CREATE INDEX IF NOT EXISTS idx_market_data_symbols_active ON market_data.symbols(is_active);

-- Latest quotes (cached)
CREATE TABLE IF NOT EXISTS market_data.quotes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol_id UUID NOT NULL REFERENCES market_data.symbols(id) ON DELETE CASCADE,
    last_price DECIMAL(15, 4) NOT NULL,
    open DECIMAL(15, 4) NOT NULL,
    high DECIMAL(15, 4) NOT NULL,
    low DECIMAL(15, 4) NOT NULL,
    close DECIMAL(15, 4) NOT NULL,
    previous_close DECIMAL(15, 4) NOT NULL,
    volume BIGINT NOT NULL DEFAULT 0,
    average_volume BIGINT NOT NULL DEFAULT 0,
    change DECIMAL(15, 4) NOT NULL DEFAULT 0,
    change_percent DECIMAL(10, 4) NOT NULL DEFAULT 0,
    week_52_high DECIMAL(15, 4),
    week_52_low DECIMAL(15, 4),
    bid DECIMAL(15, 4),
    ask DECIMAL(15, 4),
    bid_size BIGINT,
    ask_size BIGINT,
    spread DECIMAL(15, 4),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    trade_time TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_market_data_quotes_symbol ON market_data.quotes(symbol_id);
CREATE INDEX IF NOT EXISTS idx_market_data_quotes_timestamp ON market_data.quotes(timestamp);

-- Historical OHLCV data
CREATE TABLE IF NOT EXISTS market_data.ohlcv (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol_id UUID NOT NULL REFERENCES market_data.symbols(id) ON DELETE CASCADE,
    timeframe VARCHAR(10) NOT NULL CHECK (timeframe IN ('1m', '5m', '15m', '30m', '1H', '4H', '1D', '1W', '1M', '1Y', '5Y')),
    open_time TIMESTAMP WITH TIME ZONE NOT NULL,
    open DECIMAL(15, 4) NOT NULL,
    high DECIMAL(15, 4) NOT NULL,
    low DECIMAL(15, 4) NOT NULL,
    close DECIMAL(15, 4) NOT NULL,
    volume BIGINT NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_market_data_ohlcv_unique ON market_data.ohlcv(symbol_id, timeframe, open_time);
CREATE INDEX IF NOT EXISTS idx_market_data_ohlcv_symbol ON market_data.ohlcv(symbol_id);
CREATE INDEX IF NOT EXISTS idx_market_data_ohlcv_timeframe ON market_data.ohlcv(timeframe);
CREATE INDEX IF NOT EXISTS idx_market_data_ohlcv_open_time ON market_data.ohlcv(open_time);

-- Market calendar
CREATE TABLE IF NOT EXISTS market_data.calendar (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    exchange VARCHAR(10) NOT NULL CHECK (exchange IN ('NSE', 'BSE', 'NFO', 'BFO', 'MCX')),
    date DATE NOT NULL,
    is_trading_day BOOLEAN NOT NULL DEFAULT TRUE,
    is_holiday BOOLEAN NOT NULL DEFAULT FALSE,
    holiday_name VARCHAR(255),
    market_open TIMESTAMP WITH TIME ZONE NOT NULL,
    market_close TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_market_data_calendar_unique ON market_data.calendar(exchange, date);
CREATE INDEX IF NOT EXISTS idx_market_data_calendar_exchange ON market_data.calendar(exchange);
CREATE INDEX IF NOT EXISTS idx_market_data_calendar_date ON market_data.calendar(date);

-- ============================================
-- WATCHLISTS SCHEMA - Watchlist tables
-- ============================================

-- Watchlists
CREATE TABLE IF NOT EXISTS watchlists.watchlists (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    is_public BOOLEAN NOT NULL DEFAULT FALSE,
    is_default BOOLEAN NOT NULL DEFAULT FALSE,
    position INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_watchlists_watchlists_user ON watchlists.watchlists(user_id);
CREATE INDEX IF NOT EXISTS idx_watchlists_watchlists_position ON watchlists.watchlists(position);

-- Watchlist items
CREATE TABLE IF NOT EXISTS watchlists.items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    watchlist_id UUID NOT NULL REFERENCES watchlists.watchlists(id) ON DELETE CASCADE,
    symbol_id UUID NOT NULL REFERENCES market_data.symbols(id) ON DELETE CASCADE,
    display_name VARCHAR(100),
    color VARCHAR(20),
    position INTEGER NOT NULL DEFAULT 0,
    alert_price_above DECIMAL(15, 4),
    alert_price_below DECIMAL(15, 4),
    alert_change_percent DECIMAL(10, 4),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_watchlists_items_watchlist ON watchlists.items(watchlist_id);
CREATE INDEX IF NOT EXISTS idx_watchlists_items_symbol ON watchlists.items(symbol_id);
CREATE INDEX IF NOT EXISTS idx_watchlists_items_position ON watchlists.items(position);

-- ============================================
-- PORTFOLIO SCHEMA - Portfolio tables
-- ============================================

-- Portfolios
CREATE TABLE IF NOT EXISTS portfolio.portfolios (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    cash_balance DECIMAL(15, 2) NOT NULL DEFAULT 0,
    is_default BOOLEAN NOT NULL DEFAULT FALSE,
    position INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_portfolio_portfolios_user ON portfolio.portfolios(user_id);
CREATE INDEX IF NOT EXISTS idx_portfolio_portfolios_position ON portfolio.portfolios(position);

-- Portfolio items (holdings)
CREATE TABLE IF NOT EXISTS portfolio.items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    portfolio_id UUID NOT NULL REFERENCES portfolio.portfolios(id) ON DELETE CASCADE,
    symbol_id UUID NOT NULL REFERENCES market_data.symbols(id) ON DELETE CASCADE,
    quantity DECIMAL(15, 6) NOT NULL DEFAULT 0,
    average_price DECIMAL(15, 4) NOT NULL DEFAULT 0,
    purchase_date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    purchase_notes TEXT,
    position INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_portfolio_items_portfolio ON portfolio.items(portfolio_id);
CREATE INDEX IF NOT EXISTS idx_portfolio_items_symbol ON portfolio.items(symbol_id);

-- Portfolio snapshots (for historical tracking)
CREATE TABLE IF NOT EXISTS portfolio.snapshots (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    portfolio_id UUID NOT NULL REFERENCES portfolio.portfolios(id) ON DELETE CASCADE,
    total_investment DECIMAL(15, 2) NOT NULL DEFAULT 0,
    total_current_value DECIMAL(15, 2) NOT NULL DEFAULT 0,
    total_profit_loss DECIMAL(15, 2) NOT NULL DEFAULT 0,
    total_profit_loss_percent DECIMAL(10, 4) NOT NULL DEFAULT 0,
    cash_balance DECIMAL(15, 2) NOT NULL DEFAULT 0,
    snapshot_date DATE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_portfolio_snapshots_unique ON portfolio.snapshots(portfolio_id, snapshot_date);
CREATE INDEX IF NOT EXISTS idx_portfolio_snapshots_portfolio ON portfolio.snapshots(portfolio_id);
CREATE INDEX IF NOT EXISTS idx_portfolio_snapshots_date ON portfolio.snapshots(snapshot_date);

-- ============================================
-- TRADING SCHEMA - Trading tables
-- ============================================

-- Orders
CREATE TABLE IF NOT EXISTS trading.orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    symbol_id UUID NOT NULL REFERENCES market_data.symbols(id) ON DELETE CASCADE,
    order_type VARCHAR(20) NOT NULL CHECK (order_type IN ('market', 'limit', 'stop_loss', 'stop_limit')),
    order_side VARCHAR(10) NOT NULL CHECK (order_side IN ('buy', 'sell')),
    quantity DECIMAL(15, 6) NOT NULL,
    price DECIMAL(15, 4),
    limit_price DECIMAL(15, 4),
    stop_price DECIMAL(15, 4),
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'open', 'partially_filled', 'filled', 'cancelled', 'rejected', 'expired')),
    filled_quantity DECIMAL(15, 6) NOT NULL DEFAULT 0,
    average_filled_price DECIMAL(15, 4),
    brokerage DECIMAL(10, 2) NOT NULL DEFAULT 0,
    taxes DECIMAL(10, 2) NOT NULL DEFAULT 0,
    total_charges DECIMAL(10, 2) NOT NULL DEFAULT 0,
    order_id VARCHAR(100),
    exchange_order_id VARCHAR(100),
    notes TEXT,
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_trading_orders_user ON trading.orders(user_id);
CREATE INDEX IF NOT EXISTS idx_trading_orders_symbol ON trading.orders(symbol_id);
CREATE INDEX IF NOT EXISTS idx_trading_orders_status ON trading.orders(status);
CREATE INDEX IF NOT EXISTS idx_trading_orders_created ON trading.orders(created_at);

-- GTT (Good Till Trigger) Orders
CREATE TABLE IF NOT EXISTS trading.gtt_orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    symbol_id UUID NOT NULL REFERENCES market_data.symbols(id) ON DELETE CASCADE,
    gtt_type VARCHAR(20) NOT NULL DEFAULT 'single' CHECK (gtt_type IN ('single', 'oco')),
    trigger_price DECIMAL(15, 4) NOT NULL,
    trigger_condition VARCHAR(10) NOT NULL CHECK (trigger_condition IN ('above', 'below')),
    order_type VARCHAR(20) NOT NULL CHECK (order_type IN ('market', 'limit', 'stop_loss', 'stop_limit')),
    order_side VARCHAR(10) NOT NULL CHECK (order_side IN ('buy', 'sell')),
    quantity DECIMAL(15, 6) NOT NULL,
    limit_price DECIMAL(15, 4),
    status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'triggered', 'cancelled', 'expired', 'executed')),
    triggered_at TIMESTAMP WITH TIME ZONE,
    executed_at TIMESTAMP WITH TIME ZONE,
    
    -- OCO (One Cancels Other) leg 2
    oco_leg2_trigger_price DECIMAL(15, 4),
    oco_leg2_order_type VARCHAR(20) CHECK (oco_leg2_order_type IN ('market', 'limit', 'stop_loss', 'stop_limit')),
    oco_leg2_order_side VARCHAR(10) CHECK (oco_leg2_order_side IN ('buy', 'sell')),
    oco_leg2_quantity DECIMAL(15, 6),
    oco_leg2_limit_price DECIMAL(15, 4),
    oco_leg2_status VARCHAR(20) CHECK (oco_leg2_status IN ('pending', 'triggered', 'cancelled', 'executed')),
    
    expiry_date TIMESTAMP WITH TIME ZONE,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_trading_gtt_user ON trading.gtt_orders(user_id);
CREATE INDEX IF NOT EXISTS idx_trading_gtt_symbol ON trading.gtt_orders(symbol_id);
CREATE INDEX IF NOT EXISTS idx_trading_gtt_status ON trading.gtt_orders(status);
CREATE INDEX IF NOT EXISTS idx_trading_gtt_expiry ON trading.gtt_orders(expiry_date);

-- Trades
CREATE TABLE IF NOT EXISTS trading.trades (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    symbol_id UUID NOT NULL REFERENCES market_data.symbols(id) ON DELETE CASCADE,
    order_id UUID REFERENCES trading.orders(id) ON DELETE SET NULL,
    order_type VARCHAR(20) NOT NULL CHECK (order_type IN ('market', 'limit', 'stop_loss', 'stop_limit')),
    order_side VARCHAR(10) NOT NULL CHECK (order_side IN ('buy', 'sell')),
    quantity DECIMAL(15, 6) NOT NULL,
    price DECIMAL(15, 4) NOT NULL,
    brokerage DECIMAL(10, 2) NOT NULL DEFAULT 0,
    taxes DECIMAL(10, 2) NOT NULL DEFAULT 0,
    total_charges DECIMAL(10, 2) NOT NULL DEFAULT 0,
    status VARCHAR(20) NOT NULL DEFAULT 'completed' CHECK (status IN ('completed', 'pending', 'failed')),
    trade_id VARCHAR(100),
    exchange_trade_id VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_trading_trades_user ON trading.trades(user_id);
CREATE INDEX IF NOT EXISTS idx_trading_trades_symbol ON trading.trades(symbol_id);
CREATE INDEX IF NOT EXISTS idx_trading_trades_order ON trading.trades(order_id);
CREATE INDEX IF NOT EXISTS idx_trading_trades_created ON trading.trades(created_at);

-- ============================================
-- ALERTS SCHEMA - Alert tables
-- ============================================

-- Alerts
CREATE TABLE IF NOT EXISTS alerts.alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    symbol_id UUID NOT NULL REFERENCES market_data.symbols(id) ON DELETE CASCADE,
    alert_type VARCHAR(20) NOT NULL CHECK (alert_type IN ('price_above', 'price_below', 'change_above', 'change_below', 'volume_above', 'volume_below', 'rsi_above', 'rsi_below', 'custom')),
    condition_value DECIMAL(15, 4) NOT NULL,
    custom_condition TEXT,
    notify_email BOOLEAN NOT NULL DEFAULT TRUE,
    notify_push BOOLEAN NOT NULL DEFAULT TRUE,
    notify_sms BOOLEAN NOT NULL DEFAULT FALSE,
    status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'triggered', 'acknowledged', 'cancelled')),
    triggered_at TIMESTAMP WITH TIME ZONE,
    triggered_price DECIMAL(15, 4),
    repeat BOOLEAN NOT NULL DEFAULT FALSE,
    repeat_interval VARCHAR(20),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_alerts_alerts_user ON alerts.alerts(user_id);
CREATE INDEX IF NOT EXISTS idx_alerts_alerts_symbol ON alerts.alerts(symbol_id);
CREATE INDEX IF NOT EXISTS idx_alerts_alerts_type ON alerts.alerts(alert_type);
CREATE INDEX IF NOT EXISTS idx_alerts_alerts_status ON alerts.alerts(status);

-- Alert history
CREATE TABLE IF NOT EXISTS alerts.history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    alert_id UUID NOT NULL REFERENCES alerts.alerts(id) ON DELETE CASCADE,
    triggered_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    price DECIMAL(15, 4),
    change DECIMAL(15, 4),
    change_percent DECIMAL(10, 4),
    volume BIGINT,
    notified BOOLEAN NOT NULL DEFAULT FALSE,
    notification_id UUID
);

CREATE INDEX IF NOT EXISTS idx_alerts_history_alert ON alerts.history(alert_id);
CREATE INDEX IF NOT EXISTS idx_alerts_history_triggered ON alerts.history(triggered_at);

-- ============================================
-- NOTIFICATIONS SCHEMA - Notification tables
-- ============================================

-- Notifications
CREATE TABLE IF NOT EXISTS notifications.notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    notification_type VARCHAR(50) NOT NULL CHECK (notification_type IN ('alert', 'order', 'trade', 'system', 'news', 'report')),
    priority VARCHAR(20) NOT NULL DEFAULT 'normal' CHECK (priority IN ('low', 'normal', 'high', 'urgent')),
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    is_archived BOOLEAN NOT NULL DEFAULT FALSE,
    data JSONB,
    related_id UUID,
    related_type VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    read_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_notifications_notifications_user ON notifications.notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_notifications_read ON notifications.notifications(is_read);
CREATE INDEX IF NOT EXISTS idx_notifications_notifications_type ON notifications.notifications(notification_type);
CREATE INDEX IF NOT EXISTS idx_notifications_notifications_created ON notifications.notifications(created_at);

-- Notification preferences
CREATE TABLE IF NOT EXISTS notifications.preferences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL UNIQUE REFERENCES auth.users(id) ON DELETE CASCADE,
    email_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    push_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    sms_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    alert_notifications BOOLEAN NOT NULL DEFAULT TRUE,
    order_notifications BOOLEAN NOT NULL DEFAULT TRUE,
    trade_notifications BOOLEAN NOT NULL DEFAULT TRUE,
    news_notifications BOOLEAN NOT NULL DEFAULT TRUE,
    report_notifications BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_notifications_preferences_user ON notifications.preferences(user_id);

-- ============================================
-- NEWS SCHEMA - News tables
-- ============================================

-- News articles
CREATE TABLE IF NOT EXISTS news.articles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    summary TEXT,
    source VARCHAR(255) NOT NULL,
    source_url VARCHAR(1000) NOT NULL,
    image_url VARCHAR(1000),
    published_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    category VARCHAR(100),
    tags VARCHAR(255)[],
    sentiment_score DECIMAL(5, 4),
    sentiment_label VARCHAR(20),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_news_articles_source ON news.articles(source);
CREATE INDEX IF NOT EXISTS idx_news_articles_published ON news.articles(published_at);
CREATE INDEX IF NOT EXISTS idx_news_articles_category ON news.articles(category);
CREATE INDEX IF NOT EXISTS idx_news_articles_sentiment ON news.articles(sentiment_score);

-- News symbol mapping
CREATE TABLE IF NOT EXISTS news.symbol_news (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    article_id UUID NOT NULL REFERENCES news.articles(id) ON DELETE CASCADE,
    symbol_id UUID NOT NULL REFERENCES market_data.symbols(id) ON DELETE CASCADE,
    relevance_score DECIMAL(5, 4) NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_news_symbol_news_unique ON news.symbol_news(article_id, symbol_id);
CREATE INDEX IF NOT EXISTS idx_news_symbol_news_article ON news.symbol_news(article_id);
CREATE INDEX IF NOT EXISTS idx_news_symbol_news_symbol ON news.symbol_news(symbol_id);

-- ============================================
-- REPORTS SCHEMA - Report tables
-- ============================================

-- Reports
CREATE TABLE IF NOT EXISTS reports.reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    report_type VARCHAR(50) NOT NULL CHECK (report_type IN ('portfolio_performance', 'trade_history', 'tax_report', 'custom')),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    parameters JSONB NOT NULL DEFAULT '{}',
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'generating', 'completed', 'failed')),
    file_path VARCHAR(1000),
    file_size BIGINT,
    file_type VARCHAR(20) CHECK (file_type IN ('csv', 'excel', 'pdf', 'json')),
    generated_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_reports_reports_user ON reports.reports(user_id);
CREATE INDEX IF NOT EXISTS idx_reports_reports_type ON reports.reports(report_type);
CREATE INDEX IF NOT EXISTS idx_reports_reports_status ON reports.reports(status);

-- Scheduled reports
CREATE TABLE IF NOT EXISTS reports.scheduled_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    report_type VARCHAR(50) NOT NULL CHECK (report_type IN ('portfolio_performance', 'trade_history', 'tax_report')),
    frequency VARCHAR(20) NOT NULL CHECK (frequency IN ('daily', 'weekly', 'monthly', 'quarterly', 'yearly')),
    next_run_at TIMESTAMP WITH TIME ZONE NOT NULL,
    last_run_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    parameters JSONB NOT NULL DEFAULT '{}',
    email_recipients VARCHAR(255)[],
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_reports_scheduled_user ON reports.scheduled_reports(user_id);
CREATE INDEX IF NOT EXISTS idx_reports_scheduled_next_run ON reports.scheduled_reports(next_run_at);

-- ============================================
-- FUNCTIONS AND TRIGGERS
-- ============================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to all tables with updated_at column
-- (This would be applied to each table individually in a real implementation)

-- ============================================
-- COMMENTS
-- ============================================

COMMENT ON SCHEMA auth IS 'Authentication and user management tables';
COMMENT ON SCHEMA users IS 'User profiles and preferences tables';
COMMENT ON SCHEMA market_data IS 'Market data and symbols tables';
COMMENT ON SCHEMA watchlists IS 'User watchlists and symbols tables';
COMMENT ON SCHEMA portfolio IS 'Portfolio and holdings tables';
COMMENT ON SCHEMA trading IS 'Trading orders and trades tables';
COMMENT ON SCHEMA alerts IS 'Price alerts and notifications tables';
COMMENT ON SCHEMA notifications IS 'User notifications tables';
COMMENT ON SCHEMA news IS 'Market news and articles tables';
COMMENT ON SCHEMA reports IS 'Reports and exports tables';

-- ============================================
-- GRANTS (for production)
-- ============================================

-- In production, you would create specific roles and grant permissions
-- Example:
-- CREATE ROLE app_user;
-- GRANT CONNECT ON DATABASE stockapp TO app_user;
-- GRANT USAGE ON SCHEMA auth, users, market_data, watchlists, portfolio, trading, alerts, notifications, news, reports TO app_user;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA auth, users, market_data, watchlists, portfolio, trading, alerts, notifications, news, reports TO app_user;
-- GRANT USAGE ON ALL SEQUENCES IN SCHEMA auth, users, market_data, watchlists, portfolio, trading, alerts, notifications, news, reports TO app_user;

-- ============================================
-- INITIAL DATA (Optional)
-- ============================================

-- Insert initial admin user (password should be hashed in production)
-- INSERT INTO auth.users (id, username, email, hashed_password, full_name, role, status, email_verified)
-- VALUES ('123e4567-e89b-12d3-a456-426614174000', 'admin', 'admin@stockapp.com', '$2b$12$...', 'Admin User', 'admin', 'active', TRUE);

-- Insert market exchanges
-- INSERT INTO market_data.symbols (symbol, exchange, symbol_type, company_name, is_active)
-- VALUES ('NSE', 'NSE', 'index', 'NSE Index', TRUE);

-- ============================================
-- END OF INITIALIZATION SCRIPT
-- ============================================
