from app.engine.initials import InitialGenerator


def test_natural_initials_do_not_pad() -> None:
    generator = InitialGenerator()

    assert generator.generate("Pecan Grove Primary").initials == "PGP"
    assert generator.generate("Gonzales Primary").initials == "GP"
    assert generator.generate("Carver Primary").initials == "CP"
    assert generator.generate("Bluff Ridge Primary").initials == "BRP"


def test_initials_flag_empty_school_name() -> None:
    result = InitialGenerator().generate("   ")

    assert result.needs_review is True
    assert "School name is required" in result.reason

