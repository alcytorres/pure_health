// NEW: Simple script to handle click events on day circles
document.addEventListener('DOMContentLoaded', () => {
  const dayCircles = document.querySelectorAll('.day-circle');
  const infoPanel = document.getElementById('day-info');

  dayCircles.forEach(circle => {
    circle.addEventListener('click', () => {
      // Read data attributes
      const day = circle.getAttribute('data-day');
      const steps = circle.getAttribute('data-steps');

      // If this is a real day (day != 0), show steps
      if (day !== "0") {
        infoPanel.textContent = `Day ${day}: Steps = ${steps}`;
      }
    });
  });
});
