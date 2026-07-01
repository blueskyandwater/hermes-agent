# Weekly Quality Report v1 Draft

## 1. Purpose

Weekly Quality Report は、Hermes の**行動品質を週次で見える化する report artifact** である。

この文書の目的は、Weekly Quality Report が何を入力として受け取り、何を出力として返し、どこまでを責務とし、どこから先を別レイヤーに委ねるかを明確にすることにある。

特に重要なのは、Weekly Quality Report が次のものではないと明示することだ。

- 自動統治 engine
- 自動 task 作成機構
- 自動 mutation pipeline
- 自動 worker dispatch 制御
- 自動 CI rerun controller
- report を authorization に変換する shortcut

Weekly Quality Report が目指すもの:

- Hermes の行動品質を定期的に可視化する
- score trend と repeated issue を report として整理する
- regression candidate を早めに見つける
- violation を感情ではなく evidence として記録する
- improvement candidate preview を示す
- Human review へ handoff する
- Quality Framework / Continuous Evolution / Improvement Backlog をつなぐ
- user agency を壊さない

中心原則:

> Weekly Quality Report observes and reports; it does not govern.

補足原則:

- Quality finding is evidence, not permission
- Report output is not authorization
- Improvement candidate preview is not task creation
- No automatic Kanban mutation
- No automatic Memory / Human Model mutation
- No automatic Constitution / Gate rule changes
- No automatic worker dispatch
- No automatic CI rerun
- Human review is required before improvement backlog mutation
- Current user instruction wins

この文書は:

- runtime 実装を追加しない
- report から task を自動作成しない
- report から backlog を自動更新しない
- report から Constitution / Gate を自動変更しない
- report から worker を自動起動しない
- report から CI を自動再実行しない

---

## 2. Scope

Weekly Quality Report v1 が扱う対象:

- 週次 report の入力 sources
- 週次 report の出力形式
- report が含む sections
- score trend の読み方
- repeated issue detection の考え方
- regression candidate detection の考え方
- violation reporting の基本形
- improvement candidate preview の位置づけ
- Human review handoff の境界
- Quality Framework / Continuous Evolution / Improvement Backlog / CI observer / Worker Architecture / Memory System との関係
- report-only boundaries

Weekly Quality Report v1 が直接扱わない対象:

- 実際の task 作成
- 実際の backlog mutation
- 実際の Memory / Human Model mutation
- 実際の Constitution / Gate mutation
- 実際の worker dispatch
- 実際の CI rerun
- runtime enforcement
- autonomous governance

---

## 3. Non-goals

Weekly Quality Report v1 の非目標を明示する。

### Non-goal 1: report を governance に変えること

Weekly Quality Report は report であり、governance engine ではない。

score が低いこと、violation があること、repeated issue が増えていることは、観測された事実であって、そのまま自動制御の根拠にはならない。

### Non-goal 2: report から task を作ること

Improvement candidate preview は preview に留まる。

report の中に candidate が書かれていても、それは task creation authorization ではない。

### Non-goal 3: report からルールを恒久化すること

one-week の observation だけで新しい permanent rule を作ってはならない。

rule の恒久化は Continuous Evolution と human review を通す必要がある。

### Non-goal 4: ユーザーを評価すること

Weekly Quality Report の評価対象は Hermes の行動品質である。

ユーザーの人格、判断、感情、価値観は評価対象ではない。

### Non-goal 5: すべてを numbers に閉じること

Metrics は重要だが、すべてを数値だけで表現できるわけではない。

Judge verdict、violation summary、qualitative issue note などの narrative layer は残す。

### Non-goal 6: 週次 report を current instruction より優先すること

Current user instruction wins.

weekly report に「この改善が必要」と書かれていても、現在の明示指示がそれを許可していなければ実行してはならない。

---

## 4. Report Inputs

Weekly Quality Report は複数の source から入力を受ける。

ただし、入力が存在することと、その入力が action permission を持つことは別である。

### 4.1 Primary inputs

主要入力は次のとおり。

- Quality Framework にもとづく score / verdict / finding
- Judge outputs
- Metrics aggregation
- session-level quality observations
- repeated issue logs
- violation records
- CI observer summary
- worker-specific observation summaries
- human review comments
- prior weekly reports

### 4.2 Optional inputs

必要に応じて以下を補助入力として扱える。

- Improvement Backlog の候補一覧
- Continuous Evolution review notes
- release / deployment timing notes
- operational incident notes
- regression triage notes
- benchmark or audit results

### 4.3 Input hierarchy

情報源の優先順位は原則として次の順で整理する。

1. official runtime evidence
2. direct logs / metrics / CI records
3. Judge scoring output
4. structured human review notes
5. previous reports
6. interpretive commentary

この順序を守る理由は、report が impression-driven になるのを防ぐためである。

### 4.4 Input quality constraints

Weekly Quality Report に入力する情報は、少なくとも次を満たすべきである。

- source が追跡できる
- time window が分かる
- fact と interpretation が分けられている
- Unknown が Unknown として書かれている
- repeated issue の判定根拠が書ける
- regression candidate の比較対象が分かる

### 4.5 Missing input handling

必要入力が不足している場合、report はそれを明示する。

例:

- Judge output missing
- metrics sample too small
- CI observer unavailable
- worker-specific evidence incomplete

不足がある場合でも、勝手に埋めて report を complete 扱いしてはならない。

---

## 5. Report Outputs

Weekly Quality Report は何を返すかを明確にする。

### 5.1 Core outputs

report の主要出力は次のとおり。

- weekly summary
- score trend summary
- verdict distribution
- repeated issue summary
- regression candidate summary
- violation summary
- improvement candidate preview
- human review handoff note
- confidence / evidence completeness note

### 5.2 Output shape

出力は次の原則に従う。

- summary は短く
- evidence は辿れる形で
- interpretation は evidence と分離
- recommendation は action authorization に見えない形で
- unknown は消さずに残す

### 5.3 Output constraints

Weekly Quality Report は以下を出力してはならない。

- 自動で作成された task ID
- 自動で書き換えられた Memory record
- 自動で変更された Constitution text
- 自動で dispatch 済み worker state
- 自動 rerun した CI result

### 5.4 Output as handoff artifact

Weekly Quality Report は final decision artifact ではなく、**human review へ渡す handoff artifact** である。

その役割は:

- 今週の状態を見える化する
- 何が repeated issue かを整理する
- 何が regression candidate かを分ける
- どの改善候補が review に値するかを preview する
- backlog mutation や implementation approval を代行しない

---

## 6. Relationship with Quality Framework

Weekly Quality Report は Quality Framework の downstream artifact である。

Quality Framework が定義するもの:

- 何を評価するか
- どの観点で score を付けるか
- verdict をどう扱うか
- worker-specific checks をどう分けるか
- quality boundary をどこに置くか

Weekly Quality Report が受け取るもの:

- quality scorecard の集約結果
- verdict summaries
- repeated findings
- worker-specific warnings
- quality boundary violations

### 6.1 Separation of concerns

Quality Framework は evaluation model であり、Weekly Quality Report は reporting artifact である。

両者は密接だが同一ではない。

- Quality Framework = 何をどう評価するか
- Weekly Quality Report = その評価を週次でどう伝えるか

### 6.2 Forbidden shortcut

禁止される shortcut:

- Quality Framework の finding をそのまま実装指示に変えること
- score の低下をそのまま task creation に変えること
- verdict を approval と誤認すること

### 6.3 Evidence flow

推奨される flow:

1. Quality Framework が score / verdict / findings を生成
2. Weekly Quality Report が trend / repetition / regression を整理
3. Human review が解釈し、必要なら Improvement Backlog へ渡す
4. Continuous Evolution が reviewed refinement として扱う

---

## 7. Relationship with Continuous Evolution

Continuous Evolution は reviewed refinement の lifecycle を定義する。

Weekly Quality Report はその lifecycle に入る前の**観測整理レイヤー**として働く。

### 7.1 What Weekly Quality Report can do

- 改善候補を preview する
- repeated issue を可視化する
- regression candidate を可視化する
- どの論点が review に値するかを整理する

### 7.2 What Weekly Quality Report cannot do

- review を省略する
- approval を代行する
- implementation を始める
- high-risk change を黙って進める

### 7.3 Handoff to Continuous Evolution

Weekly Quality Report から Continuous Evolution に渡すとよい論点:

- repeated issue が structural gap か
- score drop が one-off か regression か
- violation が process gap か implementation gap か
- improvement candidate が local patch で済むか policy review が必要か
- permanent rule 化を検討すべきか、まだ早いか

### 7.4 No implicit evolution

report が存在しても、Hermes が勝手に evolve してよいわけではない。

Weekly Quality Report の存在は、evolution permission ではない。

---

## 8. Relationship with Improvement Backlog

Improvement Backlog は inventory layer である。

Weekly Quality Report は backlog のための**候補 preview source**にはなれるが、backlog そのものではない。

### 8.1 Preview, not mutation

report 内の improvement candidate preview は:

- preview である
- candidate inventory seed である
- backlog task creation ではない

### 8.2 Backlog mutation boundary

次の行為は Weekly Quality Report の責務外である。

- backlog item の新規作成
- backlog status の変更
- backlog priority の変更
- backlog item の close / merge / split

これらには human review が必要である。

### 8.3 Preferred connection

望ましい接続は次のとおり。

- Weekly Quality Report が candidate preview を出す
- human reviewer が preview を見て必要なものだけ選ぶ
- Improvement Backlog に inventory として追加するか判断する
- Continuous Evolution が reviewed refinement として扱う

---

## 9. Relationship with CI Observer

CI observer は runtime / test / workflow failure などの evidence source になりうる。

Weekly Quality Report は CI observer を evidence source として参照できるが、CI observer を制御してはならない。

### 9.1 CI observer から受け取るもの

- failure count
- flaky patterns
- skipped workflow anomalies
- repeated test regression signs
- runtime integration drift signals

### 9.2 Weekly report での扱い

Weekly Quality Report では、CI observer から受け取った事象を次のように扱う。

- fact: 何が起きたか
- frequency: 何回起きたか
- trend: 増えているか減っているか
- impact: どの surface に影響したか
- uncertainty: 未確定点は何か

### 9.3 Forbidden CI actions

Weekly Quality Report は以下をしてはならない。

- CI rerun を自動実行する
- failure に応じて worker を自動 dispatch する
- workflow file を自動変更する
- alert threshold を自動上書きする

---

## 10. Report Sections

Weekly Quality Report の標準 section を定義する。

### 10.1 Executive summary

最初に短い summary を置く。

含める内容:

- 今週の全体傾向
- score の方向感
- 目立つ repeated issue
- review が必要な high-risk point

### 10.2 Scope and evidence coverage

report がどの範囲を見たか、何が missing かを明示する。

例:

- sessions covered
- worker surfaces covered
- CI data covered
- missing sources
- incomplete metrics note

### 10.3 Score snapshot

現在週の主要 score を一覧化する。

例の観点:

- instruction following
- execution accuracy
- scope discipline
- evidence handling
- reporting quality
- safety boundary adherence

### 10.4 Trend section

前週比や rolling window で見た trend をまとめる。

### 10.5 Repeated issue section

繰り返し出ている issue を整理する。

### 10.6 Regression candidate section

以前より悪化している可能性がある点を分ける。

### 10.7 Violation section

boundary violation や policy bypass を整理する。

### 10.8 Improvement candidate preview section

実装許可ではない preview として改善候補を並べる。

### 10.9 Human review handoff section

最後に、どの論点を人間が review すべきかを明示する。

---

## 11. Score Trend

Weekly Quality Report は single-week snapshot だけでなく trend を扱う。

### 11.1 Why trend matters

一回の低スコアだけでは、one-off miss か structural problem か判断しにくい。

trend を見ることで次が分かりやすくなる。

- 回復しているのか
- 横ばいなのか
- 徐々に悪化しているのか
- 特定 worker だけ悪いのか
- report quality だけ落ちているのか

### 11.2 Trend categories

trend は最低でも次のカテゴリで扱う。

- improving
- stable
- fluctuating
- deteriorating
- insufficient evidence

### 11.3 Trend interpretation constraints

trend の解釈には制約を置く。

- sample size が少ないなら断定しない
- one-off incident を structural と呼ばない
- large-context week と quiet week を単純比較しない
- route / worker / environment 変化を無視しない

### 11.4 Trend as evidence, not command

trend が悪化しても、それは command ではない。

trend は review priority を上げる材料にはなるが、action authorization ではない。

---

## 12. Repeated Issue Detection

repeated issue detection は、同種の問題が単発ではなく繰り返し発生しているかを見るための section である。

### 12.1 What counts as repeated

repeated issue と呼ぶには、最低でも次のいずれかが必要である。

- 同種の violation が複数週で観測される
- 同種の miss が複数 surface で観測される
- 同じ worker / route / task type で再発する
- review note と metrics の両方が同じ傾向を示す

### 12.2 What does not count automatically

次は automatic repeated issue にはしない。

- 一度だけの失敗
- evidence が曖昧な anecdote
- user instruction の変更で見え方が変わっただけの差分
- input difficulty 上昇だけで説明できる低下

### 12.3 Why repeated issue matters

repeated issue は:

- structural gap の候補になる
- Improvement Backlog に preview する価値がある
- Continuous Evolution で review する価値がある

ただし repeated issue でも automatic task ではない。

### 12.4 Reporting format

repeated issue は少なくとも次で書く。

- issue label
- observed count / weeks
- affected surfaces
- evidence references
- likely class
- uncertainty
- review recommendation

---

## 13. Regression Candidate Detection

regression candidate detection は、以前より悪くなった可能性がある点を整理するための section である。

### 13.1 Candidate, not verdict

この section で扱うのは regression **candidate** であり、確定 verdict ではない。

悪化の兆候があることと、真の regression であることは同じではない。

### 13.2 Signals for regression candidates

候補として扱える signal の例:

- 同じ task class で score が連続低下
- 以前は守れていた boundary violation が増えた
- report quality の omission が増えた
- execution verification の抜けが再発した
- CI observer 由来の同種 failure が増えた

### 13.3 Comparison baseline

regression candidate を語るときは baseline を明示する。

例:

- previous week
- rolling 4-week average
- pre-change period
- post-change period

### 13.4 False positive controls

誤検出を減らすため、少なくとも次を確認する。

- task mix が変わっていないか
- route / model / worker configuration が変わっていないか
- evidence coverage が落ちていないか
- user instruction style が変わっていないか

### 13.5 Handoff meaning

regression candidate は human review に渡すべき論点である。

だが、それだけで rollback / rerun / mutation を自動で起こしてはならない。

---

## 14. Violation Reporting

violation reporting は、boundary breach や policy bypass を weekly report の中で見える化する section である。

### 14.1 What is a violation here

ここでいう violation は主に次を指す。

- scope violation
- unauthorized mutation attempt
- evidence-free claim
- report-only boundary breach
- auto-action shortcut
- explicit instruction override

### 14.2 Reporting goals

violation reporting の目的:

- 責めることではなく、再発防止のための evidence を残す
- severity を整理する
- repetition を可視化する
- structural gap か one-off かを見分ける材料にする

### 14.3 Severity buckets

v1 では簡易に次の buckets を使える。

- low: 軽微な形式崩れ、影響限定
- medium: review quality の欠損、誤解の余地あり
- high: unauthorized action に近い、または trust を大きく損なう
- critical: 明確な boundary breach、即 review 必須

### 14.4 Violation report template

各 violation は次を含める。

- label
- severity
- fact summary
- affected area
- evidence reference
- repeat status
- immediate containment note
- review-needed flag

### 14.5 No automatic punishment

Weekly Quality Report は violation を報告できても、punishment engine ではない。

- auto-disable しない
- auto-suppress しない
- auto-restrict しない
- auto-dispatch しない

---

## 15. Improvement Candidate Preview

improvement candidate preview は、report の終盤で「review に値する改善候補」を preview する section である。

### 15.1 Why preview exists

report が purely descriptive すぎると、改善につながりにくい。

一方で、report がそのまま task creation になると危険である。

preview section はこの中間を担う。

### 15.2 What preview should include

各 candidate preview は少なくとも次を持つ。

- candidate title
- origin evidence
- likely problem class
- expected benefit
- risk level
- whether review should be local or policy-level

### 15.3 What preview must not imply

preview は以下を意味しない。

- task が作られた
- backlog に入った
- implementation approval が出た
- this week 中に着手する

### 15.4 Candidate sizing

preview では改善候補を大きくしすぎない。

望ましい粒度:

- small behavioral refinement
- reporting template improvement
- boundary reminder improvement
- specific verification gap closure

避けたい粒度:

- repo-wide rewrite
- policy overhaul
- constitution rewrite from one weekly report

---

## 16. Human Review Handoff

Weekly Quality Report は最後に human review へ handoff する。

### 16.1 Why handoff matters

report が self-closing になると、report 自身が暗黙の governance layer になってしまう。

そのため、最終判断は human review に明示的に handoff する。

### 16.2 Handoff questions

handoff では例えば次を問う。

- この repeated issue は backlog candidate に値するか
- この regression candidate は追加検証が必要か
- この violation は one-off か structural gap か
- この candidate preview は low-risk refinement か rule-level review か
- いま着手すべきか、保留すべきか

### 16.3 High-risk review requirement

特に次の領域は high-risk change とみなす。

- Constitution changes
- Gate rule changes
- Memory / Human Model mutation
- worker dispatch policy changes
- auto-action / auto-mutation related changes

これらは explicit approval が必要である。

### 16.4 Report output is not approval

handoff を書いても、それは approval を発行したことにはならない。

report output is not authorization.

---

## 17. Dangerous Examples

Weekly Quality Report v1 で避けるべき dangerous examples を並べる。

### Dangerous example 1: low score → auto task creation

悪い例:

> Score が 72 に落ちたので、improvement task を自動作成した。

なぜ危険か:

- score を authorization にしている
- human review を飛ばしている
- backlog boundary を破っている

### Dangerous example 2: repeated issue → permanent rule

悪い例:

> 同じ miss が2回出たので、新しい permanent rule を system prompt に追加した。

なぜ危険か:

- repeated issue を過大解釈している
- rule bloat を招く
- review / approval を飛ばしている

### Dangerous example 3: violation report → worker dispatch

悪い例:

> report で violation を検出したので、review worker を自動 dispatch した。

なぜ危険か:

- report-only boundary breach
- worker control を report が奪っている

### Dangerous example 4: regression candidate → CI rerun

悪い例:

> regression candidate が出たので、CI を自動 rerun した。

なぜ危険か:

- candidate を action command に変えている
- CI observer と report の責務を混同している

### Dangerous example 5: weekly report → memory mutation

悪い例:

> report でユーザーの preference らしき傾向が見えたので Memory を自動更新した。

なぜ危険か:

- report から profile mutation へ飛んでいる
- past context を current approval と誤認している

### Dangerous example 6: no data → fabricated confidence

悪い例:

> CI observer データが無いが、たぶん安定しているので問題なしと書いた。

なぜ危険か:

- missing input を埋めてしまっている
- evidence integrity を壊している

---

## 18. Report-only Boundaries

Weekly Quality Report は report-only artifact である。

この boundary を明文化する。

### 18.1 Allowed behaviors

Weekly Quality Report がしてよいこと:

- 観測結果を整理する
- score trend を見せる
- repeated issue を要約する
- regression candidate を列挙する
- violation を分類する
- improvement candidate preview を提示する
- human review への handoff を書く

### 18.2 Disallowed behaviors

Weekly Quality Report がしてはならないこと:

- task を自動作成する
- Kanban status を変える
- Memory / Human Model を自動変更する
- Constitution / Gate text を自動変更する
- worker を起動する
- CI を再実行する
- code/config/docs を黙って修正する

### 18.3 Boundary statement

Weekly Quality Report は、**reporting layer** である。

reporting layer は:

- observes
- organizes
- summarizes
- highlights
- hands off

だが、次はしない。

- authorizes
- mutates
- dispatches
- reruns
- governs

### 18.4 Current instruction precedence

たとえ過去の weekly report で改善候補が繰り返し挙がっていても、現在の user instruction が no-change / docs-only / read-only を要求しているなら、それが優先される。

Current user instruction wins.

---

## 19. Open Questions

Weekly Quality Report v1 の時点で残る open questions を整理する。

### Open question 1: weekly window の定義

- calendar week に固定するか
- rolling 7 days にするか
- timezone をどう固定するか

### Open question 2: trend smoothing

- raw score のまま見せるか
- moving average を使うか
- outlier week をどう扱うか

### Open question 3: repeated issue threshold

- 何回で repeated と呼ぶか
- cross-worker repetition をどう数えるか
- severity と frequency の掛け合わせをどう扱うか

### Open question 4: evidence completeness scoring

- missing data をどこまで score に反映するか
- evidence coverage を separate metric にするか

### Open question 5: report audience layers

- operator 向けと strategic review 向けを分けるか
- one-page summary と full appendix を分けるか

### Open question 6: candidate preview cap

- 毎週いくつまで preview を出すか
- backlog bloat を避けるための上限を設けるか

### Open question 7: integration with metrics automation

- automated metrics aggregation の範囲をどこまで許すか
- report generation と report interpretation をどこで分けるか

### Open question 8: violation severity normalization

- severity の定義を worker 共通にするか
- task class ごとに補正するか

---

## 20. Next Recommended Task

Weekly Quality Report v1 の次に文書化すると接続が良くなる候補を示す。

第一候補は次である。

- `docs/product/foundation-pillar-map-v1.md`

理由:

- Hermes Foundation / Decision Profile / Human Model / Memory System / Worker Architecture / Quality Framework / Continuous Evolution / Improvement Backlog / Weekly Quality Report の接続関係を一枚で俯瞰できる
- 各補助文書の責務境界を横断的に見やすくできる
- rule 増殖ではなく boundary visibility を高める方向だから

次点候補:

- `docs/product/review-artifact-pipeline-v1.md` (optional future doc; not yet created)
- `docs/product/quality-signals-catalog-v1.md` (optional future doc; not yet created)

ただし、これらは design-only artifact として扱い、実装や自動 mutation に短絡させないことが重要である。

---

## Appendix A. Suggested Minimal Weekly Report Skeleton

以下は実装ではなく、report artifact の最小構成例である。

1. Executive Summary
2. Scope & Evidence Coverage
3. Weekly Score Snapshot
4. Trend Overview
5. Repeated Issues
6. Regression Candidates
7. Violations
8. Improvement Candidate Preview
9. Human Review Handoff
10. Unknowns / Evidence Gaps

この skeleton は template であり、authorization ではない。

---

## Appendix B. Interpretation Discipline

Weekly Quality Report を読む側は、少なくとも次の discipline を保つべきである。

- fact と opinion を混ぜない
- candidate と approved task を混同しない
- repeated issue と permanent rule を短絡しない
- trend と deterministic command を混同しない
- report artifact と governance engine を混同しない

この discipline が崩れると、Weekly Quality Report は user agency を支える artifact ではなく、silent governance の入口になってしまう。

---

## Appendix C. Summary Statements to Preserve

Weekly Quality Report v1 で繰り返し守るべき短文を最後に固定する。

- Weekly Quality Report observes and reports; it does not govern
- Quality finding is evidence, not permission
- Report output is not authorization
- Improvement candidate preview is not task creation
- No automatic Kanban mutation
- No automatic Memory / Human Model mutation
- No automatic Constitution / Gate rule changes
- No automatic worker dispatch
- No automatic CI rerun
- Human review is required before improvement backlog mutation
- Current user instruction wins
