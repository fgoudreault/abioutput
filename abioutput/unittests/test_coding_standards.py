from flake8.api import legacy as flake8
import unittest


class CodeQualityTest(unittest.TestCase):
    def test_flake8_conformance(self):
        # call the styleguide
        style_guide = flake8.get_style_guide()
        report = style_guide.check_files()

        if report.total_errors > 0:  # pragma: no cover
            msg = "Found code syntax errors (and warnings)!\n"
            nerr = "Number of errors = %s\n" % report.total_errors
            self.fail(msg + nerr)
