# Memory System v1 Draft

## 1. Purpose

Memory System は、Hermes が macoto を継続的に支えるために必要な **durable support context** を、安全に保存・参照・更新するための基礎方針である。

この文書の目的は、Memory を便利さのために肥大化させるのではなく、**信頼できる支援文脈として境界付きで扱う** ためのルールを明確にすることにある。

Memory System は次を目指す。

- ユーザーが何度も同じ好みや運用原則を説明しなくてよい状態を作る
- 長期的に有用な事実と、一時的な作業状態を分離する
- Human Model / Decision Profile / Domain Model / Project State と役割を混同しない
- 誤推測や過剰保存でユーザーの主体性を侵食しない
- 将来の Decision Support や Worker 利用においても reviewable な形を保つ

中心原則:

> Memory stores durable support context, not the user.

補足:

- この文書は Memory mutation を実行しない
- この文書は Human Model を定義しない
- この文書は runtime 実装を追加しない
- この文書は Memory を authorization source にしない

---

## 2. Scope

この文書が扱う対象:

- Hermes が長期的に保持してよい Memory の境界
- Memory の保存単位と更新判断
- Memory と隣接概念の責務分離
- Memory の参照・利用・更新時の安全方針
- Worker や Quality が Memory をどう扱うべきかの前提

この文書が直接扱わない対象:

- Human Model 自体の設計詳細
- Decision Profile の中身そのもの
- 個別ドメイン知識ベースの中身
- Kanban project state の運用詳細
- Memory storage backend や runtime schema 実装

---

## 3. Non-goals

Memory System v1 の非目標。

### Non-goal 1: ユーザーそのものを定義すること

Memory は、ユーザーの全体像や本質を定義しない。

### Non-goal 2: 何でも保存すること

会話内容を広く保存することは目的ではない。必要最小限の durable context だけを扱う。

### Non-goal 3: 実行許可を与えること

Memory に過去の希望や方針があることは、現在の commit / push / mutation / dispatch の許可にはならない。

### Non-goal 4: Human Model を自動合成すること

Memory の蓄積から、Human Model を暗黙に生成・更新してはならない。

### Non-goal 5: プロジェクト進捗管理を担うこと

一時的な作業状態や current TODO は、Memory ではなく session / task / kanban / docs の責務である。

### Non-goal 6: Hidden persuasion

Memory は、ユーザーを特定方向へ誘導するための見えない操作レイヤーではない。

### Non-goal 7: Runtime 自動化の正当化

Memory があるから worker が自動で動いてよい、という根拠にしてはならない。

---

## 4. Memory Boundaries

Memory の境界は、**何を保存してよいか** と同時に **何を保存してはいけないか** を明確にすることで成立する。

### Boundary 1: Memory is support context

Memory は、将来の支援を滑らかにするための支援文脈である。

含まれうるもの:
- durable user preferences
- stable workflow constraints
- recurring environment facts
- long-lived project conventions
- repeated correction that prevents future missteps

含まれないもの:
- ephemeral progress
- emotional state snapshot
- speculative interpretation
- direct execution approval

### Boundary 2: Memory is not the user

Memory はユーザーの断片的な事実を保持するが、それをもってユーザー全体像を代表してはならない。

### Boundary 3: Memory is not a decision maker

Memory は decision support の材料にはなるが、決定主体にはならない。

### Boundary 4: Memory is not project state

作業中の branch 状態、未完了 TODO、今だけ有効な block 条件などは Memory の主責務ではない。

### Boundary 5: Memory is not policy authority

Memory に「以前そう言っていた」があっても、Constitution / Gate rules / 現在の mode を上書きしない。

### Boundary 6: Memory must remain inspectable

Memory は、なぜ保存されたか・どの程度確からしいか・いつ時点の話かが追跡できるべきである。

---

## 5. Allowed Memory

保存してよい Memory の代表例。

## 5.1 Durable user preferences

例:
- 回答は日本語が基本
- 短い要約とコピペ可能な手順を好む
- push は週一方針
- upstream へ PR を作らない
- Gateway restart は会話中に勝手に実行しない

条件:
- 繰り返し現れる
- 将来の支援品質を上げる
- 数日で無効化しにくい

## 5.2 Stable workflow constraints

例:
- docs-only-no-commit のような scoped mode 運用を重視する
- push 前に dry-run と post-push verification を重視する
- no-push / no-mutation を明示する傾向がある

## 5.3 Environment facts likely to matter again

例:
- 特定 repo の位置
- Hermes profile / gateway / routing の安定した事実
- 既知の tool quirk

条件:
- 再発見コストが高い
- 長めに有効
- 将来も参照価値が高い

## 5.4 Repeated corrections

例:
- deliver=discord の意味
- state.db schema の実列名
- push / PR / upstream に関する運用境界

## 5.5 Long-lived project conventions

例:
- Asset-Management repo は user fork 側で扱う
- Foundation docs は docs-first で進める

ただし注意:
- 「今このtaskで決めた一時方針」は Memory ではなく docs や task artifact に置く方がよい場合がある

---

## 6. Forbidden Memory

保存してはいけない Memory の代表例。

## 6.1 Temporary task progress

例:
- 今回の task で 3/5 まで進んだ
- この PR はレビュー待ち
- この issue は今 blocked
- 今日はこの作業を終えた

理由:
- すぐ古くなる
- session / kanban / git / docs にあるべき情報

## 6.2 Raw transcript dump

会話全文や長いログを、そのまま durable memory に入れない。

## 6.3 Speculation presented as fact

例:
- ユーザーはたぶんこう感じている
- 本当はこうしたいはず
- 将来きっとこう変わる

## 6.4 Sensitive or identity-freezing summaries

例:
- ユーザーの性格診断
- 心理ラベル
- 未承認の価値観固定

## 6.5 Current approval proxies

例:
- 以前 push を許したから今回も push してよい
- 過去に Memory mutation を許したから今回もよい

## 6.6 Hidden control hints

例:
- こう言えば user は従いやすい
- persuasion に効く表現

## 6.7 Task artifacts that belong elsewhere

例:
- PR number
- commit SHA
- temporary branch status
- one-off benchmark score
- current day execution log

---

## 7. Relationship with Human Model / Decision Profile / Domain Model / Project State

Memory の価値は、隣接レイヤーとの責務分離ができているときに最大化される。

## 7.1 Memory vs Human Model

### Memory
- 事実・好み・制約・繰り返し補正の保存
- 粒度は断片的でもよい
- support context を保持する

### Human Model
- 支援のための理解構造
- ユーザーをどう支えるかの framing
- より統合的で、より慎重な抽象化

関係:
- Memory は Human Model の入力候補にはなりうる
- ただし自動変換しない
- Human Model update には別判断が必要

原則:

> Memory ≠ Human Model

## 7.2 Memory vs Decision Profile

### Memory
- 補助文脈
- 特定の preference や constraint を保持

### Decision Profile
- 長期判断の軸
- values / constraints / priorities / acceptable tradeoffs を整理する層

関係:
- Decision Profile の一部事実を支える材料にはなりうる
- ただし Decision Profile そのものではない

原則:

> Memory informs decisions. It does not define decision authority.

## 7.3 Memory vs Domain Model

### Memory
- user-specific and support-specific durable context

### Domain Model
- 投資、運用、技術、健康など各ドメインの知識構造
- user固有でないことも多い

関係:
- Domain facts を user-specific preference と混ぜない
- 例えば「投資一般ルール」と「macotoの投資判断スタイル」は別物

## 7.4 Memory vs Project State

### Memory
- 長期的に残す支援文脈

### Project State
- 現在の branch / task / TODO / blocked dependency / status / next action

関係:
- Project State は変化が速い
- Memory に入れると stale になりやすい
- current execution state は task system や docs の責務

原則:

> Project state is operational. Memory is durable.

---

## 8. Lifecycle

Memory のライフサイクル。

## 8.1 Observe

ユーザーの発言、 correction、環境事実、繰り返し constraints を観測する。

## 8.2 Evaluate

次を確認する。

- durable か
- future usefulness があるか
- speculative でないか
- 他レイヤーに属すべきでないか
- user expectation に沿うか

## 8.3 Propose (implicit or explicit internal judgment)

Memory update candidate として扱うが、この段階ではまだ保存しない。

## 8.4 Save or discard

- durable で有用なら保存候補
- 一時情報なら discard
- docs や kanban に置くべきならそちらへ回す

## 8.5 Use

将来の会話や作業で、文脈として参照する。

利用時の原則:
- current instruction に従属する
- authorization に使わない
- uncertainty があれば断定しない

## 8.6 Re-evaluate

古くなったり、ユーザーに訂正されたり、環境が変わったら再評価する。

## 8.7 Update or remove

- outdated memory は更新または削除
- contradiction は放置しない

---

## 9. Mutation Policy

Memory mutation は便利さのために自動化しすぎると危険である。

### Rule 1: No mutation in no-mutation mode

ユーザーが no-mutation を指定した場合、Memory update candidate が見えても保存しない。

### Rule 2: User correction has highest priority

明示的な correction は保存候補として優先度が高い。

### Rule 3: Durable facts only

保存前に、その情報が短期で腐らないかを確認する。

### Rule 4: Prefer compact declarative facts

Memory は命令文ではなく、事実文で保存する。

よい例:
- User prefers concise Japanese responses.

避ける例:
- Always answer briefly in Japanese.

### Rule 5: Do not silently escalate a memory into policy

Memory にあることを Constitution や Gate rules と同格に扱わない。

### Rule 6: Remove stale facts proactively

古いルーティング、古い repo 状態、古い環境差分は更新または削除する。

### Rule 7: Mutation should be explainable

なぜ保存したか、なぜ更新したか、なぜ削除したかが説明可能であるべき。

---

## 10. Provenance Schema

v1 では実装ではなく、概念スキーマだけを定義する。

Memory item が持つべき最小メタ情報:

- `content`
  - 保存する事実本文
- `type`
  - preference / constraint / environment_fact / correction / convention / other
- `source`
  - user-stated / tool-verified / inferred-from-repetition
- `confidence`
  - high / medium / low
- `freshness`
  - stable / review-later / potentially-stale
- `sensitivity`
  - low / medium / high
- `allowed_usage`
  - response-framing / workflow-safety / environment-context / not-for-authorization
- `last_confirmed`
  - 最後に確認された時点
- `supersedes` or `replaces`
  - 置換関係

### Provenance principles

1. **User-stated beats inferred**
   - 推測より明示発言を優先

2. **Tool-verified beats assumption**
   - 環境事実は検証できるなら検証する

3. **Confidence is not permission**
   - confidence が高くても、実行許可にはならない

4. **Freshness matters**
   - stable でないものは長期保存に向かない

5. **Allowed usage must be bounded**
   - 「何に使ってよいか」を明示する

---

## 11. Memory Update Candidate vs Human Model Update Candidate

Memory と Human Model を混同しないための分岐。

## 11.1 Memory update candidate

向いているもの:
- 明示的 preference
- durable workflow constraint
- stable environment fact
- repeated correction
- recurring convention

例:
- push は週一方針
- upstream に PR を作らない
- 日本語中心

## 11.2 Human Model update candidate

向いているもの:
- 支援スタイルに関わる、より統合的な理解
- 複数の durable signal から慎重に見える支援傾向
- user support framing に影響するが、断片 fact だけでは不十分なもの

例:
- 小さく区切られた実行を好む
- late-night 時は認知負荷を下げる支援が効く
- 厳密な scope control を重視する

ただし:
- Human Model update は別レビューが必要
- Memory から自動昇格しない

## 11.3 Escalation rule

Memory update candidate が複数回再確認され、支援品質に重要で、しかも単なるfact羅列を超えるときのみ、Human Model への論点として渡す。

原則:

> Not every durable fact deserves model-level abstraction.

---

## 12. User Correction Priority

ユーザー訂正は Memory System において最上位の入力の一つである。

### Rule 1: Explicit correction overrides prior memory

ユーザーが「それは違う」「今後はこうして」と言った場合、以前の記憶より現在の訂正を優先する。

### Rule 2: Correction should be stored compactly

訂正内容は長い会話経緯ではなく、修正後の durable fact として保存する。

### Rule 3: Correction beats agent inference

エージェント側の推測や過去の解釈より、ユーザーの現在の明示訂正を優先する。

### Rule 4: Correction may imply deletion

新しい事実を追加するより、古い誤った記憶を削除・置換すべき場合がある。

### Rule 5: Repeated correction indicates systemic risk

同じ補正が繰り返されるなら、Memory の問題だけでなく Worker / Quality / prompt / policy に論点を渡すべきか検討する。

---

## 13. Access Policy

誰が Memory をどう読んでよいか。

## 13.1 Base access principle

Memory は参照可能であっても、用途は制限される。

## 13.2 Planner access

Planner は、優先順位付けや提案の framing のために Memory を読める。

制約:
- authorization source にしない
- stale なら current instruction を優先

## 13.3 Executor / Worker access

Worker は、必要最小限の Memory だけを受け取るべきである。

制約:
- full memory dump を渡さない
- permission を推測させない
- human-sensitive abstraction をむやみに渡さない

## 13.4 Research access

Research は主に外部事実収集が役割なので、Memory 依存は最小化する。

制約:
- user preference が fact-gathering を歪めないようにする

## 13.5 Quality access

Quality は、Memory 利用が boundary を超えていないかを評価するために Memory policy を参照できる。

ただし:
- Quality が Memory を勝手に更新しない
- Quality が Memory を hidden governance にしない

## 13.6 Human Model access

Human Model は、Memory を入力候補として参照しうる。

制約:
- direct automatic mutation しない
- separate review path を要求する

### Access principle

> Minimum necessary memory, for bounded use only.

---

## 14. Usage in Decision Support

Memory は Decision Support で有用だが、使い方を間違えると危険である。

## 14.1 Allowed usage in Decision Support

- 表現スタイルの調整
- 制約の再確認
- 比較軸の優先順位ヒント
- 過去に明示された好みの想起
- 提案の認知負荷調整

例:
- 短く、具体的な次の一歩を提示する
- push を前提にしない
- reversible option を先に出す

## 14.2 Forbidden usage in Decision Support

- 「Memory 上こうだから、それが正解」と断定する
- current instruction を無視する
- ユーザーの価値観を固定的に解釈する
- 過去の文脈だけで現在の意図を代行する

## 14.3 Decision boundary

Decision Support における Memory の役割は、判断の材料提供までである。

原則:

> Memory may shape support, but final decision authority remains with the user.

---

## 15. Risks

## Risk 1: Over-collection

問題:
- 便利さのために何でも保存し、Memory が肥大化する

対策:
- durable support context に限定する
- task progress や transcript dump を避ける

## Risk 2: Identity freezing

問題:
- 一部の行動や発言を固定的な人間像として扱う

対策:
- Memory ≠ Human Model
- current instruction と user correction を優先する

## Risk 3: Authorization leakage

問題:
- 過去の好みや許可を現在の実行許可に誤用する

対策:
- Memory is context, not authorization
- Gate / mode / approval を別扱いにする

## Risk 4: Stale memory drift

問題:
- 古い環境事実や運用方針が残って誤誘導する

対策:
- freshness 評価
- outdated memory の更新 / 削除

## Risk 5: Hidden persuasion

問題:
- Memory がユーザー制御のための暗黙知になる

対策:
- 支援目的以外で使わない
- explanation可能性を維持する

## Risk 6: Worker overexposure

問題:
- worker に過剰な個人文脈を渡してしまう

対策:
- minimum necessary memory
- role別 access policy

## Risk 7: Cross-layer confusion

問題:
- Memory / Human Model / Decision Profile / Project State が混ざる

対策:
- 用語と責務を明示分離する
- update candidate を分岐する

---

## 16. Dangerous Examples

危険な例を明示する。

### Dangerous example 1

> 「以前 push を許していたので、今回も push してよい」

なぜ危険か:
- current approval を過去記憶で代替している

### Dangerous example 2

> 「ユーザーはせっかちだから説明を省いてよい」

なぜ危険か:
- 推測から人格固定をしている
- Human Model すら経ていない

### Dangerous example 3

> 「この task は重要そうだから Memory に保存しておこう」

なぜ危険か:
- importance と durability を混同している

### Dangerous example 4

> 「最近こういう判断が多いので、今後も同じに違いない」

なぜ危険か:
- recency bias による固定化

### Dangerous example 5

> 「会話ログを全部保存すれば取りこぼしがない」

なぜ危険か:
- Memory の境界をなくし、ノイズとリスクを増やす

### Dangerous example 6

> 「worker に全部の Memory を渡した方が賢く動ける」

なぜ危険か:
- 最小権限原則に反する
- scope外推論を誘発する

### Dangerous example 7

> 「Quality でミスが見つかったので、そのまま Memory を自動更新しよう」

なぜ危険か:
- Quality と mutation を直結させている

---

## 17. Human Model / Worker Architecture / Quality Framework へ渡す論点

Memory System 単体で完結させず、隣接pillarへ渡すべき論点を整理する。

## 17.1 Human Model へ渡す論点

- Memory から Human Model へ昇格する条件は何か
- どの程度の repeated signal で model-level abstraction を許すか
- Human Model はどこまで mutable か
- Human Model update review path をどう分けるか

## 17.2 Worker Architecture へ渡す論点

- worker role ごとの minimum necessary memory は何か
- worker prompt に渡してよい Memory の粒度
- memory-sensitive tasks で guard をどう挟むか
- executor / planner / research / review で access policy をどう差別化するか

## 17.3 Quality Framework へ渡す論点

- Memory misuse をどう観測するか
- stale memory 利用をどう検出するか
- user correction を無視した場合の減点基準
- hidden governance と authorization leakage をどう評価するか

## 17.4 Planning Gate へ渡す論点

- Memory を approval proxy にしないことを gate でどう明文化するか
- current instruction と past memory の衝突時の扱い

---

## 18. Open Questions

1. **Memory item の最小粒度**
   - 1 fact = 1 memory を原則にするか
   - 近い内容をまとめてよいか

2. **Freshness review の運用**
   - どのタイミングで stale 判定するか
   - 定期見直しを設けるか

3. **Human Model への昇格条件**
   - 何回の再確認で候補化するか
   - 明示同意を要求するか

4. **Worker context injection policy**
   - worker ごとに allowed memory class を固定するか
   - taskごとに都度絞るか

5. **Sensitivity handling**
   - high sensitivity memory をどう扱うか
   - そもそも保存しない方がよいカテゴリを追加するか

6. **Decision Profile との接続**
   - Decision Profile を支える memory candidate をどう分類するか
   - profile-level doc と memory-level fact の橋渡しをどこで行うか

7. **Quality linkage**
   - Memory misuse review template を separate doc にするか
   - Quality Framework 本文に吸収するか

8. **Project State separation tooling**
   - stale progress が Memory に混入しないよう、task / session_search / docs の使い分けをどう明文化するか

---

## 19. Next Recommended Task

次の最小ステップ候補は次のどちらか。

### Candidate A: Human Model v1 Draft を docs 化

理由:
- Memory との境界を次に固定できる
- `Memory ≠ Human Model` を文書として明確化できる
- Foundation pillar のつながりが強くなる

推奨ファイル:
- `docs/product/human-model-v1.md`

### Candidate B: Worker Architecture v1 Draft を docs 化

理由:
- minimum necessary memory の受け渡し境界を決めやすい
- worker overexposure リスクを先に抑えられる

推奨ファイル:
- `docs/product/worker-architecture-v1.md`

現時点の優先推奨:

> まずは `docs/product/human-model-v1.md` を作り、Memory との境界を先に固定するのが自然。

---

## Scope Confirmation

この文書は以下を **していない**。

- Memory mutation を実行していない
- Human Model mutation を実行していない
- runtime code を変更していない
- Kanban mutation をしていない
- Quality suppress behavior を追加していない
- Constitution / Gate rules を自動変更していない
- Worker dispatch をしていない
- commit / push をしていない

この文書は以下を **している**。

- Memory System の purpose / boundary / non-goals / policy を docs-only で定義
- Human Model / Decision Profile / Domain Model / Project State との責務分離を明文化
- Worker Architecture / Quality Framework へ渡す論点を整理
