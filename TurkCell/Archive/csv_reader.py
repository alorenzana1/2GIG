import csv
import os
included_cols = [3,4,7]

currentPath = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(currentPath, "..", "Americo")
os.chdir(path)

for file in os.listdir(path):
    if file.endswith(".csv"):
        print(file)
        with open(file, 'rt') as file:
            reader = csv.reader(file, delimiter=',')
            for row in reader:
                content = list(row[i] for i in included_cols)
                print content
        os.system("pause")
