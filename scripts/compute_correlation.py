import pandas as pd
import numpy as np
from scipy.stats import pearsonr
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import pdist
import argparse, csv

# Define a custom distance metric
# You want to measure the distance based on the absolute difference from 1 or -1
def custom_distance(x):
    return np.abs(np.abs(x) - 1)

ap = argparse.ArgumentParser()
ap.add_argument('-i', '--input-file', required=True, help="Input metric file.")
ap.add_argument('-w', '--time-window', required=True, help="Time window length.")
ap.add_argument('-o', '--output-file', required=True, help="Output cluster file.")

args = vars(ap.parse_args())

file_path = args['input_file']
time_window = int(args['time_window'])
output_path = args['output_file']

# Step 1: Read the .xlsx file and save the data frames
sheet_names = ['review_count', 'review_rating', 'review_polarity']
metrics_pairs = [['review_count', 'review_count'],
                 ['review_rating', 'review_rating'],
                 ['review_polarity', 'review_polarity'],
                 ['review_count', 'review_rating'],
                 ['review_count', 'review_polarity'],
                 ['review_rating', 'review_polarity']
                 ]
data_frames = {}

for sheet_name in sheet_names:
    df = pd.read_excel(file_path, sheet_name=sheet_name, header=1, index_col=0)
    data_frames[sheet_name] = df.iloc[0:10,0:].fillna(0)

# Step 2: Calculate correlations for each metric combination
app_packages = data_frames['review_count'].index.tolist()
correlation_matrices = {}

for metric_pair in metrics_pairs:
    metric_data_a = data_frames[metric_pair[0]].to_numpy()
    metric_data_b = data_frames[metric_pair[1]].to_numpy()
    num_apps, num_dates = metric_data_a.shape

    for i in range(num_apps):
        app_a = app_packages[i]
        for j in range(i+1, num_apps):
            app_b = app_packages[j]

            for days_back in range(num_dates):
                if days_back >= time_window:

                    subset_a = pd.to_numeric(metric_data_a[i, days_back - 14:days_back], errors='coerce')
                    subset_b = pd.to_numeric(metric_data_b[j, days_back - 14:days_back], errors='coerce')

                    # Compute correlation
                    if not (np.isnan(subset_a).any() or np.isnan(subset_b).any()):
                        correlation = pearsonr(subset_a, subset_b)[0]
                    else:
                        correlation = None

                    matrix_key = f'{app_a}-{app_b}-{metric_pair[0]}-{metric_pair[1]}'
                    
                    if matrix_key not in correlation_matrices:
                        correlation_matrices[matrix_key] = []

                    correlation_matrices[matrix_key].append(correlation)

def find_clusters(data, threshold, direction):
    data = np.array(data)
    data = data * direction  # Adjust direction for high or low clusters
    clusters = []
    current_cluster = []

    for i, value in enumerate(data):
        if value >= threshold:
            current_cluster.append(i)
        else:
            if current_cluster:
                clusters.append(current_cluster)
                current_cluster = []

    # Handle the case when the last element is part of a cluster
    if current_cluster:
        clusters.append(current_cluster)

    # OPTION A: Return only the largest cluster
    # max_cluster = []
    # for cluster in clusters:
    #     if len(cluster) > len(max_cluster):
    #         max_cluster = cluster
    # 
    # return max_cluster

    # OPTION B: Return all clusters
    return clusters

# Define a function to get cluster details
def get_cluster_details(cluster, columns):
    if cluster:
        start_date = columns[cluster[0]]
        end_date = columns[cluster[-1]]
        return start_date, end_date
    else:
        return None, None
    
def safe_split(text):
    if text is not None and text != 'None':
        return text.split(" - ")[0]
    else:
        return None

clusters = [['App1','Metric1','App2','Metric2','Cluster_StartDate','Cluster_EndDate','CorrelationSymbol']]

# Step 3: Create separate correlation matrices
for matrix_key, correlations in correlation_matrices.items():
    date_labels = data_frames['review_count'].columns.tolist()[-len(correlations):]
    correlation_matrix = pd.DataFrame(data=np.array(correlations).reshape(1, -1), columns=date_labels, index=[matrix_key])
    print(f'Correlation Matrix for {matrix_key}:')
    #if 'rating' in matrix_key:
    #    print(correlation_matrix.iloc[0])

    # Find clusters of high values (near 1)
    high_threshold = 0.5  # Adjust the threshold as needed
    high_clusters = find_clusters(correlation_matrix.iloc[0], high_threshold, direction=1)

    # Find clusters of low values (near -1)
    low_threshold = -0.5  # Adjust the threshold as needed
    low_clusters = find_clusters(correlation_matrix.iloc[0], low_threshold, direction=-1)

    # Get cluster details for high and low clusters

    split_key = matrix_key.split("-")

    # OPTION A: Return largest cluster
    #high_cluster_details = [get_cluster_details(high_clusters, correlation_matrix.columns)]
    #low_cluster_details = [get_cluster_details(low_clusters, correlation_matrix.columns)]

    #clusters.append([split_key[0],
    #                split_key[2],
    #                split_key[1],
    #                split_key[3],
    #                safe_split(high_cluster_details[0][0]),
    #                safe_split(high_cluster_details[0][1]),
    #                safe_split(low_cluster_details[0][0]),
    #                safe_split(low_cluster_details[0][1])])

    # OPTION B: Return all clusters
    high_cluster_details = [get_cluster_details(cluster, correlation_matrix.columns) for cluster in high_clusters]
    low_cluster_details = [get_cluster_details(cluster, correlation_matrix.columns) for cluster in low_clusters]

    for cluster in high_cluster_details:
        clusters.append([split_key[0],
                    split_key[2],
                    split_key[1],
                    split_key[3],
                    safe_split(cluster[0]),
                    safe_split(cluster[1]),1])
        
    for cluster in low_cluster_details:
        clusters.append([split_key[0],
                    split_key[2],
                    split_key[1],
                    split_key[3],
                    safe_split(cluster[0]),
                    safe_split(cluster[1]),-1])

    # Print cluster details
    for i, (start, end) in enumerate(high_cluster_details):
        print(f"High Cluster {i + 1}: Start Date = {start}, End Date = {end}")

    for i, (start, end) in enumerate(low_cluster_details):
        print(f"Low Cluster {i + 1}: Start Date = {start}, End Date = {end}")

    print("")

# Open the CSV file for writing
with open(output_path, mode='w', newline='') as file:
    writer = csv.writer(file)

    # Write each row of the matrix to the CSV file
    for row in clusters:
        writer.writerow(row)