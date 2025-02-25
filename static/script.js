document.addEventListener('DOMContentLoaded', () => {
  const dayCircles = document.querySelectorAll('.day-circle');
  const infoPanel = document.getElementById('day-info');

  // NEW: Define a variable to store the timeout ID for delaying the hover actions
  let hoverTimeout;

  // NEW: Set default text
  infoPanel.textContent = 'Hover over a day to see details.';

  dayCircles.forEach(circle => {
    // NEW: Use mouseover with a delay
    circle.addEventListener('mouseover', () => {
      clearTimeout(hoverTimeout);
      hoverTimeout = setTimeout(() => {
        const day = circle.getAttribute('data-day');
        const value = circle.getAttribute('data-value');
        if (day !== "0") {
          const monthAbbr = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][parseInt(document.getElementById('month').value) - 1];
          let displayValue;
          // NEW: For steps and calories, format as integer with commas; otherwise, use one decimal.
          if (dataType === 'steps' || dataType === 'calories') {
              displayValue = parseInt(value).toLocaleString();
          } else {
              displayValue = parseFloat(value).toFixed(1);
          }
          infoPanel.textContent = `${monthAbbr} ${day}: ${displayValue} ${chartUnit}`;
        }
      }, 300);
    });

    // NEW: Use mouseout with a delay to reset the text
    circle.addEventListener('mouseout', () => {
      clearTimeout(hoverTimeout); // NEW: Clear any pending update
      hoverTimeout = setTimeout(() => { // NEW: Delay reset by 300ms
        infoPanel.textContent = 'Hover over a day to see details.';
      }, 300); // NEW: 300ms delay
    });
  });

  if (typeof chartLabels !== 'undefined' && typeof chartValues !== 'undefined') {
    const ctx = document.getElementById('lineChart').getContext('2d');
    const chart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: chartLabels,
        datasets: [{
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
          },
          // NEW: Customize tooltip to show only value and unit (e.g., 10,000 steps)
          tooltip: {
            callbacks: {
              label: function(context) {
                const value = context.parsed.y; // Y-axis value (e.g., 20856 for steps)
                let displayValue;
                if (dataType === 'steps') {
                  displayValue = parseInt(value).toLocaleString(); // Add commas (e.g., 20,856)
                } else {
                  displayValue = parseFloat(value).toFixed(1); // One decimal for sleep/hydration (e.g., 8.0, 2.0)
                }
                // NEW: Use shortened units: 'steps' -> 'steps', 'hours' -> 'hrs', 'liters' -> 'L'
                const unit = dataType === 'steps' ? 'steps' : (dataType === 'sleep' ? 'hrs' : 'L');
                return `${displayValue} ${unit}`;
              }
            }
          }
          // REMOVE: Old tooltip format with date
          // label: function(context) {
          //   const label = context.label;
          //   const value = context.parsed.y;
          //   let displayValue;
          //   if (dataType === 'steps') {
          //     displayValue = parseInt(value).toLocaleString();
          //   } else {
          //     displayValue = parseFloat(value).toFixed(1);
          //   }
          //   return `${label}: ${displayValue}`;
          // }
        }
      }
    });
  }
});