document.addEventListener('DOMContentLoaded', function() {

// durch videos switchen
const urls = [
    "http://192.168.0.145:8090/?action=stream", //Camera dierekt
    "{{ url_for('video_gesture') }}", //Camera mit gestenerkennung
    "{{ url_for('video_label') }}", //Camera mit label erkennung, must noch getestet werden
    "http://localhost/8080", //Lider ansicht, subject to change
];
let currentIndex = 0;
const img = document.getElementById('stream');
function updateStream() {
    img.src = urls[currentIndex] + "&t=" + new Date().getTime(); 
}
document.querySelector('.arrow.left').addEventListener('click', () => {
    currentIndex = (currentIndex - 1 + urls.length) % urls.length;
    updateStream();
});
document.querySelector('.arrow.right').addEventListener('click', () => {
    currentIndex = (currentIndex + 1) % urls.length;
    updateStream();
});


// Auswertung Button zum anclicken
const actionButtons = document.getElementsByClassName('actionButton');
for (const button of actionButtons) {
  button.addEventListener('click', function() {
    fetch('/button-click', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id: this.id })
    });
  });
}
// Auswertung Button die nicht an den roboter senden
const insideButtons = document.getElementsByClassName('insideButton');
for (const button of insideButtons) {
  button.addEventListener('click', function() {
    fetch('/button-click-inside', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id: this.id })
    });
  });
}

// Auswertung Button zum gedrückthalten
const holdButtons = document.getElementsByClassName('holdButton');
    for (const button of holdButtons) {
        button.addEventListener('mousedown', function() {
            fetch('/button-press', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id: this.id })
            });
        });
        button.addEventListener('mouseup', function() {
            fetch('/button-release', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id: this.id })
            });
        });
    }


//Auswertung Tastatureingaben
const pressedKeys = new Set();
document.addEventListener('keydown', function(event) {
    if (!pressedKeys.has(event.key)) {
        pressedKeys.add(event.key);
        fetch('/key-down', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ key: event.key })
        });
    }
});
document.addEventListener('keyup', function(event) {
    if (pressedKeys.has(event.key)) {
        pressedKeys.delete(event.key);
        fetch('/key-up', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ key: event.key })
        });
    }
});

});