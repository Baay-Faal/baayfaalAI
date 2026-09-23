"""
Banc de tests unitaires pour la Phase 4 (Interface Vocale Locale STT / TTS).
100 % Python Standard Library (unittest).
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from voice.listener import BaayListener
from voice.speaker import BaaySpeaker, clean_text_for_speech


class TestPhase4Voice(unittest.TestCase):
    def test_01_text_cleaning_for_speech(self):
        raw_text = "Voici un test **important** avec ```code block``` et un [lien](http://example.com) !"
        cleaned = clean_text_for_speech(raw_text)

        self.assertNotIn("```", cleaned)
        self.assertNotIn("**", cleaned)
        self.assertNotIn("http://example.com", cleaned)
        self.assertIn("important", cleaned)
        self.assertIn("lien", cleaned)

    def test_02_wake_word_detection(self):
        listener = BaayListener()

        self.assertTrue(listener.contains_wake_word("Bonjour Baay Faal"))
        self.assertTrue(listener.contains_wake_word("Dis moi Baye Fall le statut"))
        self.assertTrue(listener.contains_wake_word("Hey Baay-Agent exécute dir"))
        self.assertFalse(listener.contains_wake_word("Exécute simplement la commande dir"))

    def test_03_speaker_initialization(self):
        speaker = BaaySpeaker()
        self.assertIn(speaker.os_type, ["Windows", "Linux", "Darwin"])


if __name__ == "__main__":
    unittest.main()
