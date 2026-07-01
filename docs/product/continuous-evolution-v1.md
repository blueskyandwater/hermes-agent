# Continuous Evolution v1 Draft

## 1. Purpose

Continuous Evolution は、Hermes を**観測された事実にもとづいて小さく改善していくための review-centered framework** である。

この文書の目的は、Hermes における改善の流れを、**勝手な自己改変**ではなく、**観測 → 改善候補 → 人間レビュー → 承認 → 小さな実装 → 検証**として定義することにある。

特に重要なのは、Continuous Evolution が次のものではないと明確にすることだ。

- 自律的な自己改変 engine
- score や backlog を authorization とみなす仕組み
- 既存 rule を自動書き換えする governance loop
- user approval を過去文脈で代用する shortcut

Continuous Evolution が目指すもの:

- Quality finding を改善の材料として扱う
- 改善候補を inventory 化するが、勝手に実行しない
- 高リスク変更ほど review と approval を強く要求する
- 小さく実装し、小さく検証する
- 改善の traceability を保つ
- user agency を壊さない

中心原則:

> Continuous Evolution improves Hermes through reviewed refinement, not autonomous mutation.

補足原則:

- Quality finding is evidence, not permission
- Improvement candidate is not authorization
- Improvement Backlog is inventory, not authorization
- Past preference is context, not current approval
- No automatic Constitution changes
- No automatic Gate rule changes
- No automatic Memory / Human Model mutation
- No automatic worker dispatch
- Human review and explicit approval are required for high-risk changes

この文書は:

- runtime 実装を追加しない
- approval engine を新設しない
- auto-refactor loop を導入しない
- worker の自律 dispatch を許可しない
- Constitution / Gate / Memory / Human Model の自動 mutation を許可しない

---

## 2. Scope

Continuous Evolution v1 が扱う対象:

- 改善候補の生成と分類
- 改善ライフサイクルの定義
- approval 境界
- backlog との接続
- rule change の禁止境界
- Quality Framework との関係
- Weekly Quality Report との関係
- CI observer / Worker Architecture / Memory System との関係
- 改善時の bounded execution 原則

Continuous Evolution v1 が直接扱わない対象:

- 自動コード修正の本実装
- 自動承認ロジック
- 自動 Constitution 更新
- 自動 Gate 更新
- 自動 Memory / Human Model 更新
- user value の自動再解釈
- permanent policy engine の runtime wiring
- repo-wide autonomous refactoring

---

## 3. Non-goals

### Non-goal 1: 自動自己改変

Continuous Evolution は、Hermes が Quality score や backlog item を見て勝手に自分を書き換える仕組みではない。

### Non-goal 2: approval の代替

改善候補が backlog に存在していても、それだけで approval にはならない。

### Non-goal 3: 過去文脈による現在承認の代用

過去の会話、memory、過去の嗜好、以前の成功事例は改善判断の context にはなるが、今回の変更承認の代わりにはならない。

### Non-goal 4: rule inflation

品質問題が見つかるたびに新しい rule を足し続けることは Continuous Evolution の目的ではない。まずは既存 rule の改善・明確化・適用ミスの是正を優先する。

### Non-goal 5: worker の自律統治

worker や cron が improvement を検知しても、それだけで自動 dispatch・自動修正・自動追記をしてはならない。

### Non-goal 6: blame mechanism

改善フレームワークは、失敗の責任追及よりも、再発防止と運用品質の改善を目的とする。

---

## 4. Improvement Lifecycle

Continuous Evolution v1 では、改善を次の順序で扱う。

1. observe
2. detect
3. formulate
4. review
5. approve
6. implement
7. verify
8. record
9. re-observe

### 4.1 Observe

観測ソースの例:

- Quality Framework の score / verdict / finding
- Weekly Quality Report
- CI observer の失敗・傾向
- 実行ログ
- user feedback
- 明示的な postmortem
- read-only repo / doc review

Observe の責務:

- 事実を集める
- 症状を記録する
- 再現条件を見つける
- 頻度・影響範囲・危険度を整理する

Observe がしてはいけないこと:

- その場で勝手に修正すること
- 影響の大きい解釈を authorization に変えること

### 4.2 Detect

観測された事実の中から、改善候補になりうるパターンを抽出する。

例:

- no-push mode なのに push 提案が混じる
- read-only review なのに mutation 提案が出る
- Quality report が user を暗黙に採点してしまう
- backlog item の存在を approval と誤解する
- Memory を authorization として扱う表現が出る

### 4.3 Formulate

改善候補を、実装案ではなく**改善仮説**として記述する。

改善仮説の最小要素:

- observed issue
- why it matters
- likely boundary violated
- possible fix direction
- risk level
- approval level needed

### 4.4 Review

review では次を確認する:

- これは本当に改善すべき問題か
- 問題は再現性があるか
- 症状ではなく原因に近いか
- 既存 rule の誤適用なのか、rule 不足なのか
- 実装せず wording 調整で足りるか
- high-risk 変更か low-risk 変更か

### 4.5 Approve

Approve は improvement candidate を action に変える唯一の入口である。

Approve に必要なもの:

- human review
- explicit approval
- scope の明示
- allowed surface の明示
- no-touch area の明示

### 4.6 Implement

Implement は bounded execution で行う。

原則:

- 小さい変更から始める
- 1回の変更対象を狭くする
- docs-only / read-only / no-commit など mode を守る
- unrelated files を触らない
- approval を超える side effect を出さない

### 4.7 Verify

Verify では少なくとも次を確認する:

- 変更が scope 内に収まっているか
- 意図した問題が改善されたか
- 新しい危険な coupling を作っていないか
- no-touch area を破っていないか
- report と tool output が一致しているか

### 4.8 Record

Record は「実装した」ことを権威化するためではなく、次回 review の追跡性を残すために行う。

記録対象の例:

- 何を観測したか
- 何を変更対象としたか
- 何が approval されたか
- 何を intentionally not changed としたか
- 何を検証したか
- 何が unresolved か

### 4.9 Re-observe

改善は1回で終わりではなく、再観測に戻る。

重要なのは:

- 変更したから改善したとは限らない
- 改善したつもりでも副作用があるかもしれない
- ルールを増やした結果、認知負荷が上がる場合がある

---

## 5. Candidate Model

Continuous Evolution における improvement candidate は、**可能な改善の記録単位**であり、承認単位ではない。

### 5.1 Candidate fields

最低限持つべき項目の例:

- title
- observed evidence
- source
- problem statement
- affected boundary
- affected layer
- risk level
- urgency
- reversibility
- recommended next action
- approval needed
- status

### 5.2 Candidate statuses

v1 では概念的に次の状態を想定する。

- observed
- clarified
- proposed
- awaiting review
- approved
- rejected
- implemented
- verified
- archived

### 5.3 Candidate interpretation rules

- candidate は issue の inventory であって命令ではない
- candidate が存在しても worker は動かない
- candidate が high priority でも approval は別に必要
- candidate は evidence quality に依存する
- weak evidence の candidate は review で止めてよい

### 5.4 Candidate types

改善候補は一枚岩ではなく、種類を分けて考える。

- documentation clarification
- reporting improvement
- evaluation rubric fix
- boundary wording correction
- test / verification gap reduction
- workflow safeguard enhancement
- runtime bug fix
- model routing / instruction framing refinement
- dangerous behavior suppression candidate

v1 では、type によって approval の重さが変わる。

---

## 6. Approval Model

Continuous Evolution では、approval が improvement candidate を実行可能な変更に変える。

### 6.1 Core rule

改善候補の existence は approval ではない。

### 6.2 Approval inputs

Approve の判断材料には次がある。

- observed evidence
- risk level
- impact surface
- reversibility
- touched artifacts
- user current instruction
- current mode
- whether external side effects exist

### 6.3 Approval classes

#### Class A: low-risk wording / docs-only

例:

- docs wording clarification
- review report phrasing correction
- explicit boundary note の追記

必要条件:

- scope が明確
- side effect が doc に限定
- user が明示的に依頼
- forbidden area を触らない

#### Class B: medium-risk operational logic

例:

- quality scoring rubric の実装変更
- report schema の変更
- worker guardrail 文言の runtime prompt 変更

必要条件:

- user の明示 approval
- changed surface の明示
- verification plan
- rollback 可能性

#### Class C: high-risk governance / authority surfaces

例:

- Constitution 変更
- Gate rule 変更
- Memory / Human Model 自動 mutation
- worker の自動 dispatch 追加
- auto-approve / auto-suppress behavior 導入

必要条件:

- 明示的な human review
- 明示的な user approval
- high-risk としての扱い
- 影響範囲と failure mode の説明
- 小さな段階的導入
- 検証計画

### 6.4 What cannot approve

以下は approval の代わりにならない:

- Quality score
- Quality verdict
- past user preference
- Improvement Backlog item
- Memory entry
- Human Model trait
- prior success
- cron detection
- worker recommendation

### 6.5 Current user instruction wins

approval 解釈で最優先なのは current user instruction である。

たとえば:

- 過去には commit を許可していても、今回が `docs-only-no-commit` なら commit しない
- 過去に runtime changes を歓迎していても、今回が docs-only なら docs 以外を変えない

---

## 7. Backlog Integration

Continuous Evolution は Improvement Backlog とつながるが、backlog を authorization とみなしてはならない。

### 7.1 Backlog role

Improvement Backlog の役割:

- 改善候補の inventory を保持する
- 優先度の議論をしやすくする
- 類似課題の再発を見える化する
- review 待ち / approval 待ちの場所を作る

### 7.2 Backlog limits

Backlog は次のことをしてはいけない。

- approval を代行する
- worker へ自動 dispatch する
- current instruction を上書きする
- risk を過小評価する
- stale candidate を current intent 扱いする

### 7.3 Backlog item interpretation

Backlog item が意味するのは:

- 「改善の候補がある」
- 「検討する価値がある」
- 「観測済みの問題がある」

Backlog item が意味しないのは:

- 「今すぐ変えてよい」
- 「もう承認済みである」
- 「worker が手を付けてよい」
- 「weekly report に載ったので自動実施してよい」

### 7.4 Inventory, not authorization

原則:

> Improvement Backlog is inventory, not authorization.

---

## 8. Rule Change Policy

Continuous Evolution v1 では、rule change を最も慎重に扱う。

### 8.1 Why rule changes are high-risk

rule は一度入ると広範囲に影響しやすい。

- 誤った rule は広く再利用される
- 境界の曖昧な rule は overreach を生む
- rule を増やしすぎると運用が複雑化する
- 例外が増えると Rule of Least Surprise に反する

### 8.2 Rule change ordering

改善時は次の順で検討する。

1. 単なる実行ミスではないか
2. wording の曖昧さではないか
3. verification 不足ではないか
4. docs clarification で十分ではないか
5. 既存 rule の修正で足りるか
6. それでも足りないときだけ新 rule を検討する

### 8.3 Prohibited automatic rule changes

以下は自動変更してはならない。

- Constitution changes
- Gate rule changes
- approval routing changes
- authorization policy changes
- memory access policy changes
- worker ownership changes

### 8.4 Human review threshold

rule change は low-risk doc wording であっても、境界定義に関わるなら human review を通すべきである。

---

## 9. Memory / Human Model / Worker / Quality Change Boundaries

Continuous Evolution は複数の framework に接続するが、それぞれの mutation 境界を越えてはならない。

### 9.1 Memory boundary

- Memory は context であり authorization ではない
- memory に過去の preference があっても current approval の代わりにはならない
- memory inconsistency を見つけても自動で修正しない
- memory cleanup candidate は separate review topic として扱う

### 9.2 Human Model boundary

- Human Model は user support の補助であり、identity の決定権を持たない
- Human Model trait から改善許可を推論しない
- user の stable preference と current instruction を混同しない
- Human Model mutation は自動で行わない

### 9.3 Worker boundary

- worker は bounded executor であり、自分で改善を承認しない
- worker は candidate を見ても勝手に dispatch / mutate しない
- worker architecture の変更は high-risk とみなす
- worker が reviewer 的 finding を持っても、silent fix はしない

### 9.4 Quality boundary

- Quality finding は evidence であり permission ではない
- Quality score は governance signal ではない
- low score を理由に自動 suppression を入れない
- high score を理由に自動 approval を与えない

### 9.5 Cross-boundary caution

複数 framework にまたがる変更は、単一doc修正より high-risk である。

例:

- quality rubric を変えた結果、weekly report の判断基準まで変わる
- worker boundary を変えた結果、dispatch policy の解釈まで変わる
- memory wording を変えた結果、authorization の誤読が増える

---

## 10. Relationship with Quality Framework

Quality Framework と Continuous Evolution は近いが同一ではない。

### 10.1 Quality Framework role

Quality Framework は:

- 観測する
- 採点する
- verdict を出す
- report する

### 10.2 Continuous Evolution role

Continuous Evolution は:

- quality finding を改善候補に変換する
- candidate を review 可能にする
- approval 境界を管理する
- reviewed refinement として実装・検証へつなぐ

### 10.3 Separation rule

- Quality は改善を承認しない
- Continuous Evolution は score を truth とみなさない
- Quality score は一つの signal にすぎない
- 改善判断は evidence set 全体で行う

### 10.4 Evidence flow

概念的な流れ:

Quality finding -> improvement candidate -> human review -> explicit approval -> bounded implementation -> verification -> re-observation

---

## 11. Relationship with Improvement Backlog

Improvement Backlog は Continuous Evolution の inventory layer である。

### 11.1 Backlog as queue, not governor

backlog は候補を保持するが、実施可否は決めない。

### 11.2 Expected flow

- candidate is added to backlog
- backlog item is reviewed
- approved item becomes scoped work
- scoped work is implemented under explicit mode
- verification is attached back to the item or follow-up report

### 11.3 Priority is not approval

priority が高いことは「先に見る価値がある」ことを意味するだけで、「今すぐ変更してよい」ことは意味しない。

---

## 12. Relationship with Weekly Quality Report

Weekly Quality Report は Continuous Evolution にとって重要な input だが、governance actor ではない。

### 12.1 Weekly report role

- recurring patterns を見つける
- regressions を見える化する
- stable improvement opportunities を示す
- high-noise issues と high-impact issues を分ける

### 12.2 Weekly report limits

weekly report は:

- approval を出さない
- auto-dispatch をしない
- rule を書き換えない
- memory / human model を更新しない
- worker へ無言の命令を出さない

### 12.3 Report to candidate flow

weekly report に載った finding は candidate になりうるが、必ず review を経由する。

### 12.4 Avoiding report tyranny

report が強くなりすぎると、「良い score を取るための行動」が「user に役立つ行動」より優先される危険がある。

Continuous Evolution はこの逆転を避ける必要がある。

---

## 13. Relationship with CI Observer / Worker Architecture / Memory System

Continuous Evolution は複数の補助システムから signal を受け取るが、どれも authorization source ではない。

### 13.1 CI observer

CI observer は:

- failure / flakiness / regression signal を出す
- 実装品質の一部を観測する
- docs-only なのか runtime issue なのかの切り分け材料になる

CI observer がしてはいけないこと:

- approval を出すこと
- worker を勝手に dispatch すること
- no-fix mode で自動修正すること

### 13.2 Worker Architecture

Worker Architecture は実行構造を定義する。

Continuous Evolution との関係:

- worker は bounded executor として改善作業を実施しうる
- ただし dispatch・approval・ownership は worker の外側で制御される
- worker は candidate の所有者ではない
- worker は自分の役割境界を超えて governance actor になってはならない

### 13.3 Memory System

Memory System は:

- 継続的な context を提供する
- 過去の preference / conventions / environment facts を保持する

Memory System がしてはいけないこと:

- 改善の approval source になること
- stale preference で current instruction を上書きすること
- mutation の自動正当化に使われること

### 13.4 Signal hierarchy

扱いの優先順は概念的にこう考える。

1. current user instruction
2. explicit approval scope
3. observed evidence
4. stable framework boundaries
5. historical context from memory

この順序を崩すと、Continuous Evolution は user agency を壊しやすい。

---

## 14. Risks

### 14.1 Autonomous mutation drift

改善の名目で自動自己改変へ滑る危険。

### 14.2 Approval laundering

backlog / report / memory / score を approval の代用品として使ってしまう危険。

### 14.3 Rule inflation

失敗のたびに新ルールを足し、複雑性だけが増える危険。

### 14.4 Governance confusion

Quality, Guard, Reviewer, Worker, Cron の責務が混ざり、誰が何を決めるかが不明瞭になる危険。

### 14.5 Silent coupling

quality rubric の変更が weekly report や worker dispatch の解釈まで静かに変えてしまう危険。

### 14.6 Stale-context override

過去 preference や memory が current instruction を押しのける危険。

### 14.7 Improvement theater

改善候補や report だけ増え、実際の改善や検証が進まない危険。

### 14.8 Goodhart-like pressure

score 改善が user value より優先される危険。

### 14.9 Over-centralization

一つの quality / evolution layer に過剰な統治権限が集まる危険。

---

## 15. Dangerous Examples

### 15.1 Dangerous example: high score means auto-approve

誤り:

- Quality score が高い
- だから今回の変更は安全
- だから approval なしで worker が実装してよい

なぜ危険か:

- score は evidence の一部でしかない
- current scope を無視している
- governance shortcut になっている

### 15.2 Dangerous example: backlog item means permission

誤り:

- backlog に「Guard を厳しくする」がある
- だから今回の会話で自動的に Gate 文言を変える

なぜ危険か:

- backlog は inventory でしかない
- 現在の指示と approval が欠けている

### 15.3 Dangerous example: memory says the user likes automation

誤り:

- memory に automation preference がある
- だから Human Model や Memory を今回自動更新してよい

なぜ危険か:

- past preference を current approval にすり替えている
- mutation boundary を越えている

### 15.4 Dangerous example: weekly report should fix this silently

誤り:

- 毎週同じ品質問題が出ている
- だから cron で silent patch を入れる

なぜ危険か:

- cron observes and reports; it must not silently govern
- review と approval を飛ばしている

### 15.5 Dangerous example: reviewer can just clean it up

誤り:

- Reviewer が最後に見つけたので、その場で黙って修正しておく

なぜ危険か:

- Reviewer reviews; it does not silently fix
- role boundary が壊れる

### 15.6 Dangerous example: rule fix by reflex

誤り:

- 1回失敗した
- だから新しい Constitution rule を追加する

なぜ危険か:

- 単なる実行ミスや wording 問題かもしれない
- rule inflation につながる

---

## 16. Implementation Candidates

Continuous Evolution v1 は design-first として扱い、実装候補は段階的に考える。

### 16.1 Candidate A: improvement candidate template

目的:

- candidate の書式を揃える
- observed issue / evidence / risk / approval needed を明確にする

低リスク。docs-first で導入しやすい。

### 16.2 Candidate B: weekly report to backlog handoff note

目的:

- weekly report finding を improvement candidate に変換する境界を明文化する
- report != authorization を固定する

### 16.3 Candidate C: high-risk change checklist

目的:

- Constitution / Gate / Memory / Human Model / Worker mutation の review 要件を固定する

### 16.4 Candidate D: candidate triage rubric

目的:

- docs clarification で足りるか
- wording drift なのか
- runtime fix が必要か
- rule change が本当に必要か

を整理する。

### 16.5 Candidate E: verification note format

目的:

- implement 後の確認項目を揃える
- 「何を変えていないか」を明示する

### 16.6 Candidate F: improvement backlog schema draft

目的:

- inventory fields を最小構成で決める
- authorization と混同しないよう status / approval fields を分ける

### 16.7 Candidate G: reviewed refinement operating note

目的:

- 観測から検証までの短い運用手順を定義する
- autonomous mutation ではないことをチーム内で再確認しやすくする

---

## 17. Open Questions

### 17.1 Candidate freshness

古い candidate をいつ stale とみなすか。

### 17.2 Evidence threshold

どの程度の再現性・頻度・影響があれば candidate 化すべきか。

### 17.3 Approval granularity

どこまでを low-risk docs clarification とし、どこからを governance-affecting change とみなすか。

### 17.4 Cross-framework changes

Quality / Worker / Memory / Human Model をまたぐ変更を、どう小さく分割して review するか。

### 17.5 Backlog ownership

Improvement Backlog を誰が maintainer として整理するのか。maintain はできても approve はできない設計をどう保つか。

### 17.6 Weekly review cadence

weekly report finding を毎回 candidate 化するのか、それとも recurring / high-impact に絞るのか。

### 17.7 Verification persistence

実施後の verification をどこに保存すると、rule inflation を招かずに traceability を保てるか。

### 17.8 Negative results

「変更しない方がよい」と判定した改善候補をどう記録し、再発見時の再議論コストを下げるか。

---

## 18. Next Recommended Task

次に作ると接続が明確になる文書候補は、**Improvement Backlog v1 Draft** である。

理由:

- Continuous Evolution は backlog integration を前提にしている
- しかし backlog は inventory であって authorization ではないという境界を、単独文書で固定した方が誤解が少ない
- Weekly Quality Report / Quality Framework / Worker Architecture との handoff も書きやすくなる

推奨タイトル:

- `docs/product/improvement-backlog-v1.md`

推奨内容:

- purpose
- item schema
- status model
- priority vs approval separation
- candidate intake rules
- review queue rules
- stale item policy
- relationship with Continuous Evolution / Quality Framework / Weekly Quality Report
- dangerous examples
- open questions

---

## Appendix A. Core Boundary Summary

短く言い直すと、Continuous Evolution v1 の境界は次の通りである。

- improves through reviewed refinement, not autonomous mutation
- uses findings as evidence, not permission
- treats backlog as inventory, not authorization
- respects current user instruction over past context
- requires human review for high-risk changes
- forbids automatic Constitution / Gate / Memory / Human Model mutation
- keeps worker execution bounded and non-owning
- returns to verification and re-observation after every approved change

## Appendix B. One-line Test

この文書の健全性を一行で試すなら次の問いになる。

> "この改善は、観測された問題をもとに、人間が scope を明示して承認し、小さく実装して検証する流れになっているか？"

Yes なら v1 の方向に近い。No なら autonomous mutation や approval laundering に寄っている可能性が高い。
