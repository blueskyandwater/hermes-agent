# Artifact Lifecycle v1

## 1. Purpose

この文書は、Hermes開発における成果物の標準ライフサイクルを定義する。

対象となる artifact:

- 設計文書
- backlog 文書
- review artifact
- 実装ファイル
- 設定変更
- Sprint / Epic close note

今回は runtime 自動化ではなく、**人間とHermesが追跡できる運用順序**を定義する。

---

## 2. Lifecycle Summary

```text
Artifact
  ↓
Review
  ↓
Commit
  ↓
Accepted
  ↓
Integration
  ↓
Done
```

補助分岐:

```text
Review → Rework
Accepted → Deferred
Integration → Rework
```

---

## 3. Lifecycle Stages

### 3.1 Artifact

**意味**
- 最初の成果物が存在する状態
- 文書なら下書き、実装なら動作候補、設計なら初版

**必要条件**
- Story の Goal と対応している
- 参照パスがある
- review 可能な最低限の形になっている

**出口**
- Review へ送る

### 3.2 Review

**意味**
- 内容妥当性、scope一致、Guard順守を確認する状態

**確認項目**
- Goal を満たしているか
- out of scope が混ざっていないか
- 重複 / 漏れ / 矛盾がないか
- 参照パスが正しいか

**出口**
- pass なら Commit へ
- 差し戻しなら Rework へ

### 3.3 Commit

**意味**
- Git 管理対象なら履歴として固定する段階
- 文書変更や実装変更が traceable になる

**必要条件**
- review pass 済み
- どの変更が正本か明確

**注意**
- commit は Done ではない
- commit は Accepted の前提条件の一つにすぎない

**出口**
- Accepted へ

### 3.4 Accepted

**意味**
- 個別 artifact として受理済み
- Story の成果物としては成立している
- ただし上位統合はまだ残ることがある

**必要条件**
- Review pass
- Commit 確認
- Guard 違反なし
- 参照先明確

**出口**
- Integration へ
- 今Sprintで閉じないなら Deferred へ

### 3.5 Integration

**意味**
- その artifact を Epic / Sprint / 他文書と接続して矛盾がないかを見る段階

**確認項目**
- 同一Epic内の他成果物と整合するか
- 用語、責務、順序がぶつからないか
- backlog / roadmap / review 結果と矛盾しないか

**出口**
- 問題なければ Done
- 問題があれば Rework

### 3.6 Done

**意味**
- 個別成果物としても、統合成果物としても閉じられる状態

**必要条件**
- 上位単位との整合性確認済み
- close note または参照先が明確
- status を閉じてよい根拠が残っている

---

## 4. Rework Rules

Rework が必要になる典型:

1. Review で scope mismatch が見つかった
2. commit 前に不足が見つかった
3. Integration で他成果物との矛盾が見つかった
4. artifact は良いが placement が間違っていた

Rework は失敗ではない。
**Done を急がず、統合品質を守るための通常工程**として扱う。

---

## 5. Artifact Types and Close Behavior

| Artifact Type | Review Focus | Integration Focus |
|---|---|---|
| Philosophy / Process Doc | 構造、責務、用語 | Backlog / Roadmap / 他方針との整合 |
| Human Model Profile | profile責務、重複 | Human Model全体構造との整合 |
| Implementation | 要件、挙動、テスト | 呼び出し経路、周辺設定との整合 |
| Review Artifact | 妥当性、根拠 | Judge / Metrics / Sprint Review との接続 |
| Sprint Note | 状態整理 | 次Sprint / Roadmap との接続 |

---

## 6. Minimum Evidence Required

各段階で最低限残すべき証跡:

- Artifact: ファイルパスまたは明示成果物
- Review: review summary または pass/fail 根拠
- Commit: commit 確認
- Accepted: 受理理由
- Integration: 整合確認メモ
- Done: close note または上位文書参照

---

## 7. Success Criteria

この文書により、Hermes開発では以下を防ぐ。

- 作った瞬間に Done 扱いすること
- commit 済みを完了と誤認すること
- Epic 統合前に close してしまうこと

今回の成果物は **Artifact Lifecycle v1** である。
