<?php
// list_images.php
$directory = './gallery';
$images = glob($directory . "/*.png");
echo json_encode($images);
?>
