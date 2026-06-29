# Definition of Done v1

## 1. Purpose

この文書は、Hermes開発で **Story / Epic / Sprint の Done 条件を混ぜない** ための基準文書である。

Done は一段階ではない。

- Story Done は個別成果物の完了
- Epic Done は複数Storyの統合完了
- Sprint Done はそのSprintの整理完了

---

## 2. Story DoD

Story が Done と言える条件:

1. **Deliverable が存在する**
   - 文書、実装、設定、レビュー記録など、Story で約束した成果物がある
2. **Scope を満たしている**
   - Story の Goal / Deliverable / Guard に沿っている
3. **Out of Scope を侵していない**
   - 勢いで別Story相当の内容まで広げていない
4. **Guard 違反がない**
   - 禁止操作、無承認変更、対象外領域への変更がない
5. **Review が完了している**
   - Reviewer が内容妥当性を確認済み
6. **必要なら Judge / Metrics が記録済み**
   - 品質評価対象なら採点・記録が残っている
7. **Commit が必要な作業なら確認済み**
   - 変更がGit管理対象なら commit 済み、または commit 対応完了が確認できる
8. **参照先が明確**
   - どの artifact が正本か分かる
9. **Kanban 状態を Done にしてよい根拠がある**
   - Review だけでなく close 可能な根拠が残っている

### Story DoD 補足

- `artifact exists` だけでは Done ではない
- `commit済み` だけでも Done ではない
- review を通して初めて Accepted / Done 候補になる

---

## 3. Epic DoD

Epic が Done と言える条件:

1. **Epic 配下の必須 Story が完了している**
   - Done または少なくとも Accepted まで進んでいる
2. **Epic の Scope 成果物が揃っている**
   - Epic の Purpose / Scope に照らして主要欠落がない
3. **Story 間の重複が解消されている**
   - 同じ責務を複数Storyで持っていない
4. **Story 間の矛盾が解消されている**
   - 定義、用語、責務境界が衝突していない
5. **Integration Review が完了している**
   - 個別Storyではなく Epic 全体として確認済み
6. **依存関係が整理されている**
   - 次Epicへ引き渡す前提が明確
7. **未完了項目が仕分け済み**
   - 残件は Deferred / Improvement Backlog / 次Epic のどこへ行くか決まっている
8. **Epic close の記録がある**
   - close note, review summary, integrated doc などが存在する

### Epic 2 用の補足基準

Human Model のような設計Epicでは、以下も確認する。

9. **Profile 間の関係が説明できる**
10. **root / sub-profile の階層が整理されている**
11. **隣接Epicとの責務境界が明確**
   - 例: Coaching Profile と Coaching System の境界

---

## 4. Sprint DoD

Sprint が Done と言える条件:

1. **Sprint Goal の達成判定がある**
   - 達成 / 一部達成 / 未達 のどれかを明示する
2. **Sprint 対象 Story の状態が整理済み**
   - Done / Deferred / Rejected / Carry-over が分かる
3. **主要成果物が一覧化されている**
   - 何を作ったか追える
4. **主要レビュー結果が整理されている**
   - Review / Judge / Metrics の結果が参照できる
5. **残課題の行き先が決まっている**
   - Improvement Backlog か次Sprintかを仕分け済み
6. **Roadmap への影響が整理されている**
   - 優先順位や順序変更が必要か確認済み
7. **次に着手する Story が1件に絞られている**
   - 勢いで枝葉へ飛ばない
8. **Sprint Review が完了している**
   - 学びと未解決点が整理済み

### Sprint DoD 補足

- 全Storyが Done でなくてもよい
- 重要なのは、**未完了を含めて状態整理が終わっていること**
- Sprint Review を通さずに次Sprintへ行かない

---

## 5. Anti-Patterns

以下は Done と見なさない。

- artifact があるだけ
- commit があるだけ
- review が始まっただけ
- board 上の status だけ更新した状態
- 「たぶん終わり」で close すること

---

## 6. Recommended Close Order

```text
Story DoD 達成
  ↓
Epic Integration Review
  ↓
Epic DoD 達成
  ↓
Sprint Review
  ↓
Sprint DoD 達成
```

Done 条件はこの順序で積み上げる。

---

## 7. Success Criteria

この文書により、Hermes開発では以下を防ぐ。

- Story と Epic の完了条件の混同
- commit 済みを Done と誤認すること
- Sprint 未整理のまま次へ進むこと

今回の成果物は **Definition of Done v1** である。
