# Improvement Backlog v1 Draft

## 1. Purpose

Improvement Backlog は、Hermes における**改善候補を管理する在庫レイヤー**である。

この文書の目的は、Improvement Backlog が何を保持し、何を保持せず、どこまでを責務とし、どこから先を別レイヤーに委ねるかを明確にすることにある。

特に重要なのは、Improvement Backlog が次のものではないと明示することだ。

- 実装許可
- 自動実行キュー
- 自動ディスパッチ機構
- 自動ルール追加エンジン
- 過去の問題から現在の承認を代行する仕組み

Improvement Backlog が目指すもの:

- 改善候補を散逸させず inventory として保持する
- Quality finding や user feedback をそのまま実装に短絡させず、候補として整理する
- one-off / repeated / regression / structural gap を区別する
- Continuous Evolution に渡す前の整理レイヤーになる
- Planning Gate と接続しつつ、無断実行を防ぐ
- user agency を壊さない

中心原則:

> Improvement Backlog is inventory, not authorization.

補足原則:

- Quality finding is evidence, not permission
- Improvement candidate is not authorization
- Backlog task is not execution approval
- Repeated issue may become a candidate, not an automatic task
- Human review is required before backlog mutation
- Human approval is required before implementation
- One-off issues should not create permanent rules by default
- Current user instruction wins
- No auto-dispatch
- No auto-mutation

この文書は:

- runtime 実装を追加しない
- 改善候補を自動作成しない
- Kanban へ自動反映しない
- Constitution / Gate / Memory / Human Model を自動変更しない
- worker の自動起動を許可しない
- backlog item から implementation permission を導出しない

---

## 2. Scope

Improvement Backlog v1 が扱う対象:

- 改善候補の受け皿としての inventory 定義
- backlog に入れる条件と入れない条件
- candidate classification
- task として保持する際の必要項目
- status semantics
- Definition of Ready / Definition of Done
- approval 境界
- Quality Framework / Continuous Evolution / Planning Gate との接続
- rule bloat prevention
- 改善候補をどの観点で下流に渡すか

Improvement Backlog v1 が直接扱わない対象:

- 実際のコード変更
- 自動 backlog 書き込み実装
- backlog item の自動優先順位変更
- auto-approve / auto-dispatch / auto-mutate
- worker assignment の自動決定
- Constitution や Gate rule の runtime 書き換え
- Memory / Human Model の自動更新
- repo / cron / config 変更の実行

---

## 3. Non-goals

### Non-goal 1: backlog を approval engine にすること

backlog に候補が存在していても、それは「考える価値がある」ことしか意味しない。実装してよいことの証明にはならない。

### Non-goal 2: issue を見つけた瞬間に task 化すること

問題が見つかっても、すべてを即座に task 化する必要はない。まず観測・分類・重複整理が優先される。

### Non-goal 3: one-off を恒久ルールに変えること

一度きりの異常や偶発失敗から、恒久的な rule を増やすことは避ける。

### Non-goal 4: human review をスキップすること

人間レビュー前に backlog mutation が確定する設計は v1 の対象外である。

### Non-goal 5: backlog を dispatch queue にすること

backlog は inventory であり、worker 起動の順番待ちリストではない。

### Non-goal 6: 現在の user instruction を過去の候補で上書きすること

過去の改善案・過去の失敗・過去の成功は context にはなるが、現在の依頼や禁止事項に優先しない。

---

## 4. Improvement Backlog Boundaries

Improvement Backlog の境界は明確でなければならない。

### 4.1 Backlog がすること

- 改善候補を記録する
- 候補の種類を区別する
- 候補の根拠を残す
- 候補の危険度・適用範囲・再現性を整理する
- review や planning のための入力を整える
- Continuous Evolution に渡す論点を見失わないようにする

### 4.2 Backlog がしないこと

- 候補を見つけた瞬間に実装する
- 候補を見つけた瞬間に worker を動かす
- 候補の存在だけで優先度を確定する
- 候補の存在だけでルール追加を正当化する
- 候補の存在だけでユーザー承認があったとみなす
- 候補の存在だけで Memory / Human Model / Constitution を書き換える

### 4.3 Boundary summary

Improvement Backlog は**inventory layer**である。

- observe layer ではない
- judge layer ではない
- approval layer ではない
- execution layer ではない
- governance mutation layer ではない

---

## 5. Relationship with Quality Framework

Quality Framework は、Hermes の行動品質を観測・採点・報告する。
Improvement Backlog は、その結果を**改善候補として整理する在庫**である。

関係の整理:

- Quality は score / verdict / finding を出す
- Improvement Backlog は finding を candidate に変換できるかを整理する
- Quality score は backlog item 作成の自動許可ではない
- Quality finding は evidence であって implementation permission ではない

### 5.1 Quality から受け取るもの

- 失敗パターン
- 再発傾向
- 逸脱の頻度
- instruction compliance 問題
- evidence quality の不足
- tool-use / scope control / safety behavior の不備
- verdict とその理由

### 5.2 Quality に返さないもの

Improvement Backlog は Quality に対して次を返さない:

- 実装命令
- suppress 指示
- 自動ルール追加要求
- worker dispatch 命令

### 5.3 Key separation

Quality は「何が起きたか」を観測する。
Backlog は「改善候補として残すべきか」を整理する。
実装可否は別レイヤーで決める。

---

## 6. Relationship with Continuous Evolution

Continuous Evolution は、改善を review-centered lifecycle として扱う。
Improvement Backlog は、その lifecycle における**candidate inventory**を担う。

### 6.1 Backlog の役割

- 観測から生まれた改善案を蓄積する
- 重複を束ねる
- 一時的な問題と構造問題を分ける
- review 候補の順序づけ材料を整える

### 6.2 Continuous Evolution の役割

- 候補を review する
- approval 要件を満たすか判断する
- 実装の大きさを小さく区切る
- 検証を通して改善として成立するかを見る

### 6.3 境界

- backlog item は Continuous Evolution の input である
- backlog item は approve 済み改善ではない
- backlog item は implementation scope を自動確定しない
- backlog item は Kanban task creation を意味しない
- Human review が backlog mutation の前に必要である

---

## 7. Relationship with Planning Gate

Planning Gate は、実行前に scope / risk / readiness / approval を確認する境界である。
Improvement Backlog は、Planning Gate に渡す前段の inventory である。

### 7.1 Backlog から Planning Gate に渡すもの

- `title`
- `summary`
- `source`
- `evidence`
- `issue_type`
- `affected_area`
- `risk_level`
- `approval_required`
- `verification_plan`
- `next_review_step`

補足:

- これは Improvement Candidate schema v1 の最小 inventory 項目である
- `approval_required` は承認要否を示すだけで、承認済みを意味しない
- `next_review_step` は review / clarification / validation の次手候補であり、implementation instruction ではない

### 7.2 Planning Gate が別途確認すべきもの

- 今回の user instruction と一致するか
- 実行許可が今あるか
- high-risk 変更か
- 既存 rule の改善で足りるか
- implementation を本当に始めるべきか

### 7.3 Important boundary

backlog に item があることは、Planning Gate 通過を意味しない。

---

## 8. Candidate Intake Rules

すべての気づきが backlog candidate になるわけではない。intake には基準が必要である。

### 8.1 Candidate にしてよい入力

- Quality Framework の repeated finding
- Weekly Quality Report の recurring pattern
- user からの明示的な不満・再指摘
- CI observer による再発エラー
- worker 運用上の構造的詰まり
- read-only review で確認された process gap
- 明確な regression
- current architecture と設計原則の一貫性欠如

### 8.2 Candidate にしない方がよい入力

- 単発の typo
- 一度きりの偶発通信失敗
- まだ再現も切り分けもできていない曖昧な違和感
- user が明確に不要と言った改善案
- 現在の依頼 scope と無関係な一般論
- 「なんとなく気になる」だけで evidence がない提案

### 8.3 Candidate 化の最低条件

candidate として残すには最低でも次が必要である:

1. `title`
2. `summary`
3. `source`
4. `evidence`
5. `issue_type`
6. `affected_area`
7. `risk_level`
8. `approval_required`
9. `verification_plan`
10. `next_review_step`

補足:

- この最小項目は `docs/product/continuous-evolution-v1.md` の Improvement Candidate schema v1 を参照する
- `approval_required` は承認済みフラグではない
- `auto_apply_allowed` は v1 では `false` 固定であり、candidate intake から auto-approve / auto-dispatch / auto-mutate を導出しない
- ここで candidate にしただけでは backlog task creation にならない

### 8.4 Intake anti-patterns

- finding をそのまま task に昇格する
- user feedback を approval と誤読する
- repeated issue らしいという印象だけで恒久 rule 候補にする
- memory に似た内容があるから current approval もあるとみなす

---

## 9. Candidate Classification

Improvement Backlog v1 では、候補を最低限次の4類型で扱う。

### 9.1 One-off

単発で発生し、再発性や構造性がまだ確認されていないもの。

例:

- 一回だけ起きた応答の言い回し崩れ
- 一時的な外部API失敗に伴う report ノイズ

扱い:

- まずは記録軽量
- rule 化しない
- しばらく再観測する

### 9.2 Repeated issue

同系統の失敗やズレが複数回確認されているもの。

例:

- docs-only 指示なのに scope report が毎回冗長化する
- mode 指示をたまに取りこぼす

扱い:

- candidate として残しやすい
- ただし自動 task 化しない
- 原因が instruction / prompt / workflow / review のどこかを切る

### 9.3 Regression

以前はできていた、または期待どおりだった振る舞いが悪化したもの。

例:

- 以前は守れていた no-push reporting が最近崩れた
- 以前より Quality report が長文化して user burden を増やした

扱い:

- 重要度が上がりやすい
- 変更点との関連を追う価値が高い
- reversion / narrow fix 候補になりやすい

### 9.4 Structural gap

単発や設定ミスではなく、設計や役割分離そのものに不足があるもの。

例:

- Quality / Backlog / Approval の責務が混ざっている
- worker-specific review point が未定義

扱い:

- docs / framework / policy 改善候補になりやすい
- high-risk な rule 変更を含むことがあるため review を厚くする

### 9.5 Optional metadata

必要に応じて次も持てる:

- risk level
- blast radius
- evidence confidence
- affected layer
- suspected root cause class
- candidate owner for review

---

## 10. Backlog Task Requirements

backlog task として保存する場合、最低限の情報が必要である。

### 10.1 Required fields

- title
- short problem statement
- candidate class
- evidence summary
- evidence source
- observed frequency or occurrence note
- affected layer
- risk note
- current status
- explicit statement that item != approval

### 10.2 Recommended fields

- suspected root cause
- impacted user experience
- constraints / forbidden actions
- current instruction conflicts
- smallest possible experiment
- approval needed from whom
- links to related backlog items

### 10.3 Example skeleton

```md
Title: Reduce docs-only report bloat in scoped repo tasks
Class: repeated issue
Status: candidate
Problem: Completion reports sometimes exceed the user's preferred compact scope.
Evidence: 3 docs-only sessions with repeated long "did not do" blocks.
Source: session review / quality report
Affected layer: reporting behavior
Risk: low if phrasing-only, higher if prompt policy changes
Approval note: This backlog item is not execution approval.
```

### 10.4 What must be avoided

- title だけで中身が空
- evidence source が不明
- current approval の有無が曖昧
- 実装方針が先に固定されている
- 「とにかく直す」だけで bounded scope がない

---

## 11. Status Semantics

status は execution state ではなく、**inventory / review readiness state** として定義する。

### 11.1 candidate

候補として記録されたが、まだ review・重複整理・優先判断が十分でない状態。

### 11.2 triaged

基本分類・重複確認・初期リスク整理が終わった状態。

### 11.3 needs-evidence

問題意識はあるが、evidence が足りず candidate の質が不十分な状態。

### 11.4 parked

今すぐ扱わないが、捨てるほどでもない状態。再観測待ち。

### 11.5 ready-for-review

review に回せるだけの材料が揃った状態。

### 11.6 approved-for-planning

人間レビューにより、planning に進めてよいと明示された状態。

### 11.7 split-into-implementation

改善候補そのものは整理済みで、別の implementation work item に分割された状態。

### 11.8 rejected

候補として不適切、不要、または現在の方針と合わないと判断された状態。

### 11.9 Important note

どの status であっても、runtime execution permission を直接意味しない。

---

## 12. Definition of Ready for Improvement Tasks

改善候補が review や planning に進むには、最低限の Ready 条件が必要である。

### DoR checklist

1. `title` と `summary` で問題が1〜3文で説明できる
2. `source` と `evidence` が示されている
3. `issue_type` が暫定でも入っている
4. `affected_area` が分かる
5. `risk_level` が粗くても示されている
6. `approval_required` が明記されている
7. `verification_plan` が最低1行ある
8. `next_review_step` が implementation instruction ではなく review step として書かれている
9. 現在の user instruction と矛盾していない
10. 自動実行前提になっていない
11. backlog item は authorization ではないと明示されている

### Not Ready examples

- 「なんか微妙」だけで根拠がない
- 問題はあるが、どのレイヤーの話か不明
- current instruction に反する改善を暗黙に含む
- すでに実装前提で書かれている

---

## 13. Definition of Done for Improvement Tasks

Improvement Backlog 上の task が Done になるとは、必ずしも実装完了を意味しない。
Done は backlog inventory としての役目を終えたことを意味する。

### DoD patterns

#### Pattern A: rejected as unnecessary

- one-off で再発性なしと判断
- 恒久対応不要
- 理由が記録済み

#### Pattern B: absorbed into approved implementation work

- review により implementation item へ分割・移送済み
- 元 backlog item は inventory として閉じられる
- どこへ引き継いだかが明示されている

#### Pattern C: resolved by clarification

- 新規 rule 追加ではなく既存 rule の明確化で十分だった
- candidate の懸念が軽減された
- 再観測方針が残っている

#### Pattern D: invalid due to weak evidence

- candidate 根拠が崩れた
- 誤認・重複・一時ノイズだった
- 却下理由が説明可能

### DoD anti-patterns

- backlog に入れたから Done
- worker に投げたから Done
- Quality finding が出たから Done
- draft 実装を書いたから Done
- approval 未取得なのに Done

---

## 14. Approval Model

Improvement Backlog 自体にも approval 境界が必要である。

### 14.1 Backlog mutation approval

新規 backlog item 作成や大きな再分類は、人間レビューを要する。
少なくとも v1 では、無断 backlog mutation を標準にしない。

### 14.2 Implementation approval

backlog item から実装に進むには、別途明示的 approval が必要である。

### 14.3 High-risk changes

次は高リスクとみなし、より強い approval を要する:

- Constitution 変更
- Gate rule 変更
- Memory / Human Model mutation
- worker dispatch policy 変更
- automatic suppression / approval / mutation の導入
- user agency に影響する runtime behavior 変更

### 14.4 Past preference boundary

過去の preference や backlog item は context ではあるが、今回の high-risk change approval を代替しない。

---

## 15. One-off / Repeated Issue / Regression / Structural Gap の扱い

この4類型は、恒久化の強さを区別するために重要である。

### 15.1 One-off

原則:

- まず rule を増やさない
- 再発観測を優先する
- inventory は軽く保つ

### 15.2 Repeated issue

原則:

- evidence を束ねる
- 既存 rule の不足か、適用ミスかを分ける
- ただし自動 task 化しない

### 15.3 Regression

原則:

- いつから悪化したかを見る
- 変更点との接続を優先して調べる
- small rollback / narrow fix が候補になりやすい

### 15.4 Structural gap

原則:

- docs / framework / role separation を見直す
- 影響範囲が大きいので review を厚くする
- implementation より先に boundary clarification が必要なことが多い

### 15.5 Escalation heuristic

次の順で escalation を強めてよい:

1. one-off
2. repeated issue
3. regression
4. structural gap

ただし、これは review priority の参考であり、authorization ではない。

---

## 16. Rule Bloat Prevention

Improvement Backlog は、改善候補の在庫である一方、rule bloat の温床にもなりうる。
そのため、v1 では明示的な予防線が必要である。

### 16.1 Default stance

新しい rule を足す前に、まず次を確認する:

- 既存 rule の表現が曖昧なだけではないか
- 既存 rule の運用が守られていないだけではないか
- one-off を過大評価していないか
- review/reporting の質で解決できないか
- local prompt wording の微修正で足りないか

### 16.2 Rule creation threshold

恒久 rule 候補に上げるには、少なくとも次のいずれかが欲しい:

- repeated issue with meaningful impact
- clear regression with known cause class
- structural gap affecting multiple tasks
- safety / approval boundary ambiguity with real incidents

### 16.3 Anti-patterns

- 問題が1回起きるたびに新 rule
- long tail の例外を全部 rule 化
- backlog item を rules backlog に変質させる
- user の瞬間的 frustration を永続 policy に変換する

---

## 17. Dangerous Examples

Improvement Backlog の誤用例を明示する。

### Example 1: finding → task → dispatch の短絡

- Quality finding が出る
- backlog に自動登録
- worker が自動起動
- 実装修正が始まる

これは v1 の設計意図に反する。

### Example 2: repeated issue を approval と誤認

「同じ問題が何度か起きているから、もう勝手に直してよい」とみなすのは危険である。

### Example 3: one-off から恒久 rule を増やす

一度だけの気まずい出力を見て、新しい Constitution や suppression rule を追加すると、rule bloat を招く。

### Example 4: current instruction override

過去 backlog に「report は短く」とあるからといって、今回の user が詳細 report を求めている場面で短縮を優先してはいけない。

### Example 5: backlog item を blame record にする

誰が悪かったかの記録ばかり増え、改善仮説や evidence 整理がない backlog は機能しない。

### Example 6: weak evidence candidate proliferation

evidence が薄い candidate を大量に積むと、本当に重要な改善が埋もれる。

---

## 18. Quality Framework へ渡す評価観点

Improvement Backlog は、Quality Framework に対して「どの観点で観測を厚くすると backlog の質が上がるか」を返せる。

### 18.1 Useful evaluation lenses

- 問題は repeated か one-off か
- instruction compliance failure か
- scope control failure か
- evidence handling failure か
- reporting burden issue か
- approval boundary confusion か
- worker-role confusion か
- current user instruction override risk か

### 18.2 Desired quality metadata

Quality finding には、可能なら次があると backlog 化しやすい:

- frequency hint
- impact note
- affected layer
- confidence / uncertainty note
- candidate class suggestion
- repeatability clue

### 18.3 Important boundary

Quality 側の metadata が豊富でも、それは backlog mutation の自動許可ではない。

---

## 19. Continuous Evolution へ渡す論点

Improvement Backlog は、Continuous Evolution に対して「この候補を review するなら何を考えるべきか」を渡す。

### 19.1 Key discussion points

- これは one-off か recurring か
- 既存 rule の改善で足りるか
- 新 rule 追加が本当に必要か
- prompt / workflow / docs / review のどこを触るべきか
- risk はどのくらいか
- approval は誰から何を得るべきか
- smallest safe change は何か
- verification は何を見ればよいか

### 19.2 Escalation questions

- user agency に触れるか
- runtime behavior を変えるか
- Memory / Human Model / Constitution / Gate に波及するか
- worker dispatch policy に触れるか
- user の current instruction と衝突しないか

### 19.3 Output expectation

Continuous Evolution へ渡す時点で、backlog item は少なくとも次を含むべきである:

- why this matters
- why this is not auto-approved
- what remains unknown
- what level of review is required

---

## 20. Open Questions

v1 時点で未確定の論点を残しておく。

### 20.1 Backlog storage model

Improvement Backlog をどこに保持するか。

- docs-based inventory
- kanban-linked artifact
- structured local DB
- hybrid model

### 20.2 Candidate deduplication policy

類似 candidate をどう束ねるか。
どの粒度で「同じ問題」とみなすかは要検討である。

### 20.3 Ownership model

誰が candidate の triage owner になるか。
Planner / Reviewer / human のどこまでを正式責務にするかは未確定である。

### 20.4 Metric thresholds

何回起きたら repeated と言えるか。
頻度閾値を固定するか、impact-weighted にするかは未確定である。

### 20.5 Approval granularity

backlog item 作成、再分類、implementation split の各段階で approval をどこまで分けるかは要設計である。

### 20.6 Relationship to long-term governance

Improvement Backlog を Constitution 改善候補の inventory にまで広げるか、別 inventory を持つかは未確定である。

---

## 21. Next Recommended Task

次に作る補助文書としては、`docs/product/weekly-quality-report-v1.md` が有力である。

理由:

- Quality Framework が何を観測するかは定義された
- Continuous Evolution が改善ライフサイクルを定義した
- Improvement Backlog が候補在庫を定義した
- 次は、それらを user-facing / review-facing にどう定期報告するかの report artifact を定義すると接続が閉じやすい

その文書で扱うとよい論点:

- Weekly Quality Report の purpose / scope
- Judge / Metrics / Summary の表示分離
- report が approval を代行しないこと
- recurring issue の見せ方
- backlog candidate への橋渡し方法
- user burden を増やさない report compactness

---

## Appendix A. Compact Mental Model

Improvement Backlog を一文で言うと:

> It remembers improvement candidates without granting the right to execute them.

短く言い換えると:

- Quality finds
- Backlog stores
- Planning checks
- Human approves
- Execution implements
- Verification confirms

この順序が崩れると、inventory が governance を乗っ取りやすくなる。

---

## Appendix B. Minimal Decision Table

| Situation | Backlog candidate? | Auto task? | Auto implementation? |
|---|---:|---:|---:|
| One-off typo | Usually no | No | No |
| Repeated reporting drift | Maybe yes | No | No |
| Clear regression | Often yes | No | No |
| Structural approval confusion | Yes | No | No |
| High-risk rule change idea | Maybe yes | No | No |
| User explicitly forbids change now | Maybe record later, but do not act now | No | No |

---

## Appendix C. Final Reminders

- backlog is not approval
- candidate is not command
- recurrence is not authorization
- history is not current consent
- classification is not implementation
- inventory is not governance
- user agency remains first
