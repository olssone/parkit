<?php
// File paths
$filePath1 = '../data.txt';
$filePath2 = '../streak.txt';
$filePath3 = '../optimal.txt';

$data = array();

// Read from filePath1
if (file_exists($filePath1) && is_readable($filePath1)) {
    $data['data'] = trim(file_get_contents($filePath1));
    $data['sysstatus'] = "Online";
} else {
    $data['data'] = 'N/A - N/A';
    $data['sysstatus'] = "Offline";
}

// Read from filePath2
if (file_exists($filePath2) && is_readable($filePath2)) {
    $data['streak'] = trim(file_get_contents($filePath2)); // Similarly, read the whole file
} else {
    $data['streak'] = 'N/A';
}

// Read from filePath3
if (file_exists($filePath3) && is_readable($filePath3)) {
    $content = file_get_contents($filePath3);
    $fields = str_getcsv(trim($content)); // Use str_getcsv to parse the CSV-formatted string
    $data['occupiedPercentage'] = isset($fields[0]) ? $fields[0] : 'NULL'; // Check if index exists
    $data['unoccupiedPercentage'] = isset($fields[1]) ? $fields[1] : 'NULL'; // Check if index exists
    $data['optimalTime'] = isset($fields[2]) ? $fields[2] : 'NULL'; // Check if index exists
} else {
    $data['occupiedPercentage'] = 'NULL';
    $data['unoccupiedPercentage'] = 'NULL';
    $data['optimalTime'] = 'NULL';
}

// Return both values in JSON format
echo json_encode($data);
?>
