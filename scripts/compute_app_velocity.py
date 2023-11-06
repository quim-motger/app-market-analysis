import csv
import json, argparse
from datetime import datetime, timedelta

metric = 'velocity'
#metric = 'downloads'

ap = argparse.ArgumentParser()
ap.add_argument('-i', '--input-file', required=True, help="Review set.")
ap.add_argument('-w', '--time-window', required=True, help="Time window length.")
ap.add_argument('-t', '--origin-date', required=True, help="origin date in '%b %d, %Y' format.")
ap.add_argument('-o', '--output-folder', required=True, help="Output folder.")

args = vars(ap.parse_args())

source_file = args['input_file']
w = int(args['time_window'])
t = args['origin_date']
output_folder = args['output_folder']

# Define the start date and end date (1 year later)
start_date = datetime.strptime(t, '%b %d, %Y')
end_date = start_date + timedelta(days=365)

# Create a list of date intervals with one-week intervals
date_intervals = []
current_date = start_date
while current_date < end_date:
    next_date = current_date + timedelta(days=w)
    date_intervals.append((current_date, next_date - timedelta(days=1)))
    current_date = next_date

date_intervals.pop()

# Create a CSV file for output
with open(source_file, 'w', newline='') as csvfile:
    csv_writer = csv.writer(csvfile)

    # Write headers
    headers = ['Package']
    for start, end in date_intervals:
        header = f"{start.strftime('%b %d, %Y')} - {end.strftime('%b %d, %Y')}"
        headers.append(header)
    csv_writer.writerow(headers)

    # Iterate through each package
    for package_info in headers[1:]:
        package_name = package_info
        row_data = [package_name]

        # Initialize a dictionary to store velocity values for each date
        velocity_values = {}

        file_name = f"data/metrics/{package_name}_{metric}.csv"

        try:
            with open(file_name, 'r') as csv_file:
                csv_reader = csv.reader(csv_file)
                next(csv_reader)  # Skip the header row
                for row in csv_reader:
                    date_str, value = row
                    date = datetime.strptime(date_str, '%b %d, %Y')

                    velocity_values[date] = int(value)
                    
        except FileNotFoundError:
            pass

        # Calculate the average velocity values for each date interval
        for start, end in date_intervals:
            dates_in_range = [start + timedelta(days=i) for i in range((end - start).days + 1)]
            values_in_range = [velocity_values[date] for date in dates_in_range if date in velocity_values.keys()]  # Collect values for the dates in the range
            # Now you can use the 'values_in_range' list as needed
            # For example, you can calculate the average velocity within the range
            if len(values_in_range) > 0:
                average_velocity = sum(values_in_range) / len(values_in_range)
            else:
                average_velocity = 0
            
            row_data.append(average_velocity)

        if metric == 'velocity':
            # Step 1: Filter out the 0 values
            filtered_data = [x for x in row_data[1:] if x != 0]

            # Step 2: Calculate the mean of the filtered data
            if len(filtered_data) > 0:
                mean_value = sum(filtered_data) / len(filtered_data)

                first = True
                for i,value in enumerate(row_data):
                    if i > 0:
                        if value == 0 and not first:
                            row_data[i] = mean_value
                        if value != 0 and first:
                            first = False

        if metric == 'downloads':
            first = True
            for i, value in enumerate(row_data):
                if i > 0:
                    #if value == 0 and not first and (i+1) < len(row_data):
                        #row_data[i] = (row_data[i-1] + row_data[i+1]) / 2
                    if value != 0 and first:
                        first = False

        print(row_data)
        csv_writer.writerow(row_data)

print("CSV file has been generated.")