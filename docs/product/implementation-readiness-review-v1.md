# Implementation Readiness Review v1 Draft

## 1. Purpose

Implementation Readiness Review は、Hermes で実装に入る前に確認すべき読み順・境界・許可条件・未解決リスクを整理するための **pre-implementation review artifact** である。

この文書の目的は、実装前に次の問いへ答えられる状態を作ることにある。

- どの Foundation docs を読んだか
- どの境界を越えてはいけないか
- 現在のユーザー指示は何を許可しているか
- どの操作が high-risk か
- どの未解決リスクが残っているか
- 実装に入る前に追加確認が必要か
- 実装後に何をもって Done とするか

中心原則:

> Implementation readiness is review, not authorization.

Implementation Readiness Review は、実装してよいかを整理するレビューであり、それ自体は実装許可ではない。

補助原則:

- Ready does not mean push-approved
- Backlog is inventory, not authorization
- Roadmap defines sequence, not permission
- Planning Gate prevents premature action
- Current user instruction wins
- High-risk actions require current explicit approval
- Read-only before mutation
- Docs-first before runtime governance
- Quality finding is evidence, not permission
- Improvement candidate is not authorization

この文書は、Hermes Foundation 文書群を実装作業へ接続するための実務チェックリストである。

---

## 2. Scope

Implementation Readiness Review v1 が扱う対象:

- 実装前に読むべき Foundation docs
- 実装前に確認すべき境界
- Planning Gate の確認項目
- Memory / Human Model / Decision Profile / Domain Model の確認項目
- Worker Architecture の確認項目
- Quality Framework の確認項目
- Continuous Evolution / Improvement Backlog の確認項目
- Git / CI / push readiness の確認項目
- implementation mode の確認項目
- Definition of Ready の確認
- Definition of Done の確認
- high-risk operation の確認
- no-go conditions
- readiness verdict model
- dangerous examples
- open questions
- next recommended task

Implementation Readiness Review v1 が直接扱わない対象:

- 実装そのもの
- runtime code 変更
- Kanban mutation
- worker dispatch
- Memory mutation
- Human Model mutation
- Decision Profile mutation
- Constitution / Gate rule mutation
- Quality suppress behavior
- CI rerun
- push / PR / merge
- cron 化
- platform 配送

---

## 3. Non-goals

Implementation Readiness Review v1 は、次のものではない。

- 実装許可書
- push 承認
- PR 承認
- merge 承認
- Kanban task 作成指示
- Kanban task 完了指示
- worker dispatch 指示
- Memory / Human Model / Decision Profile 更新指示
- Constitution / Gate rule 更新指示
- CI rerun 指示
- runtime governance 導入指示
- 自動改善エンジン
- 品質違反の自動抑制機構
- backlog item の自動採用機構

特に重要な非目的:

> A readiness review may conclude that work is ready to discuss or ready to plan, but it does not create operational permission.

---

## 4. Readiness Review Boundaries

Readiness Review の責務は **判断材料の整理** であり、実行権限の付与ではない。

| Area | Readiness Review may do | Readiness Review must not do |
| --- | --- | --- |
| Scope | 実装対象を明確化する | scope を勝手に拡張する |
| Docs | 参照すべき文書を列挙する | docs を実装許可として扱う |
| Risks | 未解決リスクを記録する | リスクを無視して実装へ進む |
| Gate | Planning Gate 確認を促す | Gate を bypass する |
| Memory | mutation 前の確認項目を示す | Memory を更新する |
| Worker | dispatch 前の確認項目を示す | worker を起動する |
| Quality | quality evidence を確認する | Quality finding を権限化する |
| Git | status / diff / CI 確認を促す | add / commit / push を実行する |

Boundary statement:

> Readiness Review can say “this appears ready for explicit approval.” It must not say “therefore execute now.”

---

## 5. Docs Reading Checklist

実装前に、少なくとも次の文書を目的別に読む。

### 5.1 Foundation orientation

- [ ] `docs/product/hermes-foundation-v1.md`
- [ ] `docs/product/foundation-pillar-map-v1.md`

確認すること:

- Foundation 全体の目的
- guide と authorization の違い
- document dependencies
- 実装前に読む順番

### 5.2 Gate and execution boundary

- [ ] `docs/product/planning-gate-policy-v1.md`
- [ ] `docs/product/worker-architecture-v1.md`

確認すること:

- Planning Gate の役割
- 実行前に必要な explicit approval
- worker boundaries
- dispatcher / worker / human の責務境界

### 5.3 Context and decision support

- [ ] `docs/product/memory-system-v1.md`
- [ ] `docs/product/human-model-v1.md`
- [ ] `docs/product/decision-support-v1.md`
- [ ] `docs/product/domain-model-v1.md`
- [ ] `docs/product/decision-profile-v1.md`

確認すること:

- context は authorization ではない
- user model は user を定義しない
- decision support は final decision を奪わない
- domain model は evidence を足すだけ
- decision profile は soft guide であり hard policy ではない

### 5.4 Quality and evolution

- [ ] `docs/product/quality-framework-v1.md`
- [ ] `docs/product/continuous-evolution-v1.md`
- [ ] `docs/product/improvement-backlog-v1.md`
- [ ] `docs/product/weekly-quality-report-v1.md`

確認すること:

- Quality Framework は behavior を評価する
- Continuous Evolution は reviewed refinement を提案する
- Improvement Backlog は inventory であり authorization ではない
- Weekly Quality Report は observe and report に留まる

---

## 6. Foundation Principles Checklist

実装前に、次の Foundation principles を満たしているか確認する。

- [ ] Current user instruction wins
- [ ] Foundation docs guide; they do not authorize execution
- [ ] Roadmap defines sequence, not permission
- [ ] Planning Gate prevents premature action
- [ ] Memory is context, not authorization
- [ ] Human Model supports the user, not defines the user
- [ ] Decision Profile is soft guide, not policy
- [ ] Domain Model adds evidence, not orders
- [ ] Worker Architecture defines boundaries
- [ ] Quality Framework evaluates behavior, not the user
- [ ] Continuous Evolution proposes reviewed refinement, not autonomous mutation
- [ ] Improvement Backlog is inventory, not authorization
- [ ] Weekly Quality Report observes and reports; it does not govern
- [ ] Read-only before mutation
- [ ] High-risk actions require current explicit approval
- [ ] Docs-first before runtime governance

If any principle conflicts with the proposed implementation, stop and ask for explicit clarification.

---

## 7. Planning Gate Checklist

Planning Gate は、実装が早すぎる状態を防ぐための boundary layer である。

実装前チェック:

- [ ] Current user instruction が実装を明示している
- [ ] mode が明確である
- [ ] allowed actions が明確である
- [ ] forbidden actions が明確である
- [ ] target repo / path / branch が明確である
- [ ] scope creep がない
- [ ] high-risk actions が含まれるか確認済み
- [ ] high-risk actions には current explicit approval がある
- [ ] read-only 確認が必要なものは実施済み
- [ ] mutation 対象が明確である
- [ ] rollback / verification strategy がある
- [ ] DoR / DoD が定義されている

Planning Gate が止めるべき例:

- “Quality issue があるから自動で rule を追加する”
- “Backlog にあるから実装する”
- “Foundation に書いてあるから worker を起動する”
- “レビューで ready と出たから push する”
- “Memory がそう言っているから user approval 扱いにする”

---

## 8. Memory / Human Model / Decision Profile / Domain Model Checklist

### 8.1 Memory System

Memory を使う前に確認すること:

- [ ] Memory は context として使っている
- [ ] Memory を authorization として使っていない
- [ ] stale / uncertain な可能性を考慮した
- [ ] current user instruction と矛盾する Memory を優先していない
- [ ] Memory mutation が必要な場合、現在の明示許可がある

禁止:

- Memory にある過去方針を現在の実行許可へ変換する
- 一時的な task progress を Memory へ保存する
- user の明示なしに Human Model / Decision Profile を書き換える

### 8.2 Human Model

Human Model を参照する前に確認すること:

- [ ] user support のために使っている
- [ ] user を固定的に定義していない
- [ ] user preference を current instruction より優先していない
- [ ] inferred trait を hard rule にしていない
- [ ] mutation には明示許可がある

### 8.3 Decision Profile

Decision Profile を参照する前に確認すること:

- [ ] soft guide として扱っている
- [ ] policy / command / authorization として扱っていない
- [ ] final decision は user に残している
- [ ] high-risk action の承認に使っていない
- [ ] mutation には明示許可がある

### 8.4 Domain Model

Domain Model を参照する前に確認すること:

- [ ] evidence / domain context として使っている
- [ ] execution order として扱っていない
- [ ] decision を自動化していない
- [ ] unknown / uncertainty を明示している
- [ ] domain facts と user preference を混同していない

---

## 9. Worker Architecture Checklist

Worker Architecture は、worker の責務境界と dispatch 条件を定義する。

実装前チェック:

- [ ] worker が必要か確認した
- [ ] single-agent で足りるなら worker を起動しない
- [ ] worker 起動に current explicit approval がある
- [ ] worker に渡す scope が限定されている
- [ ] worker に forbidden actions を明記できる
- [ ] worker output の verification 方法がある
- [ ] worker が Kanban mutation してよいか明確である
- [ ] worker failure 時の扱いが明確である
- [ ] worker が memory / profile / runtime config を勝手に変更しない

Worker dispatch no-go:

- user が docs-only-no-commit と言っている
- read-only review が指定されている
- worker 起動禁止が明示されている
- task が小さく、直接処理で十分
- worker に渡す境界が曖昧
- verification 不能な外部副作用がある

---

## 10. Quality Framework Checklist

Quality Framework は Hermes の行動品質を評価するための framework であり、user を評価しない。

実装前チェック:

- [ ] Quality finding は evidence として扱っている
- [ ] Quality finding を permission として扱っていない
- [ ] score / issue / regression candidate を自動 mutation に変換していない
- [ ] Quality suppress behavior を導入していない
- [ ] Quality improvement が必要なら review path を通す
- [ ] current user instruction と衝突していない
- [ ] Quality Framework を runtime governance として勝手に接続していない

Quality no-go:

- 低スコアを理由に Constitution を自動変更する
- repeated issue を理由に Memory を自動変更する
- report の recommendation を task creation に変換する
- Quality finding を user approval 扱いにする

---

## 11. Continuous Evolution / Improvement Backlog Checklist

### 11.1 Continuous Evolution

Continuous Evolution は、改善候補を reviewed refinement として扱う。

チェック項目:

- [ ] improvement candidate は candidate のまま扱っている
- [ ] reviewed refinement と autonomous mutation を区別している
- [ ] change proposal と adopted change を区別している
- [ ] current explicit approval なしに rules / memory / runtime を変更していない
- [ ] metrics regression をもとにする場合も、実行許可とは分けている

### 11.2 Improvement Backlog

Improvement Backlog は inventory であり authorization ではない。

チェック項目:

- [ ] backlog item を存在確認しただけで実装していない
- [ ] priority と permission を混同していない
- [ ] candidate / accepted / scheduled / implemented を混同していない
- [ ] backlog mutation に current explicit approval がある
- [ ] backlog から worker dispatch へ自動接続していない

---

## 12. Git / CI / Push Readiness Checklist

実装前に Git / CI / push 境界を確認する。

### 12.1 Git state

- [ ] target repo が正しい
- [ ] branch が正しい
- [ ] HEAD が期待値と一致している
- [ ] working tree 状態を確認した
- [ ] untracked files を把握した
- [ ] 既存変更と今回変更の境界が明確
- [ ] user が許可した path のみ変更する

推奨 read-only commands:

```bash
git status -sb
git rev-parse --short HEAD
git branch --show-current
git diff -- <path>
git diff --check
```

### 12.2 CI readiness

- [ ] CI を見る必要があるか確認した
- [ ] workflow rerun が禁止されていないか確認した
- [ ] skipped / not applicable を failure と混同しない
- [ ] CI rerun には current explicit approval がある

### 12.3 Push readiness

Push 前には別途 explicit approval が必要。

- [ ] user が push を現在明示許可している
- [ ] target remote / branch が明示されている
- [ ] dry-run が必要なら実施済み
- [ ] push 後 verification が定義されている
- [ ] upstream への push / PR ではない

Readiness Review が ready と言っても、push-approved にはならない。

---

## 13. Implementation Mode Checklist

実装に入る前に mode を明確にする。

代表的な mode:

| Mode | Meaning | Allowed by default | Requires extra approval |
| --- | --- | --- | --- |
| `read-only-review` | 読み取り確認のみ | status / diff / logs | writes / mutation |
| `docs-only-no-commit` | 指定 docs 作成のみ | write specified docs, status, diff | add / commit / push |
| `local-commit-only` | local commit まで | add / commit specified scope | push / PR |
| `push-only` | push verification/execution のみ | status / dry-run / explicit push | file edits / Kanban mutation |
| `implementation-no-push` | 実装と検証まで | code/docs edit, tests | push / PR / deployment |
| `ops-read-only` | 運用確認のみ | logs / status / diagnostics | restart / mutation |

Mode checklist:

- [ ] mode が user message に明記されている
- [ ] mode の allowed actions を理解した
- [ ] mode の forbidden actions を理解した
- [ ] mode と current request が矛盾していない
- [ ] mode が曖昧なら最小安全側で解釈する
- [ ] high-risk action は mode だけで許可された扱いにしない

---

## 14. Definition of Ready Confirmation

Implementation Readiness Review の Definition of Ready は、実装に入るための条件を整理する。

A task is Ready for explicit implementation approval when:

- [ ] target repo / branch / path が明確
- [ ] scope が明確
- [ ] allowed actions が明確
- [ ] forbidden actions が明確
- [ ] required docs を読んだ
- [ ] Planning Gate に抵触していない
- [ ] high-risk actions が特定されている
- [ ] high-risk actions の承認要件が明確
- [ ] input artifacts が存在する
- [ ] expected output が明確
- [ ] verification commands が明確
- [ ] rollback / no-go branch が明確
- [ ] commit / push / PR の扱いが明確

Important:

> Definition of Ready means the task can be considered for execution. It does not execute the task and does not approve push.

---

## 15. Definition of Done Confirmation

Implementation Readiness Review は、実装後に何を確認すべきかも先に定義する。

A task is Done only when the user-approved scope has been completed and verified.

Docs-only DoD example:

- [ ] 指定ファイルが存在する
- [ ] 指定内容が含まれている
- [ ] 既存 docs を変更していない
- [ ] runtime code を変更していない
- [ ] `git status -sb` を確認した
- [ ] `git diff -- <path>` を確認した
- [ ] untracked new file なら `git diff --no-index -- /dev/null <path>` を確認した
- [ ] `git diff --check` を確認した
- [ ] add / commit / push していないことを明示した

Implementation DoD example:

- [ ] code change が指定 scope 内
- [ ] tests / checks が実行済み
- [ ] failures があれば正直に報告
- [ ] no hidden mutation
- [ ] no unauthorized push / PR
- [ ] final report が evidence-based

Done is not:

- file exists only
- agent says complete
- worker says complete without verification
- commit exists but checks failed
- push succeeded without approval

---

## 16. High-risk Operation Checklist

High-risk operations require current explicit approval.

High-risk examples:

- git push
- PR creation
- merge
- release
- deploy
- destructive file deletion
- database mutation
- Kanban mutation
- worker dispatch
- cron creation / update / removal
- service restart
- systemd unit changes
- credential / config mutation
- Memory / Human Model / Decision Profile mutation
- Constitution / Gate rule mutation
- Quality suppress behavior
- workflow rerun
- public posting / cross-platform sending

Checklist:

- [ ] 操作が high-risk か分類した
- [ ] current explicit approval がある
- [ ] target が明確
- [ ] dry-run / read-only verification が可能なら先に実施した
- [ ] rollback path がある
- [ ] user expectation と一致している
- [ ] operation result を検証できる

If approval is missing, stop before the operation.

---

## 17. No-go Conditions

以下の条件に該当する場合、実装に進まない。

### 17.1 Scope no-go

- target repo が不明
- target branch が不明
- target files が不明
- allowed / forbidden actions が矛盾している
- user request が read-only なのに mutation が必要
- task が複数文書・複数領域へ膨らんでいる

### 17.2 Authorization no-go

- high-risk action に current explicit approval がない
- backlog / roadmap / report を approval と誤読している
- Memory を approval として扱っている
- Quality finding を permission として扱っている
- worker dispatch が禁止されている

### 17.3 Evidence no-go

- 参照すべき docs が存在しない
- live state が前提と違う
- git branch / HEAD が前提と違う
- diff が想定外
- tests / checks が実行不能で代替確認もない
- tool output と final claim が一致しない

### 17.4 Safety no-go

- destructive action の対象が曖昧
- rollback path がない
- secrets が露出する可能性がある
- service restart が chat / gateway を中断する可能性がある
- user が避けたい運用に反している

---

## 18. Readiness Verdict Model

Readiness Review は、次のような verdict を返す。

### 18.1 Verdict levels

| Verdict | Meaning | Next action |
| --- | --- | --- |
| `Ready for explicit approval` | 実装判断に必要な材料は揃っている | user approval を待つ |
| `Ready for docs-only work` | docs-only の範囲なら進められる | 指定 docs だけ作成 |
| `Needs clarification` | scope / permission / target が不足 | 質問する |
| `Blocked by missing evidence` | 必要な事実確認が未完了 | read-only 確認を行う |
| `Blocked by authorization` | high-risk approval がない | 実行しない |
| `No-go` | 現条件では危険または矛盾 | stop and report |

### 18.2 Recommended verdict format

```text
Readiness Verdict: <level>
Reason: <1-3 bullets>
Allowed now: <actions>
Forbidden now: <actions>
Required before execution: <checks or approval>
```

### 18.3 Confidence

Confidence は必要時のみ付ける。

Use confidence when:

- evidence が不完全
- assumptions がある
- high-risk boundary が近い
- user に判断してほしい tradeoff がある

Avoid confidence when:

- read-only facts が明確
- docs-only outcome が確認済み
- scope が単純

---

## 19. Dangerous Examples

### 19.1 Backlog as authorization

Dangerous:

> Improvement Backlog にあるので実装します。

Safe:

> Improvement Backlog に候補があります。実装するには現在の明示許可が必要です。

### 19.2 Readiness as push approval

Dangerous:

> Ready なので push します。

Safe:

> Ready は実装準備の確認です。push には別途 explicit approval が必要です。

### 19.3 Quality finding as mutation permission

Dangerous:

> Weekly report で低スコアだったので Constitution を更新します。

Safe:

> Weekly report は evidence です。rule change は review と user approval が必要です。

### 19.4 Memory as current instruction

Dangerous:

> Memory に push 方針があるので push します。

Safe:

> Memory は preference context です。現在の user instruction が push を許可しているか確認します。

### 19.5 Worker dispatch by architecture doc

Dangerous:

> Worker Architecture にあるので worker を起動します。

Safe:

> Worker Architecture は boundary を定義します。dispatch には現在の許可が必要です。

### 19.6 Docs-first misunderstood as docs-only forever

Dangerous:

> Docs-first なので実装は常に禁止です。

Safe:

> Docs-first は runtime governance 前に設計を明確にする原則です。明示許可があれば実装できます。

---

## 20. Open Questions

Implementation Readiness Review v1 の未決事項:

1. Readiness verdict を将来 Kanban task metadata として記録するか。
2. Readiness Review を CI observer とどう接続するか。
3. `Definition of Ready` を project-wide standard doc として分離するか。
4. high-risk operation taxonomy を Foundation docs 全体で共通化するか。
5. worker dispatch 前 review を separate artifact にするか。
6. Memory / Human Model mutation review を separate checklist にするか。
7. push readiness を user-specific Git workflow doc と統合するか。
8. Weekly Quality Report の findings を readiness review にどう引用するか。
9. Continuous Evolution の adoption review と readiness review の境界をどう表現するか。
10. runtime implementation 前に必要な minimum evidence set をどう定義するか。

Current v1 stance:

- Open questions are design prompts only.
- They do not authorize implementation.
- They do not create backlog items automatically.
- They do not mutate Kanban / Memory / Human Model / Decision Profile.

---

## 21. Next Recommended Task

次に作成するとよい Foundation 補助文書:

`docs/product/high-risk-operation-taxonomy-v1.md`

目的:

- Hermes における high-risk operation を分類する
- read-only / reversible / state-changing / destructive / external-side-effect を分ける
- current explicit approval が必要な操作を明確にする
- Planning Gate / Implementation Readiness Review / Worker Architecture / Git workflow の共通参照にする

Suggested sections:

1. purpose
2. scope
3. risk categories
4. read-only operations
5. reversible local mutations
6. repository mutations
7. external side effects
8. service/runtime operations
9. memory/profile/governance mutations
10. worker/kanban operations
11. approval requirements
12. verification requirements
13. dangerous examples
14. open questions

Boundary:

> High-risk Operation Taxonomy classifies risk; it does not approve action.

---

## Summary

Implementation Readiness Review v1 は、Hermes が実装に入る前に必要な確認を整理する実務チェックリストである。

It confirms:

- what to read
- what boundaries apply
- what current instruction allows
- what high-risk approvals are needed
- what no-go conditions exist
- what Done should mean

It does not:

- implement
- approve push
- create tasks
- mutate Kanban
- mutate Memory / Human Model / Decision Profile
- dispatch workers
- rerun CI
- change runtime governance

Final principle:

> Readiness helps Hermes avoid premature action. It never replaces the user’s current explicit instruction.
