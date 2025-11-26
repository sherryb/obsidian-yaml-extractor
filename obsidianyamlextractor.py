#----------------------------------
# IMPORTS BLOCK
#----------------------------------
try:
    import sys
    import os
    import re
    import yaml
    import csv
    from io import StringIO
    from datetime import datetime

except ImportError as e:
    print(e)

#--------------------------------
# Get the Obsidian daily notes directory from the user.
# Note for users: on windows this is typically C:\Users\{Username}\Obsidian\Vault\{etc}
# Refer to Obsidian to get the actual vault directory if needed.
#--------------------------------
user_dir = input("Please enter the Obsidian daily notes directory:\n")


#----------------------------------
# Parse YAML from the raw data
#----------------------------------
def parse_yaml(dailynote):

    # The magic regex
    pattern = re.compile(r"^---\s*\n(.*?)\n---\s*", re.DOTALL | re.MULTILINE)

    yaml_chunks = []
    for match in pattern.findall(dailynote):
        try:
            data = yaml.safe_load(match)
            if isinstance(data, dict):
                yaml_chunks.append(data)
        except yaml.YAMLError as e:
            print(f"YAML error: {e}")

    return yaml_chunks


#----------------------------------
# Get Data - iterate through documents and parse the text
# I haven't fully tested this but I think it will work as intended.
# It certainly does for now but I may need to refactor this slightly when 2026 rolls around.
#----------------------------------
def get_data():
    all_yaml_data = []

    for folder in os.listdir(user_dir):
        folder_path = os.path.join(user_dir, folder)

        # Skip non-directories (like stray files)
        if not os.path.isdir(folder_path):
            continue

        for month in os.listdir(folder_path):
            month_path = os.path.join(folder_path, month)
            if not os.path.isdir(month_path):
                continue

            for day in os.listdir(month_path):
                daypath = os.path.join(month_path, day)
                if not os.path.isfile(daypath):
                    continue

                try:
                    with open(daypath, "r", encoding="utf-8") as f:
                        raw_text = f.read()
                        yaml_chunks = parse_yaml(raw_text)

                        # Flatten all YAML blocks and tag each with date
                        for chunk in yaml_chunks:
                            # Optionally store date (remove '.md' or other extensions)
                            chunk["date"] = os.path.splitext(day)[0]
                            all_yaml_data.append(chunk)

                except UnicodeDecodeError:
                    pass

    return all_yaml_data



def prepare_csv(datadict : dict):

    if isinstance(datadict, dict):
        datadict = [datadict]

    elif not isinstance(datadict, list):
        raise TypeError("Must pass dict or list of dicts")

    headers = sorted({key for item in datadict for key in item.keys()})

    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=headers)
    writer.writeheader()
    writer.writerows(datadict)

    return output.getvalue()



if __name__ == "__main__":
    yamldata = get_data()
    csv = prepare_csv(yamldata)

    outputdir = input("Please enter the output directory: ")
    if not os.path.isdir(outputdir):
        os.mkdir(outputdir)

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    with open(f"{outputdir}\\output-{timestamp}.csv", "w", newline="") as f:
        f.write(csv)
        print("Daily note data dumped to CSV, have a nice day :)")



