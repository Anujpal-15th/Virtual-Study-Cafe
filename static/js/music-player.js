/* 
 * Music Player Component
 * Custom HTML5 Audio Player with playlist support
 */

class MusicPlayer {
    constructor() {
        this.audio = new Audio();
        this.currentTrackIndex = 0;
        this.isPlaying = false;
        this.volume = 0.5;
        
        // Music playlist - Add your music files here
        this.playlist = [
            {
                title: "Lofi Study Beat 1",
                artist: "Study Music",
                file: "/static/music/track1.mp3"
            },
            {
                title: "Chill Vibes",
                artist: "Focus Sounds",
                file: "/static/music/track2.mp3"
            },
            {
                title: "Peaceful Piano",
                artist: "Relaxing Tunes",
                file: "/static/music/track3.mp3"
            },
            {
                title: "Nature Sounds",
                artist: "Ambient",
                file: "/static/music/track4.mp3"
            }
        ];
        
        this.init();
    }
    
    init() {
        this.audio.volume = this.volume;
        this.audio.addEventListener('ended', () => this.nextTrack());
        this.audio.addEventListener('timeupdate', () => this.updateProgress());
        this.loadTrack(this.currentTrackIndex);
    }
    
    loadTrack(index) {
        if (index < 0 || index >= this.playlist.length) return;
        
        const track = this.playlist[index];
        this.audio.src = track.file;
        this.currentTrackIndex = index;
        
        // Update UI
        this.updateTrackInfo();
    }
    
    updateTrackInfo() {
        const track = this.playlist[this.currentTrackIndex];
        const titleEl = document.getElementById('track-title');
        const artistEl = document.getElementById('track-artist');
        
        if (titleEl) titleEl.textContent = track.title;
        if (artistEl) artistEl.textContent = track.artist;
    }
    
    play() {
        this.audio.play();
        this.isPlaying = true;
        this.updatePlayButton();
    }
    
    pause() {
        this.audio.pause();
        this.isPlaying = false;
        this.updatePlayButton();
    }
    
    togglePlay() {
        if (this.isPlaying) {
            this.pause();
        } else {
            this.play();
        }
    }
    
    nextTrack() {
        this.currentTrackIndex = (this.currentTrackIndex + 1) % this.playlist.length;
        this.loadTrack(this.currentTrackIndex);
        if (this.isPlaying) this.play();
    }
    
    previousTrack() {
        this.currentTrackIndex = (this.currentTrackIndex - 1 + this.playlist.length) % this.playlist.length;
        this.loadTrack(this.currentTrackIndex);
        if (this.isPlaying) this.play();
    }
    
    setVolume(value) {
        this.volume = value;
        this.audio.volume = value;
    }
    
    seek(value) {
        const time = (value / 100) * this.audio.duration;
        this.audio.currentTime = time;
    }
    
    updateProgress() {
        const progressBar = document.getElementById('progress-bar');
        const currentTimeEl = document.getElementById('current-time');
        const durationEl = document.getElementById('duration-time');
        
        if (progressBar && this.audio.duration) {
            const progress = (this.audio.currentTime / this.audio.duration) * 100;
            progressBar.value = progress;
        }
        
        if (currentTimeEl) {
            currentTimeEl.textContent = this.formatTime(this.audio.currentTime);
        }
        
        if (durationEl && this.audio.duration) {
            durationEl.textContent = this.formatTime(this.audio.duration);
        }
    }
    
    updatePlayButton() {
        const playBtn = document.getElementById('play-pause-btn');
        if (playBtn) {
            playBtn.textContent = this.isPlaying ? '⏸' : '▶';
        }
    }
    
    formatTime(seconds) {
        if (isNaN(seconds)) return '0:00';
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    }
}

// Initialize player when DOM is ready
let musicPlayer;
document.addEventListener('DOMContentLoaded', function() {
    musicPlayer = new MusicPlayer();
    
    // Setup event listeners
    const playPauseBtn = document.getElementById('play-pause-btn');
    const nextBtn = document.getElementById('next-btn');
    const prevBtn = document.getElementById('prev-btn');
    const volumeSlider = document.getElementById('volume-slider');
    const progressBar = document.getElementById('progress-bar');
    
    if (playPauseBtn) {
        playPauseBtn.addEventListener('click', () => musicPlayer.togglePlay());
    }
    
    if (nextBtn) {
        nextBtn.addEventListener('click', () => musicPlayer.nextTrack());
    }
    
    if (prevBtn) {
        prevBtn.addEventListener('click', () => musicPlayer.previousTrack());
    }
    
    if (volumeSlider) {
        volumeSlider.addEventListener('input', (e) => {
            musicPlayer.setVolume(e.target.value / 100);
        });
    }
    
    if (progressBar) {
        progressBar.addEventListener('input', (e) => {
            musicPlayer.seek(e.target.value);
        });
    }
});
