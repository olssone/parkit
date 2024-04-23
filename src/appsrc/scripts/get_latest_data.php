<?php
// File paths
$filePath1 = '../data.txt';
$filePath2 = '../streak.txt';

$data = array();

// Read from filePath1
if (file_exists($filePath1) && is_readable($filePath1)) {
    $data['data'] = trim(file_get_contents($filePath1));
    $data['sysstatus'] = "Online";
} else {
    $data['data'] = 'Live data is not available.';
    $data['sysstatus'] = "Offline";
}

// Read from filePath2
if (file_exists($filePath2) && is_readable($filePath2)) {
    $data['streak'] = trim(file_get_contents($filePath2)); // Similarly, read the whole file
} else {
    $data['streak'] = 'Streak data is not available.';
}

// Return both values in JSON format
echo json_encode($data);
?>
