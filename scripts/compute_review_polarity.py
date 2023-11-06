import json
import csv
import os
import requests
import argparse
from datetime import datetime, timedelta

ap = argparse.ArgumentParser()
ap.add_argument('-i', '--input-file', required=True, help="Review set.")
ap.add_argument('-w', '--time-window', required=True, help="Time window length.")
ap.add_argument('-t', '--origin-date', required=True, help="Origin date in '%b %d, %Y' format.")
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

import random

def classify_reviews_by_interval(reviews, date_intervals, max_reviews=10):
    classified_reviews = {}

    for interval in date_intervals:
        start_date, end_date = interval.split(' - ')

        start_date = datetime.strptime(start_date, '%b %d, %Y')
        end_date = datetime.strptime(end_date, '%b %d, %Y')

        interval_reviews = []
        reviews_within_interval = []

        for review in reviews:
            review_date = datetime.strptime(review['at'], '%b %d, %Y')

            if start_date <= review_date <= end_date:
                interval_reviews.append(review)

        # Select randomly from interval_reviews
        if len(interval_reviews) <= max_reviews:
            reviews_within_interval = interval_reviews
        else:
            reviews_within_interval = random.sample(interval_reviews, max_reviews)

        classified_reviews[interval] = reviews_within_interval

    return classified_reviews

def calculate_average_values(arr):
    object_averages = []

    for obj in arr:
        text_arr = obj['text']
        average = sum(sub_arr[1] for sub_arr in text_arr) / len(text_arr)
        object_averages.append(average)

    if len(object_averages) > 0:
        overall_average = sum(object_averages) / len(object_averages)
    else:
        overall_average = 0

    return overall_average

def convert_to_json(data, dates):
    csv_data = []
    csv_data.append(dates)

    for app in data:

        reviews = classify_reviews_by_interval(app['reviews'], dates)
        json_data = {'data':[], 'include': [0,1,2,3,4]}

        app_data = [0]*(len(dates)+1)
        app_data[0] = app['package_name']

        count_reviews_per_week = []
        for review_set in reviews.values():

            for review in review_set:
                json_data['data'].append({'id': review['reviewId'], 'text': review['review']})
            count_reviews_per_week.append(len(review_set))

        response = send_post_request(json_data)

        if response is not None:
        
            for i in range(0, len(dates)):
            # Assign the average polarity score for that week
                if i == 0:
                    start_index = 0
                else:
                    start_index = sum(count_reviews_per_week[0:i-1])
                end_index = sum(count_reviews_per_week[0:i]) - 1
                app_data[int(i%len(dates)+1)] = calculate_average_values(response[start_index:end_index])

            csv_data.append(app_data)

        else:
            print("Could not add data for " + app_data[0])

    return csv_data

def send_post_request(json_data):
    # Set the URL for the POST request
    url = 'http://127.0.0.1:5000/polarity'

    # Send the POST request with JSON data as the body
    print('Sending request to sa-filter-tool...')
    response = requests.post(url, json=json_data)

    # Check the response status code
    if response.status_code == 200:
        print('POST request successful!')
        return json.loads(response.content.decode('utf-8'))
    else:
        print('POST request failed. Status code:', response.status_code)
        return None

# Open the JSON file
with open(source_file) as json_file:
    # Load the contents of the file
    data = json.load(json_file)

response = convert_to_json(data, dates)

with open(os.path.join(output_folder, 'review_polarity.csv'), 'w', newline='') as csvfile:
	writer = csv.writer(csvfile)
	for row in response:
		writer.writerow(row)