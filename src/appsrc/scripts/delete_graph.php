<?php
// Authentication and security checks here
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['file'])) {
    $file = $_POST['file'];
    $filePath = '../gallery/' . basename($file); // Prevent directory traversal
    if (file_exists($filePath)) {
        unlink($filePath);
        echo json_encode(['success' => true]);
    } else {
        echo json_encode(['error' => 'File does not exist']);
    }
} else {
    echo json_encode(['error' => 'Invalid request']);
}
?>
