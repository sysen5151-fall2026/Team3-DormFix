"""The live gate must identify the original model even when API aliases collide."""
import unittest
from unittest.mock import patch
from scripts.start_model import DEFAULT_MODEL, loaded, original

class OriginalModelTests(unittest.TestCase):
    def test_require_original_instruct_family(self):
        self.assertTrue(original({"type":"llm","key":"lmstudio-community/Meta-Llama-3.1-8B-Instruct-GGUF"}))
        for key in ("Meta-Llama-3.1-8B","Qwen2.5-0.5B-Instruct","Llama-3.2-8B-Instruct",
                    "Meta-Llama-3.1-70B-Instruct","Meta-Llama-3.1-8B-Instruct-finetuned"):
            with self.subTest(key=key):
                self.assertFalse(original({"type":"llm","key":key}))

    def test_wrong_weights_cannot_pass_on_alias_alone(self):
        items = [{"type":"llm","key":"Qwen2.5-0.5B-Instruct","loaded_instances":[{"id":DEFAULT_MODEL}]},
                 {"type":"llm","key":"Meta-Llama-3.1-8B-Instruct","loaded_instances":[]}]
        with patch("scripts.start_model.models", return_value=items):
            with self.assertRaises(RuntimeError):
                loaded()
            items[1]["loaded_instances"].append({"id":"user-llama"})
            self.assertEqual(loaded()[1],"user-llama")
            with self.assertRaises(RuntimeError):
                loaded(requested=DEFAULT_MODEL)
