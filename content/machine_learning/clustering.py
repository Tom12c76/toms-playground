import streamlit as st
import pandas as pd
import numpy as np
import scipy.cluster.hierarchy
import plotly.express as px
from sklearn.preprocessing import StandardScaler

def main():
    st.header("Portfolio Analysis: Reduce, Reuse, Recycle")
    st.write("""
    This tool helps you identify potentially redundant assets in your portfolio 
    by grouping them based on selected financial metrics. Use the slider to see how
    assets group together as the similarity requirement is relaxed.
    """)

    # --- 1. Data Input and Filtering (Replicated from correlation_matrix_revisited.py) ---
    try:
        # Retrieve dataframes from session state
        if 'ptf' in st.session_state and 'tall' in st.session_state:
            ptf = st.session_state.ptf
            tall = st.session_state.tall
        else:
            st.error("Portfolio data not found. Please go back to the 'Data Input' page and load your data first.")
            return

        # Unpivot the tall dataframe to get log returns
        logret = tall.reset_index().pivot(index='Date', columns='Ticker', values='logret')

        # Get unique sectors from the portfolio
        unique_sectors = sorted(ptf['Sector'].unique().tolist())

        # Create a multi-select widget for sector selection
        selected_sectors = st.multiselect(
            'Filter assets by sector:',
            options=unique_sectors,
            default=[] 
        )

        # If no sectors are selected, use all sectors
        if not selected_sectors:
            selected_sectors = unique_sectors

        # Filter the portfolio based on selected sectors
        filtered_ptf = ptf[ptf['Sector'].isin(selected_sectors)]
        filtered_tickers = filtered_ptf['Ticker'].unique().tolist()

        # Filter the logret dataframe to include only the tickers from selected sectors
        if not filtered_tickers or len(filtered_tickers) < 2:
            st.warning("Please select at least two assets to perform a cluster analysis.")
            return
            
        logret_filtered = logret[filtered_tickers]

        # --- 2. Feature Selection and Calculation ---
        st.subheader("Clustering Parameters")
        
        cluster_on = st.multiselect(
            'Select features to cluster on:',
            options=['Correlation', 'Annualized Return', 'Annualized Volatility'],
            default=['Correlation']
        )

        if not cluster_on:
            st.warning("Please select at least one feature to cluster on.")
            return

        # Calculate features for all assets
        annualized_returns = logret_filtered.mean() * 252
        annualized_volatility = logret_filtered.std() * np.sqrt(252)
        features_df = pd.DataFrame({
            'Annualized Return': annualized_returns,
            'Annualized Volatility': annualized_volatility
        })

        # --- 3. Perform Clustering based on Selection ---
        st.success(f"Data loaded for {len(logret_filtered.columns)} assets. Ready for clustering analysis.")

        # Perform hierarchical clustering to get the linkage matrix
        if cluster_on == ['Correlation']:
            # Method 1: Cluster on correlation distance (as before)
            corr_matrix = logret_filtered.corr()
            distance_matrix = 1 - corr_matrix
            corr_condensed = scipy.cluster.hierarchy.distance.squareform(distance_matrix)
            z = scipy.cluster.hierarchy.linkage(corr_condensed, method='average')
        else:
            # Method 2: Cluster on a mix of features
            # Use only the features selected by the user (excluding 'Correlation')
            feature_list = [f for f in cluster_on if f != 'Correlation']
            if not feature_list:
                st.error("If not using 'Correlation', you must select 'Annualized Return' and/or 'Annualized Volatility'.")
                return
            
            data_for_clustering = features_df[feature_list]
            
            # Standardize the features to give them equal weight
            scaler = StandardScaler()
            scaled_features = scaler.fit_transform(data_for_clustering)
            
            # Use euclidean distance for multi-feature clustering
            z = scipy.cluster.hierarchy.linkage(scaled_features, method='average', metric='euclidean')

        # --- 4. Interactive Slider and Cluster Display ---
        st.subheader("Cluster Your Assets")
        num_assets = len(logret_filtered.columns)
        
        n_clusters = st.slider(
            'Select the number of clusters:',
            min_value=1,
            max_value=num_assets,
            value=num_assets,
            step=1
        )

        labels = scipy.cluster.hierarchy.fcluster(z, n_clusters, criterion='maxclust')
        cluster_df = pd.DataFrame({'Ticker': logret_filtered.columns, 'Cluster': labels})

        # --- 5. Risk/Return Scatter Plot of Clusters ---
        st.subheader("Cluster Risk vs. Return Profile")

        # Merge cluster labels with feature data
        plot_data = features_df.join(cluster_df.set_index('Ticker'))
        
        # Calculate the average for each cluster
        cluster_avg = plot_data.groupby('Cluster').mean()
        
        # --- Create custom coloring logic ---
        # Get the size of each cluster
        cluster_sizes = plot_data.groupby('Cluster').size().rename('Size')
        cluster_avg = cluster_avg.join(cluster_sizes)

        # Create a new column for the color group
        # Single-asset clusters get a generic group, multi-asset clusters keep their name
        cluster_avg['Color Group'] = cluster_avg.index.astype(str)
        cluster_avg.loc[cluster_avg['Size'] == 1, 'Color Group'] = 'Single Asset'

        # Create a new column for marker size based on the number of assets
        cluster_avg['Marker Size'] = cluster_avg['Size'] * 10

        # Get ticker names for hover text
        plot_data_for_hover = plot_data.reset_index()
        cluster_tickers_agg = plot_data_for_hover.groupby('Cluster')['Ticker'].apply(lambda x: ', '.join(x)).reset_index()
        cluster_tickers_agg = cluster_tickers_agg.rename(columns={'Ticker': 'Tickers'})

        cluster_avg = cluster_avg.join(cluster_tickers_agg.set_index('Cluster'))
        cluster_avg['Cluster'] = cluster_avg.index.astype(str)

        if not cluster_avg.empty:
            fig = px.scatter(
                cluster_avg,
                x='Annualized Volatility',
                y='Annualized Return',
                color='Color Group',  # Use the new custom color group
                size='Marker Size',   # Use the calculated marker size
                text='Tickers',
                hover_name=cluster_avg.index,
                hover_data={'Cluster': False, 'Tickers': True, 'Size': True},
                title='Average Risk/Return per Cluster',
                # Assign grey to single assets, let Plotly handle the rest
                color_discrete_map={'Single Asset': 'lightgrey'}
            )
            fig.update_traces(textposition='top center')
            fig.update_layout(
                xaxis_title="Annualized Volatility (Risk)",
                yaxis_title="Annualized Return",
                legend_title="Cluster Group",
                yaxis_tickformat='.0%', # Format y-axis as percentage
                xaxis_tickformat='.0%'  # Format x-axis as percentage
            )
            # Reverse X-axis as requested
            fig.update_xaxes(autorange="reversed")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Generate clusters to see the risk/return profile plot.")

        # --- 6. Display Results and "Who Wins" Logic ---
        st.subheader(f"Asset Groups (for {n_clusters} clusters)")

        for i in sorted(cluster_df['Cluster'].unique()):
            cluster_tickers = cluster_df[cluster_df['Cluster'] == i]['Ticker'].tolist()
            
            with st.expander(f"**Cluster {i}**: `{', '.join(cluster_tickers)}`"):
                if len(cluster_tickers) > 1:
                    st.write("This cluster contains multiple, highly-correlated assets. Compare them below to identify potential redundancies.")
                    
                    required_cols = ['Name', 'Ticker', 'Expense Ratio', 'AUM']
                    if all(col in ptf.columns for col in ['Expense Ratio', 'AUM', 'Name']):
                        comparison_df = ptf[ptf['Ticker'].isin(cluster_tickers)][required_cols].copy()
                        comparison_df = comparison_df.sort_values(by='Expense Ratio', ascending=True).set_index('Ticker')
                        
                        st.dataframe(comparison_df.style.highlight_min(subset='Expense Ratio', color='lightgreen'))
                        winner = comparison_df.index[0]
                        st.success(f"**Recommendation:** Based on the lowest expense ratio, **{winner}** is the most cost-effective choice in this group.")
                    else:
                        st.warning("Cannot provide a 'winner' recommendation because 'Expense Ratio' or 'AUM' data is missing from your portfolio file.")
                        st.write("The assets in this group are:")
                        st.json(cluster_tickers)
                else:
                    st.write(f"This asset, **{cluster_tickers[0]}**, is in a cluster by itself, indicating it is distinct from other assets based on the selected features.")

    except Exception as e:
        st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()

