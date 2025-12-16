// on load add event handler
document.addEventListener('DOMContentLoaded', async function() {
    // switch through video sources
    const urls = [
        "http://192.168.0.145:8090/?action=stream", //dierekt camera image
        "http://localhost:5000/video_gesture", //camera image with gesture recognition overlay
    ];
    const descriptions = [
        "regular view", 
        "gesture recognition", 
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
        conf.label_mode_active,
        conf.roaming_mode_active,
        conf.obsticle_detection_active,
        conf.slam_active,
        conf.visualiation_active
    ]
    
    // get the buttons in the right order to avoid bugs
    const modeIds = [
    'modebtn',     
    'modevoice',   
    'modegesture', 
    'modelabel',   
    'moderoam',    
    'modeod',     
    'modeslam',   
    'modevisual'  
    ];
    const modiButtons = modeIds.map(id => document.getElementById(id)).filter(Boolean);
    modiButtons.forEach((button, i) => {
    if (modesArray[i] === true) {
        button.classList.add('active');
    } else {
        button.classList.remove('active');
    }
    button.addEventListener('click', () => {
        modesArray[i] = !modesArray[i];
        updateButtonUI(button, modesArray[i]);
        enforceExclusivity(i, modesArray); 
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
        const beforeLast = payload.text.slice(0, payload.text.lastIndexOf("\n"));
        const prevNL = beforeLast.lastIndexOf("\n");
        let penultimate = prevNL >= 0 ? beforeLast.slice(prevNL + 1) : beforeLast;
        if (penultimate.includes("emergency stop")) { //react to emergency stop
            document.getElementById("ackstop").classList.remove("deactivated");
            document.getElementById("ackstop").disabled = false;
            console.log("emergency im log gelesen")
            if (modesArray[4] === true)
            {
                simulateClick(document.getElementById("moderoam"));
            }
        }
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
    //emergenvy stop design
    document.getElementById("ackstop").addEventListener('click', () => {
            document.getElementById("ackstop").disabled = true;
            document.getElementById("ackstop").classList.add("deactivated");
            console.log("stop ack gedrückt")
        });

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
        'label_mode_active',
        'roaming_mode_active',
        "obsticle_detection_active",
        "slam_active",
        "visualiation_active"
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

// if free roam is activated all other modes get deactivated
function enforceExclusivity(changedIndex, modesArray) {
    if (changedIndex === 4 && modesArray[4] === true) {
      const voiceBtn = document.getElementById('modevoice');
      const gestureBtn = document.getElementById('modegesture');
      const buttonBtn = document.getElementById('modebtn');

      if (modesArray[1] && voiceBtn)   simulateClick(voiceBtn);
      if (modesArray[2] && gestureBtn) simulateClick(gestureBtn);
      if (modesArray[0] && buttonBtn)  simulateClick(buttonBtn);
    }
    if (changedIndex !== 4 && modesArray[changedIndex] === true && modesArray[4] === true) {
    const roamBtn = document.getElementById('moderoam');
    if (roamBtn) simulateClick(roamBtn);
    }
  }

// helper for de prefix
function updateButtonUI(button, isActive) {
    if (isActive) {
      button.classList.add('active');
      if (button.classList.contains('textDe')) {
        button.textContent = `de${button.textContent}`;
        button.classList.add('text');
        button.classList.remove('textDe');
      }
    } else {
      button.classList.remove('active');
      if (button.classList.contains('text')) {
        button.textContent = button.textContent.slice(2);
        button.classList.add('textDe');
        button.classList.remove('text');
      }
    }
  }
function simulateClick(el) {
    if (!el) return;
    el.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
  }
