// NEW: Handle drop-down functionality
function closeAllDropdowns() {
  document.querySelectorAll('.dropdown').forEach(dropdown => {
    dropdown.style.display = 'none';
  });
}

document.querySelectorAll('.form-select-button').forEach(button => {
  button.addEventListener('click', function(e) {
    closeAllDropdowns();
    const dropdown = this.nextElementSibling;
    if (dropdown && dropdown.classList.contains('dropdown')) {
      dropdown.style.display = 'block';
    }
  });
});

document.querySelectorAll('.dropdown').forEach(dropdown => {
  dropdown.addEventListener('click', function(e) {
    if (e.target.tagName === 'LI') {
      const selectedValue = e.target.getAttribute('data-value');
      const button = this.previousElementSibling;
      button.innerText = selectedValue;
      const hiddenInputId = button.id === 'year-button' ? 'hidden-year' : 'hidden-month';
      document.getElementById(hiddenInputId).value = selectedValue;
      closeAllDropdowns();
    } else {
      closeAllDropdowns();
    }
  });
});

// NEW: Close drop-downs when clicking outside
document.addEventListener('click', function(e) {
  if (!e.target.closest('.month-year-form')) {
    closeAllDropdowns();
  }
});