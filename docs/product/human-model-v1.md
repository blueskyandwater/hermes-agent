# Human Model v1 Draft

## 1. Purpose

Human Model は、Hermes が macoto を長期的に支えるために必要な **human understanding layer** を、過剰推測や人格固定化を避けながら設計するための基礎文書である。

この文書の目的は、Hermes がユーザーを「都合のよい内部キャラクター」として扱うことを防ぎつつ、支援品質を上げるために必要な理解の境界を定義することにある。

Human Model は次を目指す。

- ユーザーの主体性を守りながら、支援の精度を上げる
- Memory に保存すべきことと、Human Model で解釈すべきことを分ける
- Decision Support に必要な人間理解を、診断や断定にせず扱う
- 長期運用で見直せる、レビュー可能な理解レイヤーにする
- Worker や runtime が Human Model を誤用して scope を広げないようにする

中心原則:

> Human Model describes support-relevant patterns, not the user's essence.

補足:

- この文書は Human Model mutation を実行しない
- この文書は Memory を更新しない
- この文書は runtime 実装を追加しない
- この文書は Decision を代行しない
- この文書はユーザーの人格診断を行わない

---

## 2. Scope

この文書が扱う対象:

- Human Model が何を表現してよいか
- Human Model と隣接概念の責務分離
- Human Model の snapshot と mutation の原則
- Decision Support における利用境界
- privacy / sensitivity / provenance の最低方針

この文書が直接扱わない対象:

- 個別の Human Model 実データ本文
- 医療・心理・診断的評価の設計
- runtime の prompt assembly 実装
- Memory storage backend や schema 実装
- Worker routing の具体コード
- User profile を自動生成する仕組み

---

## 3. Non-goals

Human Model v1 の非目標。

### Non-goal 1: ユーザーの本質を定義すること

Human Model は、ユーザーの本質・正体・完全な性格像を定義しない。

### Non-goal 2: 診断やラベリングを行うこと

Human Model は、心理診断・医療判断・病理推定のレイヤーではない。

### Non-goal 3: 記憶の置き換え

Human Model は Memory の代替ではない。Durable facts を蓄積する場所としては使わない。

### Non-goal 4: 意思決定の自動化

Human Model があるからといって、Hermes がユーザーの代わりに判断してよいことにはならない。

### Non-goal 5: scope expansion の正当化

「このユーザーはこういう人だから」という理由で、push / dispatch / mutation / auto-approve を進めてはならない。

### Non-goal 6: Project State の吸収

現在の作業状況、未完了タスク、直近の気分や一時的ブロッカーを Human Model に混ぜない。

### Non-goal 7: 永久固定化

Human Model は、一度書いたら不変の人物像ではない。暫定的で見直し可能なものとして扱う。

---

## 4. Model Boundaries

Human Model の境界は、**何を理解対象にしてよいか** と **何を理解対象にしてはいけないか** を分けることで成立する。

### Boundary 1: Human Model is about support-relevant patterns

Human Model は、支援に影響する傾向や反応パターンを扱う。

含まれうるもの:
- 長期的に観測される意思決定傾向
- 仕事の進め方の好み
- 認知負荷への反応傾向
- 支援スタイルに対する好み
- エネルギーや集中の使い方に関する、非診断的な基礎観察

含まれないもの:
- 人格の断定
- 病理ラベル
- 一時的感情の固定化
- 監視や採点のための特徴量
- user agency を上書きする hidden control hints

### Boundary 2: Human Model is not Memory

Human Model は解釈レイヤーであり、事実ストアではない。

- Memory は durable fact / preference / correction を保持する
- Human Model はそれらを背景として、支援上のパターン理解を整理する

### Boundary 3: Human Model is not a control plane

Human Model は routing / approval / permission の authority source ではない。

- 「慎重に進めた方がよい傾向」があっても current approval の代わりにはならない
- 「勢いがあるタイプ」でも高リスク操作の許可にはならない

### Boundary 4: Human Model is not exhaustive

Human Model は、ユーザー全体像を説明し尽くすことを目指さない。

常に:
- partial
- revisable
- context-limited
- reviewable

である。

### Boundary 5: Human Model must preserve ambiguity

判断に十分な事実がないときは、曖昧さを残す。

- 断定しない
- 1回の会話で恒久的傾向を決めない
- Unknown を明示する

---

## 5. Allowed Information

Human Model に含めてよい情報は、長期支援に意味があり、かつ診断や監視に転化しにくいものに限る。

### Allowed category 1: Support style preferences

例:
- 短い要約を好む
- copy-paste しやすい手順を好む
- 疲れている時は次の一歩を小さくしてほしい
- 長い理論より実務的な切り分けを好む

### Allowed category 2: Decision style tendencies

例:
- まず小さく試してから判断したい
- 抽象論より現実のログや結果を重視する
- 大きい変更より可逆な小変更を好む
- 自分で最終決定したい

### Allowed category 3: Work mode patterns

例:
- 深夜は認知負荷を下げた方がよい
- debugging では current status → likely cause → next command の形式が効く
- 監視と推論を分離した運用を好む

### Allowed category 4: Stable boundary conditions

例:
- upstream に push しない
- weekly push 方針
- docs-only-no-commit を重視する
- Rule of Least Surprise を重視する

### Allowed category 5: Long-term orientation relevant to support

例:
- ローカル保存やデータ所有権を重視する
- 20年以上使う前提でシステムを育てたい
- AIを道具ではなく伴走者として育てたい

Allowed information の条件:

- durable である
- support-relevant である
- non-diagnostic である
- current session を越えて有用である
- user agency を侵食しない

---

## 6. Forbidden Information

Human Model に入れてはいけない情報。

### Forbidden category 1: Diagnostic claims

例:
- 精神状態の診断
- 病名推定
- 性格類型の断定
- 医療的・病理的な解釈

### Forbidden category 2: Raw private detail without support necessity

例:
- 不要に細かい私生活情報
- 支援に不要な固有事情
- センシティブ情報の詳細列挙

### Forbidden category 3: Temporary emotional snapshots

例:
- 今日イライラしていた
- この会話では弱気だった
- さっき迷っていた

これらを恒久的傾向として保存してはならない。

### Forbidden category 4: Execution shortcuts

例:
- この人はたぶんOKと言うはずだから push してよい
- いつも自動化を好むから dispatch してよい
- 慎重派だから blocked のままでよい

### Forbidden category 5: Compliance or scoring profile

例:
- 指示遵守率
- mood score
- 従順さスコア
- persuasion susceptibility

### Forbidden category 6: Unverified interpretation presented as fact

例:
- たぶん孤独を埋めるためにHermesを使っている
- 不安が強いから細かい確認を求める
- 権威に反発する性格だからこのルールを嫌う

推測は Human Model に直書きしてはならない。

---

## 7. Relationship with Memory / Decision Profile / Domain Model

Human Model は単独で成立するのではなく、隣接レイヤーとの責務分離で意味を持つ。

### 7.1 Relationship with Memory

Memory:
- durable facts
- stable preferences
- recurring corrections
- environment facts
- long-lived conventions

Human Model:
- それらを背景にした支援上の理解パターン
- ただし推測を事実化しない

Rule:

> Memory stores what is known. Human Model frames how support should interpret it, cautiously.

### 7.2 Relationship with Decision Profile

Decision Profile:
- ユーザーの価値観
- 長期目標
- 制約
- 判断基準

Human Model:
- その価値観や制約が、実際の支援ではどう現れやすいかを補助的に理解する

Decision Profile が「何を大事にするか」なら、Human Model は「その人間的運用上、どう支援すると負荷が減るか」に近い。

### 7.3 Relationship with Domain Model

Domain Model:
- 投資
- 仕事
- プロダクト
- 健康
- 学習
など、対象世界の構造を表す。

Human Model:
- その対象世界に向き合うユーザーの傾向を表す。

Domain Model は外界、Human Model は支援対象としての人間側に近い。

### 7.4 Relationship with Project State

Project State は current progress / blockers / branch / task status を扱う。

Human Model は current project state を保持しない。

### 7.5 Relationship with Constitution

Constitution は運用原則や制約を定義する。

Human Model は Constitution を上書きしない。

- Human Model は「なぜこのルールが支援上有効か」を理解する補助にはなる
- しかし例外許可の根拠にはならない

---

## 8. Snapshot Policy

Human Model は、連続会話の印象の寄せ集めではなく、**reviewable snapshot** として扱う。

### Policy 1: Snapshot over stream

常時流し込みではなく、ある程度まとまった観察単位ごとに snapshot として整理する。

### Policy 2: Versioned, not silently drifting

Human Model は、可能な限り version / date / provenance を伴う。

例:
- v1 baseline
- v1.1 clarified after repeated corrections
- v2 after explicit user review

### Policy 3: Confidence is bounded

snapshot に含まれる各観察は、確信度や根拠の強さに差がある。

最低限:
- strong observation
- repeated observation
- tentative observation
- unknown

を区別できることが望ましい。

### Policy 4: User-correctable

Human Model snapshot は、ユーザーが訂正・否定・保留できる対象である。

### Policy 5: No emotional overfitting

短期的な会話ムードを、snapshot の主軸にしてはならない。

---

## 9. Mutation Policy

Human Model の更新は、便利さより慎重さを優先する。

### Rule 1: Mutation requires evidence, not vibe

更新根拠は、反復観察・明示発言・明確な訂正・長期一貫性に基づく。

弱い根拠:
- 単発の印象
- AI側の解釈の気持ちよさ
- narrative coherence だけの仮説

### Rule 2: Explicit correction outranks inference

ユーザーの明示訂正は、AIの推測より優先される。

### Rule 3: Scope-limited updates

Human Model の一部更新が、隣接レイヤー全体の自動変更を引き起こしてはならない。

禁止例:
- Human Model更新を理由に Memory を自動更新
- Human Model更新を理由に Constitution を自動変更
- Human Model更新を理由に worker routing を自動変更

### Rule 4: High-sensitivity areas need extra caution

以下は特に慎重に扱う:
- health-like interpretation
- emotional vulnerability interpretation
- identity claims
- relationship dependency claims

### Rule 5: Silence is not confirmation

ユーザーが否定しなかったことは、Human Model の確証にならない。

### Rule 6: Mutation should be reviewable

更新は、後から「なぜ変わったか」を辿れるべきである。

---

## 10. Usage in Decision Support

Human Model は、Decision Support の中で有用だが、利用境界を守る必要がある。

### Allowed use 1: Framing support

- どの粒度で説明すると負荷が低いか
- どの順序で選択肢を出すと考えやすいか
- どの程度の慎重さが必要か

### Allowed use 2: Cognitive load adjustment

- 疲れている時は候補数を減らす
- 実行前に最小ステップを提示する
- ログベースで整理する

### Allowed use 3: Conflict detection with current proposal

提案がユーザーの既知の運用傾向や価値観とズレていそうなら、ズレを明示する。

例:
- この提案は weekly push 方針とズレる
- この提案は可逆性重視とズレる

### Allowed use 4: Ambiguity flagging

Human Model が十分に確信を持てない場合、Decision Support に Unknown として反映する。

### Disallowed use 1: Final decision substitution

Human Model を理由に、ユーザーの代わりに重要判断を確定してはならない。

### Disallowed use 2: Behavioral steering without visibility

相手の傾向を利用して、こっそり誘導してはならない。

### Disallowed use 3: Permission laundering

Human Model を使って危険操作の承認を“読み取ったことにする”のは禁止。

Rule:

> Human Model may shape how Hermes supports a decision, but never who owns the decision.

---

## 11. Privacy / Sensitivity / Provenance

Human Model は、その性質上、Memory よりも解釈的でセンシティブになりやすい。

### 11.1 Privacy

最小化原則:
- 支援に不要な個人情報は入れない
- detail richness より support usefulness を優先する
- private detail collection を目的化しない

### 11.2 Sensitivity

高感度領域:
- health-like information
- emotional fragility interpretations
- identity and self-worth interpretations
- dependency / attachment interpretations

これらは原則として:
- 断定しない
- 低頻度でしか更新しない
- explicit wording か慎重な review を要する

### 11.3 Provenance

各観察には、可能な限り provenance を持たせる。

最低限の provenance 例:
- explicit user statement
- repeated session pattern
- correction-driven update
- inferred but tentative

推奨:
- source type
- date range
- confidence band
- last reviewed timestamp

### 11.4 Visibility and contestability

Human Model は、見えない内部真実ではなく、将来的に review / correction 可能な支援仮説として扱う。

---

## 12. Risks

Human Model v1 の主要リスク。

### Risk 1: Overconfidence

少ない観察から人物像を作りすぎるリスク。

### Risk 2: Hidden persuasion

ユーザー理解を、より良い支援ではなく、誘導に使ってしまうリスク。

### Risk 3: Identity freezing

過去の傾向を未来の固定像として扱うリスク。

### Risk 4: Boundary collapse

Memory / Decision Profile / Domain Model / Constitution / Project State との境界が崩れるリスク。

### Risk 5: Sensitivity drift

支援品質向上を口実に、不要にセンシティブな解釈へ踏み込むリスク。

### Risk 6: Runtime misuse

Human Model を、worker dispatch や auto-approval の裏根拠にしてしまうリスク。

### Risk 7: Self-fulfilling support loop

AI が作った Human Model に合わせて応答し続け、ユーザー理解を狭めてしまうリスク。

---

## 13. Dangerous Usage Examples

危険な使い方の例を明示する。

### Example 1: Push approval laundering

危険:

> このユーザーは普段慎重だから、今回何も言っていないのは実質OKだろう。

問題:
- approval の捏造
- Human Model の権限誤用

正しい扱い:
- current approval がないなら push しない

### Example 2: Emotional fixation

危険:

> 最近弱気な発言があったので、この人は自己効力感が低い人だ。

問題:
- 一時感情の固定化
- 診断的解釈

正しい扱い:
- 当該会話文脈の一時状態として扱い、恒久モデル化しない

### Example 3: Memory substitution

危険:

> Human Model に「簡潔さを好む」とあるから、Memory にある個別運用ルールはもう不要。

問題:
- 解釈レイヤーが事実レイヤーを潰している

正しい扱い:
- 支援方針と durable fact は別に保持する

### Example 4: Compliance scoring

危険:

> 反論率が高いので、今後は説得コストを下げる話し方へ最適化しよう。

問題:
- 誘導設計
- user agency の侵害

正しい扱い:
- 納得可能性を高めるのはよいが、誘導のための最適化にしない

### Example 5: Domain overreach

危険:

> 投資判断で慎重な人だから、技術選定でも自動的に保守寄りだと扱ってよい。

問題:
- domain transfer の過剰一般化

正しい扱い:
- ドメイン間の傾向移植は慎重に行い、Unknown を残す

---

## 14. Memory System タスクへ渡す論点

Human Model から Memory System へ渡すべき論点。

1. **Boundary contract の明文化**
   - durable fact と support interpretation をどう分離するか

2. **correction propagation rule**
   - ユーザー訂正が Memory と Human Model にどう反映されるか

3. **shared provenance vocabulary**
   - explicit / repeated / tentative / corrected などの共通語彙

4. **sensitivity escalation rule**
   - 高感度情報をどちらに置くべきか、そもそも置かないべきか

5. **review cadence**
   - Memory は都度更新寄り、Human Model は snapshot review 寄りにするのか

---

## 15. Decision Support / Domain Model / Decision Style へ渡す論点

Human Model から隣接pillarへ渡すべき論点。

### 15.1 Decision Support へ

- Human Model をどう framing 支援に使うか
- Unknown をどう残すか
- 価値観と認知負荷調整をどう分離するか
- final decision ownership をどう明示し続けるか

### 15.2 Domain Model へ

- ドメイン固有知識と人間側傾向をどう切り分けるか
- domain transfer の一般化をどこまで許すか
- 投資 / 開発 / 健康など異なる領域で同じ傾向を流用してよい条件は何か

### 15.3 Decision Style へ

- 選択肢数
- 先に結論を出すか、材料を並べるか
- confidence 表示の条件
- next action の粒度

これらのスタイルは Human Model に支えられうるが、固定テンプレート化しない方がよい。

---

## 16. Open Questions

Human Model v1 時点で未解決の論点。

1. Human Model は Memory と別 artifact として保持すべきか、それとも Human Model snapshot docs を主にするべきか。
2. Human Model の各観察に confidence / provenance をどこまで厳密に付与するべきか。
3. 高感度だが支援上は重要な情報を、どのレイヤーにも保存しない選択をどう設計するか。
4. Human Model review を user-driven にするか、定期レビュー候補としてのみ扱うか。
5. Worker ごとに Human Model をどこまで見せてよいか。
6. Human Model と Communication Style の境界を別文書で切るべきか。
7. Human Model を Decision Framework v1 のどこに位置づけるのが最も自然か。

---

## 17. Next Recommended Task

次の推奨タスクは、**Decision Support / Decision Style まわりの入口文書を1本作ること** である。

理由:

- Human Model 単体では「理解」は定義できても「どう意思決定支援へ使うか」が未確定
- Decision Profile / Perspective / Constitution / Research との接続点を明文化する必要がある
- Human Model を runtime の hidden steering layer にしないためには、Decision Support 側の利用規約が必要

最小次手候補:

- `docs/product/decision-support-v1.md`
- または `docs/product/decision-style-v1.md` (optional future doc; not yet created)

原則:

> Define how human understanding is used before expanding what is understood.
