document.addEventListener('DOMContentLoaded', function () {
    // Only run on pages that have the prediction chart canvas
    if (document.getElementById('predictionChart')) {
        fetchPrediction();
    }
});

function fetchPrediction() {
    fetch('/api/prediction')
        .then(response => response.json())
        .then(data => {
            renderPredictionChart(data);
            updatePredictionText(data);
        })
        .catch(error => console.error('Error fetching prediction:', error));
}

function updatePredictionText(data) {
    const textElement = document.getElementById('predictionText');
    if (!textElement) return;

    if (data.predicted_amount > 0) {
        textElement.innerHTML = `Forecast for <strong>${data.prediction_month}</strong>: <span class="text-primary">₹${data.predicted_amount}</span>`;
    } else {
        textElement.innerText = "Not enough data to generate a forecast.";
    }
}

function renderPredictionChart(data) {
    const canvas = document.getElementById('predictionChart');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const labels = data.labels;
    const actuals = data.actuals;

    // Create a combined dataset for visualization
    const chartLabels = [...labels, data.prediction_month];

    // Actuals dataset: ends at the last actual point
    const actualDataPoints = [...actuals, null];

    // Prediction dataset should start from the last actual point to connect the line
    const lastActual = actuals[actuals.length - 1];
    const predictionDataPoints = new Array(actuals.length - 1).fill(null);
    predictionDataPoints.push(lastActual);
    predictionDataPoints.push(data.predicted_amount);

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: chartLabels,
            datasets: [
                {
                    label: 'Actual Spending',
                    data: actualDataPoints,
                    borderColor: '#4e73df',
                    backgroundColor: 'rgba(78, 115, 223, 0.1)',
                    fill: true,
                    tension: 0.3
                },
                {
                    label: 'Predicted',
                    data: predictionDataPoints,
                    borderColor: '#f6c23e',
                    borderDash: [5, 5],
                    backgroundColor: 'rgba(246, 194, 62, 0.1)',
                    fill: false,
                    tension: 0.3,
                    pointRadius: 5,
                    pointBackgroundColor: '#f6c23e'
                }
            ]
        },
        options: {
            responsive: true,
            plugins: {
                tooltip: {
                    mode: 'index',
                    intersect: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function (value) {
                            return '₹' + value;
                        }
                    }
                }
            }
        }
    });
}
