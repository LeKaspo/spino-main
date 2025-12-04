document.addEventListener('DOMContentLoaded', async function() {
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

    //anzeige welche modi aktiviert sind
    const conf = await fetchStatus();
    const modesArray = [
        conf.button_mode_active,
        conf.voice_mode_active,
        conf.gesture_mode_active,
        conf.label_mode_active
    ]

    const modiButtons = document.querySelectorAll('.modiButton');
    modiButtons.forEach((button, i) => {
        if (modesArray[i] == true) {
            button.classList.add('active');
        } else {
            button.classList.remove('active');
        }
        button.addEventListener("click", () => {
            modesArray[i] = !modesArray[i]
            if (modesArray[i] == true) {
                button.classList.add('active');
            } else {
                button.classList.remove('active');
            }
            saveStatus(modesArray)
        });
    });
    deactiveButtons(modesArray[0]);

    document.getElementById('modebtn').addEventListener("click", () => {
        deactiveButtons(modesArray[0]);
    });
});

//Hilfsfunktion für Button deaktivierung
function deactiveButtons(btnsActive) {
    const controlbtns = [
        document.getElementById('start'),
        document.getElementById('undoMovement'),
        document.getElementById('q'),
        document.getElementById('w'),
        document.getElementById('e'),
        document.getElementById('a'),
        document.getElementById('s'),
        document.getElementById('d'),
    ];
    controlbtns.forEach(button => {
        if (btnsActive == true){
            button.disabled = false;
            button.classList.remove("deactivated");
        } else {
            button.disabled = true;
            button.classList.add("deactivated");
        }
    });
}

//Hilfsfunktionen für zugrif auf config
async function fetchStatus() {
  const res = await fetch('/api/config'); 
  if (!res.ok) throw new Error('GET /api/config failed');
  return await res.json(); 
}
async function saveStatus(modesArray) {
    const keys = [
        'button_mode_active',
        'voice_mode_active',
        'gesture_mode_active',
        'label_mode_active'
    ];
    const status = {};
    keys.forEach((key, index) => {
        status[key] = !!modesArray[index]; 
    });
    const res = await fetch('/api/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(status),
    });
    if (!res.ok) throw new Error('POST /api/config failed');
}
