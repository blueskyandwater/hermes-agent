# Quality Framework v1 Draft

## 1. Purpose

Quality Framework は、Hermes の**行動品質**を観測・採点・報告するための補助文書である。

この文書の目的は、Quality が何を評価対象にし、どこまでを責務とし、どこから先を担当しないかを明確にすることにある。特に重要なのは、Quality が **Hermes の行動品質を観測する layer** であって、**自動統治・自動修正・自動承認の layer ではない** ことをはっきりさせることである。

Quality Framework が目指すもの:

- Hermes の出力と行動を review 可能な形で観測する
- 何が良く、何が危険で、何が不足していたかを可視化する
- Judge / Metrics / Report の責務を混同しない
- Worker Architecture と接続しつつ、silent governance を防ぐ
- user agency を壊さない改善ループを支える

中心原則:

> Quality observes, scores, and reports. It does not silently govern.

補足:

- Quality evaluates Hermes behavior, not the user
- Judge judges. Judge does not govern
- Metrics records measurable facts. Metrics does not decide policy
- Report informs the user. It does not act on behalf of the user
- Quality score is evidence, not approval
- Quality finding is evidence, not permission
- No auto-approve
- No auto-suppress
- No auto-mutate
- No auto-dispatch
- User agency remains first

この文書は:

- runtime 実装を追加しない
- 自動 suppression rule を導入しない
- worker を自動制御しない
- Kanban mutation を実行しない
- CI / Cron / GitHub / Discord の既存運用を変更しない
- approval engine を新設しない

---

## 2. Scope

この文書が扱う対象:

- Hermes の行動品質に対する評価観点
- scorecard / verdict / report の基本モデル
- worker ごとの観測ポイント
- Judge / Metrics / Report の責務分離
- Worker Architecture との接続境界
- CI observer との関係
- silent governance を避けるための禁止境界

この文書が直接扱わない対象:

- ユーザー本人の人格評価
- ユーザーの意思決定の正誤判定
- 専門領域そのものの truth engine
- 自動修正パイプラインの実装
- 自動承認ロジック
- 行動制御 policy engine
- full runtime telemetry schema の確定

---

## 3. Non-goals

Quality Framework v1 の非目標を明示する。

### Non-goal 1: Hermes を自動統治すること

Quality は採点できても、そこで得た score を使って Hermes を自動的に制御してはならない。

### Non-goal 2: ユーザーを採点すること

評価対象は Hermes の応答・判断・実行・報告の品質であり、ユーザーではない。

### Non-goal 3: approval の代行

高スコアや良い verdict は、危険操作や高リスク行為の approval にはならない。

### Non-goal 4: silent fix

Quality は問題を検出しても、黙って修正や mutation を行わない。

### Non-goal 5: failure の隠蔽

低スコアや逸脱の記録を suppress して見えなくすることはしない。

### Non-goal 6: blame engine になること

Quality は責めるための仕組みではなく、振る舞いの改善点を明らかにするための仕組みである。

---

## 4. Evaluation Dimensions

Quality Framework は、Hermes の行動を複数の観点から評価する。

### 4.1 Goal alignment

- ユーザーの依頼に近づいたか
- 目的に対して無関係な脱線をしていないか
- mode や scope を守ったか
- 「頼まれていないこと」を増やしていないか

### 4.2 Instruction compliance

- 明示された許可/禁止を守ったか
- 現在の user instruction を優先したか
- stale context や過去運用を current intent より上に置いていないか
- no-commit / no-push / read-only のような制約を守ったか

### 4.3 Evidence quality

- 事実を事実として扱ったか
- 推測を推測として分離したか
- source を伴う検証を行ったか
- tool output と最終報告が一致しているか

### 4.4 Safety and boundedness

- 不要な side effect を起こしていないか
- 危険操作の approval を勝手に補っていないか
- authorization と context を混同していないか
- 権限の外に出ていないか

### 4.5 Reasoning clarity

- 判断理由が追えるか
- 過剰説明ではなく、必要十分な整理になっているか
- fact / assumption / risk / value を混ぜていないか
- 次の一歩が明確か

### 4.6 Operational quality

- 実行したと言ったことを本当に実行したか
- verification を省略していないか
- 実行結果の handoff が practical か
- 長すぎず、短すぎず、使える報告になっているか

### 4.7 Role discipline

- Planner が勝手に実行していないか
- Executor が勝手に approval を出していないか
- Researcher が提案や断定を混ぜていないか
- Reviewer が黙って修正していないか
- Guard / Judge / Metrics / Report が責務を越境していないか

### 4.8 User agency preservation

- 最終判断を user に残したか
- 高スコアを approval の代替として使っていないか
- user correction を受け入れられる構造になっているか
- 「正しそうだからやる」を防げているか

---

## 5. Scorecard Model

Quality Framework v1 では、scorecard を**観測記録**として扱う。

### 5.1 Scorecard の役割

scorecard は、Hermes の行動品質を複数軸で記録し、比較可能にするためのものである。

scorecard が提供するもの:

- どこが良かったか
- どこが弱かったか
- 改善前後で何が変わったか
- どの worker / mode / task type で崩れやすいか

scorecard が提供しないもの:

- approval
- automatic allow/deny
- worker dispatch permission
- policy override

### 5.2 基本構造

scorecard には最低限、以下のような観点が含まれる。

- task identifier or session identifier
- evaluated worker / role
- evaluated mode
- evaluation timestamp
- dimension scores
- overall score
- verdict
- observed evidence
- notable issues
- recommended follow-up

### 5.3 点数の意味

点数はあくまで品質の観測値であり、次を意味しない。

- 高得点 = 自動で正しい
- 高得点 = 危険操作を許可できる
- 低得点 = ユーザーの意図が悪い
- 中得点 = 自動で suppression すべき

### 5.4 定量と定性の併用

Quality では、数値だけでは不十分である。

必要なのは:

- measurable count / rate / pass-fail
- short qualitative explanation
- evidence-linked notes
- unknown / not observed の明示

単なる平均点だけでは、「何が起きたか」「なぜ問題なのか」が見えなくなる。

---

## 6. Verdict Model

verdict は、scorecard を補助する**短い判定ラベル**である。

### 6.1 verdict の役割

verdict は、人間が一目で状況を把握するための要約である。

例:

- Excellent
- Good
- Needs Improvement
- Blocked Observation
- Inconclusive

### 6.2 verdict の境界

verdict は以下をしてはならない。

- task approval
- policy decision
- automatic retry decision
- automatic rollback decision
- mutation permission

### 6.3 verdict と evidence の関係

verdict は evidence の要約であって、evidence の代替ではない。

原則:

- verdict without evidence は弱い
- evidence without verdict は読みにくい
- 両方必要だが、優先されるのは evidence

### 6.4 Inconclusive の重要性

観測不足・ログ不足・評価不能時には、無理に良し悪しを決めず `Inconclusive` を使う。

これは fail-open を防ぐために重要である。

---

## 7. Worker-specific Checks

Worker Architecture と接続するため、worker ごとの観測項目を分けて考える。

### 7.1 Planner checks

見るポイント:

- 問題設定が適切か
- 優先順位付けが practical か
- 不要な複雑化を避けたか
- 実行権限のないことを実行前提にしていないか
- 提案数や次の一歩が過剰でないか

失敗例:

- Planner が勝手に実行命令を出す
- Planner が approval 済み前提で話を進める
- Planner が stale memory を policy として扱う

### 7.2 Executor checks

見るポイント:

- 指示どおりの操作だけを行ったか
- scope 外ファイルを触っていないか
- verification を行ったか
- side effect を正しく報告したか
- していないことを「した」と言っていないか

失敗例:

- no-commit 指示中に commit する
- read-only task で mutation する
- verification なしで成功と報告する

### 7.3 Researcher checks

見るポイント:

- source hierarchy を守ったか
- fact / unknown / opinion / rumor を分けたか
- 判断や指示を混ぜていないか
- 調査範囲を誇張していないか

失敗例:

- SNS の噂を確定情報として扱う
- 調査結果に recommendation を混ぜる
- source を示さず断定する

### 7.4 Reviewer checks

見るポイント:

- 実際の output を根拠に評価しているか
- 過度に甘くないか
- 修正ではなく review に徹しているか
- 重要な逸脱を見落としていないか

失敗例:

- Reviewer が黙って output を補修する
- Reviewer が user を評価する
- Reviewer が自己採点を鵜呑みにする

### 7.5 Guard checks

見るポイント:

- 実行前の事実確認ができているか
- user instruction と禁止事項を正しく読んでいるか
- 権限の有無を確認しているか
- NG の時に止められているか

失敗例:

- Guard が approval を出す
- Guard が memory を authorization に変える
- Guard が曖昧なまま通す

### 7.6 Dispatcher / Cron / Observer checks

見るポイント:

- route と approval を混同していないか
- backlog を authorization にしていないか
- observe/report の範囲を越えていないか
- silent action をしていないか

失敗例:

- Dispatcher が勝手に許可する
- Cron が自動修正を始める
- Observer が failure classification を誤用して governance に使う

---

## 8. Judge / Metrics / Report Separation

Quality Framework v1 では、Judge / Metrics / Report を明確に分離する。

### 8.1 Judge

Judge は、Hermes の output や行動を**採点・判定**する。

Judge の責務:

- 評価軸に沿って採点する
- output-based に問題点を指摘する
- Good Points / Issues / Improvement を簡潔に返す

Judge の非責務:

- policy を決めること
- approval を与えること
- 自動修正すること
- worker を dispatch すること

### 8.2 Metrics

Metrics は、**測れる事実**だけを記録する。

Metrics の責務:

- 実行回数
- 成功/失敗数
- 質問数
- tool call 数
- constraint violation count
- average score
- N/A の明示

Metrics の非責務:

- 何をすべきか決めること
- policy を変更すること
- qualitative judgment を代行すること

### 8.3 Report

Report は、Judge と Metrics をもとに**人に伝える**役割を持つ。

Report の責務:

- 現状を短く整理する
- evidence と metrics を読みやすく要約する
- 重要な変化を可視化する
- 人間が次の判断をしやすくする

Report の非責務:

- 自動で行動すること
- suppression / mutation / dispatch を行うこと
- approval として振る舞うこと

### 8.4 分離の理由

この分離を崩すと、次の危険が起きる。

- Judge が governance になってしまう
- Metrics が policy engine になってしまう
- Report が approval message と誤認される
- 低品質な自動制御が増える

---

## 9. Quality Boundaries

Quality Framework には、明確な越境禁止ラインが必要である。

### 9.1 Quality は authorization source ではない

どれだけ score が高くても、以下の許可にはならない。

- push
- merge
- PR 作成
- destructive operation
- billing-impacting change
- cron mutation
- policy mutation

### 9.2 Quality は silent governance をしてはならない

禁止される例:

- スコアが低い worker を自動停止する
- 特定 profile を自動で mute する
- quality note を理由に task を自動 cancel する
- report を見て自動 reroute する

### 9.3 Quality finding は evidence であって命令ではない

Quality finding は:

- 見直しの根拠にはなる
- review の材料にはなる
- improvement 候補にはなる

しかし以下にはならない:

- 自動承認
- 自動修正
- 自動処罰
- 自動 dispatch

### 9.4 Unknown を残せること

評価不能なものは unknown / not observed / inconclusive として残す。

曖昧なまま判定して governance に流用する方が危険である。

---

## 10. Relationship with CI Observer

Quality Framework は、CI observer と接続できるが、同一ではない。

### 10.1 CI observer の役割

CI observer は、CI / workflow / run status などの**外部実行事実**を観測する。

例:

- workflow succeeded / failed / skipped
- run logs availability
- commit-level observation
- not_applicable classification

### 10.2 Quality との関係

Quality は、CI observer の出力を一部 evidence として使える。

たとえば:

- 「Hermes が CI failure を誤分類した」
- 「skipped workflow を failed 扱いした」
- 「ログ未観測なのに断定した」

のような品質問題を評価できる。

### 10.3 境界

ただし、CI observer 自体は Quality ではない。

- CI observer は外部状態を観測する
- Quality は Hermes の扱い方を評価する

### 10.4 禁止される混同

- CI success → Hermes approval
- CI skipped → quality suppress
- observer warning → auto mutation
- CI result → user intent override

---

## 11. Relationship with Worker Architecture

Quality Framework は Worker Architecture に従属するのではなく、**接続しつつ越境しない**。

### 11.1 接続点

Quality は次を観測対象にできる。

- worker role discipline
- mode compliance
- scope adherence
- approval handling
- reporting quality
- verification completeness

### 11.2 越境禁止

Quality は次をしてはならない。

- worker を自動的に再配属する
- worker 権限を自動で変更する
- low score を理由に task を自動停止する
- worker 出力を黙って差し替える

### 11.3 Review loop の位置づけ

Worker Architecture 側で review step を持つとしても、Quality はその review の**観測・整理**を助けるものであり、実行権を持たない。

### 11.4 User agency の保持

最終的に:

- どの issue を重く見るか
- 何を改善対象にするか
- どの worker をどう運用するか

は user または明示的な human-approved governance が決める。

---

## 12. Risks

Quality Framework にも固有のリスクがある。

### 12.1 Score worship

点数だけが独り歩きし、具体的 evidence が無視される危険。

### 12.2 Governance creep

評価機能がだんだん policy engine や suppression engine に変質する危険。

### 12.3 False confidence

高得点が「安全」「承認済み」と誤解される危険。

### 12.4 Metric gaming

本質改善ではなく、見かけの score 改善だけを狙う危険。

### 12.5 Over-penalizing uncertainty

Unknown や Inconclusive を悪とみなして、無理な断定を誘発する危険。

### 12.6 User displacement

Quality report が強すぎて、user の判断空間を圧迫する危険。

### 12.7 Hidden coupling

Quality と Worker Architecture / Cron / Dispatcher が密結合し、いつの間にか silent control chain が生まれる危険。

---

## 13. Dangerous Examples

ここでは、Quality Framework の誤用例を示す。

### Example 1: 高スコアだから push してよい

誤り。

score は evidence であって authorization ではない。push には別の明示承認が必要である。

### Example 2: Judge が Needs Improvement を出したので task を自動停止

誤り。

Judge は判定するだけであり、停止権限は持たない。

### Example 3: Metrics で質問数が多いので自動 suppress

誤り。

質問数は観測値であり、文脈なしの suppression 判断には使えない。

### Example 4: Report が low confidence と書いたので cron を自動 pause

誤り。

Report は inform するだけで、操作権限はない。

### Example 5: Quality finding を根拠に user の current instruction を無視

誤り。

Current user instruction wins。Quality finding は補助情報にすぎない。

### Example 6: skipped CI を failure 扱いして品質問題として断定

誤り。

未観測・not applicable・skipped は区別しなければならない。

### Example 7: 低品質 worker output を Reviewer が黙って書き換える

誤り。

Reviewer は review する役割であり、silent fix は責務違反である。

---

## 14. Implementation Candidates

Quality Framework v1 は design 文書であり、ここでは implementation candidate を列挙するだけに留める。

### Candidate 1: session-level scorecard

各セッション/タスクごとに:

- dimension score
- verdict
- evidence note
- blocking issue count
- instruction compliance flag

を保存する軽量形式。

### Candidate 2: judge report template

Judge が一定フォーマットで返すテンプレート。

例:

- Score
- Good Points
- Issues
- Improvement

### Candidate 3: metrics aggregation layer

日次 / 週次で:

- 平均スコア
- role別の violation count
- mode別の failure pattern
- N/A count
- not observed count

を集計する層。

### Candidate 4: quality dashboard artifact

人間向けに:

- trend
- repeated issues
- improvement candidates
- evidence links

を一覧化する artifact。

### Candidate 5: worker-specific audit checklist

Planner / Executor / Researcher / Reviewer / Guard / Dispatcher / Cron ごとに、最小限の監査項目を固定する。

### Candidate 6: explicit boundary tests

将来的な runtime 実装で必要になりうるもの:

- no auto-approve test
- no auto-suppress test
- no auto-mutate test
- no auto-dispatch test
- report-is-not-action test

### Candidate 7: CI observer linkage notes

CI observer 由来 evidence を Quality に渡すときの:

- observed
- not observed
- not applicable
- skipped
- failed

の分類メモ。

これらは候補であり、この文書自体は採用や実装を確定しない。

---

## 15. Open Questions

Quality Framework v1 の段階で未解決として残す論点。

1. Scorecard の最小必須項目はどこまでか
2. Judge の採点粒度を role別に変えるべきか
3. Metrics の「N/A」と「not observed」をどこまで分けるべきか
4. Quality report の頻度は session / daily / weekly のどこが最適か
5. CI observer evidence をどの程度強く品質判断に使うべきか
6. User-facing report と internal audit artifact を分けるべきか
7. self-evaluation と judge-evaluation の重み付けをどう分けるべきか
8. quality trend を profile / mode / worker 単位でどう比較するか
9. Quality findings を human-approved improvement backlog にどう接続するか
10. 「評価疲れ」を防ぐための最小観測セットは何か

---

## 16. Next Recommended Task

次の補助文書候補としては、以下が自然である。

### Option A: `docs/product/ci-observer-v1.md` (future candidate; not yet created)

Quality と CI observer の境界をさらに明確化できる。

### Option B: `docs/product/reporting-and-governance-boundaries-v1.md` (future candidate; not yet created)

Report / Governance / Approval の混同防止を個別に整理できる。

### Option C: `docs/product/foundation-pillar-map-v1.md`

Foundation / Planning Gate / Memory / Human Model / Decision Support / Domain Model / Decision Profile / Worker Architecture / Quality Framework の接続地図を作れる。

現時点で最も効果が高いのは次だと考えられる。

> Recommended next task: `docs/product/foundation-pillar-map-v1.md`

理由:

- pillar docs 間の接続関係を 1 枚で見やすくできる
- overlap / gap / boundary collision を発見しやすい
- runtime 実装前の設計レビュー土台として使いやすい

---

## Appendix: Short Summary

Quality Framework v1 の要点はシンプルである。

- Quality は Hermes の行動品質を評価する
- Quality は user を評価しない
- Quality は観測・採点・報告をする
- Quality は approval・suppression・mutation・dispatch をしない
- Judge / Metrics / Report は分離する
- Quality score は evidence であり authorization ではない
- User agency remains first
