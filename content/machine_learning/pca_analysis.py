import streamlit as st
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
import seaborn as sns
import matplotlib.pyplot as plt

def main():
    st.title("PCA Analysis")
    st.write("This page is dedicated to Principal Component Analysis (PCA).")

    # Error control for session state access
    if 'tall' in st.session_state:
        # Retrieve the tall dataframe from the session state
        tall = st.session_state.tall
    else:
        st.error("Tall dataframe not found in session state. Please return to previous step.")
        st.stop()

    # Unpivot the tall dataframe to get log returns    
    logret = tall.reset_index().pivot(index='Date', columns='Ticker', values='logret')

    if 'Portfolio' in logret.columns:
        logret = logret.drop(columns='Portfolio', axis=1)

    # Perform PCA analysis
    st.write("Performing PCA analysis on log returns...")
    # pca = PCA(n_components=logret.shape[1])
    pca = PCA(n_components=29)
    pca.fit(logret.dropna())

    # Create a DataFrame for factor loadings
    factor_loadings = pd.DataFrame(
        pca.components_.T,
        index=logret.columns,
        columns=[f"PC{i+1}" for i in range(pca.n_components_)]
    )

    st.write("Factor Loadings:")
    st.dataframe(factor_loadings)

    # let's plot the explained variance
    st.write("Explained Variance Ratio:")
    explained_variance = pd.DataFrame(
        pca.explained_variance_ratio_,
        index=[f"PC{i+1}" for i in range(pca.n_components_)],
        columns=["Explained Variance"]
    )
    # Calculate cumulative explained variance
    explained_variance['Cumulative Explained Variance'] = explained_variance['Explained Variance'].cumsum()

    st.dataframe(explained_variance)
    # let's make a plotly chart of the explained variance as a bar chart
    st.write("Explained Variance Bar Chart:")
    fig = plt.figure(figsize=(10, 6))
    plt.bar(explained_variance.index, explained_variance['Explained Variance'], color='blue')
    plt.plot(explained_variance.index, explained_variance['Cumulative Explained Variance'], color='red', marker='o')
    plt.title("Explained Variance Ratio")
    plt.xlabel("Principal Components")
    plt.ylabel("Explained Variance")
    plt.xticks(rotation=45)
    plt.legend(['Cumulative Explained Variance', 'Explained Variance'])
    plt.tight_layout()
    st.pyplot(fig)


    # Generate a Seaborn clustermap
    st.write("Generating a Seaborn clustermap...")
    sns.set_theme(font_scale=0.8)
    cluster_grid = sns.clustermap(
        factor_loadings,
        metric='euclidean',
        method='average',
        cmap='coolwarm',
        col_cluster=False  # Keep factors in original order
    )
    plt.close()  # Close the figure to prevent duplicate rendering
    st.pyplot(cluster_grid.figure)

    # Use PC1 and PC2 from factor_loadings to create an interactive Plotly scatter plot
    st.write("Scatter Plot of PC1 vs PC2 (color-coded by PC3):")
    import plotly.express as px
    
    # Create a DataFrame with the necessary data for plotting
    plot_df = pd.DataFrame({
        'PC1': factor_loadings['PC1'],
        'PC2': factor_loadings['PC2'],
        'PC3': factor_loadings['PC3'],
        'Stock': factor_loadings.index
    })
    
    # Create the Plotly scatter plot with PC3 as color
    fig = px.scatter(
        plot_df, 
        x='PC1', 
        y='PC2', 
        text='Stock',
        color='PC3',
        color_continuous_scale='viridis',
        hover_data={'Stock': True, 'PC1': ':.4f', 'PC2': ':.4f', 'PC3': ':.4f'},
        title='Scatter Plot of PC1 vs PC2 (color-coded by PC3)'
    )
    
    # Customize the plot appearance
    fig.update_traces(
        textposition='top center',
        marker=dict(size=10, opacity=0.7),
    )
    
    # Calculate the axis range to make them symmetrical
    max_abs_x = max(abs(plot_df['PC1'].min()), abs(plot_df['PC1'].max()))
    max_abs_y = max(abs(plot_df['PC2'].min()), abs(plot_df['PC2'].max()))
    max_range = max(max_abs_x, max_abs_y) * 1.1  # Add 10% padding
    
    fig.update_layout(
        autosize=True,
        height=600,
        xaxis_title="PC1",
        yaxis_title="PC2",
        coloraxis_colorbar=dict(title="PC3"),
        xaxis=dict(range=[-max_range, max_range]),
        yaxis=dict(range=[-max_range, max_range]),
        xaxis_zeroline=True,
        yaxis_zeroline=True
    )
    
    # Display the plot
    st.plotly_chart(fig, use_container_width=True)
