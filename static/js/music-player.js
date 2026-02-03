// Music Player - Expandable Design with Playlist
class MusicPlayer {
    constructor() {
        this.audio = new Audio();
        this.playlist = [
            { title: 'Forever', artist: 'Niladri Kumar', src: '/static/music/SpotiDownloader.com - Forever - Niladri Kumar.mp3' }
        ];
        this.currentTrackIndex = 0;
        this.isPlaying = false;
        this.volume = 0.5;
        this.audio.volume = this.volume;

        this.initElements();
        this.attachEvents();
        this.renderPlaylist();
        this.loadTrack(0);
    }

    initElements() {
        // Panel elements
        this.toggleBtn = document.getElementById('musicToggleBtn');
        this.panel = document.getElementById('musicPlayerPanel');
        this.closeBtn = document.getElementById('closePlayerBtn');

        // Display elements
        this.trackTitle = document.getElementById('currentTrackTitle');
        this.trackArtist = document.getElementById('currentTrackArtist');
        this.currentTimeDisplay = document.getElementById('currentTime');
        this.durationDisplay = document.getElementById('duration');

        // Control elements
        this.playBtn = document.getElementById('playBtn');
        this.prevBtn = document.getElementById('prevBtn');
        this.nextBtn = document.getElementById('nextBtn');
        this.progressBar = document.getElementById('progressBar');

        // Volume elements
        this.volumeSlider = document.getElementById('volumeSlider');
        this.volumeUpBtn = document.getElementById('volumeUpBtn');
        this.volumeDownBtn = document.getElementById('volumeDownBtn');
        this.volumePercentage = document.getElementById('volumePercentage');

        // Playlist container
        this.playlistContainer = document.getElementById('playlistContainer');
    }

    attachEvents() {
        // Toggle panel
        this.toggleBtn.addEventListener('click', () => this.togglePanel());
        this.closeBtn.addEventListener('click', () => this.closePanel());

        // Playback controls
        this.playBtn.addEventListener('click', () => this.togglePlay());
        this.prevBtn.addEventListener('click', () => this.previousTrack());
        this.nextBtn.addEventListener('click', () => this.nextTrack());

        // Progress bar
        this.progressBar.addEventListener('input', (e) => this.seek(e.target.value));

        // Volume controls
        this.volumeSlider.addEventListener('input', (e) => this.setVolume(e.target.value / 100));
        this.volumeUpBtn.addEventListener('click', () => this.increaseVolume());
        this.volumeDownBtn.addEventListener('click', () => this.decreaseVolume());

        // Audio events
        this.audio.addEventListener('timeupdate', () => this.updateProgress());
        this.audio.addEventListener('loadedmetadata', () => this.updateDuration());
        this.audio.addEventListener('ended', () => this.nextTrack());

        // Close panel when clicking outside
        document.addEventListener('click', (e) => {
            if (!this.panel.contains(e.target) && !this.toggleBtn.contains(e.target)) {
                if (this.panel.classList.contains('active')) {
                    this.closePanel();
                }
            }
        });
    }

    renderPlaylist() {
        this.playlistContainer.innerHTML = '';
        this.playlist.forEach((track, index) => {
            const item = document.createElement('div');
            item.className = 'playlist-item';
            if (index === this.currentTrackIndex) {
                item.classList.add('active');
                if (this.isPlaying) item.classList.add('playing');
            }
            
            item.innerHTML = `
                <div class="track-number">${index + 1}</div>
                <div class="track-info-playlist">
                    <div class="track-title">${track.title}</div>
                    <div class="track-artist">${track.artist}</div>
                </div>
                <span class="playing-indicator">♪</span>
            `;
            
            item.addEventListener('click', () => {
                this.loadTrack(index);
                this.play();
            });
            
            this.playlistContainer.appendChild(item);
        });
    }

    togglePanel() {
        this.panel.classList.toggle('active');
        if (this.panel.classList.contains('active')) {
            this.renderPlaylist(); // Refresh playlist when opening
        }
    }

    closePanel() {
        this.panel.classList.remove('active');
    }

    loadTrack(index) {
        if (index >= 0 && index < this.playlist.length) {
            this.currentTrackIndex = index;
            const track = this.playlist[index];
            
            this.audio.src = track.src;
            this.trackTitle.textContent = track.title;
            this.trackArtist.textContent = track.artist;
            
            this.renderPlaylist(); // Update playlist highlight
        }
    }

    play() {
        this.audio.play().then(() => {
            this.isPlaying = true;
            this.playBtn.innerHTML = '⏸';
            this.toggleBtn.classList.add('playing');
            this.renderPlaylist();
        }).catch(err => {
            console.log('Playback error:', err);
        });
    }

    pause() {
        this.audio.pause();
        this.isPlaying = false;
        this.playBtn.innerHTML = '▶';
        this.toggleBtn.classList.remove('playing');
        this.renderPlaylist();
    }

    togglePlay() {
        if (this.isPlaying) {
            this.pause();
        } else {
            this.play();
        }
    }

    nextTrack() {
        const nextIndex = (this.currentTrackIndex + 1) % this.playlist.length;
        this.loadTrack(nextIndex);
        if (this.isPlaying) this.play();
    }

    previousTrack() {
        const prevIndex = (this.currentTrackIndex - 1 + this.playlist.length) % this.playlist.length;
        this.loadTrack(prevIndex);
        if (this.isPlaying) this.play();
    }

    setVolume(value) {
        this.volume = Math.max(0, Math.min(1, value));
        this.audio.volume = this.volume;
        this.volumeSlider.value = this.volume * 100;
        this.volumePercentage.textContent = Math.round(this.volume * 100) + '%';
    }

    increaseVolume() {
        this.setVolume(this.volume + 0.1);
    }

    decreaseVolume() {
        this.setVolume(this.volume - 0.1);
    }

    seek(value) {
        const time = (value / 100) * this.audio.duration;
        if (!isNaN(time)) {
            this.audio.currentTime = time;
        }
    }

    updateProgress() {
        if (this.audio.duration) {
            const progress = (this.audio.currentTime / this.audio.duration) * 100;
            this.progressBar.value = progress;
            this.currentTimeDisplay.textContent = this.formatTime(this.audio.currentTime);
        }
    }

    updateDuration() {
        if (this.audio.duration) {
            this.durationDisplay.textContent = this.formatTime(this.audio.duration);
        }
    }

    formatTime(seconds) {
        if (isNaN(seconds)) return '0:00';
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    }
}

// Initialize player when page loads
document.addEventListener('DOMContentLoaded', () => {
    const player = new MusicPlayer();
});
