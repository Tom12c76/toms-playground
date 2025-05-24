import streamlit as st
import base64
import os
import google.generativeai as genai
from google.generativeai import types


def fetch_news_summary(api_key, ticker, perf_ticker, perf_index):
    try:
        genai.configure(api_key=api_key)
        
        model_name = "gemini-1.5-flash-latest" # Using a more recent model, ensure it supports the features you need.
                                         # "gemini-2.0-flash" might not be a valid public model name.
                                         # Check Google's documentation for available model names.

        # Prepare the prompt
        query = (
            f"Please analyze the news for {ticker} shares in order to understand the recent price performance. "
            f"The stock has returned approximately {perf_ticker:.1%} over the past year, "
            f"compared to {perf_index:.1%} for the broader market. "
            f"Identify the key news events and factors that have contributed "
            f"to this performance. Please source your answers when possible to the company or "
            f"news outlets with some reference to the original news source. "
            f"Focus on financial news and analysis. "
            f"Please provide a concise summary of the key factors that have influenced the stock's performance. "
            f"Include both positive and negative drivers. "
        )
        
        system_instruction_text = """
You are an AI assistant specialized in financial news analysis. Your primary task is to analyze news articles, financial reports, and market data to identify the key factors that have contributed to a specific stock's performance over a defined period. You should prioritize information that directly explains the stock's upward or downward movements. You should always source the original news source when possible.

**Your Core Function:**

1.  **Data Retrieval:** Access and process relevant news articles, press releases, SEC filings (10-K, 10-Q, 8-K), analyst reports, and financial data related to the specified stock over the given time frame. Use search queries that emphasize financial news and analysis.

2.  **Causal Analysis:** Identify specific events, announcements, or trends that likely influenced the stock's price. Focus on factors such as:
    *   Earnings reports (beats, misses, guidance).
    *   Product launches and innovations.
    *   Mergers, acquisitions, and divestitures.
    *   Management changes.
    *   Industry trends and competitive landscape.
    *   Macroeconomic factors.
    *   Analyst ratings and price target changes.
    *   Any other company-specific events.

3.  **Justification Assessment:** Quantify the impact of each factor (if possible) on the stock price. Prioritize factors that can logically explain the magnitude and direction of the stock's performance.

4.  **Summary Generation:** Produce a concise and well-structured summary that explains the stock's performance based on the identified causal factors. The summary should:
    *   Begin with the overall stock performance (e.g., "+17% over the past year").
    *   Highlight the key positive drivers (with specific examples from the news).
    *   Acknowledge any counteracting factors or headwinds.
    *   Cite the news source for each piece of information.
    *   Prioritize primary sources (e.g., company press releases, SEC filings) over secondary sources (news articles).

5.  **Prioritize Financial Reporting:** Financial and Business articles should be prioritized to give you the context for the information required.

**Important Considerations:**

*   **Time Period:** Strictly adhere to the specified time period.
*   **Accuracy:** Verify information from multiple reputable sources.
*   **Objectivity:** Present the information in a neutral and unbiased manner.
*   **Relevance:** Focus on information that is directly relevant to the stock's performance.
*   **Conciseness:** Keep the summary concise and easy to understand.

You should now await a specific request for a stock and period to analyze.
"""
        
        generation_config = types.GenerationConfig( # Use types.GenerationConfig
            temperature=1,
            top_p=0.95,
            top_k=40,
            max_output_tokens=8192,
            response_mime_type="text/plain", # response_mime_type is part of GenerationConfig
        )
        
        tools = [types.Tool(google_search_retrieval=types.GoogleSearchRetrieval())]

        model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=generation_config,
            system_instruction=system_instruction_text, # Pass system instruction text directly
            tools=tools
        )
        
        contents = [
            types.Content( # This structure for contents is generally for chat history. For a single query, just the query text might be enough.
                role="user", # Or simply pass the query string to generate_content
                parts=[types.Part.from_text(text=query)],
            ),
        ]
        
        # For non-chat, you can often pass the query directly or a list of parts
        response = model.generate_content(query) # Simpler call for single-turn query

        return response.text
    except Exception as e:
        return f"Error generating news summary: {str(e)}\n\nPlease check your API key and try again."


def main():
    st.title("News Summaries")
    
    # Get ptf and tall from session state
    if 'ptf' in st.session_state:
        ptf = st.session_state.ptf
    else:
        st.warning("No portfolio data found in session state. Please go back and load your portfolio first.")
        return
    
    if 'tall' in st.session_state:
        tall = st.session_state.tall
    else:
        st.warning("No calculated data found in session state. Please go back and calculate portfolio data first.")
        return
    
    # Add API key input to sidebar
    with st.sidebar:
        st.subheader("Gemini API Key")
        api_key = st.text_input("Enter your Gemini API Key", type="password")
        st.info("Your API key is required to fetch news summaries using Google's Gemini model.")
    
    st.subheader("Financial News Summarization")
    st.info("AIzaSyCLiVBiLWYKH04qVhd8Dj45mmNaG-s8Bzc")
    st.write("""
    This tool allows you to summarize financial news articles for stocks in your portfolio.
    Select an industry group and a stock to get concise summaries of key financial information.
    """)
    
    # Get all available sectors from the portfolio data
    available_sectors = sorted(ptf['Sector'].unique().tolist())
    
    # Create a dropdown to select the industry group (sector)
    selected_sector = st.selectbox("Select Industry Group", available_sectors)
    
    # Filter tickers by selected sector
    filtered_ptf = ptf[ptf['Sector'] == selected_sector]
    
    # Create a dropdown to select a stock from the filtered list
    ticker_options = [(row['Ticker'], f"{row['Ticker']} - {row['Name']}") for _, row in filtered_ptf.iterrows()]
    ticker_display = [t[1] for t in ticker_options]
    selected_display = st.selectbox("Select Stock", ticker_display)
    
    # Get the selected ticker code
    selected_ticker = None
    for t, display in ticker_options:
        if display == selected_display:
            selected_ticker = t
            break
    
    perf_ticker = tall.loc[selected_ticker, 'cumret'].iloc[-1]
    perf_index = tall.loc['Portfolio', 'cumret'].iloc[-1]

    if st.button("Fetch News"):
        if not api_key:
            st.error("Please enter your Gemini API key in the sidebar.")
        elif selected_ticker:
            with st.spinner(f"Fetching news for {selected_ticker}..."):
                news_summary = fetch_news_summary(api_key, selected_ticker, perf_ticker, perf_index)
                st.subheader(f"News Summary for {selected_ticker}")
                st.markdown(news_summary)
        else:
            st.error("Please select a stock first.")


if __name__ == "__main__":
    main()