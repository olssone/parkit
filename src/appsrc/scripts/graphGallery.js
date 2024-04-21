let images = [];
let currentImageIndex = 0;

fetch('scripts/list_graphs.php')
    .then(response => response.json())
    .then(data => {
        images = data;
        if (images.length > 0) {
            showImage(0);
        } else{
            var ele    = document.getElementById('gal');
            var ele2   = document.getElementById('gallery-nav');
            var newele = document.createElement('div');
            var newH2  = document.createElement('h2');
            newH2.textContent = 'No Saved Graphs!';
            newele.appendChild(newH2);
            ele.insertAdjacentElement('afterend', newele);
            ele.remove();
            ele2.remove();
        }
    })
    .catch(error => console.error('Unable to load images:', error));

function showImage(index) {
    currentImageIndex = index;
    document.getElementById('galleryImage').src = images[index];
    const filename = images[index].split('/').pop();
    document.getElementById('caption').innerText = formatDateString(filename);
    updateNavigation();
}

function updateNavigation() {
    document.getElementById('prevButton').style.display = currentImageIndex > 0 ? '' : 'none';
    document.getElementById('nextButton').style.display = currentImageIndex < images.length - 1 ? '' : 'none';
}

function nextImage() {
    if (currentImageIndex < images.length - 1) {
        showImage(currentImageIndex + 1);
    }
}

function previousImage() {
    if (currentImageIndex > 0) {
        showImage(currentImageIndex - 1);
    }
}

function saveImage() {
    const currentImage = images[currentImageIndex];
    const link = document.createElement('a');
    link.href = currentImage;
    link.download = currentImage.split('/').pop();
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

function formatDateString(inputString) {
    // Extract the date and time part from the input string
    const dateTimePattern = /(\d{4})-(\d{2})-(\d{2})-(\d{2})-(\d{2})-(\d{2})/;
    const match = inputString.match(dateTimePattern);

    if (!match) {
        return "Invalid input string";
    }

    // Create a new Date object from the extracted parts
    const year = match[1];
    const month = parseInt(match[2], 10) - 1; // Month index is 0-based in JavaScript
    const day = match[3];
    const hour = match[4];
    const minute = match[5];
    const second = match[6];
    const date = new Date(year, month, day, hour, minute, second);

    // Define options for formatting the date
    const options = {
        weekday: 'long', // e.g., Monday
        year: 'numeric', // e.g., 2024
        month: 'long', // e.g., April
        day: 'numeric', // e.g., 19
        hour: 'numeric', // e.g., 13
        minute: 'numeric', // e.g., 30
        second: 'numeric', // e.g., 35
        hour12: false // Use 24-hour format
    };

    // Use toLocaleDateString for locale-specific output
    return "Graph generated: " + date.toLocaleDateString('en-US', options);
}