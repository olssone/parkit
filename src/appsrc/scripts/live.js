async function fetchAndParseCSV() {
    const url = 'csv/parkit-data.csv'; // Adjust the path to your CSV file

    try {
        const response = await fetch(url);
        const data = await response.text();
        const lines = data.split('\n');
        
        // Process lines to find the first timestamp
        for (let i = 0; i < lines.length; i++) {
            // Skip empty lines, headers (assuming the first line is a header), and comments
            if (i === 0 || lines[i].startsWith('#') || lines[i].trim() === '') {
                continue;
            }
            const entries = lines[i].split(',');
            const timestamp = entries[2].trim(); 
            console.log(timestamp);
            document.getElementById('sysStarted').innerText = "System Started On: " + timestamp;
            break;
        }
    } catch (error) {
        console.error('Error fetching or parsing the CSV file:', error);
    }
}

function fetchData() {
    fetch('scripts/get_latest_data.php')
    .then(response => response.json())
    .then(data => {
        console.log(data);
        const dataContent = data.data;
        const streakContent = data.streak;
        const sysStatus = data.sysstatus;

        document.getElementById('dataDisplay').innerText = dataContent;
        document.getElementById('streakDisplay').innerText = streakContent;
        var status = document.getElementById('sysStatus');
        if (sysStatus.includes("Online")) {
            status.innerText = "System Status: Online";
            // This will change the sysStarted id in live.html
            fetchAndParseCSV();
        } else {
            document.getElementById('sysStatus').innerText = "System Status: Offline";
            document.getElementById('sysStarted').innerText = "System Started On: N/A";
        }
        
    })
    .catch(error => console.error('Error fetching data: ', error));
}



setInterval(fetchData, 1000);
