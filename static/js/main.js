// Mobile hamburger menu
document.addEventListener('DOMContentLoaded', function () {
  const hamburger = document.getElementById('hamburger-btn');
  const mobileNav = document.getElementById('mobile-nav');

  if (hamburger && mobileNav) {
    hamburger.addEventListener('click', function () {
      mobileNav.classList.toggle('open');
      const icon = hamburger.querySelector('i');
      if (icon) {
        icon.classList.toggle('fa-bars');
        icon.classList.toggle('fa-times');
      }
    });
    // Close on outside click
    document.addEventListener('click', function (e) {
      if (!hamburger.contains(e.target) && !mobileNav.contains(e.target)) {
        mobileNav.classList.remove('open');
        const icon = hamburger.querySelector('i');
        if (icon) { icon.classList.add('fa-bars'); icon.classList.remove('fa-times'); }
      }
    });
  }

  // Confirm dialogs for destructive actions
  document.querySelectorAll('[data-confirm]').forEach(function (el) {
    el.addEventListener('click', function (e) {
      if (!confirm(el.dataset.confirm)) {
        e.preventDefault();
        return false;
      }
    });
  });

  // Slider live value display
  document.querySelectorAll('input[type=range][data-display]').forEach(function (slider) {
    const display = document.getElementById(slider.dataset.display);
    if (display) {
      display.textContent = slider.value;
      slider.addEventListener('input', function () {
        display.textContent = this.value;
      });
    }
  });

  // Auto-close flash messages
  setTimeout(function () {
    document.querySelectorAll('.alert[data-auto-close]').forEach(function (el) {
      el.style.transition = 'opacity 0.5s';
      el.style.opacity = '0';
      setTimeout(function () { el.remove(); }, 500);
    });
  }, 5000);
});
