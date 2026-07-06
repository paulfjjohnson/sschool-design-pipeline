from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class InitialResult:
    initials: str
    needs_review: bool = False
    reason: str = ""


class InitialGenerator:
    _ignored_words = {"the", "of", "and", "&"}

    def generate(self, school_name: str) -> InitialResult:
        normalized = school_name.strip()
        if not normalized:
            return InitialResult("", True, "School name is required.")

        words = [
            word.strip(" .'\"()[]{}")
            for word in normalized.replace("-", " ").split()
            if word.strip(" .'\"()[]{}")
        ]
        meaningful = [word for word in words if word.lower() not in self._ignored_words]
        if not meaningful:
            return InitialResult("", True, "School name does not contain usable words.")

        initials = "".join(word[0].upper() for word in meaningful if word[0].isalpha())
        if not initials:
            return InitialResult("", True, "School name does not contain alphabetic initials.")
        return InitialResult(initials)

