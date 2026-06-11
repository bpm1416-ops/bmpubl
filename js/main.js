const toggle = document.querySelector('.nav-toggle');
const nav = document.getElementById('site-nav');

if (toggle && nav) {
  toggle.addEventListener('click', () => {
    const open = nav.classList.toggle('open');
    toggle.classList.toggle('open', open);
    toggle.setAttribute('aria-expanded', open);
  });

  // Close nav when a link is clicked (mobile)
  nav.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => {
      nav.classList.remove('open');
      toggle.classList.remove('open');
      toggle.setAttribute('aria-expanded', 'false');
    });
  });
}

// Karussell mit Instrument-Tabs
document.querySelectorAll('.carousel-tabs').forEach(tabGroup => {
  const tabs = tabGroup.querySelectorAll('.carousel-tab');
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      const targetId = tab.dataset.target;
      // Alle Karussells in dieser Sektion verstecken
      tabGroup.parentElement.querySelectorAll('.carousel').forEach(c => c.style.display = 'none');
      const target = document.getElementById(targetId);
      if (target) target.style.display = 'flex';
    });
  });
});

// Karussell Navigation
document.querySelectorAll('.carousel').forEach(carousel => {
  const imgs = carousel.querySelectorAll('.carousel-track img');
  const counter = carousel.querySelector('.carousel-counter');
  let current = 0;

  function show(index) {
    imgs.forEach(img => img.classList.remove('active'));
    imgs[index].classList.add('active');
    if (counter) counter.textContent = (index + 1) + ' / ' + imgs.length;
  }

  if (imgs.length > 0) show(0);

  carousel.querySelector('.carousel-prev').addEventListener('click', () => {
    current = (current - 1 + imgs.length) % imgs.length;
    show(current);
  });
  carousel.querySelector('.carousel-next').addEventListener('click', () => {
    current = (current + 1) % imgs.length;
    show(current);
  });
});
