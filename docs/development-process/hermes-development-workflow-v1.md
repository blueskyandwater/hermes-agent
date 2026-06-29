# Hermes Development Workflow v1

## 1. Purpose

この文書は、Hermes本体ではなく**Hermesを継続的に育てるための開発Workflow**を標準化するための基準文書である。

対象は以下に限定する。

- Product Backlog から Story 着手までの流れ
- Story 実行中の状態遷移
- Review / Accepted / Done までの閉じ方
- Deferred / Rejected の扱い

今回は**設計のみ**を対象とする。

- Hermes本体の実装変更はしない
- Human Model / Decision Framework / Worker Architecture の新規追加はしない
- Kanbanの実運用ステータスはまだ変更しない
- 本文書は今後の標準運用の基準とする

---

## 2. Workflow Summary

```text
Planning
  ↓
Todo
  ↓
In Progress
  ↓
Review
  ↓
Accepted
  ↓
Done

Planning / Todo / In Progress / Review / Accepted から
  ├─→ Deferred
  └─→ Rejected
```

---

## 3. State Definitions

### 3.1 Planning

**意味**
- まだ着手確定していない検討状態
- backlog grooming / roadmap / improvement review 中の項目
- scope, priority, dependency, DoD を整理中の状態

**入る条件**
- 新Epic / Story / Improvement Candidate が発生した
- まだ作るか保留で、優先順位判断が終わっていない

**出る条件**
- 目的、成果物、Guard、依存関係、優先順位が明確になった

**担当**
- Primary: Planner
- Support: Guard, Reviewer

### 3.2 Todo

**意味**
- 着手可能な状態
- scope と deliverable が確定している
- 今Sprintで扱ってよいと判断済み

**入る条件**
- Planning の整理が完了した
- 依存関係が解消または許容済み
- Story DoD が定義済み

**出る条件**
- 実作業を開始する
- または今Sprintで扱わないと判断する

**担当**
- Primary: Planner
- Support: Guard

### 3.3 In Progress

**意味**
- 成果物を実際に作成している状態
- 設計、文書作成、実装、検証のいずれかが進行中

**入る条件**
- 担当と作業対象が明確で、実作業を開始した

**出る条件**
- review可能な artifact が存在する
- または一旦保留 / 却下にする判断が出た

**担当**
- Primary: Executor
- Support: Guard

### 3.4 Review

**意味**
- artifact は作成済みで、内容妥当性や品質確認を待っている状態
- 実装や文書の有無ではなく、**通してよいか**を確認する段階

**入る条件**
- deliverable が存在する
- scope に対する自己確認が終わっている

**出る条件**
- review pass で Accepted に進む
- 修正が必要なら In Progress に戻る
- 不採用なら Rejected に進む

**担当**
- Primary: Reviewer
- Support: Guard, Judge, Metrics

### 3.5 Accepted

**意味**
- Story成果物としては受理済み
- review を通過し、必要な commit まで確認済み
- ただし Epic 統合や Sprint close がまだ残る場合の待機状態

**入る条件**
- Review pass
- Guard 違反なし
- 必要な commit / artifact 参照先が確認済み

**出る条件**
- Epic 統合上の矛盾がないと確認できた
- Sprint の文脈でも完了扱いしてよい

**担当**
- Primary: Reviewer
- Support: Planner

### 3.6 Done

**意味**
- Story または Epic として完全に閉じられる状態
- artifact / review / integration / status 整理が終わっている

**入る条件**
- Accepted 済み
- 上位単位（Epic / Sprint）との整合が取れている
- close note 相当の記録がある

**担当**
- Primary: Planner
- Support: Reviewer

### 3.7 Deferred

**意味**
- 今はやらないが、候補として残す状態
- priority / dependency / timing の理由で先送りする

**入る条件**
- 必要性はあるが今Sprintでは扱わない
- 前提条件がまだ揃っていない

**出る条件**
- 次Sprint以降に再評価する

**担当**
- Primary: Planner

### 3.8 Rejected

**意味**
- 重複、方針不一致、不要化などにより採用しない状態

**入る条件**
- backlog上の価値よりも混乱や重複の方が大きい
- Won’t Yet / out of scope / duplicate と判断した

**出る条件**
- 原則として再オープンしない
- 再開する場合は新Candidateとして扱う

**担当**
- Primary: Planner
- Support: Reviewer, Guard

---

## 4. Transition Rules

### Planning → Todo
必要条件:
1. Goal が明確
2. Deliverable が明確
3. Priority が明確
4. Dependency が把握済み
5. Story DoD が書ける

### Todo → In Progress
必要条件:
1. 今Sprintで扱う判断がある
2. 実作業対象が確定している
3. Guard 上の禁止事項に触れない

### In Progress → Review
必要条件:
1. Artifact が存在する
2. 自己確認が終わっている
3. Scope 外へ広げていない

### Review → In Progress
必要条件:
1. Review で差し戻しが発生した
2. 修正対象が明確

### Review → Accepted
必要条件:
1. Review pass
2. Guard 違反なし
3. 必要な記録先が明確
4. Commit が必要な作業なら commit 確認済み

### Accepted → Done
必要条件:
1. Epic 統合上の矛盾なし
2. 依存Storyとの関係整理済み
3. 完了として残す記録がある

### Planning / Todo / In Progress / Review / Accepted → Deferred
必要条件:
1. 今Sprintの優先順位から外す理由がある
2. 再評価タイミングを記録できる

### Planning / Todo / In Progress / Review / Accepted → Rejected
必要条件:
1. 重複 / 不要 / 方針違反 / out of scope のいずれか
2. 却下理由を残せる

---

## 5. Role Mapping

| State | Primary | Main Responsibility |
|---|---|---|
| Planning | Planner | backlog整理、優先順位、依存確認 |
| Todo | Planner | 着手可能状態へ整える |
| In Progress | Executor | artifact作成 |
| Review | Reviewer | 内容妥当性確認 |
| Accepted | Reviewer | 受理判定と統合待ち管理 |
| Done | Planner | 完了閉鎖と上位整合 |
| Deferred | Planner | 先送り判断 |
| Rejected | Planner | 却下判断 |

補助責務:
- Guard: 実行前監査、逸脱防止
- Judge: 出力品質の採点
- Metrics: 測定値の記録

---

## 6. Operating Principles

1. **todo を万能状態にしない**
   - 未着手、review待ち、統合待ちを同じ状態に混ぜない
2. **artifact ができても即 Done にしない**
   - Review と Accepted を挟む
3. **commit 済み = Done ではない**
   - Epic 統合確認前は Accepted 扱いに留める
4. **Deferred と Rejected を分ける**
   - 今やらないものと、採用しないものを混同しない
5. **改善案は思いつきで実装しない**
   - Improvement Lifecycle に流す

---

## 7. Relationship to Current Kanban

現行Kanbanでは native の状態表現が不足しているため、当面はこの文書を**意味上の標準**として先に固定する。

- 現在の board 表現は暫定でよい
- ただし今後の Story / Epic 運用はこの状態定義を基準に解釈する
- Kanban 実装変更は別Storyで扱う

---

## 8. Success Criteria

この Workflow v1 により、Hermes 開発は以下を満たす。

- backlog の整理状態と実作業状態を分けて扱える
- artifact 作成後に review / accepted を通せる
- Story / Epic / Sprint の close 条件を混同しない
- 改善案を勢いで実装せず、review 可能なプロセスに乗せられる

今回の成果物は **Hermes Development Workflow v1** である。
