<?php

/**
 * Export an array as downladable Excel CSV
 * @param array   $header
 * @param array   $data
 */
function toUTF8CSV($header, $data)
{
    $sep  = ",";
    $eol  = "\n";
    $csv  =  count($header) ? '"' . implode('"' . $sep . '"', $header) . '"' . $eol : '';
    foreach ($data as $line) {
        $csv .= '"' . implode('"' . $sep . '"', $line) . '"' . $eol;
    }
    $encoded_csv = mb_convert_encoding($csv, 'UTF-16LE', 'UTF-8');

    return chr(255) . chr(254) . $encoded_csv;
}


$csv_filename = $argv[1];

if (($handle = fopen($csv_filename, 'r')) === false) {
    echo 'error while opening ' . $csv_filename;
    exit;
}

if (($header = fgetcsv($handle, 1000, ",")) === false) {
    echo 'error while getting csv header of ' . $csv_filename;
    exit;
}

$rows = [];
while (($row = fgetcsv($handle, 1000, ",")) !== false) {
    $rows[] = $row;
}

fclose($handle);

$csv_UTF8 = toUTF8CSV($header, $rows);
$handle = fopen(str_replace('.csv', '-utf8.csv', $csv_filename), 'w');
fwrite($handle, $csv_UTF8);
fclose($handle);
