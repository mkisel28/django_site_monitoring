function getCookie(name) {
  var cookieValue = null;
  if (document.cookie && document.cookie !== '') {
      var cookies = document.cookie.split(';');
      for (var i = 0; i < cookies.length; i++) {
          var cookie = jQuery.trim(cookies[i]);
          // Does this cookie string begin with the name we want?
          if (cookie.substring(0, name.length + 1) === (name + '=')) {
              cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
              break;
          }
      }
  }
  return cookieValue;
}


function hash(string) {
  const utf8 = new TextEncoder().encode(string);
  return crypto.subtle.digest('SHA-256', utf8).then((hashBuffer) => {
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  const hashHex = hashArray
  .map((bytes) => bytes.toString(16).padStart(2, '0'))
  .join('');
  return hashHex;
  });
  }
function getGpuInfo() {
  const canvas = document.createElement('canvas');
  const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');

  if (!gl) {
      return null; 
  }

  const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
  return debugInfo ? {
      vendor: gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL),
      renderer: gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL)
  } : null;
}
let fingerprint = {
  userAgent: navigator.userAgent,
  screenWidth: screen.width,
  screenHeight: screen.height,
  colorDepth: screen.colorDepth,
  timeOffset: new Date().getTimezoneOffset(),
  gpu: getGpuInfo(),

};

function getFingerprint() {
  let fingerprint = {
    userAgent: navigator.userAgent,
    screenWidth: screen.width,
    screenHeight: screen.height,
    colorDepth: screen.colorDepth,
    timeOffset: new Date().getTimezoneOffset(),
    gpu: getGpuInfo(),
  }
  return fingerprint;
}

console.log(JSON.stringify(getFingerprint()));
hash(JSON.stringify(getFingerprint())).then(
  hashedFingerprint =>
  fetch('/api/finger/', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken')
      },
      body: JSON.stringify(hashedFingerprint)
  })
  .then(response => response.json())
  .then(data => console.log('Fingerprint sent:', data))
  
  ); 