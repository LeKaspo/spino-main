// on load add event handler
document.addEventListener('DOMContentLoaded', async function() {
    // switch through video sources
    const urls = [
        "http://192.168.0.145:8090/?action=stream", //dierekt camera image
        "http://localhost:5000/video_gesture", //camera image with gesture recognition overlay
        "http://localhost:5000/video_label", //camera image with label recognition overlay not yet implementet
        "http://localhost/8080", //lidar map, not yet implementen, probaply diffrent url
    ];
    const descriptions = [
        "regular view", 
        "gesture recognition", 
        "label recognition", 
        "lidar map", 
    ];
    let currentIndex = 0;
    function updateStream() {
        document.getElementById('stream').src = urls[currentIndex];
        document.getElementById('video-description').innerText = descriptions[currentIndex]
    }
    document.querySelector('.arrow.left').addEventListener('click', () => {
        currentIndex = (currentIndex - 1 + urls.length) % urls.length;
        updateStream();
    });
    document.querySelector('.arrow.right').addEventListener('click', () => {
        currentIndex = (currentIndex + 1) % urls.length;
        updateStream();
    });

    //send button id to the endpoint
    const actionButtons = document.getElementsByClassName('actionButton');
    for (const button of actionButtons) {
        button.addEventListener('click', function() {
            let payload = { id: this.id };
            if (this.classList.contains('hasParam')) {
                const targetId = this.dataset.paramTarget;
                const input = document.getElementById(targetId)
                if (!verify(this.id, input)) {
                    return;
                }
                payload.param = input.value;
            }
            fetch('/button-click', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
            });
        });
    }

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

    //mode switching
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
                if (button.classList.contains('textDe')){
                    button.textContent = `de${button.textContent}`
                    button.classList.add('text');
                    button.classList.remove('textDe');
                }
            } else {
                button.classList.remove('active');
                if (button.classList.contains('text')){
                    button.textContent = button.textContent.slice(2)
                    button.classList.add('textDe');
                    button.classList.remove('text');
                }
            }
            saveStatus(modesArray)
        });
    });
    // make buttons that can't be used gray
    deactiveButtons(modesArray[0]); //on load
    document.getElementById('modebtn').addEventListener("click", () => { //if button mode gets deactivated
        deactiveButtons(modesArray[0]);
    });

    //loger boxen update if there is new content
    const box1 = document.getElementById("box1");
    const box2 = document.getElementById("box2");
    const es = new EventSource("/api/logs/stream");
    es.addEventListener("box1", (evt) => {
        const payload = JSON.parse(evt.data);
        box1.value = payload.text || "";
        box1.scrollTop = box1.scrollHeight;
    });
    es.addEventListener("box2", (evt) => {
        const payload = JSON.parse(evt.data);
        box2.value = payload.text || "";
        box2.scrollTop = box2.scrollHeight;
    });
    // clear button for logger box
    const clearbtn = document.getElementsByClassName('clearbtn');
    for (const button of clearbtn) {
        button.addEventListener('click', function() {
        fetch('/api/clear', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id: this.id })
            });
        });
    }
});

// helper funktions
function deactiveButtons(btnsActive) {
    const controlbtns = [
        document.getElementById('turn180'),
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

// get and save system_status
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

// check if setSpeed input is valid
function verify(id, input) {
  if (!input) return false;
    const raw = input.value.trim();
    if (raw === '') return false;

  if (id == "setSpeed")
  {
    const val = Number(raw);
    if (Number.isNaN(val)) return false;

    const min = input.min ? Number(input.min) : 0.01;
    const max = input.max ? Number(input.max) : 1;
    if (val < min || val > max) {
        return false;
    }
  }
  return true;
}



