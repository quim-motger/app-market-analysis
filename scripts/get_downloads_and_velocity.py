import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import csv

# Function to extract data from HTML source
def extract_data(html_source):
    soup = BeautifulSoup(html_source, 'html.parser')
    dl_data = []
    velocity_data = []
    
    for path in soup.find_all('path'):
        data_series = path.get('data-series')
        data_v = path.get('data-v')
        
        if data_series == 'dl':
            date_timestamp, value = map(int, data_v.strip('[]').split(','))
            date = datetime.fromtimestamp(date_timestamp).strftime("%b %d, %Y")
            dl_data.append((date, value))
        elif data_series == 'velocity':
            date_timestamp, value = map(int, data_v.strip('[]').split(','))
            date = datetime.fromtimestamp(date_timestamp).strftime("%b %d, %Y")
            velocity_data.append((date, value))
    
    return dl_data, velocity_data

# Function to process data for a given package and save to CSV
def process_package(package):
    url = f'https://www.appbrain.com/chart.svg?type=downloads&pkg={package}'
    
    # Send an HTTP GET request
    response = requests.get(url)
    
    if response.status_code == 200:
        dl_data, velocity_data = extract_data(response.text)
        save_to_csv(package, 'downloads', dl_data)
        save_to_csv(package, 'velocity', velocity_data)
    else:
        print(f"Failed to retrieve data for package: {package}")

# Function to save data to CSV
def save_to_csv(package, data_type, data):
    file_name = f"data/metrics/{package}_{data_type}.csv"
    
    with open(file_name, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['Date', 'Value'])
        csv_writer.writerows(data)
        print(f"Saved data to {file_name}")

# Specify the JSON file path
json_file_path = 'data/query/twitter-related-apps.json'

# Read JSON data from the file
with open(json_file_path, 'r') as json_file:
    json_data = json.load(json_file)

# Process JSON data
for item in json_data:
    package = item['package']
    process_package(package)