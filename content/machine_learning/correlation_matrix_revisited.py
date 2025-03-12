import streamlit as st
import seaborn as sns
import scipy
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

def main():
    st.title("Correlation Matrix Revisited")
    st.write("This is the content of the Correlation Matrix Revisited page.")

    # Error control for session state access
    if 'ptf' in st.session_state:
        # Retrieve the ptf dataframe from the session state
        ptf = st.session_state.ptf
        # Display the ptf dataframe
        st.write("Portfolio Dataframe:")
        st.write(ptf)
    else:
        st.error("Portfolio dataframe not found in session state. Please return to previous step.")
    
    # Error control for tall dataframe
    if 'tall' in st.session_state:
        # Retrieve the tall dataframe from the session state
        tall = st.session_state.tall
        # Display the tall dataframe
        st.write("Tall Dataframe:")
        st.write(tall)
    else:
        st.error("Tall dataframe not found in session state. Please return to previous step.")

    # let's unpivot the tall dataframe
    st.write("Unpivoting the tall dataframe...")
    # Unpivot the tall dataframe
    logret = tall.reset_index().pivot(index='Date', columns='Ticker', values='logret')
    # Display the unpivoted dataframe
    st.write("Unpivoted Portfolio Dataframe:")
    st.write(logret)

    # Calculate the correlation matrix from logret
    st.write("Calculating the correlation matrix...")
    corr_matrix = logret.corr()
    # Display the correlation matrix
    st.write("Correlation Matrix:")
    st.write(corr_matrix)

    # Generate some data
    np.random.seed(0)
    x = np.arange(10)
    y = 2.5 * x + np.random.normal(size=x.size)
    
    # Perform linear regression
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    
    # Display the results with Streamlit
    st.write(f"Slope: {slope}")
    st.write(f"Intercept: {intercept}")
    st.write(f"R-squared: {r_value**2}")
    
    # Plot the data and the regression line
    fig, ax = plt.subplots()
    ax.scatter(x, y, label='Data')
    ax.plot(x, slope * x + intercept, color='red', label='Fitted line')
    ax.legend()
    st.pyplot(fig)

    # let's plot an sns.clustermap of the correlation matrix
    st.write("Plotting the sns.clustermap of the correlation matrix...")
    
    sns.set_theme(font_scale=0.7)
    plt.figure(figsize=(10, 10))
    sns.clustermap(corr_matrix, annot=True, cmap='coolwarm')
    st.pyplot()

if __name__ == "__main__":
    main()

