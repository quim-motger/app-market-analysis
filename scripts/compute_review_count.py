import argparse
import json
import csv
import matplotlib.pyplot as plt
import os
from datetime import datetime, timedelta
from dateutil.relativedelta import *

def merge_dates_v2(dates_dict, num_bins, w, t):
	
	# Determine the start and end dates. TODO: parameterize end date
	start_date = datetime.strptime(t, '%b %d, %Y')
	end_date = datetime.strptime('Jun 05, 2023', '%b %d, %Y')

	# Convert date strings to datetime objects and sort in ascending order
	date_keys = sorted([datetime.strptime(key, '%b %d, %Y') for key in dates_dict.keys() if datetime.strptime(key, '%b %d, %Y') >= end_date - relativedelta(years=1)])

	# Initialize the new dictionary
	merged_dict = {}

	# Merge the dates into bins and calculate the sum for each bin
	bin_start_date = start_date
	for i in range(num_bins):
		# Determine the end date for the bin
		bin_end_date = bin_start_date + timedelta(days=w-1)
		if bin_end_date > end_date:
			bin_end_date = end_date
		# Create the interval key in the format '%b %d, %Y - %b %d, %Y'
		interval_key = bin_start_date.strftime('%b %d, %Y') + ' - ' + bin_end_date.strftime('%b %d, %Y')
		# Calculate the sum of values for the bin
		sum_values = sum(dates_dict[date.strftime('%b %d, %Y')] for date in date_keys if bin_start_date <= date <= bin_end_date)
		# Add the key-value pair to the new dictionary
		merged_dict[interval_key] = sum_values
		# Update the start date for the next bin
		bin_start_date = bin_end_date + timedelta(days=1)
	return merged_dict


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

with open(source_file, 'r', encoding='utf-8') as file:
	data = json.load(file)

csv_matrix = []

for app in data:

	date_reviews = {}
	if app['reviews'] is not None:
		for review in app['reviews']:
			if 'at' in review:
				if review['at'] not in date_reviews:
					date_reviews[review['at']] = 1
				else:
					date_reviews[review['at']] += 1

	plt.rcParams["figure.autolayout"] = True

	# TODO: parameterize historic data
	date_reviews = merge_dates_v2(date_reviews, int(365/w), w, t)
	
	# If csv_matrix empty, build headers
	if len(csv_matrix) == 0:
		heading = ['App / Time window']
		for key in date_reviews.keys():
			heading.append(key)
		csv_matrix.append(heading)

	# Build csv row
	row = [app['package_name']]
	for val in date_reviews.values():
		row.append(val)
	csv_matrix.append(row)

# Save files
if not os.path.exists(output_folder):
	os.makedirs(output_folder)
		
output_file_path = os.path.join(output_folder, 'review_count.csv')

with open(output_file_path, 'w', newline='') as csvfile:
	writer = csv.writer(csvfile)
	for row in csv_matrix:
		writer.writerow(row)