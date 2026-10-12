import pytest

from src.emotion_client import (FallbackEmotionClient, KeywordEmotionClient,
                                TransformerEmotionClient, create_emotion_client,
                                validate_text)
from src.exceptions import AnalysisError, InvalidInputError


@pytest.mark.parametrize("bad", ["", "   ", "\n\t", None, 123])
def test_validate_text_rejects_empty_or_non_string(bad):
    with pytest.raises(InvalidInputError):
        validate_text(bad)


def test_validate_text_rejects_too_long():
    with pytest.raises(InvalidInputError):
        validate_text("a" * 1001)


def test_validate_text_strips():
    assert validate_text("  hi  ") == "hi"


@pytest.mark.parametrize("text,label", [
    ("I am so happy and excited", "joy"),
    ("I feel lonely and sad", "sadness"),
    ("I am furious, I hate this", "anger"),
    ("I'm scared and anxious", "fear"),
    ("I love you, darling", "love"),
    ("Wow, what an unexpected surprise", "surprise"),
])
def test_keyword_client_labels(text, label):
    result = KeywordEmotionClient().get_emotion(text)
    assert result.label == label
    assert result.source == "keyword"
    assert 0 < result.score < 1  # never claims 100 %


def test_keyword_client_no_match_is_neutral_zero():
    result = KeywordEmotionClient().get_emotion("The table is made of wood")
    assert result.label == "neutral" and result.score == 0.0


def test_transformer_nested_list_output():
    fake = lambda text: [[{"label": "sadness", "score": 0.2},  # noqa: E731
                          {"label": "Joy", "score": 0.8}]]
    result = TransformerEmotionClient(classifier=fake).get_emotion("hello")
    assert result.label == "joy" and result.score == 0.8


def test_transformer_flat_output():
    fake = lambda text: [{"label": "anger", "score": 0.91234}]  # noqa: E731
    result = TransformerEmotionClient(classifier=fake).get_emotion("hello")
    assert result.label == "anger" and result.score == 0.9123


def test_transformer_wraps_model_crash():
    def broken(text):
        raise RuntimeError("CUDA out of memory")
    with pytest.raises(AnalysisError):
        TransformerEmotionClient(classifier=broken).get_emotion("hello")


def test_transformer_empty_output():
    with pytest.raises(AnalysisError):
        TransformerEmotionClient(classifier=lambda t: []).get_emotion("hello")


def test_fallback_switches_to_keyword_when_model_fails():
    def broken(text):
        raise RuntimeError("model down")
    client = FallbackEmotionClient(TransformerEmotionClient(classifier=broken))
    result = client.get_emotion("I am happy")
    assert result.source == "keyword" and result.label == "joy"
    assert "model down" in client.last_error


def test_fallback_does_not_hide_bad_input():
    with pytest.raises(InvalidInputError):
        FallbackEmotionClient(None).get_emotion("   ")


def test_create_offline_client_uses_keyword():
    client = create_emotion_client(offline=True)
    assert client.name == "keyword"
    assert client.get_emotion("so happy").label == "joy"
