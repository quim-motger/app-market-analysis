import pandas as pd
import argparse

ap = argparse.ArgumentParser()
ap.add_argument('-i', '--input-file', required=True, help="Input metric file.")
ap.add_argument('-o', '--output-folder', required=True, help="Output folder to save event files.")
ap.add_argument('-k', '--sensitivity-factor', required=True, help="Sensitivity factor for event detection")

args = vars(ap.parse_args())

file_path = args['input_file']
output_path = args['output_folder']
k = int(args['sensitivity_factor'])

# Step 1: Read the .xlsx file and save the data frames
sheet_names = ['review_count', 'review_rating', 'review_polarity']
data_frames = {}

for sheet_name in sheet_names:
    df = pd.read_excel(file_path, sheet_name=sheet_name, header=1, index_col=0)
    data_frames[sheet_name] = df.iloc[0:10,0:].fillna(0)

    # Compute average differences
    data_frames[sheet_name + "_diff"] = data_frames[sheet_name].diff(axis=1)

    # Compute standard deviations
    data_frames[sheet_name + "_sd"] = data_frames[sheet_name + "_diff"].expanding(axis=1).std()

    # Compute event matrix
    result_df = (data_frames[sheet_name + "_diff"] > k * data_frames[sheet_name + "_sd"]).astype(int) - (data_frames[sheet_name + "_diff"] < -k * data_frames[sheet_name + "_sd"]).astype(int)

    result_df.to_csv(output_path + "/" + sheet_name + "_events.csv")