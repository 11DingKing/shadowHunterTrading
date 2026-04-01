# Shadow-Hunter v10.4 Dockerfile
# Multi-stage build with noVNC for web access to PyQt6 GUI

FROM python:3.11-slim AS base

# Install system dependencies for PyQt6 + X11 + VNC
RUN apt-get update && apt-get install -y --no-install-recommends \
    # X11 and display
    xvfb \
    x11vnc \
    # noVNC for web access
    novnc \
    websockify \
    # Core libraries
    libglib2.0-0 \
    # Qt/OpenGL dependencies
    libgl1 \
    libegl1 \
    libxkbcommon0 \
    libxkbcommon-x11-0 \
    # XCB dependencies (critical for Qt6)
    libxcb1 \
    libxcb-cursor0 \
    libxcb-glx0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render0 \
    libxcb-render-util0 \
    libxcb-shape0 \
    libxcb-shm0 \
    libxcb-sync1 \
    libxcb-xfixes0 \
    libxcb-xinerama0 \
    libxcb-xkb1 \
    # Other Qt deps
    libdbus-1-3 \
    libfontconfig1 \
    libfreetype6 \
    libx11-6 \
    libx11-xcb1 \
    # Fonts
    fonts-wqy-microhei \
    fonts-noto-cjk \
    # Cleanup
    && rm -rf /var/lib/apt/lists/*

# Set environment
ENV DISPLAY=:99
ENV QT_QPA_PLATFORM=xcb
ENV PYTHONUNBUFFERED=1
ENV XDG_RUNTIME_DIR=/tmp/runtime-root

# Create app directory
WORKDIR /app

# Upgrade pip and install Python dependencies (use only binary wheels)
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --only-binary=:all: -r requirements.txt

# Copy application code
COPY . .

# Create startup script with proper cleanup
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
echo "========================================"\n\
echo "  Shadow-Hunter v10.4 Starting..."\n\
echo "========================================"\n\
\n\
# Cleanup any stale X locks\n\
rm -f /tmp/.X99-lock\n\
rm -rf /tmp/.X11-unix/X99\n\
\n\
# Create runtime directory\n\
mkdir -p /tmp/runtime-root\n\
chmod 700 /tmp/runtime-root\n\
\n\
# Start Xvfb\n\
Xvfb :99 -screen 0 1280x800x24 -ac +extension GLX +render -noreset &\n\
XVFB_PID=$!\n\
sleep 2\n\
\n\
# Verify Xvfb is running\n\
if ! kill -0 $XVFB_PID 2>/dev/null; then\n\
    echo "ERROR: Xvfb failed to start"\n\
    exit 1\n\
fi\n\
\n\
# Start VNC server\n\
x11vnc -display :99 -forever -shared -rfbport 5900 -nopw -xkb &\n\
sleep 1\n\
\n\
# Start noVNC\n\
websockify --web /usr/share/novnc 6080 localhost:5900 &\n\
sleep 1\n\
\n\
echo ""\n\
echo "========================================"\n\
echo "  Startup Success!"\n\
echo "  Access URL: http://localhost:8081"\n\
echo "========================================"\n\
echo ""\n\
\n\
# Start PyQt6 application\n\
exec python main.py\n\
' > /start.sh && chmod +x /start.sh

# Expose noVNC port
EXPOSE 6080

CMD ["/start.sh"]
