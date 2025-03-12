import streamlit as st
import seaborn as sns
import scipy
import matplotlib.pyplot as plt
# import numpy as np
# from scipy import stats
# import pandas as pd
# import plotly.express as px
import plotly.figure_factory as ff



def main():
    st.title("Correlation Matrix Revisited")
    st.write("This is the content of the Correlation Matrix Revisited page.")

    # Error control for session state access
    if 'ptf' in st.session_state:
        # Retrieve the ptf dataframe from the session state
        ptf = st.session_state.ptf
        # st.write(ptf)
    else:
        st.error("Portfolio dataframe not found in session state. Please return to previous step.")
    
    # Error control for tall dataframe
    if 'tall' in st.session_state:
        # Retrieve the tall dataframe from the session state
        tall = st.session_state.tall
    else:
        st.error("Tall dataframe not found in session state. Please return to previous step.")

    # Unpivot the tall dataframe
    logret = tall.reset_index().pivot(index='Date', columns='Ticker', values='logret')

    # Calculate the correlation matrix from logret
    corr_matrix = logret.drop('Portfolio', axis=1).corr()
    
    # let's plot an sns.clustermap of the correlation matrix
    st.write("Plotting the sns.clustermap of the correlation matrix...")
    
    sns.set_theme(font_scale=0.5)
    fig, ax = plt.subplots(figsize=(20, 20))
    cluster_grid = sns.clustermap(corr_matrix, annot=True, cmap='coolwarm')
    plt.close() # Close the figure as clustermap creates its own figure
    st.pyplot(cluster_grid.figure)

    # let's calculate a dendrogram of the correlation matrix
    st.write("Calculating the dendrogram of the correlation matrix...")
    
    # Create distance matrix from correlation matrix
    corr_condensed = scipy.cluster.hierarchy.distance.squareform(1 - corr_matrix)
    z = scipy.cluster.hierarchy.linkage(corr_condensed, method='average')
    
    # Create dendrogram with plotly
    fig = ff.create_dendrogram(
        corr_matrix,
        orientation='right',
        labels=corr_matrix.columns,
        linkagefun=lambda x: z,
        color_threshold=0.7  # Adjust this threshold as needed
    )
    
    # Update layout for better visibility
    fig.update_layout(yaxis=dict(autorange="reversed"))
    fig.update_layout(
        width=900,
        height=800,
        margin=dict(l=200, r=20, b=30, t=30)
    )
    
    # Display in Streamlit
    st.plotly_chart(fig)
    

if __name__ == "__main__":
    main()