<?php
// Reads data from appsrc/data.txt
$filePath = '../data.txt';

if (file_exists($filePath) && is_readable($filePath)) {
  $lines = file($filePath);
  $lastLine = end($lines);
  echo $lastLine;

} else {
    echo 'The Park It! system is offline. Live data is not available.';
}
?>
