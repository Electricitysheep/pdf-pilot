#!/bin/bash
# Commands to be recorded by asciinema for README demo
# Usage: asciinema rec demo.cast --command 'bash scripts/demo_commands.sh'

sleep 1

echo '$ pdf_pilot --list-engines'
sleep 0.5
pdf_pilot --list-engines
sleep 1

echo ''
echo '$ pdf_pilot example.pdf -o demo.md -e pymupdf -v'
sleep 0.5

# Find any PDF in the project to demo with
PDF=""
if [ -f "test.pdf" ]; then
    PDF="test.pdf"
elif ls *.pdf 1>/dev/null 2>&1; then
    PDF=$(ls *.pdf | head -1)
fi

if [ -n "$PDF" ]; then
    pdf_pilot "$PDF" -o demo.md -e pymupdf -v
    sleep 1
    echo ''
    echo '$ head -20 demo.md'
    sleep 0.5
    head -20 demo.md
    sleep 1
    echo ''
    echo "$ wc -c demo.md"
    sleep 0.5
    wc -c demo.md
else
    # Demo without a PDF
    echo ''
    echo '[INFO] No PDF found in current directory.'
    echo '       Usage: pdf_pilot <input.pdf> -o <output.md>'
    echo ''
    echo '$ pdf_pilot paper.pdf -o output.md -e auto -v'
    echo '[INFO] This will auto-detect and convert the document.'
    echo ''
    echo '# Example Python API usage:'
    python3 -c "
from pdf_pilot.convert import convert
print('from pdf_pilot.convert import convert')
print('doc = convert(\"input.pdf\", \"output.md\")')
print(f'Pages: {doc.page_count}, Engine: {doc.metadata[\"engine\"]}')
" 2>/dev/null || echo 'Python API call (requires a PDF file)'
fi

sleep 1
echo ''
echo '=== pdf_pilot — The only PDF converter you will ever need ==='
