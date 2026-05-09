"""Generate simple test PDFs for CI when real fixtures aren't available."""

import fitz

# Multi-column style PDF
doc = fitz.open()
page = doc.new_page()

# Heading + body text for realistic extraction
y_pos = 50
text_data = [
    ("Introduction", 14),
    ("Natural language processing has seen remarkable progress in recent years. "
     "The Transformer architecture has become the de facto standard for many NLP tasks, "
     "including machine translation, text summarization, and question answering.", 10),
    ("Background", 14),
    ("Previous work has shown that attention mechanisms can capture long-range dependencies "
     "in sequential data more effectively than recurrent or convolutional approaches.", 10),
    ("Method", 14),
    ("We propose a novel approach based on self-attention mechanisms that processes "
     "all positions in parallel, enabling efficient training on modern hardware.", 10),
    ("Results", 14),
    ("Our model achieves state-of-the-art results on multiple benchmarks, "
     "with quality improvements that scale significantly with model size.", 10),
    ("Conclusion", 14),
    ("We have demonstrated that the proposed approach works well across diverse tasks. "
     "Future work will extend to multilingual and multimodal settings.", 10),
]

for text, size in text_data:
    page.insert_text((50, y_pos), text, fontsize=size)
    y_pos += size + 15
    if y_pos > 750:
        page = doc.new_page()
        y_pos = 50

doc.Save("tests/fixtures/chelsea_pdta.pdf")
doc.close()

# Table PDF
doc = fitz.open()
page = doc.new_page()

headers = ["Name", "Value", "Category"]
rows = [
    ["Apple", "1.50", "Fruit"],
    ["Bread", "3.00", "Grain"],
    ["Milk", "2.75", "Dairy"],
    ["Cheese", "4.25", "Dairy"],
]

y = 72
for h in headers:
    page.insert_text((72 + headers.index(h) * 150, y), h, fontsize=12)
y = 92
for row in rows:
    for cell in row:
        page.insert_text((72 + row.index(cell) * 150, y), cell, fontsize=10)
    y += 20

doc.Save("tests/fixtures/federal-register.pdf")
doc.close()

# Scanned-style PDF (minimal text, mostly empty = high scan score)
doc = fitz.open()
page = doc.new_page()
page.insert_text((50, 50), "Scanned Document Sample", fontsize=14)
doc.Save("tests/fixtures/scanned.pdf")
doc.close()

print("Test PDFs generated")
