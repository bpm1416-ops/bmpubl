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

// Cover-Karussell im Buch-Hero
document.querySelectorAll('.cover-carousel').forEach(carousel => {
  const imgs = carousel.querySelectorAll('.cover-carousel-stage img');
  const label = carousel.querySelector('.cover-carousel-label');
  const dotsWrap = carousel.querySelector('.cover-carousel-dots');
  let current = 0;

  const dots = Array.from(imgs).map((img, i) => {
    const dot = document.createElement('button');
    dot.type = 'button';
    dot.setAttribute('aria-label', 'Cover ' + img.dataset.label + ' anzeigen');
    dot.addEventListener('click', () => show(i));
    dotsWrap.appendChild(dot);
    return dot;
  });

  function show(index) {
    current = (index + imgs.length) % imgs.length;
    imgs.forEach((img, i) => img.classList.toggle('active', i === current));
    dots.forEach((dot, i) => dot.classList.toggle('active', i === current));
    if (label) label.textContent = imgs[current].dataset.label;
  }

  show(0);
  carousel.querySelector('.cover-carousel-prev').addEventListener('click', () => show(current - 1));
  carousel.querySelector('.cover-carousel-next').addEventListener('click', () => show(current + 1));
});
