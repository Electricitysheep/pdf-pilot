"""测试配置和夹具"""

import logging
from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def fixtures_dir():
    return FIXTURES_DIR


@pytest.fixture
def multi_column_pdf():
    """多栏排版 PDF"""
    path = FIXTURES_DIR / "chelsea_pdta.pdf"
    if not path.exists():
        pytest.skip(f"Fixture not found: {path}")
    return str(path)


@pytest.fixture
def table_pdf():
    """含表格的 PDF"""
    path = FIXTURES_DIR / "federal-register.pdf"
    if not path.exists():
        pytest.skip(f"Fixture not found: {path}")
    return str(path)


@pytest.fixture
def academic_pdf():
    """学术论文 (公式/表格)"""
    path = FIXTURES_DIR / "attention.pdf"
    if not path.exists():
        pytest.skip(f"Fixture not found: {path}")
    return str(path)


@pytest.fixture
def scanned_pdf():
    """扫描型 PDF"""
    path = FIXTURES_DIR / "scanned.pdf"
    if not path.exists():
        pytest.skip(f"Fixture not found: {path}")
    return str(path)


@pytest.fixture
def output_dir(tmp_path):
    return tmp_path / "output"


@pytest.fixture
def caplog(caplog):
    caplog.set_level(logging.DEBUG)
    return caplog
