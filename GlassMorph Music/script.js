// --- 0. Generate Spectrum Bars (Original Design) ---
const spectrumContainer = document.getElementById('spectrum');
for (let i = 0; i < 50; i++) {
    const bar = document.createElement('div');
    bar.classList.add('bar');
    bar.style.animationDuration = `${Math.random() * 0.5 + 0.5}s`;
    bar.style.height = `${Math.random() * 50 + 20}px`;
    spectrumContainer.appendChild(bar);
}

// --- 1. Variables & Elements ---
const audio = document.getElementById('localAudio');
const fileInput = document.getElementById('fileInput');
const loadFilesBtn = document.getElementById('loadFilesBtn');
const playBtn = document.getElementById('playBtn');
const playIcon = document.getElementById('playIcon');
const prevBtn = document.getElementById('prevBtn');
const nextBtn = document.getElementById('nextBtn');

const disc = document.getElementById('disc');
const bars = document.querySelectorAll('.bar'); // The background bars
const songTitle = document.getElementById('songTitle');
const currTimeText = document.getElementById('currTime');
const totalTimeText = document.getElementById('totalTime');
const progressFill = document.getElementById('progressFill');
const progressBarBg = document.getElementById('progressBarBg');

let playlist = [];
let currentIndex = 0;
let isDragging = false;

// --- 2. File Loading Logic ---
loadFilesBtn.addEventListener('click', () => fileInput.click());

fileInput.addEventListener('change', (e) => {
    const files = Array.from(e.target.files);
    if (files.length > 0) {
        playlist = files;
        currentIndex = 0;
        loadTrack(currentIndex);
        playTrack();
    }
});

function loadTrack(index) {
    if (index < 0 || index >= playlist.length) return;

    const file = playlist[index];
    // Create a URL for the local file
    audio.src = URL.createObjectURL(file);
    audio.load();

    // Set Title (Remove file extension)
    const cleanName = file.name.replace(/\.[^/.]+$/, "");
    songTitle.innerText = cleanName;
}

// --- 3. Playback Control ---
function playTrack() {
    audio.play().then(() => {
        updateUIState(true);
    }).catch(e => console.error(e));
}

function pauseTrack() {
    audio.pause();
    updateUIState(false);
}

function togglePlay() {
    if (playlist.length === 0) {
        loadFilesBtn.click(); // Prompt to load if empty
        return;
    }
    if (audio.paused) playTrack();
    else pauseTrack();
}

function nextTrack() {
    if (playlist.length === 0) return;
    currentIndex = (currentIndex + 1) % playlist.length;
    loadTrack(currentIndex);
    playTrack();
}

function prevTrack() {
    if (playlist.length === 0) return;
    currentIndex = (currentIndex - 1 + playlist.length) % playlist.length;
    loadTrack(currentIndex);
    playTrack();
}

// --- 4. UI Updates & Animation ---
function updateUIState(isPlaying) {
    if (isPlaying) {
        playIcon.classList.remove('fa-play');
        playIcon.classList.add('fa-pause');

        // Animate Disc
        disc.classList.remove('paused');
        disc.classList.add('spinning');

        // Animate Title
        songTitle.classList.remove('paused-text');

        // Animate Spectrum Background (CSS Animation)
        bars.forEach(bar => bar.style.animationPlayState = 'running');

    } else {
        playIcon.classList.remove('fa-pause');
        playIcon.classList.add('fa-play');

        disc.classList.add('paused');
        songTitle.classList.add('paused-text');

        bars.forEach(bar => bar.style.animationPlayState = 'paused');
    }
}

// Event Listeners
playBtn.addEventListener('click', togglePlay);
nextBtn.addEventListener('click', nextTrack);
prevBtn.addEventListener('click', prevTrack);
audio.addEventListener('ended', nextTrack); // Auto-play next

// --- 5. Timeline & Time Format ---
audio.addEventListener('timeupdate', () => {
    if (isDragging) return;

    const currentTime = audio.currentTime;
    const duration = audio.duration;

    if (!isNaN(duration)) {
        const percent = (currentTime / duration) * 100;
        progressFill.style.width = `${percent}%`;
        currTimeText.innerText = formatTime(currentTime);
        totalTimeText.innerText = formatTime(duration);
    }
});

audio.addEventListener('loadedmetadata', () => {
    totalTimeText.innerText = formatTime(audio.duration);
});

function formatTime(seconds) {
    if (isNaN(seconds)) return "00:00";
    const min = Math.floor(seconds / 60);
    const sec = Math.floor(seconds % 60);
    return `${min < 10 ? '0' + min : min}:${sec < 10 ? '0' + sec : sec}`;
}

// --- 6. Drag & Seek Logic ---
function getSeekTime(e) {
    const rect = progressBarBg.getBoundingClientRect();
    let clickX = e.clientX - rect.left;

    if (clickX < 0) clickX = 0;
    if (clickX > rect.width) clickX = rect.width;

    const percentage = clickX / rect.width;
    return percentage * audio.duration;
}

progressBarBg.addEventListener('mousedown', (e) => {
    if (playlist.length === 0) return;
    isDragging = true;
    const time = getSeekTime(e);
    const percent = (time / audio.duration) * 100;
    progressFill.style.width = `${percent}%`;
    currTimeText.innerText = formatTime(time);
});

document.addEventListener('mousemove', (e) => {
    if (!isDragging) return;
    const time = getSeekTime(e);
    const percent = (time / audio.duration) * 100;
    progressFill.style.width = `${percent}%`;
    currTimeText.innerText = formatTime(time);
});

document.addEventListener('mouseup', (e) => {
    if (!isDragging) return;
    isDragging = false;
    if (playlist.length > 0) {
        const time = getSeekTime(e);
        audio.currentTime = time;
    }
});
