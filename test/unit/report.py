import tempfile
import unittest
from pathlib import Path

from docx import Document

from tools.openmotor_report import (
    DEFAULT_TEMPLATE,
    generate_report,
    load_template,
)


class ReportGeneratorMethods(unittest.TestCase):

    def test_template_has_required_bilingual_sections(self):
        template = load_template(DEFAULT_TEMPLATE)
        self.assertIn("PURPOSE AND SCOPE", template["sections"]["purpose"])
        self.assertIn("OBJETIVO E ESCOPO", template["sections"]["purpose"])
        self.assertIn("disclaimer_en", template["text"])
        self.assertIn("disclaimer_pt", template["text"])

    def test_generates_complete_word_report(self):
        motorPath = (
            Path(__file__).parents[1]
            / "data"
            / "regression"
            / "simple"
            / "motor.ric"
        )
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "report.docx"
            config = {
                "motor": str(motorPath),
                "output": str(output),
                "template": str(DEFAULT_TEMPLATE),
                "metadata": {
                    "motor_name": "Test Motor",
                    "project": "Unit Test",
                    "prepared_by": "openMotor",
                    "organization": "openMotor",
                    "document_id": "TEST-001",
                    "revision": "A",
                    "status": "Test",
                    "date": "2026-09-21",
                },
                "simulation": {"map_dim": 250},
                "figures": {
                    "dpi": 72,
                    "regression_map_dim": 64,
                    "regression_contours": 3,
                    "keep_png_files": False,
                },
            }
            result = generate_report(config)
            self.assertEqual(result["output"], str(output))
            self.assertTrue(output.is_file())
            self.assertGreater(output.stat().st_size, 20_000)

            document = Document(output)
            text = "\n".join(
                paragraph.text for paragraph in document.paragraphs
            )
            self.assertIn("INTERNAL BALLISTICS MOTOR REPORT", text)
            self.assertIn("SIMULATED PERFORMANCE", text)
            self.assertIn("CONCLUSIONS / CONCLUSÕES", text)
            self.assertGreaterEqual(len(document.inline_shapes), 4)


if __name__ == "__main__":
    unittest.main()
