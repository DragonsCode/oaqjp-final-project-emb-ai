const RunSentimentAnalysis = () => {
    const text = document.getElementById("textToAnalyze").value;
    const output = document.getElementById("system_response");
    const xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
        if (this.readyState !== 4) return;
        try {
            output.textContent = JSON.parse(this.responseText).response;
        } catch {
            output.textContent = "Emotion service unavailable. Please try again later.";
        }
    };
    xhttp.onerror = () => {
        output.textContent = "Emotion service unavailable. Please try again later.";
    };
    xhttp.open("GET", "emotionDetector?textToAnalyze=" + encodeURIComponent(text), true);
    xhttp.send();
};
