#!/bin/bash
# Record an asciinema demo and convert to GIF
# Requirements: asciinema, agg (asciinema GIF generator)
#
# Usage:
#   1. Run: bash scripts/record_demo.sh
#   2. This will record a 30-second session
#   3. Output: demo.gif in the project root

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "=== pdf_pilot Demo Recording ==="
echo ""
echo "This will record a 30-second terminal session."
echo "Recording to demo.cast..."
echo ""

cd "$PROJECT_DIR"

# Record the asciinema cast file
# Usage: asciinema rec <output-file>
# Then run these commands manually inside the recording:
cat << 'INSTRUCTIONS'

Run the following steps inside the asciinema recorder:

  $ pdf_pilot --list-engines
  $ pdf_pilot test.pdf -o demo.md -e pymupdf -v
  $ head -20 demo.md
  $ wc -c demo.md

Then type 'exit' to stop recording.

Or record directly with a pre-typed script:

  asciinema rec demo.cast --command 'bash scripts/demo_commands.sh'

After recording, convert to GIF:

  agg demo.cast demo.gif --theme monokai --font-size 20

INSTRUCTIONS

# Alternative: if agg is available, record directly
if command -v agg &> /dev/null && command -v asciinema &> /dev/null; then
    echo "Recording with asciinema..."
    asciinema rec demo.cast \
        --command 'bash scripts/demo_commands.sh' \
        --title 'pdf_pilot demo' \
        --desc 'Multi-engine PDF converter with auto-routing' \
        --cwd "$PROJECT_DIR"

    echo "Converting to GIF..."
    agg demo.cast demo.gif \
        --theme monokai \
        --font-size 20 \
        --padding 5

    echo "Done! GIF saved as: demo.gif"
else
    echo "Missing dependencies. Install them with:"
    echo "  pip install agg     # asciinema GIF generator"
    echo "  # or: npm install -g @asciinema/agg"
    echo "  # or: brew install asciinema"
fi
