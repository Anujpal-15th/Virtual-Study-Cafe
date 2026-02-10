let chatSocket = null;
let peerConnection = null;
let localStream = null;
let remoteStream = null;
let isCallActive = false;
let isMicOn = true;
let isCameraOn = true;

// Timer variables
let timerInterval = null;
let timerMinutes = 25;
let timerSeconds = 0;
let timerRunning = false;

// WebRTC configuration
const rtcConfig = {
    iceServers: [
        { urls: 'stun:stun.l.google.com:19302' }
    ]
};


/**
 * Initialize WebSocket connection to the room
 * Connects to ws://localhost:8000/ws/rooms/{room_code}/
 */
function initWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/rooms/${ROOM_CODE}/`;
    
    chatSocket = new WebSocket(wsUrl);
    
    // When connection opens
    chatSocket.onopen = function(e) {
        console.log('WebSocket connected');
        updateVideoStatus('Connected - Ready for video call');
    };
    
    // When message received from server
    chatSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        handleWebSocketMessage(data);
    };
    
    // When connection closes
    chatSocket.onclose = function(e) {
        console.log('WebSocket disconnected');
        updateVideoStatus('Disconnected');
        setTimeout(initWebSocket, 3000); // Reconnect after 3 seconds
    };
    
    // On error
    chatSocket.onerror = function(e) {
        console.error('WebSocket error:', e);
    };
}

/**
 * Handle incoming WebSocket messages
 * Routes messages based on type
 */
function handleWebSocketMessage(data) {
    const type = data.type;
    
    switch(type) {
        case 'chat':
            displayChatMessage(data);
            break;
        
        case 'user_join':
            displayNotification(`${data.username} joined the room`);
            updateMembersList();
            // If we have an active call and no peer connection, create the offer
            // This ensures the existing user initiates the connection
            if (isCallActive && localStream && !peerConnection && data.username !== USERNAME) {
                console.log('Creating peer connection for new user:', data.username);
                setTimeout(() => createPeerConnection(), 1500);
            }
            break;
        
        case 'user_leave':
            displayNotification(`${data.username} left the room`);
            updateMembersList();
            // Reset peer connection when user leaves
            if (peerConnection) {
                peerConnection.close();
                peerConnection = null;
                const remoteVideo = document.getElementById('remote-video');
                const remotePlaceholder = document.getElementById('remote-placeholder');
                const remoteOverlay = document.getElementById('remote-overlay');
                if (remoteVideo) remoteVideo.srcObject = null;
                if (remotePlaceholder) remotePlaceholder.style.display = 'flex';
                if (remoteOverlay) remoteOverlay.style.display = 'none';
                updateVideoStatus('Peer disconnected - Waiting for others');
            }
            break;
        
        case 'webrtc_offer':
            handleWebRTCOffer(data);
            break;
        
        case 'webrtc_answer':
            handleWebRTCAnswer(data);
            break;
        
        case 'webrtc_ice':
            handleWebRTCICE(data);
            break;
        
        case 'timer':
            handleTimerEvent(data);
            break;
    }
}

// ===== CHAT FUNCTIONALITY =====

/**
 * Display a chat message in the chat box
 */
function displayChatMessage(data) {
    const chatMessages = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'chat-message';
    
    // Highlight own messages
    if (data.username === USERNAME) {
        messageDiv.classList.add('own');
    }
    
    // Format timestamp
    const timestamp = new Date(data.timestamp).toLocaleTimeString();
    
    messageDiv.innerHTML = `
        <div class="message-username">${data.username}</div>
        <div class="message-text">${escapeHtml(data.message)}</div>
        <div class="message-time">${timestamp}</div>
    `;
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

/**
 * Display a notification (join/leave) in the chat
 */
function displayNotification(message) {
    const chatMessages = document.getElementById('chat-messages');
    const notifDiv = document.createElement('div');
    notifDiv.className = 'notification-message';
    notifDiv.textContent = message;
    
    chatMessages.appendChild(notifDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

/**
 * Send a chat message through WebSocket
 */
function sendChatMessage(message) {
    if (chatSocket && chatSocket.readyState === WebSocket.OPEN) {
        chatSocket.send(JSON.stringify({
            type: 'chat',
            message: message
        }));
    }
}

/**
 * Update members count (placeholder - in real app would fetch from server)
 */
function updateMembersList() {
    // In a full implementation, you would request updated member list from server
    // For now, just increment/decrement the count displayed
}

/**
 * Escape HTML to prevent XSS attacks
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ===== WEBRTC VIDEO CALL FUNCTIONALITY =====

/**
 * Start a video call
 * Gets user media (camera + mic) and makes it ready for connection
 */
async function startCall() {
    console.log('Starting call for user:', USERNAME);
    
    if (isCallActive) {
        console.log('Call already active');
        return;
    }
    
    try {
        // Get user's camera and microphone
        console.log('Requesting camera and microphone access...');
        updateVideoStatus('Requesting camera and microphone access...');
        
        localStream = await navigator.mediaDevices.getUserMedia({
            video: true,
            audio: true
        });
        
        console.log('Media access granted');
        
        // Display local video
        const localVideo = document.getElementById('local-video');
        const localPlaceholder = document.getElementById('local-placeholder');
        localVideo.srcObject = localStream;
        
        // Hide placeholder when video starts
        localVideo.onloadedmetadata = () => {
            localPlaceholder.style.display = 'none';
            console.log('Local video loaded');
        };
        
        // Set initial states
        isCallActive = true;
        isMicOn = true;
        isCameraOn = true;
        
        console.log('Setting isCallActive to true and updating buttons');
        updateCallButtons();
        
        // Send notification to others that we joined
        if (chatSocket && chatSocket.readyState === WebSocket.OPEN) {
            chatSocket.send(JSON.stringify({
                type: 'user_join',
                username: USERNAME
            }));
        }
        
        const memberCount = parseInt(document.getElementById('members-count')?.textContent || '1');
        if (memberCount > 1) {
            updateVideoStatus('Connected - Ready for video call');
            // Create peer connection if others are in the room
            setTimeout(() => createPeerConnection(), 1000);
        } else {
            updateVideoStatus('Ready - Waiting for others to join');
        }
        
    } catch (error) {
        console.error('Error starting call:', error);
        handleVideoError(error, 'Start video call');
        isCallActive = false;
        updateCallButtons();
    }
}

/**
 * Create peer connection and send offer
 */
async function createPeerConnection() {
    // Prevent creating multiple peer connections
    if (peerConnection) {
        console.log('Peer connection already exists');
        return;
    }
    
    try {
        console.log('Creating new peer connection...');
        // Create peer connection
        peerConnection = new RTCPeerConnection(rtcConfig);
        
        // Add local stream tracks to peer connection
        localStream.getTracks().forEach(track => {
            console.log('Adding track to peer connection:', track.kind);
            peerConnection.addTrack(track, localStream);
        });
        
        // Handle incoming remote stream
        peerConnection.ontrack = function(event) {
            console.log('Received remote track:', event.track.kind);
            remoteStream = event.streams[0];
            const remoteVideo = document.getElementById('remote-video');
            const remotePlaceholder = document.getElementById('remote-placeholder');
            const remoteOverlay = document.getElementById('remote-overlay');
            
            remoteVideo.srcObject = remoteStream;
            
            // Hide placeholder and show overlay when remote video starts
            remoteVideo.onloadedmetadata = () => {
                remotePlaceholder.style.display = 'none';
                remoteOverlay.style.display = 'flex';
            };
            
            updateVideoStatus('Connected with peer');
        };
        
        // Handle ICE candidates
        peerConnection.onicecandidate = function(event) {
            if (event.candidate) {
                // Send ICE candidate to other peer via WebSocket
                chatSocket.send(JSON.stringify({
                    type: 'webrtc_ice',
                    candidate: event.candidate
                }));
            }
        };
        
        // Create and send offer
        const offer = await peerConnection.createOffer();
        await peerConnection.setLocalDescription(offer);
        
        // Send offer through WebSocket
        chatSocket.send(JSON.stringify({
            type: 'webrtc_offer',
            offer: offer
        }));
        
        updateVideoStatus('Calling...');
        
    } catch (error) {
        console.error('Error creating peer connection:', error);
        updateVideoStatus('Ready - Waiting for others');
    }
}

/**
 * Handle incoming WebRTC offer from another peer
 */
async function handleWebRTCOffer(data) {
    // Don't handle own offers
    if (data.username === USERNAME) {
        return;
    }
    
    console.log('Received WebRTC offer from:', data.username);
    
    try {
        // Get user media if not already have it
        if (!localStream) {
            console.log('Getting local media for answering offer...');
            localStream = await navigator.mediaDevices.getUserMedia({
                video: true,
                audio: true
            });
            
            const localVideo = document.getElementById('local-video');
            const localPlaceholder = document.getElementById('local-placeholder');
            localVideo.srcObject = localStream;
            
            // Hide placeholder when video starts
            localVideo.onloadedmetadata = () => {
                localPlaceholder.style.display = 'none';
            };
            
            isCallActive = true;
            updateCallButtons();
        }
        
        // Create peer connection if not exists
        if (!peerConnection) {
            console.log('Creating peer connection for answering offer...');
            peerConnection = new RTCPeerConnection(rtcConfig);
            
            // Add local tracks
            localStream.getTracks().forEach(track => {
                console.log('Adding local track to peer connection:', track.kind);
                peerConnection.addTrack(track, localStream);
            });
            
            // Handle remote stream
            peerConnection.ontrack = function(event) {
                console.log('Received remote track:', event.track.kind);
                remoteStream = event.streams[0];
                const remoteVideo = document.getElementById('remote-video');
                const remotePlaceholder = document.getElementById('remote-placeholder');
                const remoteOverlay = document.getElementById('remote-overlay');
                const remoteName = document.getElementById('remote-name');
                
                remoteVideo.srcObject = remoteStream;
                if (remoteName) remoteName.textContent = data.username;
                
                // Hide placeholder and show overlay when remote video starts
                remoteVideo.onloadedmetadata = () => {
                    remotePlaceholder.style.display = 'none';
                    remoteOverlay.style.display = 'flex';
                };
                
                updateVideoStatus('Connected with peer');
            };
            
            // Handle ICE candidates
            peerConnection.onicecandidate = function(event) {
                if (event.candidate) {
                    console.log('Sending ICE candidate');
                    chatSocket.send(JSON.stringify({
                        type: 'webrtc_ice',
                        candidate: event.candidate
                    }));
                }
            };
        }
        
        // Set remote description (offer)
        console.log('Setting remote description (offer)');
        await peerConnection.setRemoteDescription(new RTCSessionDescription(data.offer));
        
        // Create answer
        console.log('Creating answer...');
        const answer = await peerConnection.createAnswer();
        await peerConnection.setLocalDescription(answer);
        
        // Send answer back
        console.log('Sending answer back');
        chatSocket.send(JSON.stringify({
            type: 'webrtc_answer',
            answer: answer
        }));
        
        isCallActive = true;
        console.log('Set isCallActive to true after handling offer');
        console.log('Calling updateCallButtons from handleWebRTCOffer');
        updateCallButtons();
        
        // Retry after delay
        setTimeout(() => {
            console.log('Retry: Updating buttons after handling offer');
            updateCallButtons();
        }, 500);
        
        updateVideoStatus('Connecting...');
        
    } catch (error) {
        console.error('Error handling offer:', error);
        updateVideoStatus('Error: ' + error.message);
    }
}

/**
 * Handle incoming WebRTC answer
 */
async function handleWebRTCAnswer(data) {
    // Don't handle own answers
    if (data.username === USERNAME) {
        return;
    }
    
    console.log('Received WebRTC answer from:', data.username);
    
    try {
        if (peerConnection) {
            console.log('Setting remote description (answer)');
            await peerConnection.setRemoteDescription(new RTCSessionDescription(data.answer));
            updateVideoStatus('Call connected');
        } else {
            console.error('No peer connection exists to set answer');
        }
    } catch (error) {
        console.error('Error handling answer:', error);
        updateVideoStatus('Error connecting: ' + error.message);
    }
}

/**
 * Handle incoming ICE candidate
 */
async function handleWebRTCICE(data) {
    // Don't handle own ICE candidates
    if (data.username === USERNAME) {
        return;
    }
    
    try {
        if (peerConnection && data.candidate) {
            console.log('Adding ICE candidate from:', data.username);
            await peerConnection.addIceCandidate(new RTCIceCandidate(data.candidate));
        } else if (!peerConnection) {
            console.warn('Received ICE candidate but no peer connection exists yet');
        }
    } catch (error) {
        console.error('Error handling ICE candidate:', error);
    }
}

/**
 * End the video call
 */
function endCall() {
    console.log('Ending call...');
    
    // Stop all local tracks
    if (localStream) {
        localStream.getTracks().forEach(track => {
            console.log('Stopping track:', track.kind);
            track.stop();
        });
        localStream = null;
    }
    
    // Close peer connection
    if (peerConnection) {
        peerConnection.close();
        peerConnection = null;
    }
    
    // Clear video elements and show placeholders
    const localVideo = document.getElementById('local-video');
    const remoteVideo = document.getElementById('remote-video');
    const localPlaceholder = document.getElementById('local-placeholder');
    const remotePlaceholder = document.getElementById('remote-placeholder');
    const remoteOverlay = document.getElementById('remote-overlay');
    const localMicIcon = document.getElementById('local-mic-icon');
    const localCamIcon = document.getElementById('local-cam-icon');
    
    if (localVideo) localVideo.srcObject = null;
    if (remoteVideo) remoteVideo.srcObject = null;
    if (localPlaceholder) localPlaceholder.style.display = 'flex';
    if (remotePlaceholder) remotePlaceholder.style.display = 'flex';
    if (remoteOverlay) remoteOverlay.style.display = 'none';
    
    // Reset icons
    if (localMicIcon) {
        localMicIcon.textContent = '🎤';
        localMicIcon.classList.remove('muted');
    }
    if (localCamIcon) {
        localCamIcon.textContent = '📹';
        localCamIcon.classList.remove('muted');
    }
    
    isCallActive = false;
    isMicOn = true;
    isCameraOn = true;
    updateCallButtons();
    updateVideoStatus('Call ended');
}

/**
 * Toggle microphone on/off
 */
function toggleMic() {
    if (localStream) {
        const audioTrack = localStream.getAudioTracks()[0];
        if (audioTrack) {
            audioTrack.enabled = !audioTrack.enabled;
            isMicOn = audioTrack.enabled;
            
            const micBtn = document.getElementById('toggle-mic-btn');
            const localMicIcon = document.getElementById('local-mic-icon');
            
            if (isMicOn) {
                micBtn.classList.remove('off');
                localMicIcon.textContent = '🎤';
                localMicIcon.classList.remove('muted');
            } else {
                micBtn.classList.add('off');
                localMicIcon.textContent = '🔇';
                localMicIcon.classList.add('muted');
            }
            console.log('Microphone:', isMicOn ? 'ON' : 'OFF');
        }
    }
}

/**
 * Toggle camera on/off
 */
function toggleCamera() {
    if (localStream) {
        const videoTrack = localStream.getVideoTracks()[0];
        if (videoTrack) {
            videoTrack.enabled = !videoTrack.enabled;
            isCameraOn = videoTrack.enabled;
            
            const cameraBtn = document.getElementById('toggle-camera-btn');
            const localCamIcon = document.getElementById('local-cam-icon');
            const localPlaceholder = document.getElementById('local-placeholder');
            const localVideo = document.getElementById('local-video');
            
            if (isCameraOn) {
                cameraBtn.classList.remove('off');
                localCamIcon.textContent = '📹';
                localCamIcon.classList.remove('muted');
                if (localVideo && localVideo.srcObject) {
                    localPlaceholder.style.display = 'none';
                }
            } else {
                cameraBtn.classList.add('off');
                localCamIcon.textContent = '📵';
                localCamIcon.classList.add('muted');
                localPlaceholder.style.display = 'flex';
            }
            console.log('Camera:', isCameraOn ? 'ON' : 'OFF');
        }
    }
}

/**
 * Update video status message
 */
function updateVideoStatus(message) {
    const statusEl = document.getElementById('video-status');
    if (statusEl) {
        statusEl.textContent = message;
    }
}

/**
 * Update call button visibility based on call state
 */
function updateCallButtons() {
    const startBtn = document.getElementById('start-call-btn');
    const endBtn = document.getElementById('end-call-btn');
    const micBtn = document.getElementById('toggle-mic-btn');
    const cameraBtn = document.getElementById('toggle-camera-btn');
    
    console.log('Updating call buttons. isCallActive:', isCallActive);
    console.log('Button elements found:', {
        startBtn: !!startBtn,
        endBtn: !!endBtn,
        micBtn: !!micBtn,
        cameraBtn: !!cameraBtn
    });
    
    if (isCallActive) {
        // Hide start button, show call controls
        if (startBtn) startBtn.classList.add('hidden');
        if (endBtn) {
            endBtn.classList.remove('hidden');
            console.log('Showing end call button');
        }
        if (micBtn) {
            micBtn.classList.remove('hidden');
            // Update mic button state
            if (isMicOn) {
                micBtn.classList.remove('off');
                micBtn.title = 'Mute microphone';
            } else {
                micBtn.classList.add('off');
                micBtn.title = 'Unmute microphone';
            }
        }
        if (cameraBtn) {
            cameraBtn.classList.remove('hidden');
            // Update camera button state
            if (isCameraOn) {
                cameraBtn.classList.remove('off');
                cameraBtn.title = 'Turn off camera';
            } else {
                cameraBtn.classList.add('off');
                cameraBtn.title = 'Turn on camera';
            }
        }
    } else {
        // Show start button, hide call controls
        if (startBtn) startBtn.classList.remove('hidden');
        if (endBtn) endBtn.classList.add('hidden');
        if (micBtn) micBtn.classList.add('hidden');
        if (cameraBtn) cameraBtn.classList.add('hidden');
    }
}

/**
 * Leave the room and return to dashboard
 */
function leaveRoom() {
    console.log('Leave room button clicked by:', USERNAME);
    
    // Confirm before leaving
    if (confirm('Are you sure you want to leave this room?')) {
        console.log('Leaving room confirmed');
        
        // End call properly
        if (isCallActive) {
            console.log('Ending active call before leaving');
            // Don't call endCall() to avoid cleanup, just stop media
            if (localStream) {
                localStream.getTracks().forEach(track => {
                    console.log('Stopping track:', track.kind);
                    track.stop();
                });
            }
        }
        
        // Close WebSocket connection
        if (chatSocket) {
            console.log('Closing WebSocket connection');
            chatSocket.close();
        }
        
        // Close peer connection
        if (peerConnection) {
            console.log('Closing peer connection');
            peerConnection.close();
        }
        
        console.log('Redirecting to home page');
        // Redirect to home page
        window.location.href = '/';
    } else {
        console.log('Leave room cancelled');
    }
}

// ===== POMODORO TIMER FUNCTIONALITY =====

/**
 * Update timer display
 */
function updateTimerDisplay() {
    const display = document.getElementById('timer-display');
    const mins = String(timerMinutes).padStart(2, '0');
    const secs = String(timerSeconds).padStart(2, '0');
    display.textContent = `${mins}:${secs}`;
}

/**
 * Start the Pomodoro timer
 */
function startTimer() {
    if (timerRunning) return;
    
    timerRunning = true;
    updateTimerButtons();
    
    timerInterval = setInterval(() => {
        if (timerSeconds === 0) {
            if (timerMinutes === 0) {
                // Timer complete!
                completeTimer();
                return;
            }
            timerMinutes--;
            timerSeconds = 59;
        } else {
            timerSeconds--;
        }
        updateTimerDisplay();
    }, 1000);
}

/**
 * Pause the timer
 */
function pauseTimer() {
    timerRunning = false;
    clearInterval(timerInterval);
    updateTimerButtons();
}

/**
 * Reset the timer
 */
function resetTimer() {
    pauseTimer();
    timerMinutes = 25;
    timerSeconds = 0;
    updateTimerDisplay();
}

/**
 * Handle timer completion
 * Save study session to database
 */
function completeTimer() {
    pauseTimer();
    
    // Get the original minutes (before countdown)
    const originalMinutes = parseInt(document.getElementById('timer-display').dataset.originalMinutes) || 25;
    
    // Show completion message
    alert(`Congratulations! You completed ${originalMinutes} minutes of focused study!`);
    
    // Save session to database via POST request
    saveStudySession(originalMinutes);
    
    // Reset timer
    resetTimer();
}

/**
 * Save study session to database
 */
function saveStudySession(minutes) {
    // Create form data
    const formData = new FormData();
    formData.append('minutes', minutes);
    formData.append('room_code', ROOM_CODE);
    
    // Get CSRF token
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
    
    // Send POST request
    fetch('/save-session/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken || getCookie('csrftoken')
        },
        body: formData
    })
    .then(response => {
        if (response.ok) {
            console.log('Session saved successfully');
        } else {
            console.error('Failed to save session');
        }
    })
    .catch(error => {
        console.error('Error saving session:', error);
    });
}

/**
 * Get cookie value by name
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Set timer to preset minutes
 */
function setTimerPreset(minutes) {
    pauseTimer();
    timerMinutes = minutes;
    timerSeconds = 0;
    updateTimerDisplay();
    
    // Store original minutes for saving later
    document.getElementById('timer-display').dataset.originalMinutes = minutes;
    
    // Update preset button styling
    document.querySelectorAll('.preset-btn').forEach(btn => {
        btn.classList.remove('active');
    });
}

/**
 * Update timer button visibility
 */
function updateTimerButtons() {
    const startBtn = document.getElementById('start-timer-btn');
    const pauseBtn = document.getElementById('pause-timer-btn');
    
    if (timerRunning) {
        startBtn.style.display = 'none';
        pauseBtn.style.display = 'inline-block';
    } else {
        startBtn.style.display = 'inline-block';
        pauseBtn.style.display = 'none';
    }
}

/**
 * Handle timer events from other users (optional)
 */
function handleTimerEvent(data) {
    // You can implement synchronized timer across users if needed
    console.log('Timer event from', data.username, ':', data.action);
}

// ===== EVENT LISTENERS =====

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded. Initializing room for user:', USERNAME);
    console.log('Room code:', ROOM_CODE);
    
    // Initialize WebSocket
    initWebSocket();
    
    // Don't auto-start video call - let user click the button
    updateVideoStatus('Ready to connect - Click "Start Call" to begin');
    
    // Verify all buttons exist
    console.log('Verifying button elements:');
    console.log('- Start call button:', document.getElementById('start-call-btn') ? 'Found' : 'NOT FOUND');
    console.log('- End call button:', document.getElementById('end-call-btn') ? 'Found' : 'NOT FOUND');
    console.log('- Toggle mic button:', document.getElementById('toggle-mic-btn') ? 'Found' : 'NOT FOUND');
    console.log('- Toggle camera button:', document.getElementById('toggle-camera-btn') ? 'Found' : 'NOT FOUND');
    console.log('- Leave room button:', document.getElementById('leave-room-btn') ? 'Found' : 'NOT FOUND');
    
    // Chat form submission
    const chatForm = document.getElementById('chat-form');
    if (chatForm) {
        chatForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const input = document.getElementById('chat-input');
            const message = input.value.trim();
            
            if (message) {
                sendChatMessage(message);
                input.value = '';
            }
        });
    }
    
    // Video call buttons
    const startCallBtn = document.getElementById('start-call-btn');
    const endCallBtn = document.getElementById('end-call-btn');
    const toggleMicBtn = document.getElementById('toggle-mic-btn');
    const toggleCameraBtn = document.getElementById('toggle-camera-btn');
    const leaveRoomBtn = document.getElementById('leave-room-btn');
    
    if (startCallBtn) {
        startCallBtn.addEventListener('click', startCall);
        console.log('Start call button listener attached');
    } else {
        console.error('Start call button not found');
    }
    
    if (endCallBtn) {
        endCallBtn.addEventListener('click', endCall);
        console.log('End call button listener attached');
    } else {
        console.error('End call button not found');
    }
    
    if (toggleMicBtn) {
        toggleMicBtn.addEventListener('click', toggleMic);
        console.log('Toggle mic button listener attached');
    } else {
        console.error('Toggle mic button not found');
    }
    
    if (toggleCameraBtn) {
        toggleCameraBtn.addEventListener('click', toggleCamera);
        console.log('Toggle camera button listener attached');
    } else {
        console.error('Toggle camera button not found');
    }
    
    if (leaveRoomBtn) {
        leaveRoomBtn.addEventListener('click', function(e) {
            console.log('Leave room button clicked by:', USERNAME);
            leaveRoom();
        });
        console.log('Leave room button listener attached');
    } else {
        console.error('Leave room button not found - trying alternative selector');
        // Try to find button by class name
        const altLeaveBtn = document.querySelector('.leave-room-btn');
        if (altLeaveBtn) {
            altLeaveBtn.addEventListener('click', function(e) {
                console.log('Leave room button clicked (alternative)');
                leaveRoom();
            });
            console.log('Leave room button found and attached via class selector');
        } else {
            console.error('Leave room button not found with any selector');
        }
    }
    
    // Timer buttons
    const startTimerBtn = document.getElementById('start-timer-btn');
    const pauseTimerBtn = document.getElementById('pause-timer-btn');
    const resetTimerBtn = document.getElementById('reset-timer-btn');
    
    if (startTimerBtn) {
        startTimerBtn.addEventListener('click', startTimer);
    }
    if (pauseTimerBtn) {
        pauseTimerBtn.addEventListener('click', pauseTimer);
    }
    if (resetTimerBtn) {
        resetTimerBtn.addEventListener('click', resetTimer);
    }
    
    // Timer presets
    document.querySelectorAll('.preset-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const minutes = parseInt(this.dataset.minutes);
            setTimerPreset(minutes);
            this.classList.add('active');
        });
    });
    
    // Custom minutes input
    const customInput = document.getElementById('custom-minutes');
    customInput.addEventListener('change', function() {
        const minutes = parseInt(this.value);
        if (minutes > 0 && minutes <= 120) {
            setTimerPreset(minutes);
        }
    });
    
    // Initialize timer display
    updateTimerDisplay();
    document.getElementById('timer-display').dataset.originalMinutes = 25;
    
    // Initialize button states
    updateCallButtons();
});

// Clean up on page unload
window.addEventListener('beforeunload', function() {
    if (chatSocket) {
        chatSocket.close();
    }
    if (isCallActive) {
        endCall();
    }
});

// ===== ERROR HANDLING =====

/**
 * Display error message to user
 */
function showUserError(message) {
    if (typeof showNotification === 'function') {
        showNotification(message, 'error', 5000);
    } else {
        alert('Room Error: ' + message);
    }
}

/**
 * Enhanced error handling for video calls
 */
function handleVideoError(error, context = 'Video call') {
    console.error(`${context} error:`, error);
    
    let userMessage = 'An error occurred with the video call. ';
    
    if (error.name === 'NotAllowedError') {
        userMessage += 'Please allow camera and microphone access, then try again.';
    } else if (error.name === 'NotFoundError') {
        userMessage += 'No camera or microphone found. Please check your devices.';
    } else if (error.name === 'NotReadableError') {
        userMessage += 'Your camera/microphone is being used by another application.';
    } else if (error.name === 'OverconstrainedError') {
        userMessage += 'Camera settings not supported by your device.';
    } else {
        userMessage += 'Please check your connection and try again.';
    }
    
    showUserError(userMessage);
    updateVideoStatus(`Error: ${error.message || 'Unknown error'}`);
}
