import subprocess, argparse
import pandas as pd

# Define the parameters
ap = argparse.ArgumentParser()
ap.add_argument('-i', '--input-file', required=True, help="File containing intersections.")
ap.add_argument('-o', '--output-folder', required=True, help="Folder containing reviews.")

args = vars(ap.parse_args())

input_file = args['input_file']
output_folder = args['output_folder']

# Define the command template
command_template = "python.exe .\\scripts\\get_reviews_by_date.py -i .\\data\\microblogging-review-set-extended.json -a \"{}\" -d \"{}\" -n 50 -o " + output_folder

intersection = pd.read_csv(input_file, sep=";")

app_names = pd.concat([intersection['App1'], intersection['App2']]).reset_index() # Replace with your app names
date_intervals = pd.concat([intersection['DateInterval1'], intersection['DateInterval2']]).reset_index()  # Replace with your date intervals

# Loop through the parameters and run the command
for i, app_name in enumerate(app_names[0]):
    command = command_template.format(app_name, date_intervals.iloc[i, 1])
    print(f"Running command for app '{app_name}' and date interval '{date_intervals.iloc[i, 1]}':\n{command}")
    
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    print(f"Command output:\n{result.stdout}")
    print(f"Command error output:\n{result.stderr}")

