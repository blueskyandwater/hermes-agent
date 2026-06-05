"""
Rule-based route classifier for incoming messages.

Determines the ``route_type`` of a user message based on simple pattern
matching, then selects the appropriate model from the routing config.
Also returns a ``classification_reason`` string explaining *why* that
route was chosen, enabling per-route monitoring in usage.log.

Routes (priority order — first match wins)
-------------------------------------------
1.  simple_command         Leading ``/`` + word (Hermes slash command)
2.  vision                 Image content detected in the message
3.  code_design            Architecture, design, planning, PR split
4.  large_implementation   Large feature implementation (explicit size keywords
                            OR implementation intent + complexity heuristics)
5.  code_implementation    Feature implementation, testing, patching
6.  code_debug             Traceback, stack trace, error analysis, log investigation
7.  code_light             Simple import/install issues, command checks, usage queries
8.  code_or_debug          (catch-all) Remaining code, debug, generic tech triggers
9.  summary                Summarisation, TL;DR, meeting notes
10. research               Research-heavy, deep investigation
11. long_context           Long document analysis (>2000 chars or explicit)
12. complex_task           ``estimate_complexity() >= 4`` — complex prompts that
                            no keyword matched (e.g. multi-step, high tech density)
13. normal_chat            DEFAULT — everyday conversation, casual Q&A

Future routes (classified but not yet associated with a model)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- sensitive_or_private
- creative_writing
- personal_advice
TODO: wire model config for the above routes once provider decisions
are made.

Usage
-----
    from agent.route_classifier import classify_message, get_route_model

    route_type, reason = classify_message(user_text)
    model = get_route_model(route_type, routing_config)

Provider fallback routing
~~~~~~~~~~~~~~~~~~~~~~~~~
When the active provider has fallen back, callers can use
``get_fallback_route_model()`` to resolve a model from either
``routing.fallback_routes`` or ``routing.fallback_routing``.  This keeps
primary-provider route models (for example ``gpt-5.5`` on OpenAI Codex)
from being reused against fallback providers (for example OpenRouter).
"""

from __future__ import annotations

import re
from typing import Optional

# ---------------------------------------------------------------------------
# Route definition — low-cost, rule-based matching
# ---------------------------------------------------------------------------

# ── simple_command ─────────────────────────────────────────────────────
# Leading ``/`` with no space = Hermes slash command.
_SIMPLE_COMMAND_RE = re.compile(r"^/\w+")

# ── code_or_debug ──────────────────────────────────────────────────────
# Triggers suggestive of code, debugging, error analysis, or system design.
_CODE_TRIGGERS = (
    # Code generation / implementation
    "write ", "implement", "create ", "build ", "generate", "refactor",
    "add ", "fix ", "debug", "compile", "function", "class ", "import ",
    "def ", "const ", "let ", "var ", "function ", "async ", "await ",
    "```", "print(", "console.log",
    # Error / log analysis
    "error", "traceback", "exception", "failed", "crash", "segfault",
    "trace", "log", "stderr", "stdout", "exit code", "non-zero",
    # System / architecture
    "architecture", "design ", "api ", "endpoint", "database", "schema",
    "migration", "deploy", "config", "pipeline", "workflow",
    "docker", "container", "kubernetes", "k8s", "ci/cd",
    # Shell / terminal
    "bash", "shell", "command", "terminal", "script",
    # Testing
    "test ", "pytest", "unittest", "mock", "assert",
    # Debugging related
    "なぜ", "原因", "エラー", "直し", "バグ", "デバッグ",
)

# ── code_implementation ────────────────────────────────────────────────
# Feature implementation, testing, patching — specific asks to write code.
_CODE_IMPL_TRIGGERS = (
    "実装して", "コードを書い", "作って", "書いて",
    "パッチを作", "パッチを書", "パッチして",
    "テスト追加", "テストを追加", "テストを書",
    "pytestを追加", "diffを確認",
    "機能を作", "機能を追加", "機能実装", "機能追加",
    "関数を作", "クラスを作", "メソッドを書",
)

# ── large_implementation ───────────────────────────────────────────────
# Larger coding tasks should be allowed to route to a stronger implementation
# model.  We intentionally combine explicit size keywords with heuristics so
# the route catches both obvious requests ("大規模に実装") and naturally phrased
# multi-step feature asks (schema + API + tests + migration).
_LARGE_IMPL_SIZE_TRIGGERS = (
    "大規模", "大きめ", "本格的", "複数ファイル", "複数箇所",
    "またがる", "全体", "一式", "エンドツーエンド", "end-to-end", "e2e",
)

_LARGE_IMPL_SCOPE_TRIGGERS = (
    "新機能", "機能追加", "認証機能", "ユーザー管理", "管理機能",
    "dbスキーマ", "データベース", "apiエンドポイント", "api endpoint",
    "endpoint", "migration", "マイグレーション", "schema", "database",
    "crud", "権限", "認証", "監査ログ",
)

# ── code_design ────────────────────────────────────────────────────────
# Architecture, design, planning, PR split — structural decisions.
_CODE_DESIGN_TRIGGERS = (
    # Japanese — user specified
    "pr分割", "実装計画",
    "設計方針", "方針レビュー",
    "アーキテクチャを見直し", "アーキテクチャ設計",
    "影響範囲", "rollback",
    "リファクタリング設計", "設計見直し",
)

# ── code_debug ─────────────────────────────────────────────────────────
# Traceback, stack trace, error analysis, log investigation.
_CODE_DEBUG_TRIGGERS = (
    # Stack traces
    "traceback", "stack trace",
    # Log analysis
    "gateway.log", "error log",
    "ログ解析", "エラー解析", "例外解析",
    # Investigation
    "原因調査", "原因を調べ", "原因を特定", "原因を調査",
    # Why analysis
    "なぜ動かない",
    # Specific errors
    "segfault",
    "exit code", "non-zero",
)

# ── code_light ─────────────────────────────────────────────────────────
# Simple import/install issues, command checks, usage queries.
_CODE_LIGHT_TRIGGERS = (
    # Import issues
    "modulenotfound", "module not found",
    "import error", "importできない",
    # Package install
    "pip install", "インストール",
    "入れない", "入らない",
    # Command check
    "command not found",
    "このコマンド",
    # Simple usage
    "使い方", "書き方",
)

# ── summary ──────────────────────────────────────────────────────────
# Explicit summarisation requests, meeting notes, TL;DR.
_SUMMARY_TRIGGERS = (
    "要約", "まとめ", "サマリー", "要点",
    "要約して", "まとめて",
    "議事録", "会議メモ",
    "ログ要約", "ログを要約",
    "summarize", "summary", "tl;dr", "tldr",
)

# ── long_context ───────────────────────────────────────────────────────
# Triggers suggesting long documents or deep processing.
_LONG_CONTEXT_TRIGGERS = (
    "long document", "analyse this", "analyze this",
    "長文", "ドキュメント解析", "コードベース",
    "long text", "long message",
    "全文", "大量", "を解析", "仕様書",
)

# ── research ───────────────────────────────────────────────────────────
_RESEARCH_TRIGGERS = (
    # English triggers
    "research", "investigate", "analyze", "survey",
    "compare ", "contrast", "evaluate",
    # Japanese triggers
    "調べ", "検索", "最新", "料金", "価格",
    "仕様を", "仕様の", "仕様は", "仕様が", "公式", "変更点",
    "アップデート", "リリースノート",
    "比較", "違い",
    "のレビュー", "レビューを", "評価",
    "情報収集", "ニュース",
    "文献", "調査", "研究",
)

# ── simple_command (additional text patterns) ──────────────────────────
_SIMPLE_COMMAND_WORDS = (
    "help", "status", "sethome", "reset", "new", "quit", "exit",
    "clear", "undo", "retry", "compress",
)

# ── Future route placeholder triggers (classified but not wired) ───────
# TODO: wire model config for these routes once provider decisions are made.
# _SENSITIVE_TRIGGERS = ("password", "credit card", "secret", ...)
# _CREATIVE_TRIGGERS  = ("poem", "story", "creative", ...)
# _ADVICE_TRIGGERS    = ("advice", "opinion", "recommend", ...)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _has_image_content(history: list) -> bool:
    """Return True if any message in *history* contains image content parts.

    Checks for ``image_url``, ``image``, and ``input_image`` content types
    used by OpenAI-compatible and multimodal providers.
    """
    for msg in history:
        if not isinstance(msg, dict):
            continue
        content = msg.get("content")
        if not isinstance(content, list):
            continue
        for part in content:
            if isinstance(part, dict) and part.get("type") in {
                "image_url",
                "image",
                "input_image",
            }:
                return True
    return False


# ---------------------------------------------------------------------------
# Complexity estimation (no API calls — pure heuristics)
# ---------------------------------------------------------------------------


def estimate_complexity(text: str) -> int:
    """Return estimated task complexity 1 (trivial) to 5 (very complex).

    Factors:
    - Multi-step markers (〜して〜して, then, first, numbered lists)
    - Technical keyword density
    - Code block presence
    - Text length
    - Questions / explicit requirements count

    Threshold recommendation:
        >= 5 → route to ``complex_task`` (high-cost model)
    """
    if not text:
        return 1

    score = 1
    lower = text.lower()

    # Multi-step markers (max +2)
    _STEP_MARKERS = (
        "して", "してから", "さらに", "その後",
        "まず", "次に", "最後に",
        "then", "after that", "first", "next", "finally",
        "step", "steps", "手順",
    )
    steps = sum(1 for m in _STEP_MARKERS if m in lower)
    score += min(steps, 2)

    # Technical keyword density (max +2)
    _TECH_TERMS = (
        "database", "api", "schema", "docker", "kubernetes", "k8s",
        "deploy", "migration", "migrate", "architecture", "pipeline",
        "ci/cd", "workflow", "infrastructure", "config", "configuration",
        "protocol", "authentication", "authorization", "encryption",
        "concurrent", "parallel", "distributed", "microservice",
        "data model", "optimize", "performance",
        "load test", "benchmark", "throughput",
    )
    density = sum(1 for t in _TECH_TERMS if t in lower)
    score += min(density // 3, 2)

    # Code block presence (max +1)
    if "```" in text:
        score += 1

    # Text length (max +2)
    if len(text) > 500:
        score += 1
    if len(text) > 1500:
        score += 1
    if len(text) > 3000:
        score += 1

    # Questions / requirements (max +1)
    questions = text.count("?") + text.count("？")
    if questions >= 2:
        score += 1
    numbered = len(re.findall(r"\d\.\s", text))
    if numbered >= 3:
        score += 1

    return min(score, 5)


def _is_large_implementation(text: str, lower: str) -> tuple[bool, str]:
    """Return whether an implementation request is large enough for its own route.

    Uses a hybrid rule:
    - explicit size/scope keywords + implementation intent → large
    - implementation intent + complexity/length/scope signals → large
    """
    has_impl_intent = any(trigger in lower for trigger in _CODE_IMPL_TRIGGERS)
    has_size_signal = any(trigger in lower for trigger in _LARGE_IMPL_SIZE_TRIGGERS)
    scope_hits = sum(1 for trigger in _LARGE_IMPL_SCOPE_TRIGGERS if trigger in lower)

    if has_impl_intent and has_size_signal:
        return True, "keyword:large_implementation"

    if not has_impl_intent:
        return False, ""

    complexity = estimate_complexity(text)
    numbered = len(re.findall(r"\d\.\s", text))
    comma_steps = sum(1 for marker in ("まず", "次に", "その後", "最後に", "まで") if marker in lower)
    if complexity >= 4 and (len(text) > 100 or scope_hits >= 2 or numbered >= 3 or comma_steps >= 3):
        return True, f"large_heuristic:complexity:{complexity}/5"
    if scope_hits >= 2:
        return True, "keyword:large_implementation"

    return False, ""


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def classify_message(
    text: str,
    history: Optional[list] = None,
    *,
    context_token_estimate: Optional[int] = None,
) -> tuple[str, str]:
    """Return ``(route_type, classification_reason)`` for *text*.

    Parameters
    ----------
    text : str
        The raw user message to classify.
    history : list or None
        Message list to check for image content.  When an image is detected
        the message is classified as ``vision`` so it can be routed to a
        vision-capable model.
    context_token_estimate : int or None
        Rough token count for the full request context.  Used to keep
        lightweight code routes (notably ``code_light``) from selecting tiny
        models on large, history-heavy turns.

    Returns
    -------
    tuple[str, str]
        ``(route_type, reason)`` where *reason* is a human-readable label
        explaining why *route_type* was chosen (e.g. ``"keyword:要約"``).
        Both values are suitable for writing to usage.log.

    Rules are evaluated in the priority order documented at the top of
    this module — the first match wins.
    """
    if not text:
        return "normal_chat", ""

    _lower = text.strip().lower()

    # 1. simple_command — leading slash
    if _SIMPLE_COMMAND_RE.match(_lower):
        return "simple_command", "starts_with_slash"

    # 2. vision — image content detected
    if history and _has_image_content(history):
        return "vision", "image_in_message"

    # 3. code_design — architecture, planning, PR split
    # Design triggers are checked before implementation because phrases like
    # 「PR分割案を作って」 contain generic implementation verbs such as 作って.
    for trigger in _CODE_DESIGN_TRIGGERS:
        if trigger in _lower:
            return "code_design", "keyword:code_design"

    # 4. large_implementation — explicit size keywords OR combined heuristics
    is_large_impl, large_impl_reason = _is_large_implementation(text, _lower)
    if is_large_impl:
        return "large_implementation", large_impl_reason

    # 5. code_implementation — specific asks to write code
    for trigger in _CODE_IMPL_TRIGGERS:
        if trigger in _lower:
            return "code_implementation", "keyword:code_implementation"

    # 6. code_debug — traceback, log analysis, investigation
    for trigger in _CODE_DEBUG_TRIGGERS:
        if trigger in _lower:
            return "code_debug", "keyword:code_debug"

    # 7. code_light — simple import/install/usage issues
    # Keep this route truly lightweight.  Some small/fast coding models work
    # for direct one-off command/import questions but reject or degrade on a
    # large accumulated conversation context.  In that case route by context
    # size instead of the local keyword so config can send it to a long-context
    # capable model.
    _CODE_LIGHT_MAX_CONTEXT_TOKENS = 6_000
    for trigger in _CODE_LIGHT_TRIGGERS:
        if trigger in _lower:
            if (
                context_token_estimate is not None
                and context_token_estimate > _CODE_LIGHT_MAX_CONTEXT_TOKENS
            ):
                return (
                    "long_context",
                    f"context_tokens>{_CODE_LIGHT_MAX_CONTEXT_TOKENS}:code_light_guard",
                )
            return "code_light", "keyword:code_light"

    # 8. code_or_debug — generic code triggers (catch-all)
    for trigger in _CODE_TRIGGERS:
        if trigger in _lower:
            return "code_or_debug", "keyword:code_or_debug"

    # 9. research — narrow match first
    for trigger in _RESEARCH_TRIGGERS:
        if trigger in _lower:
            return "research", "keyword:research"

    # 10. summary — summarisation requests (before long_context)
    for trigger in _SUMMARY_TRIGGERS:
        if trigger in _lower:
            return "summary", "keyword:summary"

    # 11. long_context — explicit long document requests
    if len(text) > 2000:
        return "long_context", "length>2000"
    for trigger in _LONG_CONTEXT_TRIGGERS:
        if trigger in _lower:
            return "long_context", "keyword:long_context"

    # 12. Complexity-based routing — catch complex prompts that no keyword matched
    complexity = estimate_complexity(text)
    if complexity >= 5:
        return "complex_task", f"complexity:{complexity}/5"

    # 13. Default
    return "normal_chat", ""


# ---------------------------------------------------------------------------
# Route model aliases — sub-routes inherit their parent's model config
# ---------------------------------------------------------------------------
# When a sub-route (code_implementation etc.) has no dedicated routing config
# entry, it falls back to the parent route's model.  This lets usage.log
# observe the new routes without requiring config.yaml changes.
_ROUTE_MODEL_ALIASES = {
    "large_implementation": "code_or_debug",
    "code_implementation": "code_or_debug",
    "code_design": "code_or_debug",
    "code_debug": "code_or_debug",
    "code_light": "code_or_debug",
}


# ---------------------------------------------------------------------------


def get_route_model(
    route_type: str,
    routing_config: dict,
) -> str:
    """Return the model name configured for *route_type*, or empty string.

    Falls back to ``routing_config.get("fallback", "")`` when the specific
    route has no entry.  Sub-routes (code_implementation etc.) are aliased
    to their parent route (code_or_debug) so they inherit its model config
    without requiring config.yaml changes.
    """
    route_cfg = routing_config.get(route_type, {})
    if isinstance(route_cfg, dict):
        model = route_cfg.get("model", "")
        if model:
            return model
    # Sub-route alias fallback — inherit parent route's model
    alias = _ROUTE_MODEL_ALIASES.get(route_type)
    if alias:
        alias_cfg = routing_config.get(alias, {})
        if isinstance(alias_cfg, dict):
            model = alias_cfg.get("model", "")
            if model:
                return model
    return routing_config.get("fallback", "")


def _route_model_from_mapping(route_type: str, route_map: dict) -> str:
    """Return a route model from a route→config mapping.

    Supports the same shapes as the primary routing config:
    ``route: {model: ...}`` or ``route: "model-name"``.  Sub-route aliases
    also inherit from their parent route.
    """
    route_cfg = route_map.get(route_type, {})
    if isinstance(route_cfg, dict):
        model = route_cfg.get("model", "")
        if model:
            return model
    elif isinstance(route_cfg, str) and route_cfg:
        return route_cfg

    alias = _ROUTE_MODEL_ALIASES.get(route_type)
    if alias:
        alias_cfg = route_map.get(alias, {})
        if isinstance(alias_cfg, dict):
            model = alias_cfg.get("model", "")
            if model:
                return model
        elif isinstance(alias_cfg, str) and alias_cfg:
            return alias_cfg
    return ""


def get_fallback_route_model(
    route_type: str,
    routing_config: dict,
) -> str:
    """Return the model configured for provider-fallback routing.

    Primary routing and provider fallback routing are intentionally separate:
    a primary route model may belong to the failed provider.  Supported config
    shapes:

    routing:
      fallback_routes:
        normal_chat: {model: deepseek/deepseek-v4-flash}

    ``fallback_routing`` is accepted as a readable alias.  If no fallback
    route is configured, callers should keep the provider fallback entry's
    own model.
    """
    if not isinstance(routing_config, dict):
        return ""

    for key in ("fallback_routes", "fallback_routing"):
        route_map = routing_config.get(key, {})
        if isinstance(route_map, dict):
            model = _route_model_from_mapping(route_type, route_map)
            if model:
                return model
            default = route_map.get("fallback", "")
            if isinstance(default, str) and default:
                return default
            if isinstance(default, dict):
                model = default.get("model", "")
                if model:
                    return model

    return ""


def get_route_type_strings() -> tuple[str, ...]:
    """Return all known route type names (for logging / validation).

    Includes both active and future (reserved) routes.
    """
    return (
        # Active routes
        "simple_command",
        "normal_chat",
        "vision",
        "large_implementation",
        "code_implementation",
        "code_design",
        "code_debug",
        "code_light",
        "code_or_debug",
        "summary",
        "long_context",
        "research",
        "complex_task",
        # Future routes (classified but not wired)
        # "sensitive_or_private",
        # "creative_writing",
        # "personal_advice",
    )


def classify_message_legacy(text: str, history: Optional[list] = None) -> str:
    """Legacy shim — returns ``route_type`` only (string).

    Deprecated: prefer ``classify_message()`` which returns the full
    ``(route_type, reason)`` tuple for richer logging.
    """
    return classify_message(text, history)[0]
