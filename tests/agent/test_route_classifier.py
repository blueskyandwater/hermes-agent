"""
Tests for route_classifier — 50+ cases covering all routes,
edge cases, and common misclassification traps.

Run with::
    python -m pytest tests/agent/test_route_classifier.py -v
"""

from __future__ import annotations

import pytest

from agent.route_classifier import (
    classify_message,
    classify_message_legacy,
    get_fallback_route_model,
    get_route_model,
    get_route_type_strings,
)


# =========================================================================
# classify_message — return type
# =========================================================================


class TestReturnType:
    """classify_message always returns (route_type, reason)."""

    def test_returns_tuple(self):
        result = classify_message("hello")
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_first_element_is_route_type(self):
        route, reason = classify_message("hello")
        assert isinstance(route, str)

    def test_second_element_is_reason(self):
        route, reason = classify_message("hello")
        assert isinstance(reason, str)

    def test_legacy_shim_returns_string(self):
        assert isinstance(classify_message_legacy("hello"), str)

    def test_legacy_matches_classify_type(self):
        assert classify_message_legacy("hello") == classify_message("hello")[0]


# =========================================================================
# simple_command
# =========================================================================


class TestSimpleCommand:
    @pytest.mark.parametrize("text,reason", [
        ("/help", "starts_with_slash"),
        ("/status", "starts_with_slash"),
        ("/sethome", "starts_with_slash"),
        ("/reset", "starts_with_slash"),
        ("/new", "starts_with_slash"),
        ("/quit", "starts_with_slash"),
        ("/exit", "starts_with_slash"),
        ("/clear", "starts_with_slash"),
        ("/undo", "starts_with_slash"),
        ("/retry", "starts_with_slash"),
        ("/compress", "starts_with_slash"),
        ("/echo", "starts_with_slash"),
    ])
    def test_recognises_slash_commands(self, text, reason):
        route, rsn = classify_message(text)
        assert route == "simple_command"
        assert rsn == reason

    @pytest.mark.parametrize("text", [
        "/ help",     # space after slash — not a command
        "help",       # no slash
        "not/a/slash",
        "//comment",
    ])
    def test_rejects_non_commands(self, text):
        route, rsn = classify_message(text)
        assert route != "simple_command"


# =========================================================================
# vision (image detection)
# =========================================================================


class _MessagesWithImage:
    """Factory for message lists with various image content shapes."""

    @staticmethod
    def image_url(text: str = "what's in this image?") -> list:
        return [{"role": "user", "content": [
            {"type": "text", "text": text},
            {"type": "image_url", "image_url": {"url": "data:image/png;base64,abc123"}},
        ]}]

    @staticmethod
    def image_only(text: str = "describe this") -> list:
        return [{"role": "user", "content": [
            {"type": "text", "text": text},
            {"type": "image", "image": {"data": b"fakebytes"}},
        ]}]

    @staticmethod
    def input_image(text: str = "analyze") -> list:
        return [{"role": "user", "content": [
            {"type": "text", "text": text},
            {"type": "input_image", "input_image": {"data": "base64..."}},
        ]}]

    @staticmethod
    def multi_turn(text: str = "and this?") -> list:
        return [
            {"role": "user", "content": "first message"},
            {"role": "assistant", "content": "ok"},
            {"role": "user", "content": [
                {"type": "text", "text": text},
                {"type": "image_url", "image_url": {"url": "https://example.com/photo.jpg"}},
            ]},
        ]

    @staticmethod
    def no_images(text: str = "hello") -> list:
        return [{"role": "user", "content": text}]


class TestVision:
    """Messages with image content should be classified as ``vision``."""

    def test_image_url_type(self):
        route, rsn = classify_message("what's this?", _MessagesWithImage.image_url())
        assert route == "vision"
        assert rsn == "image_in_message"

    def test_image_type(self):
        route, rsn = classify_message("describe", _MessagesWithImage.image_only())
        assert route == "vision"
        assert rsn == "image_in_message"

    def test_input_image_type(self):
        route, rsn = classify_message("analyze", _MessagesWithImage.input_image())
        assert route == "vision"
        assert rsn == "image_in_message"

    def test_multi_turn_with_image(self):
        route, rsn = classify_message("and this?", _MessagesWithImage.multi_turn())
        assert route == "vision"
        assert rsn == "image_in_message"

    def test_no_history_returns_normal_chat(self):
        route, rsn = classify_message("hello")
        assert route == "normal_chat"

    def test_no_images_in_history_returns_normal_chat(self):
        route, rsn = classify_message("hello", _MessagesWithImage.no_images())
        assert route == "normal_chat"

    def test_vision_beats_code_triggers(self):
        """Vision wins over code triggers — image is more important."""
        route, rsn = classify_message(
            "fix this bug",
            _MessagesWithImage.image_url("fix this bug"),
        )
        assert route == "vision", f"Expected vision, got {route}"

    def test_slash_command_beats_vision(self):
        """simple_command still beats vision for internal commands."""
        route, rsn = classify_message(
            "/help",
            _MessagesWithImage.image_url("/help"),
        )
        assert route == "simple_command"

    def test_vision_beats_summary(self):
        route, rsn = classify_message(
            "要約して",
            _MessagesWithImage.image_url("要約して"),
        )
        assert route == "vision"

    def test_empty_history(self):
        route, rsn = classify_message("hello", [])
        assert route == "normal_chat"


# =========================================================================
# code_or_debug
# =========================================================================


class TestCodeOrDebug:
    """code_or_debug — catch-all for generic code/tech triggers."""

    @pytest.mark.parametrize("text,reason", [
        # Code generation
        ("write a python function", "keyword:code_or_debug"),
        ("implement fibonacci", "keyword:code_or_debug"),
        ("create an api endpoint", "keyword:code_or_debug"),
        ("build a docker image", "keyword:code_or_debug"),
        ("generate sql schema", "keyword:code_or_debug"),
        ("refactor this class", "keyword:code_or_debug"),
        # Debugging / errors (generic, not specific enough for sub-routes)
        ("fix this bug", "keyword:code_or_debug"),
        ("debug this crash", "keyword:code_or_debug"),
        # System / architecture
        ("design a database schema", "keyword:code_or_debug"),
        ("migration plan", "keyword:code_or_debug"),
        ("config pipeline", "keyword:code_or_debug"),
        ("docker container crash", "keyword:code_or_debug"),
        # Japanese debugging (generic)
        ("なぜエラーになる？", "keyword:code_or_debug"),
        ("バグを直して", "keyword:code_or_debug"),
        ("デバッグして", "keyword:code_or_debug"),
    ])
    def test_code_or_debug(self, text, reason):
        route, rsn = classify_message(text)
        assert route == "code_or_debug", f"'{text}' → {route}"
        assert rsn == reason

    def test_rejects_casual_use_of_code_words(self):
        """'test' alone in casual context should not trigger code_or_debug."""
        route, rsn = classify_message("これテストです")
        assert route != "code_or_debug"


# =========================================================================
# code_implementation
# =========================================================================


class TestCodeImplementation:
    @pytest.mark.parametrize("text,reason", [
        ("この機能を実装して", "keyword:code_implementation"),
        ("コードを書いてください", "keyword:code_implementation"),
        ("パッチ案を作って", "keyword:code_implementation"),
        ("pytestを追加して", "keyword:code_implementation"),
        ("テストを追加して", "keyword:code_implementation"),
        ("テスト追加", "keyword:code_implementation"),
        ("diffを確認して", "keyword:code_implementation"),
    ])
    def test_code_implementation(self, text, reason):
        route, rsn = classify_message(text)
        assert route == "code_implementation", f"'{text}' → {route}"
        assert rsn == reason


class TestLargeImplementation:
    @pytest.mark.parametrize("text", [
        "認証機能を大規模に実装して",
        "複数ファイルにまたがる新機能を実装して",
        "DBスキーマ、APIエンドポイント、テストまで含めて機能追加して",
    ])
    def test_explicit_large_implementation_keywords(self, text):
        route, rsn = classify_message(text)
        assert route == "large_implementation", f"'{text}' → {route}"
        assert rsn == "keyword:large_implementation"

    def test_large_implementation_by_combined_heuristics(self):
        text = (
            "ユーザー管理機能を実装して。"
            "まずdatabase schemaを追加して、次にAPI endpointを作り、"
            "その後migrationとpytestも追加して、最後にconfig更新までお願いします。"
            "要件: 1. CRUD 2. 認証 3. 監査ログ"
        )
        route, rsn = classify_message(text)
        assert route == "large_implementation"
        assert rsn.startswith("large_heuristic:")

    def test_small_implementation_stays_code_implementation(self):
        route, rsn = classify_message("テストを追加して")
        assert route == "code_implementation"
        assert rsn == "keyword:code_implementation"


# =========================================================================
# code_design
# =========================================================================


class TestCodeDesign:
    @pytest.mark.parametrize("text,reason", [
        ("PR分割案を作って", "keyword:code_design"),
        ("実装計画を立てて", "keyword:code_design"),
        ("設計方針をレビューして", "keyword:code_design"),
        ("方針レビューをお願い", "keyword:code_design"),
        ("アーキテクチャを見直して", "keyword:code_design"),
        ("アーキテクチャ設計を考えて", "keyword:code_design"),
        ("影響範囲を確認して", "keyword:code_design"),
        ("rollback方法も考えて", "keyword:code_design"),
        ("リファクタリング設計", "keyword:code_design"),
        ("設計見直し", "keyword:code_design"),
    ])
    def test_code_design(self, text, reason):
        route, rsn = classify_message(text)
        assert route == "code_design", f"'{text}' → {route}"
        assert rsn == reason


# =========================================================================
# code_debug
# =========================================================================


class TestCodeDebug:
    @pytest.mark.parametrize("text,reason", [
        ("このTracebackを解析して", "keyword:code_debug"),
        ("Traceback (most recent call last)", "keyword:code_debug"),
        ("stack traceを見せて", "keyword:code_debug"),
        ("gateway.logを見て原因を調べて", "keyword:code_debug"),
        ("error logを確認して", "keyword:code_debug"),
        ("ログ解析して", "keyword:code_debug"),
        ("エラー解析して", "keyword:code_debug"),
        ("例外解析して", "keyword:code_debug"),
        ("原因を調べて", "keyword:code_debug"),
        ("原因を調査して", "keyword:code_debug"),
        ("原因を特定して", "keyword:code_debug"),
        ("原因調査", "keyword:code_debug"),
        ("なぜ動かないか調べて", "keyword:code_debug"),
        ("exit code 1", "keyword:code_debug"),
        ("non-zero exit code", "keyword:code_debug"),
        ("segfaultが出た", "keyword:code_debug"),
    ])
    def test_code_debug(self, text, reason):
        route, rsn = classify_message(text)
        assert route == "code_debug", f"'{text}' → {route}"
        assert rsn == reason


# =========================================================================
# code_light
# =========================================================================


class TestCodeLight:
    @pytest.mark.parametrize("text,reason", [
        ("ModuleNotFoundError", "keyword:code_light"),
        ("ModuleNotFoundErrorが出た", "keyword:code_light"),
        ("module not found", "keyword:code_light"),
        ("import errorが出る", "keyword:code_light"),
        ("pip installで入らない", "keyword:code_light"),
        ("インストールできない", "keyword:code_light"),
        ("入れない", "keyword:code_light"),
        ("command not found", "keyword:code_light"),
        ("このコマンドで合ってる？", "keyword:code_light"),
        ("使い方を教えて", "keyword:code_light"),
    ])
    def test_code_light(self, text, reason):
        route, rsn = classify_message(text)
        assert route == "code_light", f"'{text}' → {route}"
        assert rsn == reason


# =========================================================================
# research
# =========================================================================


class TestResearch:
    @pytest.mark.parametrize("text,reason", [
        # English triggers
        ("research this topic", "keyword:research"),
        ("investigate the issue", "keyword:research"),
        ("analyze the data", "keyword:research"),
        ("survey the landscape", "keyword:research"),
        ("compare GPT-5 and Claude", "keyword:research"),
        ("contrast these approaches", "keyword:research"),
        ("evaluate the results", "keyword:research"),
        # Japanese triggers
        ("OpenRouterの料金を調べて", "keyword:research"),
        ("Gemini 2.5 Flashの価格を教えて", "keyword:research"),
        ("最新のAI動向を検索", "keyword:research"),
        ("Hermes Agentの最新変更点を調べて", "keyword:research"),
        ("Claude Sonnet 4の仕様を確認して", "keyword:research"),
        ("DeepSeekの公式情報を調べて", "keyword:research"),
        ("GPT-5の変更点を調査", "keyword:research"),
        ("Perplexityの最新アップデート", "keyword:research"),
        ("Hermes Agent リリースノート", "keyword:research"),
        ("ClaudeとGPT-4の違い", "keyword:research"),
        ("OpenRouterのレビュー", "keyword:research"),
        ("DeepSeek V4の評価", "keyword:research"),
        ("情報収集して", "keyword:research"),
        ("AIニュースを調べて", "keyword:research"),
        ("文献を調査して", "keyword:research"),
        ("研究して", "keyword:research"),
        ("Claude Sonnet 4の仕様が知りたい", "keyword:research"),
    ])
    def test_research(self, text, reason):
        route, rsn = classify_message(text)
        assert route == "research", f"'{text}' → {route}"
        assert rsn == reason

    def test_research_not_triggered_by_casual_usage(self):
        """日本語の「調子」は「調べ」と異なるので research にならない."""
        route, rsn = classify_message("今日の調子どう？")
        assert route != "research"


# =========================================================================
# summary
# =========================================================================


class TestSummary:
    @pytest.mark.parametrize("text,reason", [
        ("以下を要約して", "keyword:summary"),
        ("要約して", "keyword:summary"),
        ("まとめて", "keyword:summary"),
        ("要点だけ教えて", "keyword:summary"),
        ("議事録を作成して", "keyword:summary"),
        ("会議メモをまとめて", "keyword:summary"),
        ("ログ要約して", "keyword:summary"),
        ("ログを要約して", "keyword:summary"),
        ("summarize this", "keyword:summary"),
        ("summary please", "keyword:summary"),
        ("tl;dr", "keyword:summary"),
        ("tldr", "keyword:summary"),
    ])
    def test_summary(self, text, reason):
        route, rsn = classify_message(text)
        assert route == "summary", f"'{text}' → {route}"
        assert rsn == reason


# =========================================================================
# long_context
# =========================================================================


class TestLongContext:
    @pytest.mark.parametrize("text,reason", [
        ("この長文を解析して", "keyword:long_context"),
        ("ドキュメント解析して", "keyword:long_context"),
        ("コードベースをレビューして", "keyword:long_context"),
        ("全文を読んで", "keyword:long_context"),
        ("大量のデータを解析", "keyword:long_context"),
        ("この仕様書を解析して", "keyword:long_context"),
        ("long document analysis", "keyword:long_context"),
        ("analyse this file", "keyword:long_context"),
    ])
    def test_long_context_triggers(self, text, reason):
        route, rsn = classify_message(text)
        assert route == "long_context", f"'{text}' → {route}"
        assert rsn == reason

    def test_long_context_by_length(self):
        text = "x" * 2500
        route, rsn = classify_message(text)
        assert route == "long_context"
        assert rsn == "length>2000"

    def test_short_text_not_long_context(self):
        text = "x" * 500
        route, rsn = classify_message(text)
        assert route != "long_context"


# =========================================================================
# normal_chat (default)
# =========================================================================


class TestNormalChat:
    @pytest.mark.parametrize("text", [
        "",
        "hello",
        "おはよう",
        "今日はいい天気だね",
        "ご飯食べた？",
        "ありがとう",
        "うん、わかった",
        "そうなんだ",
        "教えてくれてありがとう",
        "おやすみ",
        "What's up?",
        "How are you?",
        "thanks",
        "👍",
        "😂",
    ])
    def test_normal_chat(self, text):
        route, rsn = classify_message(text)
        assert route == "normal_chat", f"'{text}' → {route}"
        assert rsn == ""

    def test_empty_text_returns_normal_chat(self):
        route, rsn = classify_message("")
        assert route == "normal_chat"


# =========================================================================
# Route prioritisation — first match wins
# =========================================================================


class TestPrioritisation:
    """Verify that rules are evaluated in the documented order."""

    def test_slash_beats_code(self):
        """simple_command (/) beats code_or_debug."""
        route, rsn = classify_message("/help fix this bug")
        assert route == "simple_command"

    def test_code_beats_research(self):
        """code_debug beats research (code triggers first)."""
        route, rsn = classify_message("このエラーを調べて原因を特定して")
        assert route == "code_debug"

    def test_research_beats_summary(self):
        """research beats summary (research before summary in order)."""
        route, rsn = classify_message("Claudeの評価を要約して")
        assert route == "research"

    def test_summary_beats_long_context(self):
        """summary beats long_context even with long text."""
        route, rsn = classify_message("以下を要約して " + "x" * 2100)
        assert route == "summary"

    def test_length_check_is_last(self):
        """long text without keyword triggers falls to long_context."""
        text = "a" * 2500
        route, rsn = classify_message(text)
        assert route == "long_context"

    def test_code_beats_normal_chat(self):
        route, rsn = classify_message("このコードにバグがある")
        assert route == "code_or_debug"


# =========================================================================
# Edge cases — common misclassification traps
# =========================================================================


class TestEdgeCases:
    """Cases that are easy to misclassify without careful rules."""

    def test_addition_vs_code(self):
        """'add ' triggers code — even in casual use."""
        route, rsn = classify_message("add two numbers")
        assert route == "code_or_debug"

    def test_casual_compare_trigger(self):
        """'compare ' triggers research."""
        route, rsn = classify_message("compare these two phones")
        assert route == "research"

    def test_fix_in_casual_context(self):
        """'fix ' triggers code_or_debug."""
        route, rsn = classify_message("fix my bike")
        assert route == "code_or_debug"

    def test_log_in_casual_context(self):
        """'log' alone triggers code_or_debug."""
        route, rsn = classify_message("I keep a daily log")
        assert route == "code_or_debug"

    def test_test_in_code_context(self):
        """'test ' in a code context should trigger code_or_debug."""
        route, rsn = classify_message("test this function")
        assert route == "code_or_debug"

    def test_code_plus_research_keyword(self):
        """Code+research → code wins (priority order)."""
        route, rsn = classify_message("このコードのバグを調べて")
        assert route == "code_or_debug"

    def test_short_summary_request(self):
        """Very short summary request."""
        route, rsn = classify_message("要約")
        assert route == "summary"

    def test_research_does_not_leak_to_normal_chat(self):
        """'調子' should NOT match '調べ'."""
        route, rsn = classify_message("調子はどう？")
        assert route == "normal_chat"

    def test_summary_plus_code(self):
        """summary + code → code wins (priority order)."""
        route, rsn = classify_message("要約＋デバッグ")
        assert route == "code_or_debug"

    def test_long_context_plus_summary(self):
        """long text with summary trigger → summary wins."""
        text = "要約して " + "x" * 2100
        route, rsn = classify_message(text)
        assert route == "summary"

    def test_summary_prefix_mixed_case(self):
        """Mixed case summary."""
        route, rsn = classify_message("TL;DR this for me")
        assert route == "summary"

    def test_research_with_code_noise(self):
        """Research with code-like noise in text."""
        route, rsn = classify_message("LLMのAPI料金を比較したい")
        assert route == "research"

    def test_spec_versus_specification_book(self):
        """'仕様' + particle = research, '仕様書' = long_context."""
        r1, _ = classify_message("Claudeの仕様を確認して")
        r2, _ = classify_message("この仕様書を解析して")
        assert r1 == "research"
        assert r2 == "long_context"

    def test_review_versus_code_review(self):
        """'のレビュー' = research, 'コードベースをレビュー' = long_context."""
        r1, _ = classify_message("OpenRouterのレビュー")
        r2, _ = classify_message("コードベースをレビューして")
        assert r1 == "research"
        assert r2 == "long_context"

    @pytest.mark.parametrize("text", [
        "こんにちは", "やあ", "お願いします", "なるほど",
        "それはいいね", "OK", "はい", "いいえ",
    ])
    def test_simple_greetings(self, text):
        route, rsn = classify_message(text)
        assert route == "normal_chat"


# =========================================================================
# get_route_model
# =========================================================================


class TestCodeLightContextGuard:
    def test_short_context_keeps_code_light(self):
        route, rsn = classify_message(
            "pip install の使い方を教えて",
            context_token_estimate=2_000,
        )
        assert route == "code_light"
        assert rsn == "keyword:code_light"

    def test_large_context_routes_code_light_to_long_context(self):
        route, rsn = classify_message(
            "pip install の使い方を教えて",
            context_token_estimate=30_000,
        )
        assert route == "long_context"
        assert rsn == "context_tokens>6000:code_light_guard"

    def test_observed_spark_failure_zone_routes_away_from_code_light(self):
        route, rsn = classify_message(
            "pip install の使い方を教えて",
            context_token_estimate=9_040,
        )
        assert route == "long_context"
        assert rsn == "context_tokens>6000:code_light_guard"

    def test_missing_context_estimate_preserves_legacy_code_light(self):
        route, rsn = classify_message("pip install の使い方を教えて")
        assert route == "code_light"
        assert rsn == "keyword:code_light"


class TestGetRouteModel:
    def test_returns_configured_model(self):
        config = {"research": {"model": "perplexity/sonar"}}
        assert get_route_model("research", config) == "perplexity/sonar"

    def test_returns_empty_for_missing_route(self):
        assert get_route_model("unknown", {"research": {}}) == ""

    def test_fallback_when_route_has_no_model(self):
        config = {"research": {}, "fallback": "deepseek/deepseek-v4-flash"}
        assert get_route_model("research", config) == "deepseek/deepseek-v4-flash"

    def test_sub_route_aliases_to_parent(self):
        """code implementation sub-routes alias to code_or_debug model."""
        config = {"code_or_debug": {"model": "deepseek/deepseek-v4-flash"}}
        assert get_route_model("code_implementation", config) == "deepseek/deepseek-v4-flash"
        assert get_route_model("large_implementation", config) == "deepseek/deepseek-v4-flash"
        assert get_route_model("code_design", config) == "deepseek/deepseek-v4-flash"
        assert get_route_model("code_debug", config) == "deepseek/deepseek-v4-flash"
        assert get_route_model("code_light", config) == "deepseek/deepseek-v4-flash"

    def test_large_implementation_can_have_dedicated_model(self):
        config = {
            "large_implementation": {"model": "openai-codex/gpt-5.5"},
            "code_or_debug": {"model": "deepseek/deepseek-v4-flash"},
        }
        assert get_route_model("large_implementation", config) == "openai-codex/gpt-5.5"


class TestGetFallbackRouteModel:
    def test_returns_fallback_route_model(self):
        config = {
            "normal_chat": {"model": "gpt-5.5"},
            "fallback_routes": {
                "normal_chat": {"model": "deepseek/deepseek-v4-flash"},
            },
        }
        assert get_fallback_route_model("normal_chat", config) == "deepseek/deepseek-v4-flash"

    def test_accepts_fallback_routing_alias_and_string_values(self):
        config = {
            "fallback_routing": {
                "research": "perplexity/sonar-pro",
            },
        }
        assert get_fallback_route_model("research", config) == "perplexity/sonar-pro"

    def test_sub_route_aliases_to_parent_fallback_route(self):
        config = {
            "fallback_routes": {
                "code_or_debug": {"model": "deepseek/deepseek-v4-pro"},
            },
        }
        assert get_fallback_route_model("code_implementation", config) == "deepseek/deepseek-v4-pro"
        assert get_fallback_route_model("large_implementation", config) == "deepseek/deepseek-v4-pro"

    def test_empty_when_no_fallback_route_configured(self):
        config = {"normal_chat": {"model": "gpt-5.5"}}
        assert get_fallback_route_model("normal_chat", config) == ""


# =========================================================================
# get_route_type_strings
# =========================================================================


class TestGetRouteTypeStrings:
    def test_returns_tuple(self):
        routes = get_route_type_strings()
        assert isinstance(routes, tuple)

    def test_includes_all_active_routes(self):
        routes = get_route_type_strings()
        required = {"simple_command", "normal_chat", "vision",
                     "code_implementation", "large_implementation",
                     "code_design", "code_debug", "code_light", "code_or_debug",
                     "summary", "research", "long_context"}
        assert required.issubset(set(routes))
