# Improvement Lifecycle v1

## 1. Purpose

この文書は、Hermes開発における改善案の標準ライフサイクルを定義する。

重要原則:

- 改善案は思いついた瞬間に実装しない
- Sprint Review を通して採用可否を判断する
- Roadmap と Sprint Planning に接続して初めて着手候補になる

---

## 2. Lifecycle Summary

```text
Candidate
  ↓
Sprint Review
  ↓
Adopt
  ↓
Roadmap
  ↓
Sprint Planning
```

補助分岐:

```text
Sprint Review
  ├─→ Defer
  └─→ Reject
```

---

## 3. Stage Definitions

### 3.1 Candidate

**意味**
- 改善案として記録されたが、まだ採用判断していない状態

**典型例**
- backlog grooming で見つかった運用負債
- review で見つかった process gap
- metrics 低下から見えた改善余地

**必要条件**
- 一文で問題を説明できる
- 何を改善したいか分かる
- まだ実装を始めていない

### 3.2 Sprint Review

**意味**
- 改善案を現在のSprint文脈で評価する場

**確認項目**
- 本当に今のボトルネックか
- 今Sprintに入れる価値があるか
- 既存EpicやRoadmapと矛盾しないか
- 別の改善案と重複していないか

### 3.3 Adopt

**意味**
- 改善案を正式採用すると決めた状態
- まだ実装開始ではなく、Roadmap に載せる段階

**必要条件**
- 採用理由が説明できる
- 優先順位が付けられる
- 対応単位（Epic / Story / improvement task）が見える

### 3.4 Roadmap

**意味**
- 改善案をどのSprint / Epic で扱うか配置する段階

**必要条件**
- いつ扱うかが明確
- 依存関係が見えている

### 3.5 Sprint Planning

**意味**
- 実際のSprint対象に落とし込む段階
- ここで初めて Planning → Todo に進める

**必要条件**
- deliverable が定義できる
- DoD が書ける
- 他の優先項目と比較済み

---

## 4. Decision Outcomes

### Adopt
採用する。

向いている条件:
- 繰り返し再発している問題
- Workflow / Quality / Development velocity に効く
- 次Sprint以降の混乱を減らす

### Defer
今は採用しないが保留する。

向いている条件:
- 価値はあるが優先度が低い
- 依存先が未完成
- 今Sprintに入れると散る

### Reject
採用しない。

向いている条件:
- 重複改善
- 問題定義が弱い
- Won’t Yet や方針違反に近い

---

## 5. Who Decides What

| Stage | Primary | Responsibility |
|---|---|---|
| Candidate | Reviewer / Planner | 問題の発見と記録 |
| Sprint Review | Planner | 採用可否の判断 |
| Adopt | Planner | 正式採用と優先付け |
| Roadmap | Planner | どこに載せるか決める |
| Sprint Planning | Planner + Guard | 実作業に落としてよいか確認 |

補助:
- Judge: 改善必要性の根拠を強める
- Metrics: 再発頻度やスコア低下の証拠を出す

---

## 6. Relationship to Backlog

Improvement Lifecycle は Product Backlog と競合しない。

位置づけ:
- Product Backlog: 何を育てるか
- Improvement Lifecycle: どう育て方を改善するか

つまり、改善案は別腹ではなく、
**Product Development Process の backlog** として扱う。

---

## 7. Adoption Rules

改善案を Adopt する前に、最低限これを確認する。

1. 問題は実在するか
2. 単発事故ではなく再発性があるか
3. 既存ルールの改善で済むか
4. 新しい複雑性を増やしすぎないか
5. Roadmap の流れを壊さないか

原則:
- **新ルール追加より既存運用改善を優先**
- **勢いでSprint scopeを広げない**
- **改善案は evidence ベースで採用する**

---

## 8. Success Criteria

この文書により、Hermes開発では以下を守る。

- 改善案を思いつきで実装しない
- Sprint Review を採用Gateとして使う
- Roadmap と Sprint Planning を経由して着手する

今回の成果物は **Improvement Lifecycle v1** である。
