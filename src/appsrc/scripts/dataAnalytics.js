function updateImage() {
    const img = document.getElementById('dataImage');
    img.src = './png/parkit-data-analytics-graph.png?time=' + new Date().getTime();
}
setInterval(updateImage, 2000);

function saveImage() {
    const img = document.getElementById('dataImage').src;
    const link = document.createElement('a');
    link.href = img;
    link.download = 'parkit-data-analytics-graph.png';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}