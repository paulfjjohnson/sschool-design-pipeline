from app.engine.typography import TextRenderer


def test_text_renderer_requires_explicit_font_for_production() -> None:
    renderer = TextRenderer(font_path=None)

    assert renderer.font_available is False


def test_text_renderer_can_render_with_default_when_explicitly_allowed() -> None:
    renderer = TextRenderer(font_path=None, allow_default_font=True)

    image = renderer.render_text("PGP", (100, 40), fill=(255, 255, 255, 255))

    assert image.mode == "RGBA"
    assert image.getbbox() is not None

