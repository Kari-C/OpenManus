import yfinance as yf
from typing import Optional, List, Dict, Any

from app.tool import BaseTool
from app.tool.base import CLIResult, ToolResult
from pydantic import Field

class YFinanceTool(BaseTool):
    """Tool for fetching stock and financial information using yfinance."""

    name: str = Field(
        default="yfinance",
        description="Name identifier for the YFinance tool"
    )

    description: str = Field(
        default="Fetch stock market data and financial information using Yahoo Finance.",
        description="Description of what the YFinance tool does"
    )

    async def execute(
        self,
        **kwargs
    ) -> ToolResult:
        """Execute financial data retrieval based on the specified action.

        Args:
            action: The action to perform ('price', 'info', 'history', 'search')
            ticker: Stock ticker symbol (e.g., AAPL, MSFT, GOOGL)
            period: Time period for historical data (e.g., 1d, 1mo, 1y)
            query: Search term for stock search
            limit: Maximum number of results for search

        Returns:
            ToolResult containing the requested financial information
        """
        try:
            # Extract parameters from kwargs
            action = kwargs.get('action')
            ticker = kwargs.get('ticker')
            period = kwargs.get('period', '1mo')
            query = kwargs.get('query')
            limit = kwargs.get('limit', 5)

            if not action:
                return ToolResult(
                    error="Missing required parameter: 'action'. Choose from: price, info, history, search"
                )

            if not ticker and action != 'search':
                return ToolResult(
                    error="Missing required parameter: 'ticker'"
                )

            if action == "price":
                result = self.get_stock_price(ticker)
            elif action == "info":
                result = self.get_company_info(ticker)
            elif action == "history":
                result = self.get_stock_history(ticker, period)
            elif action == "search":
                result = self.search_stocks(query or ticker, limit)
            else:
                return ToolResult(
                    error=f"Invalid action: {action}. Choose from: price, info, history, search"
                )

            if isinstance(result, str) and action in ["price", "info", "history", "search"]:
                result += "\n\n---\nFinancial data retrieval complete. If this was the only task, please call the terminate tool when you're done with all tasks."

            return ToolResult(output=result)
        except Exception as e:
            return ToolResult(error=f"Error executing YFinance tool: {str(e)}")

    def get_company_info(self, ticker: str) -> str:
        """Get company information for a ticker symbol.

        Args:
            ticker: Stock ticker symbol (e.g., AAPL, MSFT, GOOGL)

        Returns:
            String containing formatted company information
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            if not info:
                return f"Unable to fetch information for ticker: {ticker}"

            # Extract relevant info
            name = info.get('shortName', 'Unknown')
            sector = info.get('sector', 'Unknown')
            industry = info.get('industry', 'Unknown')
            summary = info.get('longBusinessSummary', 'No summary available')
            market_cap = info.get('marketCap', 'Unknown')
            if isinstance(market_cap, (int, float)):
                market_cap = f"${market_cap/1000000000:.2f}B"

            # Format the result
            result = f"Company Information for {name} ({ticker}):\n\n"
            result += f"Sector: {sector}\n"
            result += f"Industry: {industry}\n"
            result += f"Market Cap: {market_cap}\n\n"
            result += f"Business Summary:\n{summary}\n"

            return result
        except Exception as e:
            return f"Error fetching company info for {ticker}: {str(e)}"

    def get_stock_history(self, ticker: str, period: str = "1mo") -> str:
        """Get historical stock price data.

        Args:
            ticker: Stock ticker symbol
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)

        Returns:
            String containing summary of historical stock data
        """
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period)

            if hist.empty:
                return f"No historical data available for {ticker} over period {period}"

            # Get basic stats
            start_price = hist['Close'].iloc[0]
            end_price = hist['Close'].iloc[-1]
            change = end_price - start_price
            pct_change = (change / start_price) * 100
            high = hist['High'].max()
            low = hist['Low'].min()

            # Format the result
            result = f"Stock History for {ticker} (Period: {period}):\n\n"
            result += f"Start Price: ${start_price:.2f}\n"
            result += f"End Price: ${end_price:.2f}\n"
            result += f"Change: ${change:.2f} ({pct_change:.2f}%)\n"
            result += f"Highest Price: ${high:.2f}\n"
            result += f"Lowest Price: ${low:.2f}\n\n"

            # Include a sample of the data
            result += "Recent price data (last 5 days if available):\n"
            sample = hist.tail(5)
            for date, row in sample.iterrows():
                result += f"{date.date()}: Open ${row['Open']:.2f}, Close ${row['Close']:.2f}, Volume {int(row['Volume'])}\n"

            return result
        except Exception as e:
            return f"Error fetching stock history for {ticker}: {str(e)}"

    def search_stocks(self, query: str, limit: int = 5) -> str:
        """Search for stocks by name or ticker.

        Args:
            query: Search term (company name or partial ticker)
            limit: Maximum number of results to return

        Returns:
            String containing search results
        """
        try:
            ticker = yf.Ticker(query)
            info = ticker.info

            if not info or 'symbol' not in info:
                return f"No stocks found matching '{query}'"

            result = f"Search results for '{query}':\n\n"

            name = info.get('shortName', 'Unknown')
            symbol = info.get('symbol', query)
            sector = info.get('sector', 'Unknown')
            industry = info.get('industry', 'Unknown')

            result += f"{symbol}: {name}\n"
            result += f"  Sector: {sector}\n"
            result += f"  Industry: {industry}\n\n"

            return result
        except Exception as e:
            return f"Error searching for stocks: {str(e)}"

    def get_stock_price(self, ticker: str) -> str:
        """Get the current stock price for a given ticker symbol.

        Args:
            ticker: Stock ticker symbol (e.g., AAPL, MSFT, GOOGL)

        Returns:
            String containing the current stock price information
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            if not info:
                return f"Unable to fetch information for ticker: {ticker}"

            current_price = info.get('currentPrice', info.get('regularMarketPrice'))
            if not current_price:
                return f"Price information not available for {ticker}"

            company_name = info.get('shortName', ticker)
            currency = info.get('currency', 'USD')

            # Add more price information
            previous_close = info.get('previousClose', 'Unknown')
            open_price = info.get('open', 'Unknown')
            day_high = info.get('dayHigh', 'Unknown')
            day_low = info.get('dayLow', 'Unknown')

            result = f"{company_name} ({ticker}) current price: {current_price} {currency}\n"
            if previous_close != 'Unknown':
                change = current_price - previous_close
                pct_change = (change / previous_close) * 100
                result += f"Change: {change:.2f} ({pct_change:.2f}%)\n"

            result += f"Previous Close: {previous_close} {currency}\n"
            result += f"Open: {open_price} {currency}\n"
            result += f"Day Range: {day_low} - {day_high} {currency}"

            return result
        except Exception as e:
            return f"Error fetching stock price for {ticker}: {str(e)}"
