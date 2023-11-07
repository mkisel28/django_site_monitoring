document.addEventListener('DOMContentLoaded', function() {
  const websiteBlocks = document.querySelectorAll('.website-block');
  
  websiteBlocks.forEach(function(block) {
      block.addEventListener('click', function(e) {
          if (e.target.tagName !== 'A' && !e.target.closest('.toggle-favorite')&& !e.target.closest('.toggle-country-favorite')) {
              const url = block.getAttribute('data-url');
              if (url) {
                  window.location.href = url;
              }
          }
      });
  });
});