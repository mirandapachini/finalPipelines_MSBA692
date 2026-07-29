import importlib
import unittest


class AppEntrypointTests(unittest.TestCase):
    def test_root_app_module_exposes_dash_app(self):
        app_module = importlib.import_module("app")
        self.assertTrue(hasattr(app_module, "app"))
        self.assertTrue(hasattr(app_module, "server"))


if __name__ == "__main__":
    unittest.main()
