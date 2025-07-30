// EFT Tapping Functionality
const eftPoints = [
    { 
        name: "Karate Chop", 
        position: { top: '80%', left: '25%' },
        affirmation: "Even though I feel [issue], I deeply and completely accept myself."
    },
    { 
        name: "Eyebrow", 
        position: { top: '15%', left: '30%' },
        affirmation: "This [issue] I'm feeling"
    },
    { 
        name: "Side of Eye", 
        position: { top: '20%', left: '25%' },
        affirmation: "All this [issue]"
    },
    { 
        name: "Under Eye", 
        position: { top: '30%', left: '30%' },
        affirmation: "I release this [issue]"
    },
    { 
        name: "Under Nose", 
        position: { top: '45%', left: '48%' },
        affirmation: "I choose to feel calm"
    },
    { 
        name: "Chin", 
        position: { top: '55%', left: '48%' },
        affirmation: "I'm letting go of this [issue]"
    },
    { 
        name: "Collarbone", 
        position: { top: '65%', left: '45%' },
        affirmation: "I'm safe and at peace"
    },
    { 
        name: "Under Arm", 
        position: { top: '70%', left: '30%' },
        affirmation: "I release all tension"
    },
    { 
        name: "Top of Head", 
        position: { top: '5%', left: '48%' },
        affirmation: "I'm filled with peace and calm"
    }
];

const eftHighlight = document.getElementById('eftHighlight');
const eftInstructions = document.getElementById('eftInstructions');
const startEftBtn = document.getElementById('startEftBtn');
const pauseEftBtn = document.getElementById('pauseEftBtn');
const eftProgress = document.getElementById('eftProgress');
const eftPointElements = document.querySelectorAll('.eft-point');

let eftInterval;
let isEftActive = false;
let isEftPaused = false;
let currentEftPoint = 0;
let totalEftTime = 600; // 10 minutes
let eftTimeRemaining = totalEftTime;
let tapCount = 0;
const tapsPerPoint = 7; // Number of taps per point
const tapDuration = 1000; // Time between taps in ms

function startEftExercise() {
    if (isEftActive) return;
    
    isEftActive = true;
    startEftBtn.style.display = 'none';
    pauseEftBtn.style.display = 'inline-block';
    currentEftPoint = 0;
    eftTimeRemaining = totalEftTime;
    tapCount = 0;
    
    // Highlight first point
    highlightEftPoint(currentEftPoint);
    
    // Start the timer
    const startTime = Date.now();
    const endTime = startTime + (totalEftTime * 1000);
    
    eftInterval = setInterval(updateEftExercise, tapDuration);
    
    function updateEftExercise() {
        if (!isEftPaused) {
            eftTimeRemaining = Math.max(0, Math.round((endTime - Date.now()) / 1000));
            
            // Update progress bar
            const progressPercent = ((totalEftTime - eftTimeRemaining) / totalEftTime) * 100;
            eftProgress.style.width = `${progressPercent}%`;
            
            // Update timer display
            const minutes = Math.floor(eftTimeRemaining / 60);
            const seconds = eftTimeRemaining % 60;
            document.querySelector('#eftExercise .duration').textContent = 
                `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
            
            // Update tap count and move to next point if needed
            tapCount++;
            if (tapCount >= tapsPerPoint) {
                tapCount = 0;
                currentEftPoint = (currentEftPoint + 1) % eftPoints.length;
                highlightEftPoint(currentEftPoint);
            }
            
            // End when time is up
            if (eftTimeRemaining <= 0) {
                endEftExercise();
                eftInstructions.textContent = 'EFT session complete! Notice how you feel.';
                eftHighlight.style.display = 'none';
            }
        }
    }
}

function highlightEftPoint(index) {
    // Remove active class from all points
    eftPointElements.forEach(el => el.classList.remove('active'));
    
    // Highlight current point
    const currentPoint = eftPoints[index];
    eftPointElements[index].classList.add('active');
    
    // Update instructions
    eftInstructions.textContent = `Tapping: ${currentPoint.name} - ${currentPoint.affirmation}`;
    
    // Position and show highlight on human figure
    if (eftHighlight) {
        eftHighlight.style.top = currentPoint.position.top;
        eftHighlight.style.left = currentPoint.position.left;
        eftHighlight.style.display = 'block';
        
        // Add pulse animation
        eftHighlight.style.animation = 'pulse 0.5s 3';
        setTimeout(() => {
            eftHighlight.style.animation = '';
        }, 1500);
    }
}

function pauseEftExercise() {
    isEftPaused = !isEftPaused;
    pauseEftBtn.textContent = isEftPaused ? 'Resume' : 'Pause';
    
    if (isEftPaused) {
        if (eftHighlight) eftHighlight.style.display = 'none';
        eftInstructions.textContent = 'EFT paused. Tap resume to continue.';
    } else {
        highlightEftPoint(currentEftPoint);
    }
}

function endEftExercise() {
    clearInterval(eftInterval);
    isEftActive = false;
    isEftPaused = false;
    startEftBtn.style.display = 'inline-block';
    pauseEftBtn.style.display = 'none';
    if (eftHighlight) eftHighlight.style.display = 'none';
    document.querySelector('#eftExercise .duration').textContent = '10 min';
    eftProgress.style.width = '0%';
    
    // Reset all points
    eftPointElements.forEach(el => el.classList.remove('active'));
    eftInstructions.textContent = 'Tap each point while repeating an affirmation about your issue.';
}

// Event listeners
startEftBtn.addEventListener('click', startEftExercise);
pauseEftBtn.addEventListener('click', pauseEftExercise);

// Make points clickable for manual navigation
eftPointElements.forEach((pointEl, index) => {
    pointEl.addEventListener('click', () => {
        if (isEftActive && !isEftPaused) {
            currentEftPoint = index;
            tapCount = 0;
            highlightEftPoint(currentEftPoint);
        }
    });
});

// Reset when modal closes
document.querySelector('#exercisesModal .close-modal').addEventListener('click', () => {
    if (isEftActive) {
        endEftExercise();
    }
});

window.addEventListener('click', function(e) {
    if (e.target === document.getElementById('exercisesModal') && isEftActive) {
        endEftExercise();
    }
});