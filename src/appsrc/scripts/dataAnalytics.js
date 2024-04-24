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
            document.getElementById('sysStarted').innerText = timestamp;
            break;
        }
    } catch (error) {
        console.error('Error fetching or parsing the CSV file:', error);
    }
}

function convertTime(time) {
    // Extract hours and minutes from the time string
    let [hours, minutes] = time.split(':').map(Number);
    
    // Determine the period (AM or PM)
    let period = hours >= 12 ? 'PM' : 'AM';
    
    // Convert hours to 12-hour format
    hours = hours % 12;
    hours = hours ? hours : 12; // the hour '0' should be '12'

    // Format the hours and minutes to ensure two digits
    hours = hours < 10 ? '0' + hours : hours;
    minutes = minutes < 10 ? '0' + minutes : minutes;

    // Construct the standard time format
    return `${hours}:${minutes} ${period}`;
}

function formatEventDetails(eventString) {
    // Split the input string by spaces to separate the datetime and duration components
    if (eventString != "No Streak Available.") {
        const [startDate, startTime, endDate, endTime, duration] = eventString.split(' ');
     
        // Combine the date and time parts for start and end times
        const startTimeComplete = startDate + ' ' + convertTime(startTime);
        const endTimeComplete = endDate + ' ' + convertTime(endTime);
    
        // Split the duration into hours, minutes, and seconds
        const [hours, mins, secs] = duration.split(':').map(Number);
    
        // Create the formatted string
        var formattedString = `From: ${startTimeComplete} To: ${endTimeComplete} `; 
        if (hours && mins && seconds) {
            formattedString = formattedString + `Duration: ${hours} hours ${mins} minutes and ${secs} seconds`;
        } else if (mins && seconds) {
            formattedString = formattedString + `Duration: ${mins} minutes and ${secs} seconds`;
        } else {
            formattedString = formattedString + `Duration: ${secs} seconds`;
        }
        return formattedString;

    } else{
        return eventString;
    }

}

function fetchData() {
    fetch('scripts/get_latest_data.php')
    .then(response => response.json())
    .then(data => {
        const dataContent = data.data;
        let dataArray = dataContent.split(" - ");
        const occupiedStatus = dataArray[0];
        const spaceStatus = dataArray[1];
        const streakContent = data.streak;
        const sysStatus = data.sysstatus;
        const occupiedPercentage = data.occupiedPercentage;
        const unoccupiedPercentage = data.unoccupiedPercentage;
        const optimalTime = data.optimalTime;

        document.getElementById('occupiedStatus').innerText = occupiedStatus;
        document.getElementById('spaceStatus').innerText = spaceStatus;
        if (streakContent != "N/A") {
            document.getElementById('streakDisplay').innerText = formatEventDetails(streakContent);
        } else {
            document.getElementById('streakDisplay').innerText = "N/A";
        }
        document.getElementById('occupiedPercentage').innerText = occupiedPercentage + "% Occupied";
        document.getElementById('unoccupiedPercentage').innerText = unoccupiedPercentage + "% Unoccupied";
        document.getElementById('optimalTime').innerText = convertTime(optimalTime);

        var status = document.getElementById('sysStatus');
        if (sysStatus.includes("Online")) {
            status.innerText = "Online";
            // This will change the sysStarted id in live.html
            fetchAndParseCSV();
        } else {
            status.innerText = "Offline";
            document.getElementById('sysStarted').innerText = "N/A";
        }
        
    })
    .catch(error => console.error('Error fetching data: ', error));
}

// Fetch the data every second
setInterval(fetchData, 1000);
