function fetchData() {
    fetch('scripts/get_latest_data.php')
    .then(response => response.text())
    .then(data => {
        document.getElementById('dataDisplay').innerText = data;
    })
    .catch(error => console.error('Error fetching data: ', error));
}
setInterval(fetchData, 1000);