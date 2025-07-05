import streamlit as st
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px

def load_and_prepare_data():
    """Loads and prepares data for PCA."""
    if 'tall' not in st.session_state:
        st.error("Tall dataframe not found in session state. Please return to previous step.")
        st.stop()
    
    tall = st.session_state.tall
    logret = tall.reset_index().pivot(index='Date', columns='Ticker', values='logret')

    if 'Portfolio' in logret.columns:
        logret = logret.drop(columns='Portfolio', axis=1)
    
    return logret

def perform_pca(logret):
    """Performs PCA on the log returns data."""
    scaler = StandardScaler()
    logret_scaled = scaler.fit_transform(logret.dropna())
    
    pca = PCA(n_components=logret.shape[1])
    pca.fit(logret_scaled)
    
    factor_loadings = pd.DataFrame(
        pca.components_.T,
        index=logret.columns,
        columns=[f"PC{i+1}" for i in range(pca.n_components_)]
    )
    
    return pca, factor_loadings, logret_scaled

def plot_explained_variance(pca):
    """Plots the explained variance and cumulative explained variance."""
    explained_variance = pd.DataFrame(
        pca.explained_variance_ratio_,
        index=[f"PC{i+1}" for i in range(pca.n_components_)],
        columns=["Explained Variance"]
    )
    explained_variance['Cumulative Explained Variance'] = explained_variance['Explained Variance'].cumsum()

    fig = go.Figure()
    fig.add_trace(
        go.Bar(x=explained_variance.index, y=explained_variance['Explained Variance'], name='Explained Variance', hovertemplate='%{y:.1%}')
    )
    fig.add_trace(
        go.Scatter(x=explained_variance.index, y=explained_variance['Cumulative Explained Variance'], name='Cumulative Explained Variance', mode='lines+markers', hovertemplate='%{y:.1%}')
    )

    # Find the first point where cumulative variance is >= 80%
    threshold = 0.8
    highlight_point = explained_variance[explained_variance['Cumulative Explained Variance'] >= threshold].iloc[0]
    highlight_index = highlight_point.name
    highlight_value = highlight_point['Cumulative Explained Variance']
    num_components = explained_variance.index.get_loc(highlight_index) + 1

    # Add a vertical line and an annotation
    fig.add_shape(
        type='line',
        x0=highlight_index,
        y0=0,
        x1=highlight_index,
        y1=highlight_value,
        line=dict(color='navy', width=2, dash='dash'),
        layer='below'
    )
    fig.add_annotation(
        x=highlight_index,
        y=highlight_value,
        text=f"{num_components} PC's explain {highlight_value:.0%}",
        showarrow=False,
        xanchor='right',
        yanchor='bottom',
        bgcolor="white"
    )

    fig.update_layout(
        title="Explained Variance Ratio",
        xaxis_title="Principal Components",
        yaxis_title="Explained Variance",
        yaxis=dict(
            tickformat=".1%"
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    st.plotly_chart(fig, use_container_width=True)
    return num_components, explained_variance

def plot_factor_loadings_clustermap(factor_loadings, num_components, explained_variance):
    """Displays a clustermap of factor loadings."""
    num_pc_for_clustermap = st.slider(
        'Select number of components for clustermap',
        min_value=1,
        max_value=len(factor_loadings.columns),
        value=num_components, # default to number of components that explain 80% of variance
        step=1
    )
    cumulative_variance_selected = explained_variance['Cumulative Explained Variance'].iloc[num_pc_for_clustermap-1]
    st.write(f"The selected {num_pc_for_clustermap} components explain {cumulative_variance_selected:.1%} of the variance.")

    # Generate a Seaborn clustermap
    sns.set_theme(font_scale=0.8)
    cluster_grid = sns.clustermap(
        factor_loadings.iloc[:, :num_pc_for_clustermap],
        metric='euclidean',
        method='average',
        cmap='coolwarm',
        col_cluster=False,  # Keep factors in original order
        cbar_pos=None
    )
    cluster_grid.figure.suptitle('SNS Clustermap', fontsize=16, y=0.98)
    st.pyplot(cluster_grid.figure)

def plot_3d_factor_loadings(factor_loadings):
    """Creates and displays a 3D scatter plot of factor loadings."""
    # Create a DataFrame with the necessary data for plotting
    plot_df = pd.DataFrame({
        'PC1': factor_loadings['PC1'],
        'PC2': factor_loadings['PC2'],
        'PC3': factor_loadings['PC3'],
        'PC4': factor_loadings['PC4'],
        'Stock': factor_loadings.index
    })
    
    # Create the Plotly 3D scatter plot
    fig = px.scatter_3d(
        plot_df, 
        x='PC1', 
        y='PC2', 
        z='PC3', 
        text='Stock',
        color='PC4',
        color_continuous_scale='viridis',
        hover_data={'Stock': True, 'PC1': ':.4f', 'PC2': ':.4f', 'PC3': ':.4f', 'PC4': ':.4f'},
        title='3D Scatter Plot of PC1 vs PC2 vs PC3 (color-coded by PC4)'
    )
    
    # Customize the plot appearance
    fig.update_traces(
        textposition='top center',
        marker=dict(size=5, opacity=0.7),
    )
    
    # Calculate the axis range to make them symmetrical
    max_abs_x = max(abs(plot_df['PC1'].min()), abs(plot_df['PC1'].max()))
    max_abs_y = max(abs(plot_df['PC2'].min()), abs(plot_df['PC2'].max()))
    max_abs_z = max(abs(plot_df['PC3'].min()), abs(plot_df['PC3'].max()))
    max_range = max(max_abs_x, max_abs_y, max_abs_z) * 1.1  # Add 10% padding
    
    fig.update_layout(
        autosize=True,
        height=700,
        scene=dict(
            xaxis_title="PC1",
            yaxis_title="PC2",
            zaxis_title="PC3",
            xaxis=dict(range=[-max_range, max_range]),
            yaxis=dict(range=[-max_range, max_range]),
            zaxis=dict(range=[-max_range, max_range]),
        )
    )
    
    # Display the plot
    st.plotly_chart(fig, use_container_width=True)

def plot_pc_time_series(pca, logret_scaled, logret):
    """Plots the time series of principal components."""
    st.subheader("Time Series of Principal Components")

    # Calculate the time series of the principal components
    pc_time_series = pca.transform(logret_scaled)
    pc_ts_df = pd.DataFrame(
        pc_time_series,
        index=logret.dropna().index,
        columns=[f"PC{i+1}" for i in range(pca.n_components_)]
    )

    # Add a multiselect for choosing which PCs to plot
    default_pcs_to_plot = [f"PC{i+1}" for i in range(min(5, pca.n_components_))]
    selected_pcs = st.multiselect(
        "Select Principal Components to plot:",
        options=pc_ts_df.columns.tolist(),
        default=default_pcs_to_plot
    )

    if selected_pcs:
        # Plot the cumulative sum of the selected PC time series
        fig_ts = px.line(
            pc_ts_df[selected_pcs].cumsum(),
            title="Cumulative Performance of Selected Principal Components"
        )
        fig_ts.update_layout(
            xaxis_title="Date",
            yaxis_title="Cumulative Log Return",
            legend_title="Principal Component"
        )
        st.plotly_chart(fig_ts, use_container_width=True)
    else:
        st.info("Select one or more Principal Components to visualize their performance over time.")

def main():
    st.title("PCA Analysis")
    st.info("""
    This page performs Principal Component Analysis (PCA) on 
    the standardized log returns of the our portfolio. 
    
    It visualizes the explained variance of the principal components, 
    allowing you to explore the factor loadings with a clustermap.
    
    Next a 3D scatter plot is generated of the first three principal 
    components PC1 - PC3, colored by PC4.
            
    Finally, the time series of the principal components is plotted,
    showing the cumulative performance of the selected components.
    """)

    logret = load_and_prepare_data()
    
    pca, factor_loadings, logret_scaled = perform_pca(logret)

    num_components_for_80_var, explained_variance_df = plot_explained_variance(pca)

    plot_factor_loadings_clustermap(factor_loadings, num_components_for_80_var, explained_variance_df)

    plot_3d_factor_loadings(factor_loadings)

    plot_pc_time_series(pca, logret_scaled, logret)
