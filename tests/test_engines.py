"""引擎测试"""

import pytest

from pdf_pilot.engines.docling_engine import DoclingEngine
from pdf_pilot.engines.pymupdf_engine import PyMuPDFEngine


class TestDoclingEngine:
    """Docling 引擎测试"""

    def test_is_available(self):
        engine = DoclingEngine()
        assert engine.is_available(), "Docling should be available"

    def test_engine_name(self):
        engine = DoclingEngine()
        assert engine.name == "docling"

    @pytest.mark.skip(
        reason=(
            "Docling layout model crashes on CPU+Windows+PyTorch "
            "(access violation in RT-DETR ResNet). "
            "Requires GPU or Linux environment."
        )
    )
    def test_extract(self, multi_column_pdf):
        engine = DoclingEngine()
        doc = engine.extract(multi_column_pdf)

        assert doc.raw_markdown, "Should produce markdown output"
        assert len(doc.raw_markdown) > 100
        assert doc.metadata.get("engine") == "docling"


class TestPyMuPDFEngine:
    """PyMuPDF 引擎测试"""

    def test_is_available(self):
        engine = PyMuPDFEngine()
        assert engine.is_available(), "PyMuPDF4LLM should be available"

    def test_engine_name(self):
        engine = PyMuPDFEngine()
        assert engine.name == "pymupdf"

    def test_extract(self, multi_column_pdf):
        engine = PyMuPDFEngine()
        doc = engine.extract(multi_column_pdf)

        assert doc.raw_markdown, "Should produce markdown output"
        assert len(doc.raw_markdown) > 100
        assert doc.metadata.get("engine") == "pymupdf"

    def test_block_structure(self, multi_column_pdf):
        engine = PyMuPDFEngine()
        doc = engine.extract(multi_column_pdf)

        assert len(doc.blocks) > 0, "Should parse blocks from markdown"

        # Check block types are valid
        valid_types = {"heading", "paragraph", "list_item", "table", "code"}
        for block in doc.blocks:
            assert block.type.value in valid_types
