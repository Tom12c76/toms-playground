import streamlit as st
import base64
import os
from google import genai
from google.genai import types


def get_news_stream(api_key, ticker, perf_ticker, perf_index):
    client = genai.Client(
        api_key=api_key,
    )
    model = "gemini-2.0-flash"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=f"""Please analyze the news for {ticker} shares in order to understand the recent price performance.
The stock has returned approximately {perf_ticker:.1%} over the past year, 
compared to {perf_index:.1%} for the broader market.
Identify the key news events and factors that have contributed 
to this performance. Please source your answers when possible to the company or 
news outlets with some reference to the original news source. 
Focus on financial news and analysis. 
Please provide a concise summary of the key factors that have influenced the stock's performance. 
Include both positive and negative drivers."""),
            ],
        ),
    ]
    tools = [
        types.Tool(google_search=types.GoogleSearch()),
    ]
    generate_content_config = types.GenerateContentConfig(
        tools=tools,
        response_mime_type="text/plain",
        system_instruction=[
            types.Part.from_text(text="""You are an AI assistant specialized in financial news analysis. Your primary task is to analyze news articles, financial reports, and market data to identify the key factors that have contributed to a specific stock's performance over a defined period. You should prioritize information that directly explains the stock's upward or downward movements. You should always source the original news source when possible.

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
    *   Begin with the overall stock performance (e.g., \"+17% over the past year\").
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

You should now await a specific request for a stock and period to analyze."""),
        ],
    )

    def stream_chunks():
        for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config,
        ):
            yield chunk.text

    return stream_chunks()  # Return the generator instead of calling st.write_stream here


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
    
    if selected_ticker: # Ensure selected_ticker is not None before accessing tall
        perf_ticker = tall.loc[selected_ticker, 'cumret'].iloc[-1]
        perf_index = tall.loc['Portfolio', 'cumret'].iloc[-1]
    else:
        # Handle the case where no stock is selected or found, perhaps by disabling the button or showing a message
        perf_ticker = 0 # Default or placeholder
        perf_index = 0  # Default or placeholder


    if st.button("Fetch News"):
        if not api_key:
            st.error("Please enter your Gemini API key in the sidebar.")
        elif selected_ticker:
            with st.spinner(f"Fetching news for {selected_ticker}..."):
                st.subheader(f"News Summary for {selected_ticker}")
                stream = get_news_stream(
                    api_key="AIzaSyCLiVBiLWYKH04qVhd8Dj45mmNaG-s8Bzc",
                    ticker=selected_ticker, 
                    perf_ticker=perf_ticker, 
                    perf_index=perf_index
                )
                st.write_stream(stream)  # Now streaming is handled here
        else:
            st.error("Please select a stock first.")


if __name__ == "__main__":
    main()

