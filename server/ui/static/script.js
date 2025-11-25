document.addEventListener('DOMContentLoaded', function() {
    
// Speicherkonstante für gedrückthalten
const pressedKeys = new Set();

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