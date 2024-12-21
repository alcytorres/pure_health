document.addEventListener('DOMContentLoaded', () => {
  // Existing day-circle click handling
  const dayCircles = document.querySelectorAll('.day-circle');
  const infoPanel = document.getElementById('day-info');

  dayCircles.forEach(circle => {
    circle.addEventListener('click', () => {
      const day = circle.getAttribute('data-day');
      const steps = circle.getAttribute('data-steps');
      if (day !== "0") {
        infoPanel.textContent = `Day ${day}: Steps = ${steps}`;
      }
    });
  });

  // NEW: Render the line chart using the data from the template
  if (typeof chartLabels !== 'undefined' && typeof chartValues !== 'undefined') {
    const ctx = document.getElementById('lineChart').getContext('2d');
    const chart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: chartLabels,
        datasets: [{
          label: 'Average Steps',
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
              text: 'Steps'
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
