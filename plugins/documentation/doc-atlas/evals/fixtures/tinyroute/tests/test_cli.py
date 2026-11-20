import contextlib
import io
import unittest

from tinyroute.cli import main


class GreetingContract(unittest.TestCase):
    def test_named_greeting(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            status = main(["--name", "Ada"])
        self.assertEqual(status, 0)
        self.assertEqual(output.getvalue(), "Hello, Ada!\n")

    def test_name_is_required(self):
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as result:
                main([])
        self.assertEqual(result.exception.code, 2)

    def test_unsupported_flag_is_rejected(self):
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as result:
                main(["--name", "Ada", "--fast"])
        self.assertEqual(result.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
