import csv
from unidecode import unidecode
from more_itertools import unique_everseen
import subprocess
import sys

csv_filename = sys.argv[1]
fieldnames = ["city_name", "low_price", "medium_price", "high_price"]
no_duplicates_csv_filename = csv_filename.replace(".csv", "-no-duplicates.csv")

with open(csv_filename, "r") as f, open(no_duplicates_csv_filename, "w") as out_file:
    out_file.writelines(unique_everseen(f))

with open(no_duplicates_csv_filename, newline="") as csvfile:
    csvreader = csv.DictReader(csvfile)
    sortedlist = sorted(
        csvreader, key=lambda row: unidecode(row["city_name"]), reverse=False
    )

sorted_csv_filename = no_duplicates_csv_filename.replace(".csv", "-sorted.csv")

with open(sorted_csv_filename, "w") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for row in sortedlist:
        writer.writerow(row)

subprocess.call(["php", "to_utf8_csv.php", sorted_csv_filename])
