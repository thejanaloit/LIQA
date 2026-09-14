# Live view

Working now: GET http://127.0.0.1:8787/v1/live/frame (screenshot poll, 25fps cap in docs).
UI embeds debugUrl. Presence label LIQA Worker.
WebRTC H.264 publisher + SFU: specified in /v1/live/webrtc — needs TURN outbound.
interactive=true: ACK the human gate then use the real Worker mouse (same PC).
Recording: PNG sequence in captures/; optional ffmpeg to MP4 as artifact.
Blur PII: off by default (future toggle).
Viewer auth: same tenant token as Control.
