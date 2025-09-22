import streamlit as st
import pandas as pd
import time
import requests
from typing import Dict, List
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
try:
    from streamlit_secrets_helper import get_google_api_key, check_secrets_status, display_secrets_help
except ImportError:
    st.warning("⚠️ streamlit_secrets_helper not found. Some features may be limited.")
    
    def get_google_api_key():
        return None
    
    def check_secrets_status():
        return {}
    
    def display_secrets_help():
        pass

# Google Gemini AI imports
# To install: pip install google-genai
from google import genai
from google.genai import types

def get_fund_data():
    """Returns the list of funds with their ISIN codes and optional URLs."""
    return [
        {
            "name": "MSIF Global Brands Fund A USD Acc", 
            "isin": "LU0119620416",
            "urls": [
                "https://www.morganstanley.com/im/publication/insights/investment-insights/ii_globalbrandsfund_us.pdf",
                "https://www.morningstar.com/funds/xlis/msif00000g/quote"
            ]
        },
        {
            "name": "M&G (Lux) European Strategic Value EUR A Acc", 
            "isin": "LU1670707527",
            "urls": [
                "https://www.mandg.com/funds/m-and-g-lux-european-strategic-value-fund"
            ]
        },
        {
            "name": "Fidelity Funds - Global Technology A-ACC-EUR", 
            "isin": "LU1213836080",
            "urls": [
                "https://www.fidelity.lu/funds/factsheet/LU1213836080"
            ]
        },
        {"name": "Nordea 1 - Global Climate and Environment BP EUR", "isin": "LU0348926287", "urls": []},
        {"name": "DWS Invest CROCI Japan JPY LC", "isin": "LU1769942159", "urls": []},
        {"name": "Allianz Thematica A (EUR)", "isin": "LU1479563717", "urls": []},
        {"name": "Capital Group New Perspective (LUX) Bh-EUR", "isin": "LU1295552621", "urls": []},
        {"name": "Janus Henderson Horizon Gl Tech Ldrs A2 EUR", "isin": "LU0572952280", "urls": []},
        {"name": "DWS Invest Global Infrastructure LC", "isin": "LU0329760770", "urls": []},
        {"name": "SPDR FTSE UK All Share UCITS ETF Acc", "isin": "IE00B7452L46", "urls": []}
    ]

def fetch_url_content(url: str) -> str:
    """
    Fetches content from a given URL for fund analysis.
    This is a custom tool that can be used by the AI.
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text[:5000]  # Limit to first 5000 characters
    except Exception as e:
        return f"Error fetching URL {url}: {str(e)}"

def create_url_fetcher_function():
    """Creates a function declaration for URL fetching tool."""
    return types.FunctionDeclaration(
        name="fetch_url_content",
        description="Fetches content from a given URL to analyze fund information from official sources",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "url": types.Schema(
                    type=types.Type.STRING,
                    description="The URL to fetch content from (e.g., fund factsheets, official documents)"
                )
            },
            required=["url"]
        )
    )

def create_fund_analysis_prompt(fund_name: str, isin: str, urls: List[str] = None) -> str:
    """Creates a detailed prompt for Gemini to analyze a UCITS fund."""
    
    url_section = ""
    if urls and len(urls) > 0:
        url_section = f"""
**Specific URLs to analyze (use the fetch_url_content tool):**
{chr(10).join([f"- {url}" for url in urls])}
"""
    else:
        url_section = f"""
**Suggested URLs to analyze (use the fetch_url_content tool):**
- Fund factsheet: Search for official factsheet or KIID document
- Morningstar page: https://www.morningstar.com (search for ISIN: {isin})
- Fund manager website: Search for official fund page
- Regulatory filings: Look for official prospectus or annual reports
"""
    
    prompt = f"""
Please provide a comprehensive analysis of the following UCITS investment fund:

Fund Name: {fund_name}
ISIN: {isin}

{url_section}

Please structure your response as a detailed fund profile including the following sections:

1. **Fund Overview**
   - Full official fund name and fund family/manager
   - Fund domicile and regulatory framework
   - Launch date and fund size (if available)

2. **Investment Objective & Strategy**
   - Primary investment objective
   - Investment strategy and approach
   - Geographic focus and sector allocation
   - Benchmark (if applicable)

3. **Asset Class & Investment Style**
   - Primary asset class (equity, fixed income, multi-asset, etc.)
   - Investment style (growth, value, blend, thematic, etc.)
   - Market capitalization focus (large, mid, small cap)
   - Investment approach (active vs passive)

4. **Portfolio Characteristics**
   - Typical number of holdings
   - Top geographical exposures
   - Sector weightings (if equity fund)
   - Currency exposure

5. **Risk Profile**
   - Risk rating/category
   - Volatility characteristics
   - Key risk factors
   - Suitable investor profile

6. **Fees & Expenses**
   - Management fee/TER (Total Expense Ratio)
   - Performance fee (if applicable)
   - Minimum investment amounts

7. **Notable Features**
   - Any unique characteristics or themes
   - ESG considerations (if applicable)
   - Distribution policy
   - Fund manager background

Please provide factual, up-to-date information and clearly indicate if any specific data is not readily available. Focus on providing actionable insights for potential investors.
"""
    return prompt

def call_gemini_api(fund_name: str, isin: str, api_key: str, model: str = "gemini-2.0-flash", enabled_tools: List[str] = None, urls: List[str] = None) -> str:
    """
    Calls Google Gemini API to analyze a UCITS fund.
    
    Args:
        fund_name: Name of the fund
        isin: ISIN code of the fund
        api_key: Google Gemini API key
        model: Model to use for analysis
        enabled_tools: List of enabled tools (Google Search, Code Execution, URL Fetcher)
        urls: List of specific URLs to analyze
    """
    if enabled_tools is None:
        enabled_tools = ["Google Search"]
        
    try:
        client = genai.Client(api_key=api_key)
        
        prompt = create_fund_analysis_prompt(fund_name, isin, urls)
        
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=prompt),
                ],
            ),
        ]
        
        # Build tools list based on user selection
        tools = []
        if "Google Search" in enabled_tools:
            tools.append(types.Tool(google_search=types.GoogleSearch()))
        if "Code Execution" in enabled_tools:
            tools.append(types.Tool(code_execution=types.CodeExecution()))
        if "URL Fetcher" in enabled_tools:
            tools.append(types.Tool(function_declarations=[create_url_fetcher_function()]))
        
        generate_content_config = types.GenerateContentConfig(
            tools=tools,
            response_mime_type="text/plain",
            system_instruction=[
                types.Part.from_text(text="""You are an AI assistant specialized in investment fund analysis. Your primary task is to analyze UCITS investment funds based on their name and ISIN code. You should provide comprehensive, factual information about fund characteristics, investment strategy, risk profile, and other relevant details.

**Your Core Function:**

1. **Data Retrieval:** Access and process relevant information about the specified UCITS fund, including:
   - Official fund documentation (prospectus, KIID)
   - Fund manager information and track record
   - Historical performance data
   - Portfolio composition and holdings
   - Fee structure and expenses
   - Risk ratings and classifications

2. **Fund Analysis:** Provide detailed analysis covering:
   - Investment objective and strategy
   - Asset class and geographic focus
   - Investment style (growth, value, thematic, etc.)
   - Portfolio characteristics and typical holdings
   - Risk profile and volatility measures
   - Fee structure and costs
   - ESG considerations if applicable

3. **Structured Response:** Format your response with clear sections:
   - Fund Overview
   - Investment Objective & Strategy  
   - Asset Class & Investment Style
   - Portfolio Characteristics
   - Risk Profile
   - Fees & Expenses
   - Notable Features

4. **Accuracy and Sources:** 
   - Prioritize official fund documents and regulatory filings
   - Cite sources when possible
   - Clearly indicate when specific data is not available
   - Focus on factual, objective information

5. **Investment Focus:** Provide actionable insights for potential investors, including:
   - Suitable investor profile
   - Investment horizon recommendations
   - Key differentiating factors
   - Competitive positioning

You should provide comprehensive, professional analysis suitable for investment decision-making."""),
            ],
        )
        
        response = client.models.generate_content(
            model=model,
            contents=contents,
            config=generate_content_config,
        )
        
        return response.text
        
    except Exception as e:
        return f"Error analyzing fund: {str(e)}"

def simulate_gemini_response(fund_name: str, isin: str) -> str:
    """
    Simulates a Gemini API response for demo purposes.
    In production, this would make an actual API call to Gemini.
    """
    # This is a demo response - in reality you'd call the Gemini API
    demo_responses = {
        "LU0119620416": """
**Fund Overview**
MSIF Global Brands Fund A USD Acc is managed by Morgan Stanley Investment Management and domiciled in Luxembourg. Launched in 2000, this UCITS fund focuses on investing in companies with strong global brand franchises with approximately $2.5 billion in assets under management.

**Investment Objective & Strategy**
The fund seeks long-term capital appreciation by investing in equity securities of companies worldwide that own, license, or operate strong global brands. The strategy focuses on companies with sustainable competitive advantages through brand recognition, pricing power, and customer loyalty. The fund manager employs a bottom-up stock selection approach, targeting companies with strong intangible assets.

**Asset Class & Investment Style**
- Primary Asset Class: Global Equities
- Investment Style: Quality Growth with Brand Focus
- Market Cap Focus: Large-cap bias (80%+) with selective mid-cap exposure
- Investment Approach: Active management with concentrated, high-conviction portfolio

**Portfolio Characteristics**
- Typically holds 40-60 positions across various sectors
- Geographic Exposure: US (65-75%), Europe (15-20%), Asia-Pacific (10-15%)
- Sector Focus: Consumer Discretionary (30%), Technology (25%), Consumer Staples (20%)
- Currency: USD base currency with global exposure creating currency risk

**Risk Profile**
- SRRI Risk Category: 6 out of 7 (High Risk)
- Suitable for investors with 5+ year investment horizon and high risk tolerance
- Key Risks: Market volatility, currency fluctuations, concentration risk, brand value erosion
- Historical volatility: 15-18% annually

**Fees & Expenses**
- Total Expense Ratio (TER): 1.50% annually
- No performance fees
- Minimum Investment: USD 1,000 for A-class shares

**Notable Features**
- Focus on companies with strong intangible assets and brand equity
- Quality-focused approach emphasizing sustainable competitive moats
- ESG integration with focus on responsible business practices
- Experienced portfolio management team with 15+ years average experience
""",
        "LU1670707527": """
**Fund Overview**
M&G (Lux) European Strategic Value EUR A Acc is managed by M&G Investments and domiciled in Luxembourg. This UCITS fund employs a contrarian value investment approach focused on European equities, with approximately €800 million in assets under management.

**Investment Objective & Strategy**
The fund aims to provide long-term capital growth by investing in undervalued European companies. Uses a contrarian approach to identify out-of-favor securities with strong fundamentals trading below intrinsic value. The strategy focuses on companies undergoing positive transformation or temporary setbacks.

**Asset Class & Investment Style**
- Primary Asset Class: European Equities
- Investment Style: Deep Value/Contrarian with Catalyst Focus
- Market Cap Focus: All-cap approach with large and mid-cap emphasis (70%+)
- Investment Approach: High conviction active management with fundamental analysis

**Portfolio Characteristics**
- Concentrated portfolio of 30-50 holdings
- Geographic Exposure: UK (35-45%), Germany (15-20%), France (12-18%), Other Europe (20-30%)
- Sector Allocation: Financials (25%), Industrials (20%), Consumer sectors (15%)
- Currency: EUR base with some currency hedging for non-EUR positions

**Risk Profile**
- SRRI Risk Category: 6 out of 7 (High Risk)
- Suitable for contrarian investors with long-term horizon (7+ years)
- Key Risks: Value trap risk, regional concentration, style risk, market timing sensitivity
- Higher volatility due to contrarian positioning

**Fees & Expenses**
- Total Expense Ratio (TER): 1.75% annually
- No performance fees
- Minimum Investment: EUR 500

**Notable Features**
- Contrarian investment philosophy focusing on unloved sectors/stocks
- Focus on companies with catalyst potential for positive change
- Strong ESG integration with stewardship engagement
- Experienced value-focused management team with proven track record
- Regular engagement with company management teams
""",
        "LU1213836080": """
**Fund Overview**
Fidelity Funds - Global Technology A-ACC-EUR is managed by Fidelity International and domiciled in Luxembourg. This UCITS fund focuses on global technology companies across all market capitalizations, with approximately $1.8 billion in assets under management.

**Investment Objective & Strategy**
The fund seeks long-term capital growth by investing primarily in equity securities of technology companies worldwide. Strategy focuses on companies that develop, advance, or use technology to gain competitive advantage. Includes both established technology leaders and emerging disruptive companies.

**Asset Class & Investment Style**
- Primary Asset Class: Global Technology Equities
- Investment Style: Growth-oriented with Innovation Focus
- Market Cap Focus: All-cap with large-cap bias (60%) and significant mid/small-cap exposure
- Investment Approach: Active bottom-up stock selection with sector expertise

**Portfolio Characteristics**
- Typically holds 80-120 positions for diversification within tech sector
- Geographic Exposure: US (70-80%), Asia (10-15%), Europe (8-12%)
- Sub-sector Focus: Software (35%), Semiconductors (25%), Internet/E-commerce (20%)
- Currency: EUR-denominated share class with global underlying exposure

**Risk Profile**
- SRRI Risk Category: 6 out of 7 (High Risk)
- Suitable for growth-oriented investors with 5+ year horizon
- Key Risks: Technology sector volatility, growth stock risk, currency risk, concentration risk
- High beta exposure to technology cycles

**Fees & Expenses**
- Total Expense Ratio (TER): 1.50% annually
- No performance fees
- Minimum Investment: EUR 2,500

**Notable Features**
- Specialist technology sector expertise with dedicated research team
- Access to global technology innovation and disruption themes
- Regular engagement with company management and industry experts
- ESG integration with focus on technology's societal impact
- Flexible approach across technology sub-sectors and market caps
"""
    }
    
    return demo_responses.get(isin, f"""
**Fund Profile for {fund_name}**

*Note: This is a demo response. In production, this would contain detailed analysis from Google Gemini AI.*

**Fund Overview**
{fund_name} (ISIN: {isin}) is a UCITS-compliant investment fund. Based on the fund name analysis, this appears to focus on [specific strategy/region/theme based on name].

**Investment Objective & Strategy**
Analysis of the fund name suggests a [sector/geographic/thematic] focused strategy targeting [specific investment universe]. The fund likely employs [active/passive] management approach.

**Asset Class & Investment Style**
- Primary Asset Class: [To be determined by AI analysis]
- Investment Style: [To be determined by AI analysis]  
- Geographic Focus: [Based on fund name analysis]
- Market Cap Focus: [To be analyzed]

**Portfolio Characteristics**
- Portfolio composition to be analyzed by Gemini AI
- Geographic and sector allocations
- Currency exposure details

**Risk Profile**
- Risk category and volatility measures would be provided by Gemini AI
- Detailed risk factor analysis
- Suitable investor profile assessment

**Fees & Expenses**
- Fee structure research and analysis
- Total expense ratio details
- Minimum investment requirements

**Notable Features**
- Unique investment characteristics and themes
- ESG considerations if applicable
- Fund manager expertise and track record
- Competitive positioning analysis

*For complete analysis, connect with Google Gemini API*
""")

def display_fund_profile(fund_info: Dict, profile: str):
    """Displays a fund profile in a nice formatted way."""
    st.subheader(f"📊 {fund_info['name']}")
    
    # Display basic info in columns
    col1, col2 = st.columns(2)
    with col1:
        st.metric("ISIN Code", fund_info['isin'])
    with col2:
        st.metric("Analysis Status", "✅ Complete")
    
    # Display the profile
    st.markdown("---")
    st.markdown(profile)
    st.markdown("---")

def main():
    st.title("🤖 AI Fund Profile Generator")
    st.markdown("### *Powered by Google Gemini AI*")
    
    st.info("""
    This tool uses Google Gemini AI to generate comprehensive profiles of UCITS investment funds 
    based on their name and ISIN code. The AI analyzes publicly available information to provide 
    detailed insights about fund characteristics, strategy, risk profile, and more.
    """)
    
    # Get fund data
    funds = get_fund_data()
    
    # Display fund list
    st.header("📋 Fund Universe")
    fund_df = pd.DataFrame(funds)
    st.dataframe(fund_df, use_container_width=True)
    
    # Analysis options
    st.header("🔍 Analysis Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        analysis_mode = st.radio(
            "Select Analysis Mode:",
            options=["Single Fund", "Batch Analysis", "Compare Funds"],
            help="Choose how you want to analyze the funds"
        )
    
    with col2:
        if analysis_mode == "Single Fund":
            selected_fund = st.selectbox(
                "Select Fund to Analyze:",
                options=range(len(funds)),
                format_func=lambda x: funds[x]['name']
            )
        elif analysis_mode == "Compare Funds":
            selected_funds = st.multiselect(
                "Select Funds to Compare (max 3):",
                options=range(len(funds)),
                format_func=lambda x: funds[x]['name'],
                max_selections=3
            )
    
    # API Configuration
    st.header("⚙️ Configuration")
    
    with st.expander("API Settings", expanded=False):
        st.markdown("### 🔑 Getting your Google Gemini API Key")
        st.markdown("""
        1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
        2. Sign in with your Google account
        3. Click "Create API Key"
        4. Copy the API key and paste it below **OR** add it to `.streamlit/secrets.toml`
        
        **Note**: Google Gemini offers free tier usage with rate limits.
        """)
        
        # Try to get API key from secrets first, then allow manual input
        secrets_api_key = get_google_api_key()
        
        if secrets_api_key:
            st.success("✅ Google API key loaded from secrets.toml")
            api_key = secrets_api_key
        else:
            api_key = st.text_input(
                "Google Gemini API Key",
                type="password",
                help="Enter your Google Gemini API key for live analysis, or configure in .streamlit/secrets.toml",
                placeholder="AIzaSy... (or configure in secrets.toml)"
            )
            
            if not api_key:
                st.info("💡 **Tip**: Configure your API key in `.streamlit/secrets.toml` for automatic loading.")
        
        model_choice = st.selectbox(
            "Model Selection",
            options=[
                "gemini-2.0-flash",
                "gemini-1.5-pro", 
                "gemini-1.5-flash"
            ],
            index=0,
            help="Choose the Google Gemini model for analysis"
        )
        
        st.markdown("### 🛠️ Tool Configuration")
        tool_options = st.multiselect(
            "Select Tools for AI Analysis",
            options=[
                "Google Search",
                "Code Execution",
                "URL Fetcher"
            ],
            default=["Google Search"],
            help="Choose which tools the AI can use during analysis"
        )
        
        use_demo = st.checkbox(
            "Use Demo Mode", 
            value=True,
            help="Enable demo mode with sample responses (disable for live API calls)"
        )
        
        st.markdown("### 🔗 Custom URLs")
        custom_urls = st.text_area(
            "Additional URLs to analyze (one per line)",
            placeholder="https://example.com/fund-factsheet.pdf\nhttps://morningstar.com/funds/...\nhttps://fundmanager.com/documents/...",
            help="Enter specific URLs you want the AI to fetch and analyze. One URL per line.",
            height=100
        )
        
        # Display secrets status
        st.markdown("### 🔐 Secrets Status")
        status = check_secrets_status()
        
        if status.get('google_gemini', False):
            st.write("✅ Google Gemini API")
        else:
            st.write("❌ Google Gemini API (not configured)")
            
        if status.get('refinitiv_data', False):
            st.write("✅ Refinitiv Data API")
        else:
            st.write("❌ Refinitiv Data API (not configured)")
            
        if status.get('refinitiv_rdp', False):
            st.write("✅ Refinitiv RDP API")
        else:
            st.write("❌ Refinitiv RDP API (not configured)")
        
        # Help section
        if st.button("📖 Show Secrets Configuration Help"):
            display_secrets_help()
    
    # Analysis execution
    if analysis_mode == "Single Fund":
        st.header("🔬 Fund Analysis")
        
        if st.button("Generate Fund Profile", type="primary"):
            fund_info = funds[selected_fund]
            
            # Combine fund URLs with custom URLs
            fund_urls = fund_info.get('urls', [])
            if custom_urls.strip():
                additional_urls = [url.strip() for url in custom_urls.strip().split('\n') if url.strip()]
                fund_urls.extend(additional_urls)
            
            with st.spinner(f"Analyzing {fund_info['name']}..."):
                if use_demo:
                    # Demo mode
                    time.sleep(2)  # Simulate API delay
                    profile = simulate_gemini_response(fund_info['name'], fund_info['isin'])
                else:
                    # Live API mode
                    if not api_key:
                        st.error("Please provide a Google Gemini API key for live analysis.")
                        return
                    
                    try:
                        profile = call_gemini_api(fund_info['name'], fund_info['isin'], api_key, model_choice, tool_options)
                    except Exception as e:
                        st.error(f"Error calling Gemini API: {str(e)}")
                        return
                
                display_fund_profile(fund_info, profile)
    
    elif analysis_mode == "Batch Analysis":
        st.header("📊 Batch Analysis")
        
        num_funds = st.slider(
            "Number of funds to analyze:",
            min_value=1,
            max_value=len(funds),
            value=3,
            help="Select how many funds to analyze in batch"
        )
        
        if st.button("Run Batch Analysis", type="primary"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i in range(num_funds):
                fund_info = funds[i]
                
                status_text.text(f"Analyzing {fund_info['name']}...")
                progress_bar.progress((i + 1) / num_funds)
                
                if use_demo:
                    time.sleep(1)  # Simulate API delay
                    profile = simulate_gemini_response(fund_info['name'], fund_info['isin'])
                else:
                    if not api_key:
                        st.error("Please provide a Google Gemini API key for live analysis.")
                        break
                    try:
                        profile = call_gemini_api(fund_info['name'], fund_info['isin'], api_key, model_choice, tool_options)
                    except Exception as e:
                        st.error(f"Error calling Gemini API: {str(e)}")
                        break
                
                display_fund_profile(fund_info, profile)
            
            status_text.text("✅ Batch analysis complete!")
    
    elif analysis_mode == "Compare Funds":
        st.header("⚖️ Fund Comparison")
        
        if not 'selected_funds' in locals() or len(selected_funds) < 2:
            st.warning("Please select at least 2 funds for comparison.")
        else:
            if st.button("Compare Selected Funds", type="primary"):
                comparison_data = []
                
                for idx in selected_funds:
                    fund_info = funds[idx]
                    
                    with st.spinner(f"Analyzing {fund_info['name']}..."):
                        if use_demo:
                            time.sleep(1)
                            profile = simulate_gemini_response(fund_info['name'], fund_info['isin'])
                        else:
                            if not api_key:
                                st.error("Please provide a Google Gemini API key for live analysis.")
                                break
                            try:
                                fund_urls = fund_info.get('urls', [])
                                profile = call_gemini_api(fund_info['name'], fund_info['isin'], api_key, model_choice, tool_options, fund_urls)
                            except Exception as e:
                                st.error(f"Error calling Gemini API: {str(e)}")
                                break
                        
                        comparison_data.append({
                            'fund': fund_info,
                            'profile': profile
                        })
                
                # Display comparison
                st.subheader("📋 Fund Comparison Results")
                
                for i, data in enumerate(comparison_data):
                    with st.container():
                        display_fund_profile(data['fund'], data['profile'])
                        if i < len(comparison_data) - 1:
                            st.markdown("---")
    
    # Sample prompt section
    st.header("📝 Sample Prompt")
    
    with st.expander("View Sample Prompt Structure", expanded=False):
        sample_fund = funds[0]
        sample_prompt = create_fund_analysis_prompt(sample_fund['name'], sample_fund['isin'])
        st.code(sample_prompt, language="text")
    
    # Technical details
    st.header("🔧 Technical Implementation")
    
    with st.expander("Implementation Details", expanded=False):
        st.markdown("""
        ### How it works:
        
        1. **Prompt Engineering**: Carefully crafted prompts ensure comprehensive analysis
        2. **Google Gemini Integration**: Uses Google's Gemini models with multiple tool capabilities
        3. **Tool Selection**: Users can enable/disable different AI tools:
           - **Google Search**: Web search for current fund information
           - **Code Execution**: Run calculations and data analysis
           - **URL Fetcher**: Fetch content from specific URLs (factsheets, etc.)
        4. **Structured Output**: Responses follow a consistent format for easy comparison
        5. **Error Handling**: Robust error handling for API failures or rate limits
        
        ### Available Tools:
        
        **🔍 Google Search Tool**
        - Searches the web for fund information
        - Accesses current market data and news
        - Finds official fund documents
        
        **💻 Code Execution Tool**
        - Performs calculations and data analysis
        - Processes numerical data
        - Creates charts or visualizations
        
        **🌐 URL Fetcher Tool**
        - Fetches content from specific URLs
        - Accesses fund factsheets and prospectuses
        - Retrieves official regulatory filings
        
        ### API Integration:
        
        ```python
        from google import genai
        from google.genai import types
        
        def call_gemini_api(fund_name, isin, api_key, enabled_tools):
            client = genai.Client(api_key=api_key)
            
            # Configure tools based on user selection
            tools = []
            if "Google Search" in enabled_tools:
                tools.append(types.Tool(google_search=types.GoogleSearch()))
            if "Code Execution" in enabled_tools:
                tools.append(types.Tool(code_execution=types.CodeExecution()))
            if "URL Fetcher" in enabled_tools:
                tools.append(types.Tool(function_declarations=[url_fetcher_function]))
            
            response = client.models.generate_content(
                model=model,
                contents=contents,
                config=types.GenerateContentConfig(tools=tools),
            )
            
            return response.text
        ```
        
        ### Features:
        - ✅ Single fund analysis
        - ✅ Batch processing
        - ✅ Fund comparison
        - ✅ Demo mode
        - ✅ Configurable models
        - ✅ Multiple AI tools
        - ✅ Progress tracking
        - ✅ Error handling
        - ✅ Custom URL fetching
        """)
    
    # Footer
    st.markdown("---")
    st.markdown("*Powered by Google Gemini AI • Built with Streamlit*")

if __name__ == "__main__":
    main()
