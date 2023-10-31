import argparse
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.colors as mcolors
from sklearn.neighbors import NeighborhoodComponentsAnalysis
from sklearn.preprocessing import StandardScaler

def main():
    parser = argparse.ArgumentParser(description='Perform KMeans clustering on data.')
    parser.add_argument('--input', type=str, help='Input CSV file')
    parser.add_argument('--labels', type=str, help='Labels CSV file')
    parser.add_argument('--output', type=str, help='Output CSV file')
    args = parser.parse_args()

    # Read the input data
    df = pd.read_csv(args.input, index_col = 0)
    df = df.transpose()
    df.to_csv("temp.csv")
    df = pd.read_csv("temp.csv", index_col = 0)

    # Perform Neighborhood Component Analysis (NCA)
    nca = NeighborhoodComponentsAnalysis(n_components=3)
    nca_result = nca.fit_transform(df, df.index)

    # Save NCA results to a CSV file
    nca_df = pd.DataFrame(nca_result, columns=['NC1', 'NC2', 'NC3'], index=df.index)
    nca_df.to_csv(args.output + '_nca.csv')

    # Perform KMeans clustering on NCA results
    kmeans = KMeans(n_clusters=8, random_state=0).fit(nca_result)

    # Read the labels data
    labels_df = pd.read_csv(args.labels)

    # Create a color map and taxa map from the labels table
    color_map = {}
    taxa_map = {}
    for index, row in labels_df.iterrows():
        color_map[row['item']] = row['color']
        taxa_map[row['item']] = row['taxa']

    # Assign colors and taxa to each dot in the PCA plot
    colors = []
    taxa = []
    for item in nca_df.index:
        color_assigned = False
        for table_item, color in color_map.items():
            if item.startswith(table_item):
                rgba_color = mcolors.to_rgba(color, alpha=0.6)  # Convert the color name to RGBA and make it 60% transparent
                colors.append(rgba_color)
                taxa.append(taxa_map[table_item])
                color_assigned = True
                break
        if not color_assigned:
            colors.append(mcolors.to_rgba('red'))
            taxa.append('Undetermined Species')

    # Plot the PCA results with clustering overlay in 3D
	
    fig = plt.figure(figsize=(10,5))
    
    ax = fig.add_subplot(111, projection='3d')
    print(colors)
    scatter = ax.scatter(nca_result[:, 0], nca_result[:, 1], nca_result[:, 2], c=colors)
    
    ax.set_xlabel('PC1 - {0}%'.format(np.round(nca.explained_variance_ratio_[0]*100, decimals=2)))
    
    ax.set_ylabel('PC2 - {0}%'.format(np.round(nca.explained_variance_ratio_[1]*100, decimals=2)))
    
    ax.set_zlabel('PC3 - {0}%'.format(np.round(nca.explained_variance_ratio_[2]*100, decimals=2)))
    
    plt.title('3D PCA with KMeans Clustering Overlay')

    # Connect the dots from the same cluster to the mean using lines
    for i in range(kmeans.n_clusters):
        cluster_points = nca_result[kmeans.labels_ == i]
        centroid = cluster_points.mean(axis=0)
        for point in cluster_points:
            ax.plot([point[0], centroid[0]], [point[1], centroid[1]], [point[2], centroid[2]], 'k-')

    # Create a legend for the plot using the taxa information
    legend_labels = dict(zip(taxa, colors))
    
    # Order the legend labels alphabetically
    sorted_legend_labels = dict(sorted(legend_labels.items()))
    
    handles = [plt.Line2D([], [], marker='o', color=color, linestyle='', markersize=10) for color in sorted_legend_labels.values()]
    
    # Move the legend to the right side of the plot
    ax.legend(handles, sorted_legend_labels.keys(), title='Taxa', bbox_to_anchor=(1.15, 1), loc='upper left')
    
    # Adjust the figure so the legend doesn't run off
    plt.subplots_adjust(right=0.85)

    # Save the plot to an SVG file
    plt.savefig(args.output + '.svg')

if __name__ == "__main__":
   main()
