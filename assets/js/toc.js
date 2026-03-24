(function() {
  var article = document.querySelector('article .page-content');
  var tocList = document.getElementById('toc-list');
  if (!article || !tocList) return;

  var headings = article.querySelectorAll('h2, h3');
  if (headings.length < 2) {
    var sidebar = document.getElementById('toc-sidebar');
    if (sidebar) sidebar.style.display = 'none';
    return;
  }

  headings.forEach(function(h) {
    var li = document.createElement('li');
    li.className = 'toc-item toc-' + h.tagName.toLowerCase();
    var a = document.createElement('a');
    a.href = '#' + h.id;
    a.textContent = h.textContent.replace(/^#\s*/, '');
    a.addEventListener('click', function(e) {
      e.preventDefault();
      h.scrollIntoView({ behavior: 'smooth' });
      history.pushState(null, null, '#' + h.id);
    });
    li.appendChild(a);
    tocList.appendChild(li);
  });

  var tocLinks = tocList.querySelectorAll('a');
  var observer = new IntersectionObserver(function(entries) {
    entries.forEach(function(entry) {
      if (entry.isIntersecting) {
        tocLinks.forEach(function(link) { link.classList.remove('active'); });
        var active = tocList.querySelector('a[href="#' + entry.target.id + '"]');
        if (active) active.classList.add('active');
      }
    });
  }, { rootMargin: '0px 0px -70% 0px', threshold: 0 });

  headings.forEach(function(h) { observer.observe(h); });
})();
