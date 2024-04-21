<?php
// Lists all the png file names in gallery
$directory = "../gallery";
$images = glob($directory . "/*.png");
echo json_encode($images);
?>
