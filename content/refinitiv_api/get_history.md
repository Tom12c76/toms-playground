# Product Requirements Document: Equity Price and Dividend History Viewer

**Author:** GitHub Copilot
**Date:** September 21, 2025
**Status:** Draft

## 1. Overview

This document outlines the requirements for a web-based application that serves as an educational tutorial and a repository of best practices. The application will demonstrate how to download historical prices and dividends for equities using the Refinitiv Data (RD) API. Furthermore, it will provide the foundation for users to learn how to calculate performance for both single stocks and portfolios of stocks. The primary mission is to be an explainer with descriptive text, code snippets, and clear visualizations of the results.

## 2. Educational Goals

Beyond its functional requirements, the application must serve as a learning tool.

- **Best Practices:** Demonstrate the correct and most efficient ways to query time-series and event-based data (prices vs. dividends) from the Refinitiv API.
- **Data Handling:** Showcase common data manipulation techniques using the `pandas` library, such as normalization, pivoting, and aligning datasets.
- **Financial Concepts:** Implicitly teach concepts like price performance normalization and the importance of aligning dividend data with price data.
- **Reproducibility:** Provide dynamically generated code snippets that allow users to reproduce the application's functionality in their own development environments, reinforcing their learning.

## 3. User Interface (UI) and Flow

The application will have a clean, intuitive interface built with Streamlit. The main components are as follows:

### 3.1. Title
- The application will display the main title: **"Equity Price and Dividend History"**.

### 3.2. Credentials Loading
- **Requirement:** The application must securely load an API key for the Refinitiv service.
- **Success:** On successful loading, a confirmation message "✅ Refinitiv credentials loaded" will be displayed.
- **Failure:** If credentials are not found, an error message "❌ Missing Refinitiv credential: [Error Details]" will be shown, and the application will halt.

### 3.3. Configuration Panel
- A section titled **"Configuration"** will allow users to set the parameters for their data query. It will be organized into two columns.

#### Column 1:
- **Instrument Selection:**
    - A multi-select dropdown labeled **"Instrument RICs"**.
    - Users can select one or more equities.
    - Default selection: `MSFT.O`, `ROG.S`, `VOD.L`.
- **Start Date:**
    - A date input labeled **"Start Date"**.
    - Default value: One year prior to the current date.

#### Column 2:
- **Currency:**
    - A read-only text field labeled **"Currency"**.
    - The value will be fixed to **"EUR"**.
- **End Date:**
    - A date input labeled **"End Date"**.
    - Default value: The current date.

### 3.4. Action Button
- A primary button labeled **"Fetch Equity Data"** will trigger the data retrieval process.
- **Validation:** If no instruments are selected when the button is clicked, a warning "Please select at least one instrument" will be displayed, and no API call will be made.

## 4. Data Fetching and Display

Upon clicking the "Fetch Equity Data" button, the following will occur:

### 4.1. Price History
- **API Call:** The application will fetch daily closing prices (`TR.PriceClose`) for the selected instruments and date range.
- **Data Normalization:** Prices will be normalized to a base of 100 as of the start date to allow for easy performance comparison.
- **Visualization:**
    - A line chart titled **"Normalized Price Performance (Rebased to 100)"** will display the performance of each selected instrument.
    - The chart will be interactive (hover-to-see-values).
- **Raw Data:** An expandable section labeled **"View Raw Price Data"** will contain a table of the raw, non-normalized price data.

### 4.2. Dividend History
- **API Call:** The application will fetch dividend ex-dates (`TR.DivExDate`) and gross dividend amounts (`TR.DivUnadjustedGross`) for the selected instruments.
- **Data Processing:**
    - The raw dividend data will be cleaned and pivoted.
    - The final table will be indexed by date, with columns for each instrument, showing the dividend amount paid on a given day.
    - Dates with no dividend payments will show a value of `0`.
- **Display:** The processed and aligned dividend data will be displayed in a data table.

## 5. Static Content

### 5.1. Documentation Section
- A section titled **"Documentation"** will explain the application's functionality, including the specific Refinitiv fields being used.
- It will also provide a list of example tickers and their corresponding company names.

### 5.2. Sample Code Section
- A section titled **"Sample Code"** will display a Python code snippet.
- This snippet will be dynamically generated based on the user's current selections (instruments, dates) to demonstrate how to perform the same API query programmatically.
