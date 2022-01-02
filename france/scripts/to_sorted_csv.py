import csv
import sys
from unidecode import unidecode

unsorted_csv_filename = sys.argv[1]

with open(unsorted_csv_filename, newline="") as csvfile:
    csvreader = csv.DictReader(csvfile)
    sortedlist = sorted(
        csvreader, key=lambda row: unidecode(row["city_name"]), reverse=False
    )


with open(unsorted_csv_filename.replace(".csv", "-sorted.csv"), "w") as f:
    fieldnames = ["city_name", "low_price", "medium_price", "high_price"]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for row in sortedlist:
        writer.writerow(row)
