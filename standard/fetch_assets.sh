#!/bin/bash
# Fonts and music are not stored in git (licences: Inter is OFL and fine to fetch; Mixkit music may not be redistributed as a file).
set -e; cd "$(dirname "$0")"
[ -s fonts/Inter.ttf ] || curl -sSL -o fonts/Inter.ttf "https://github.com/google/fonts/raw/main/ofl/inter/Inter%5Bopsz,wght%5D.ttf"
[ -s music/discover.mp3 ] || curl -sSL -A "Mozilla/5.0" -o music/discover.mp3 "https://assets.mixkit.co/music/587/587.mp3"
ls -la fonts music
