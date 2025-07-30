const breathingCircle = document.getElementById('breathingCircle');
const breathingText = document.getElementById('breathingText');
const breathingInstructions = document.getElementById('breathingInstructions');
const startBreathingBtn = document.getElementById('startBreathingBtn');
const pauseBreathingBtn = document.getElementById('pauseBreathingBtn');
const breathingProgress = document.getElementById('breathingProgress');

let breathingInterval;
let isBreathing = false;
let isPaused = false;
let totalSeconds = 300; // 5 minutes
let remainingSeconds = totalSeconds;
let breathPhase = 'in'; // 'in' or 'out'

function resetBreathingExercise() {
    if (isBreathing) {
        clearInterval(breathingInterval);
        isBreathing = false;
        isPaused = false;
        remainingSeconds = totalSeconds;
        breathingProgress.style.width = '0%';
        breathingCircle.classList.remove('breathing-in', 'breathing-out');
        breathingText.textContent = 'Ready';
        breathingInstructions.textContent = 'Breathe in through your nose, out through your mouth';
        startBreathingBtn.style.display = 'inline-block';
        pauseBreathingBtn.style.display = 'none';
        document.querySelector('#breathingExercise .duration').textContent = '5 min';
    }
}

function startBreathingExercise() {
    isBreathing = true;
    startBreathingBtn.style.display = 'none';
    pauseBreathingBtn.style.display = 'inline-block';
    
    const startTime = Date.now();
    const endTime = startTime + (totalSeconds * 1000);
    
    breathingInterval = setInterval(() => {
        if (!isPaused) {
            remainingSeconds = Math.max(0, Math.round((endTime - Date.now()) / 1000));
            
            const progressPercent = ((totalSeconds - remainingSeconds) / totalSeconds) * 100;
            breathingProgress.style.width = `${progressPercent}%`;
            
            const cycleSeconds = remainingSeconds % 10;
            
            if (cycleSeconds > 6) {
                if (breathPhase !== 'in') {
                    breathPhase = 'in';
                    breathingCircle.classList.remove('breathing-out');
                    breathingCircle.classList.add('breathing-in');
                    breathingText.textContent = 'Breathe In';
                    breathingInstructions.textContent = 'Breathe in slowly through your nose...';
                }
            } else {
                if (breathPhase !== 'out') {
                    breathPhase = 'out';
                    breathingCircle.classList.remove('breathing-in');
                    breathingCircle.classList.add('breathing-out');
                    breathingText.textContent = 'Breathe Out';
                    breathingInstructions.textContent = 'Breathe out slowly through your mouth...';
                }
            }
            
            const minutes = Math.floor(remainingSeconds / 60);
            const seconds = remainingSeconds % 60;
            document.querySelector('#breathingExercise .duration').textContent = 
                `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
            
            if (remainingSeconds <= 0) {
                endBreathingExercise();
                breathingText.textContent = 'Complete!';
                breathingInstructions.textContent = 'Great job! Take a moment to notice how you feel.';
            }
        }
    }, 1000);
}

function pauseBreathingExercise() {
    isPaused = !isPaused;
    pauseBreathingBtn.textContent = isPaused ? 'Resume' : 'Pause';
    
    if (isPaused) {
        breathingCircle.classList.remove('breathing-in', 'breathing-out');
        breathingText.textContent = 'Paused';
    } else {
        if (breathPhase === 'in') {
            breathingCircle.classList.add('breathing-in');
        } else {
            breathingCircle.classList.add('breathing-out');
        }
    }
}

function endBreathingExercise() {
    resetBreathingExercise();
}

// Event listeners
startBreathingBtn.addEventListener('click', startBreathingExercise);
pauseBreathingBtn.addEventListener('click', pauseBreathingExercise);

// Modal event listeners
const exercisesModalEl = document.getElementById('exercisesModal');
const closeExercisesModalEl = exercisesModalEl ? exercisesModalEl.querySelector('.close-modal') : null;
if (closeExercisesModalEl && exercisesModalEl) {
    closeExercisesModalEl.addEventListener('click', function() {
        exercisesModalEl.style.display = 'none';
        document.body.style.overflow = 'auto';
        resetBreathingExercise();
    });
    window.addEventListener('click', function(e) {
        if (e.target === exercisesModalEl) {
            exercisesModalEl.style.display = 'none';
            document.body.style.overflow = 'auto';
            resetBreathingExercise();
        }
    });
}