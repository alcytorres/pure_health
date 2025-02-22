document.addEventListener('DOMContentLoaded', () => {
  const dayCircles = document.querySelectorAll('.day-circle');
  const infoPanel = document.getElementById('day-info');

  // NEW: Dynamic day info based on data type
  dayCircles.forEach(circle => {
    circle.addEventListener('click', () => {
      const day = circle.getAttribute('data-day');
      const value = circle.getAttribute('data-value');
      if (day !== "0") {
        // NEW: Updated format with commas, units, and capitalized month
        const monthAbbr = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][parseInt(document.getElementById('month').value) - 1];
        const numericValue = dataType === 'steps' ? parseInt(value) : parseFloat(value).toFixed(1);
        const displayValue = dataType === 'steps' ? numericValue.toLocaleString() : numericValue;
        infoPanel.textContent = `${monthAbbr} ${day}: ${displayValue} ${chartUnit}`;
      }
    });
  });

  if (typeof chartLabels !== 'undefined' && typeof chartValues !== 'undefined') {
    const ctx = document.getElementById('lineChart').getContext('2d');
    const chart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: chartLabels,
        datasets: [{
          // NEW: Dynamic label
          label: 'Average ' + chartLabel,
          data: chartValues,
          borderColor: '#00adee',
          backgroundColor: 'rgba(0, 173, 238, 0.2)',
          fill: true,
          tension: 0.2,
          pointRadius: 3,
          pointBackgroundColor: '#00adee'
        }]
      },
      options: {
        scales: {
          y: {
            beginAtZero: true,
            title: {
              display: true,
              // NEW: Dynamic y-axis title
              text: chartUnit.charAt(0).toUpperCase() + chartUnit.slice(1)
            }
          },
          x: {
            title: {
              display: true,
              text: 'Date Range'
            }
          }
        },
        plugins: {
          legend: {
            display: true
          }
        }
      }
    });
  }
});



