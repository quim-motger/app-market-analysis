import json, os, csv, argparse
from datetime import datetime, timedelta

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

start_date = datetime.strptime(t, '%b %d, %Y')
end_date = start_date + timedelta(days=360)

current_date = start_date
dates = []
while current_date <= end_date:
	interval_end_date = current_date + timedelta(days=w-1)
	dates.append((f"{current_date.strftime('%b %d, %Y')} - {interval_end_date.strftime('%b %d, %Y')}"))
	current_date += timedelta(days=w)

def is_date_in_interval(date_str, interval_str):
	date_format = "%b %d, %Y"
	date = datetime.strptime(date_str, date_format)
	interval_start, interval_end = interval_str.split(" - ")

	start_date = datetime.strptime(interval_start, date_format)
	end_date = datetime.strptime(interval_end, date_format)

	return start_date <= date <= end_date

# Open the JSON file
with open(source_file) as json_file:
	# Load the contents of the file
	data = json.load(json_file)

output_data = []
header = ['App / Time window']
for date in dates:
	header.append(date)
output_data.append(header)

print("Iterating over reviews. This might take a while...")

# Convert to JSON for sent service
for i,app in enumerate(data):

	app_data = [0]*(len(dates)+1)
	app_data[0] = app['package_name']
	
	date_sum = [0]*len(dates)
	date_count = [0]*len(dates)

	# Init out structure
	for j,date in enumerate(dates):
		for review in app['reviews']:
			if is_date_in_interval(review['at'], date):
				date_count[j] += 1
				date_sum[j] += review['score'] - 1 # normalized from [1,5] to [0,4]

	for j, result in enumerate(date_sum):
		if date_count[j] > 0:
			app_data[j+1] = date_sum[j] / date_count[j]
		else:
			app_data[j+1] = 0

	output_data.append(app_data)

with open(os.path.join(output_folder, 'review_rating.csv'), 'w', newline='') as csvfile:
	writer = csv.writer(csvfile)
	for row in output_data:
		writer.writerow(row)