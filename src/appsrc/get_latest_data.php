<?php
// Specify the same file used in data_receiver.php
$filePath = './data.txt';

// Check if the data file exists and is readable
if (file_exists($filePath) && is_readable($filePath)) {
  $lines = file($filePath);
  $lastLine = end($lines);
  echo $lastLine;

} else {
    // If the file doesn't exist or isn't readable, return an error message
    echo 'The Park It! system is offline. Live data is not available.';
}
?>
