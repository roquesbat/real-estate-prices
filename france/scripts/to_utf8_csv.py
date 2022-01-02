import subprocess

subprocess.call(
    ["php", "to_utf8_csv.php", "prices-Yvelines-2021-12-31-no-duplicates-sorted.csv"]
)
