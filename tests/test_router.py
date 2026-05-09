"""路由器测试"""


from pdf_pilot.config import Config
from pdf_pilot.convert import _create_engines
from pdf_pilot.router import EngineRouter


class TestEngineRouter:
    """路由器测试"""

    def test_available_engines(self):
        """检查可用引擎列表"""
        config = Config()
        engines = _create_engines(config)
        router = EngineRouter(engines)

        available = router.get_available_engines()
        assert len(available) >= 1, "应至少有一个可用引擎"
        assert "pymupdf" in available

    def test_force_engine(self, multi_column_pdf):
        """强制指定引擎"""
        config = Config()
        engines = _create_engines(config)
        router = EngineRouter(engines)

        engine = router.route(multi_column_pdf, force_engine="docling")
        assert engine.name == "docling"

        engine = router.route(multi_column_pdf, force_engine="pymupdf")
        assert engine.name == "pymupdf"

    def test_auto_route_english_simple(self, multi_column_pdf):
        """英文简单 PDF 自动路由"""
        config = Config()
        engines = _create_engines(config)
        router = EngineRouter(engines)

        engine = router.route(multi_column_pdf)
        assert engine.name in ("docling", "pymupdf")

    def test_fallback_on_unavailable(self, multi_column_pdf):
        """不存在引擎的降级"""
        config = Config()
        engines = _create_engines(config)
        router = EngineRouter(engines)

        # mineru 可能不可用
        engine = router.route(multi_column_pdf, force_engine="mineru")
        # 如果不可用，应降级到可用引擎
        assert engine.name in ("docling", "pymupdf", "mineru")

    def test_list_engines(self):
        """列出引擎信息"""
        config = Config()
        engines = _create_engines(config)
        router = EngineRouter(engines)

        info = router.list_engines()
        assert len(info) >= 2
        for e in info:
            assert "name" in e
            assert "available" in e
            assert "priority" in e
