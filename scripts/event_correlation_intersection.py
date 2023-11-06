import argparse, csv
import pandas as pd
from datetime import datetime, timedelta

def sort(matrix):
    def extract_date(date_str):
        # Extract the start and end dates from the given string
        dates = date_str.split(' - ')
        start_date = datetime.strptime(dates[0], '%b %d, %Y')
        end_date = datetime.strptime(dates[1], '%b %d, %Y')
        return start_date, end_date

    # Sort the matrix based on the item at position 0 (alphabetically, descending)
    #matrix.sort(key=lambda row: row[0], reverse=True)

    # Find the index of the date strings in each row
    date_index1 = 2
    date_index2 = 6

    for row in matrix:
        start_date1, end_date1 = extract_date(row[date_index1])
        start_date2, end_date2 = extract_date(row[date_index2])

        if start_date1 > start_date2:
            # Swap the elements at positions [0:3] and [4:7]
            row[:3], row[4:7] = row[4:7], row[:3]

    return matrix

def intersection(positive_correl_date, date_intervals, events_1, events_2, k):
    # Iterate through the date intervals
    for start_date, end_date in date_intervals:
        if start_date <= positive_correl_date <= end_date:
            # Format the start and end dates as strings
            start_date_str = start_date.strftime('%b %d, %Y')
            end_date_str = end_date.strftime('%b %d, %Y')

            matching_intervals = []

            # Create the date interval string using the template
            matching_interval_1 = f"{start_date_str} - {end_date_str}"
            matching_intervals.append(matching_interval_1)

            # Calculate the size of the interval (duration)
            interval_size = end_date - start_date

            # Calculate the start and end dates for the second interval
            second_start_date = start_date - interval_size - timedelta(days=1)
            second_end_date = end_date - interval_size - timedelta(days=1)

            # Format the second interval as a string
            matching_interval_2 = f"{second_start_date.strftime('%b %d, %Y')} - {second_end_date.strftime('%b %d, %Y')}"
            matching_intervals.append(matching_interval_2)

            break
    
    intersection_intervals = []

    #TODO automatic generate date pair intervals
    matching_intervals = [
        [matching_interval_1,matching_interval_1],
        [matching_interval_2,matching_interval_2],
        [matching_interval_1,matching_interval_2],
        [matching_interval_2,matching_interval_1],
    ]

    for matching_interval_1, matching_interval_2 in matching_intervals:
        #for matching_interval_2 in matching_intervals:
        if events_1[matching_interval_1] != 0 and events_2[matching_interval_2] != 0:
            # If positive correlation, then both events must have the same sign
            if k == 1 and events_1[matching_interval_1] == events_2[matching_interval_2]:
                intersection_intervals.append([matching_interval_1, matching_interval_2])

            # If negative correlation, then both events must have different sign
            if k == -1 and events_1[matching_interval_1] != events_2[matching_interval_2]:
                intersection_intervals.append([matching_interval_1, matching_interval_2])

    #if len(intersection_intervals) > 0:
    #    return [intersection_intervals[0]]
    #else:
    #    return []
    
    return intersection_intervals

def remove_duplicate_rows(matrix):
    # Initialize a set to store unique rows
    unique_rows = set()

    # Initialize a new matrix to store the result
    result_matrix = []

    # Iterate through the original matrix
    for row in matrix:
        # Convert the row to a tuple to make it hashable
        row_tuple = tuple(row)
        # Check if the row is unique, and if so, add it to the result matrix and the set
        if row_tuple not in unique_rows:
            result_matrix.append(row)
            unique_rows.add(row_tuple)

    return result_matrix

ap = argparse.ArgumentParser()
ap.add_argument('-c', '--clusters', required=True, help="File containing clusters.")
ap.add_argument('-e', '--events', required=True, help="Folder containing events.")
ap.add_argument('-o', '--output-file', required=True, help="File to save intersection events.")

args = vars(ap.parse_args())

clusters_file = args['clusters']
events_folder = args['events']
output_file = args['output_file']

sheet_names = ['review_count', 'review_rating', 'review_polarity']
event_df = {}

date_format = '%b %d, %Y'  # Format for dates

for sheet_name in sheet_names:
    event_df[sheet_name] = pd.read_csv(events_folder + "/" + sheet_name + "_events.csv", index_col=0)

clusters_df = pd.read_csv(clusters_file)

date_intervals = [[datetime.strptime(date_interval.split(" - ")[0], date_format), datetime.strptime(date_interval.split(" - ")[1], date_format)] for date_interval in event_df[sheet_names[0]].columns.tolist()]

intersection_events = []

for index, row in clusters_df.iterrows():
    events_1 = event_df[row['Metric1']].loc[row['App1']]
    events_2 = event_df[row['Metric2']].loc[row['App2']]

    if pd.notna(row['Cluster_StartDate']):
        correl_date = datetime.strptime(str(row['Cluster_StartDate']), date_format)
    
        # For positive correl, both events must be 1 or -1
        correl_event_intervals = intersection(correl_date, date_intervals, events_1, events_2, row['CorrelationSymbol'])

        # We add the event if
        for correl_event_interval in correl_event_intervals:
            intersection_events.append([row['App1'], row['Metric1'], correl_event_interval[0], events_1[correl_event_interval[0]], 
                                        row['App2'], row['Metric2'], correl_event_interval[1], events_2[correl_event_interval[1]]])

intersection_events = remove_duplicate_rows(intersection_events)
intersection_events = sort(intersection_events)

print(str(len(intersection_events)-1) + " events found\n")

intersection_events.insert(0, ['App1','Metric1','DateInterval1','E1','App2','Metric2','DateInterval2','E2'])

# Write the matrix to the CSV file
with open(output_file, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    for row in intersection_events:
        print(row)
        writer.writerow(row)