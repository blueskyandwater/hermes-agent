# Review Pipeline v1

## 1. Purpose

この文書は、Hermes開発における **Review Worker / Judge / Metrics** の責務と順番を整理する基準文書である。

目的は、

- 重複評価を減らすこと
- 「誰が何を確認するか」を明確にすること
- Review 結果を Story / Epic / Sprint close へ接続すること

---

## 2. Pipeline Summary

```text
Artifact Ready
  ↓
Review Worker
  ↓
Judge
  ↓
Metrics
  ↓
Accepted / Rework
```

補足:
- Guard は Review 前後の監査役として併走してよい
- すべてのStoryで Judge / Metrics が必須とは限らない
- ただし Quality Framework 対象では極力通す

---

## 3. Role Responsibilities

### 3.1 Review Worker

**役割**
- 成果物の内容妥当性を確認する
- scope と deliverable の一致を見る
- 重複 / 漏れ / 依存 / 粒度 / 実装順の妥当性を確認する

**答える問い**
- これは要求に対して合っているか
- 余計なものを混ぜていないか
- 欠けているものは何か
- 上位設計と矛盾していないか

**出力**
- pass / needs revision / blocked
- 根拠つき所見

### 3.2 Judge

**役割**
- Hermes の出力品質を採点する
- Constitution / Core OS / 品質基準への適合度を厳しめに見る

**答える問い**
- 出力品質は高いか
- 冗長すぎないか
- 必要な構造と明確さがあるか
- 目的への近づき方は適切か

**出力**
- Score
- Good Points
- Issues
- Improvement

### 3.3 Metrics

**役割**
- 測定可能な事実だけを記録する
- スコア、件数、通過率、残件数などを保持する

**答える問い**
- 何点だったか
- 何件あったか
- 前回比で改善したか
- N/A にすべき項目は何か

**出力**
- measurable counts
- scores
- status tallies
- N/A 明示

---

## 4. Order and Gating

### Step 1: Review Worker
最初に通す。

理由:
- そもそも内容が要求に合っていないなら、その後の採点は意味が薄い
- まず correctness / scope / dependency を確認する

### Step 2: Judge
Review pass 後に通す。

理由:
- 内容妥当性が取れた上で、出力品質を評価する
- 内容がズレている状態で品質だけ高く見えても意味がない

### Step 3: Metrics
最後に記録する。

理由:
- Review と Judge の結果が出た後でないと、記録する値が定まらない
- 測定は最終結果を写す役割に徹する

---

## 5. Decision Rules

### Accepted に進める条件
1. Review Worker が pass 相当
2. Guard 違反なし
3. Judge が必須対象なら実施済み
4. Metrics が必須対象なら記録済み

### Rework に戻す条件
1. Review Worker が needs revision
2. Judge の主要 Issues が close を妨げる
3. Integration に耐えない構造欠陥がある

### Blocked 扱いにする条件
1. 依存成果物が未完成
2. 正本ファイルや対象範囲が未確定
3. Judge / Metrics 以前に前提不足

---

## 6. Avoiding Overlap

重複しやすい領域を明確に分ける。

| Role | 見るもの | 見ないもの |
|---|---|---|
| Review Worker | 内容妥当性、scope、依存、構造 | 厳密な採点集計 |
| Judge | 出力品質、構成品質、基準適合 | backlog進行管理 |
| Metrics | 数値記録、件数、スコア保存 | 内容解釈の最終判断 |

原則:
- **Review Worker は採点者ではない**
- **Judge は backlog manager ではない**
- **Metrics は評価者ではない**

---

## 7. Minimum Review Outputs

最低限残すべきもの:

- Review Worker: verdict + 根拠
- Judge: score + improvement 1件
- Metrics: counts / scores / N/A

これがあれば Sprint Review で再利用しやすい。

---

## 8. Relationship to Workflow

Review Pipeline は Workflow 上こう位置づく。

```text
In Progress
  ↓
Review Worker
  ↓
Judge
  ↓
Metrics
  ↓
Accepted
  ↓
Done
```

つまり Review は単一イベントではなく、
**内容確認 → 品質採点 → 測定記録** のパイプラインとして扱う。

---

## 9. Success Criteria

この文書により、Hermes開発では以下を満たす。

- Review と Judge の役割重複を減らす
- Metrics を最後の記録係として安定させる
- Review結果を Accepted / Done へ接続できる

今回の成果物は **Review Pipeline v1** である。
