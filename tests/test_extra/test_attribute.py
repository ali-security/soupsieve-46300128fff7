"""Test attribute selectors."""
from .. import util
import soupsieve as sv


class TestAttribute(util.TestCase):
    """Test attribute selectors."""

    MARKUP = """
    <div id="div">
    <p id="0">Some text <span id="1"> in a paragraph</span>.</p>
    <a id="2" href="http://google.com">Link</a>
    <span id="3">Direct child</span>
    <pre id="pre">
    <span id="4">Child 1</span>
    <span id="5">Child 2</span>
    <span id="6">Child 3</span>
    </pre>
    </div>
    """

    def test_attribute_not_equal_no_quotes(self):
        """Test attribute with value that does not equal specified value (no quotes)."""

        # No quotes
        self.assert_selector(
            self.MARKUP,
            'body [id!=\\35]',
            ["div", "0", "1", "2", "3", "pre", "4", "6"],
            flags=util.HTML5
        )

    def test_attribute_not_equal_quotes(self):
        """Test attribute with value that does not equal specified value (quotes)."""

        # Quotes
        self.assert_selector(
            self.MARKUP,
            "body [id!='5']",
            ["div", "0", "1", "2", "3", "pre", "4", "6"],
            flags=util.HTML5
        )

    def test_attribute_not_equal_double_quotes(self):
        """Test attribute with value that does not equal specified value (double quotes)."""

        # Double quotes
        self.assert_selector(
            self.MARKUP,
            'body [id!="5"]',
            ["div", "0", "1", "2", "3", "pre", "4", "6"],
            flags=util.HTML5
        )

    def assert_syntax_error_no_timeout(self, pattern):
        """Assert pattern fails for syntax error, not timeout error."""

        import signal
        import time

        def timeout_handler(signum, frame):
            raise TimeoutError

        # `SIGALRM` is not available on Windows, so there we only check the elapsed time.
        has_alarm = hasattr(signal, 'SIGALRM')
        if has_alarm:
            old_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(3)

        passed = False
        start = time.perf_counter()
        try:
            with self.assertRaises(sv.SelectorSyntaxError):
                sv.compile(pattern)
            passed = True
        except TimeoutError:
            pass
        finally:
            if has_alarm:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)
        self.assertTrue(passed)
        self.assertLess(time.perf_counter() - start, 3)

    def test_bad_attribute_unclused(self):
        """Test bad attribute fails for syntax error, not timeout error."""

        self.assert_syntax_error_no_timeout('[a="' + ('x' * 300))

    def test_bad_attribute_unclosed_single_quote(self):
        """Test bad attribute with single quote fails for syntax error, not timeout error."""

        self.assert_syntax_error_no_timeout("[a='" + ('x' * 300))

    def test_bad_pseudo_contains_unclosed(self):
        """Test unclosed quoted value in `:-soup-contains()` fails for syntax error, not timeout error."""

        # `:-soup-contains()` shares the same quoted value pattern as attributes.
        self.assert_syntax_error_no_timeout(':-soup-contains("' + ('x' * 300))
        self.assert_syntax_error_no_timeout(":-soup-contains('" + ('x' * 300))

    def test_bad_pseudo_lang_unclosed(self):
        """Test unclosed quoted value in `:lang()` fails for syntax error, not timeout error."""

        # `:lang()` shares the same quoted value pattern as attributes.
        self.assert_syntax_error_no_timeout(':lang("' + ('x' * 300))
        self.assert_syntax_error_no_timeout(":lang('" + ('x' * 300))

    def test_attribute_quoted_value_still_matches(self):
        """Test that closed quoted values, including escapes, still match after the ReDoS fix."""

        markup = """
        <div>
        <span id="1" data-a='x"y'>a</span>
        <span id="2" data-a="x'y">b</span>
        <span id="3" data-a="x\\y">c</span>
        </div>
        """

        self.assert_selector(markup, '[data-a="x\\"y"]', ["1"], flags=util.HTML5)
        self.assert_selector(markup, "[data-a='x\\'y']", ["2"], flags=util.HTML5)
        self.assert_selector(markup, '[data-a="x\\\\y"]', ["3"], flags=util.HTML5)
