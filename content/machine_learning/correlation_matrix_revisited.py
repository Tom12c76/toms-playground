import streamlit as st
import seaborn as sns
import scipy
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import plotly.figure_factory as ff
import plotly.graph_objects as go
from plotly.subplots import make_subplots
 



def main():
    st.subheader("Correlation Matrix Revisited")
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

    # Get unique sectors from the portfolio
    unique_sectors = sorted(ptf['Sector'].unique().tolist())

    # Create a multi-select widget for sector selection
    selected_sectors = st.multiselect(
        'Select sectors to include in the correlation matrix:',
        options=unique_sectors,
        default=[]  # Default: no sectors selected
    )

    # If no sectors are selected, use all sectors
    if not selected_sectors:
        selected_sectors = unique_sectors

    # Filter the portfolio based on selected sectors
    filtered_ptf = ptf[ptf['Sector'].isin(selected_sectors)]

    # Get the tickers from the filtered portfolio
    filtered_tickers = filtered_ptf['Ticker'].unique().tolist()

    # Filter the logret dataframe to include only the tickers from selected sectors
    # Always include 'Portfolio' column if it exists
    if 'Portfolio' in logret.columns:
        filtered_logret = logret[filtered_tickers + ['Portfolio']]
    else:
        filtered_logret = logret[filtered_tickers]

    # Use the filtered dataframe for further analysis
    logret = filtered_logret

    # Calculate the correlation matrix from logret
    corr_matrix = logret.drop('Portfolio', axis=1).corr()
    
    # Place the clustermap in an expander
    with st.expander("Seaborn Clustermap for reference", expanded=False):
        st.write("Plotting the sns.clustermap of the correlation matrix...")
        
        sns.set_theme(font_scale=0.5)
        fig, ax = plt.subplots(figsize=(20, 20))
        cluster_grid = sns.clustermap(
            corr_matrix,
            annot=True,
            cmap='coolwarm',
            method='average',  # Linkage method: 'average', 'single', 'complete', 'weighted', etc.
            metric='euclidean'  # Distance metric: 'euclidean', 'correlation', 'cosine', etc.
        )
        plt.close() # Close the figure as clustermap creates its own figure
        st.pyplot(cluster_grid.figure)

    # let's calculate a dendrogram of the correlation matrix
    st.write("Calculating the dendrogram of the correlation matrix...")
    
    # Create distance matrix from correlation matrix
    corr_condensed = scipy.cluster.hierarchy.distance.squareform(1 - corr_matrix)

    # Linkage methods: 'single', 'complete', 'average', 'weighted', 'centroid', 'median', 'ward'
    # Distance metrics: 'euclidean', 'correlation', 'cosine', 'cityblock', 'braycurtis', etc.
    z = scipy.cluster.hierarchy.linkage(corr_condensed, method='average', metric='euclidean')
    
    # Create dendrogram with plotly
    fig_dendro = ff.create_dendrogram(
        corr_matrix,
        orientation='right',
        labels=corr_matrix.columns,
        linkagefun=lambda x: z,
        color_threshold=0.7  # Adjust this threshold as needed
    )
    
    # Update layout for better visibility
    fig_dendro.update_layout(yaxis=dict(autorange="reversed"))
    fig_dendro.update_layout(
        width=900,
        height=800,
        margin=dict(l=200, r=20, b=30, t=30)
    )
    
    # Display in Streamlit
    st.plotly_chart(fig_dendro)

    # Extract Y positions and tickers from the dendrogram
    y_labels = fig_dendro['layout']['yaxis']['ticktext']
    y_values = fig_dendro['layout']['yaxis']['tickvals']
    
    # Initialize data for our dataframe
    ticker_y_color_data = []
    
    # Extract colors for each ticker
    for trace in fig_dendro['data']:
        if 'marker' in trace and 'color' in trace['marker'] and 'x' in trace and 'y' in trace:
            for i, x_val in enumerate(trace['x']):
                if x_val == 0 or (i < len(trace['x'])-1 and trace['x'][i+1] == 0):
                    y_val = trace['y'][i]
                    if y_val in y_values:
                        idx = y_values.index(y_val)
                        ticker = y_labels[idx]
                        color = trace['marker']['color']
                        ticker_y_color_data.append({
                            'Ticker': ticker,
                            'Y_Value': y_val,
                            'Color': color
                        })
    
    # Create a dataframe with the collected data
    ticker_colors_df = pd.DataFrame(ticker_y_color_data).sort_values('Y_Value').reset_index(drop=True)

    # let's add  for each ticker to the dataframe
    df_hbar = ticker_colors_df.copy()
    df_hbar['Return'] = df_hbar['Ticker'].apply(lambda x: np.exp(logret[x].sum())-1)
    df_hbar = df_hbar.sort_values('Y_Value').reset_index(drop=True)

    # from ticker_colors_df create a plotly horizontal bar chart of the returns using the colors from the dendrogram
    st.write("Creating a plotly horizontal bar chart of the returns using the colors from the dendrogram...")   
    hbar_chart = go.Figure()
    hbar_chart.add_trace(go.Bar(
        x=df_hbar['Return'],
        y=df_hbar['Y_Value'],
        marker=dict(color=df_hbar['Color']),
        orientation='h'
    ))
    hbar_chart.update_layout(
        title='Returns for each ticker',
        xaxis_title='Return',
        yaxis_title='Ticker',
        # use the same y-axis labels as the dendrogram
        yaxis=dict(
            tickvals=y_values,
            ticktext=y_labels,
            autorange="reversed"
        ),
        width=900,
        height=800)
    st.plotly_chart(hbar_chart)

    # Sort the correlation matrix according to the dendrogram order
    sorted_tickers = ticker_colors_df['Ticker'].tolist()
    sorted_corr = corr_matrix.loc[sorted_tickers, sorted_tickers]

    # Create heatmap
    heatmap_fig = go.Figure(data=go.Heatmap(
        z=sorted_corr.values,
        x=sorted_corr.columns,
        y=sorted_corr.index,
        colorscale='RdBu_r',
        zmin=-1,
        zmax=1,
        colorbar=dict(title='Correlation')
    ))

    # Update layout to match dendrogram
    heatmap_fig.update_layout(
        title='Correlation Matrix Heatmap',
        width=900,
        height=800,
        yaxis=dict(
            tickvals=y_values,
            ticktext=y_labels,
            autorange="reversed"
        ),
        margin=dict(l=200, r=50, b=100, t=50),
    )

    # Display in Streamlit
    st.plotly_chart(heatmap_fig)

    # Create a combined figure with dendrogram and heatmap side by side with synchronized y-axis
    st.subheader("Combined Dendrogram and Correlation Heatmap")
    
    # Get the ticker order and their exact y positions from the dendrogram
    ticker_to_position = {}
    for idx, (ticker, y_val) in enumerate(zip(y_labels, y_values)):
        ticker_to_position[ticker] = y_val
    
    # Sort the correlation matrix according to the dendrogram order
    sorted_tickers = ticker_colors_df['Ticker'].tolist()
    sorted_corr = corr_matrix.loc[sorted_tickers, sorted_tickers]
    
    # Get the exact y positions for each ticker in the sorted order
    sorted_y_positions = [ticker_to_position[ticker] for ticker in sorted_tickers]
    
    # Create subplot figure
    combined_fig = make_subplots(
        rows=1, 
        cols=2,
        shared_yaxes=True,
        horizontal_spacing=0.01,
        column_widths=[0.3, 0.7],
        subplot_titles=["Dendrogram", "Correlation Heatmap"]
    )
    
    # Add dendrogram traces to the first subplot
    for trace in fig_dendro['data']:
        combined_fig.add_trace(trace, row=1, col=1)
    
    # Add heatmap to the second subplot - using exact dendrogram y positions
    combined_fig.add_trace(
        go.Heatmap(
            z=sorted_corr.values,
            x=sorted_corr.columns,
            y=sorted_y_positions,  # Use the exact y positions from the dendrogram
            colorscale='RdBu_r',
            zmin=-1,
            zmax=1,
            showscale=False  # Hide the color bar
        ),
        row=1, col=2
    )
    
    # Set the y-axis properties for both subplots to use only ticker symbols
    combined_fig.update_yaxes(
        tickvals=sorted_y_positions,
        ticktext=sorted_tickers,  # Use ticker symbols for dendrogram y-axis
        autorange="reversed",
        showticklabels=True,  # Show ticklabels on first subplot
        row=1, col=1  # Apply to first subplot
        )
    
    # Update layout
    combined_fig.update_layout(
        height=900,
        width=1200,
        title="Combined Dendrogram and Correlation Matrix",
        showlegend=False,
        margin=dict(l=150, r=50, b=50, t=80),
    )
    
    # Display the combined figure
    st.plotly_chart(combined_fig)

if __name__ == "__main__":
    main()