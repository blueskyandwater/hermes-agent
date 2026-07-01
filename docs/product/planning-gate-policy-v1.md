# Planning Gate Policy v1 Draft

## 1. Purpose

Planning Gate Policy は、Hermes が **Backlog is inventory, not authorization** を実務運用に落とすための gate policy である。

この文書の目的は、Kanban task が存在すること、Roadmap に載っていること、Memory に過去方針が残っていること、Quality で改善候補が見つかったことを、**そのまま実行許可に変換しない** ための境界を明確にすることにある。

Planning Gate は、Hermes Foundation の中で次を担う。

- task を在庫として見る
- 実行可能な task と、まだ planning の task を分ける
- mode / status / approval / risk の関係を明確にする
- dispatcher や worker が自律的に scope を広げることを防ぐ
- docs-first / read-only first の原則を守る

中心原則:

> Planning Gate prevents premature action.

補足:

- この文書は **運用ポリシー** であり、runtime guard 実装そのものではない
- この文書は task を完了させない
- この文書は dispatch を許可しない
- この文書は push / PR / workflow rerun / Memory mutation / Human Model mutation を許可しない

---

## 2. Status Semantics

Planning Gate では、Kanban status を「進捗表示」ではなく「実行可能性の手がかり」として扱う。

### 2.1 `todo`

意味:
- backlog上に存在する
- まだ着手前
- inventory であって authorization ではない

解釈:
- 実行許可ではない
- dispatcher が自動dispatchしてはいけない
- worker が着手してはいけない
- planning-only の検討対象にはなる

### 2.2 `blocked`

意味:
- 明確な前提不足、依存未解決、承認不足、または設計未完了がある

解釈:
- 実行禁止
- unblock 前に read-only 調査や docs-only planning は可能なことがある
- dispatcher / worker は着手してはいけない

### 2.3 `ready`

意味:
- Definition of Ready を満たし、実行候補として扱える

解釈:
- ただちに何でも実行できる、という意味ではない
- mode が許可しなければ mutation は不可
- high-risk action は別途 current approval が必要
- ready は dispatch 候補であり、無条件承認ではない

### 2.4 `in_progress`

意味:
- 許可済み scope で実行が始まっている

解釈:
- scope外へ拡張してはいけない
- worker / executor は指示された範囲だけを進める
- 途中で高リスク操作が出た場合、追加承認なしで進まない

### 2.5 `done`

意味:
- Definition of Done を満たし、結果が確認済み

解釈:
- done は成果物確認を含む
- “やったつもり” ではない
- draft 作成だけで done になるとは限らない

### 2.6 `archived` or equivalent closed state

意味:
- 現行の実行対象ではない

解釈:
- 再利用は参考情報としてのみ
- 再開時は新しい gate judgment が必要

### Core status rule

> `todo` と `blocked` は inventory であり、dispatch authorization ではない。

---

## 3. Gate Rules

Planning Gate の基本ルール。

### Rule 1: Backlog is inventory, not authorization

task の存在は、実行許可ではない。

必要な別要素:
- status
- mode
- scope
- risk judgment
- current approval

### Rule 2: Read-only first

不明な場合はまず確認する。

許されやすい行為:
- read-only inspection
- docs review
- status verification
- dependency確認
- diff / logs / existing docs の確認

### Rule 3: Docs-first for governance changes

以下は先に docs-only で定義・整理する。

- Constitution変更
- Gate rules変更
- Memory policy変更
- Human Model policy変更
- Worker permission変更
- Quality governance変更

### Rule 4: No mutation without explicit mode

mode が明示されていない限り、mutation を行わない。

例:
- file write
- git add
- commit
- push
- Kanban mutation
- task create / complete / unblock
- Memory mutation
- Human Model mutation
- workflow rerun
- dispatcher dispatch

### Rule 5: Ready is necessary, not sufficient

`ready` は実行候補であり、最終承認ではない。

追加条件:
- mode が合っている
- user approval が必要なら現在の承認がある
- risk が許容される
- scope が明確

### Rule 6: Approval must be current

過去の会話、Memory、Roadmap、品質改善履歴は current approval の代替にならない。

### Rule 7: Quality findings are not auto-actions

Quality finding / Improvement Candidate は task 自動化・dispatch 自動化・rule自動変更に直結しない。

### Rule 8: Dispatcher cannot approve

dispatcher は task を配る仕組みであり、実行権限を創出しない。

### Rule 9: Worker cannot widen scope

worker は与えられた mode / task / boundary の中でだけ動く。

### Rule 10: Safe noop is valid

条件が足りないときは、進まず止まるのが正しい。

---

## 4. Definition of Ready

task が `ready` と判断されるための最小条件。

### Required conditions

1. **Purpose is clear**
   - task の目的が1〜3文で説明できる

2. **Scope is bounded**
   - 何をやるか
   - 何をやらないか
   - 対象ファイル / 対象領域 / 対象surface が明確

3. **Dependencies are resolved or explicitly accepted**
   - 依存task
   - 前提docs
   - 必要な review
   - 必要な approval

4. **Mode is explicit**
   - planning-only
   - docs-only-no-commit
   - docs-only-local-commit-approved
   - push-only
   - review-only
   - など

5. **Risk class is understood**
   - read-only か
   - local mutation か
   - external surface か
   - push / publish / rerun / cron / memory mutation を含むか

6. **Success condition is observable**
   - 成功時に何を確認するか明確
   - file exists / diff / tests / status / logs など

7. **Blocked factors are absent**
   - 必須情報不足がない
   - 禁止事項と衝突しない
   - Gate policyに反しない

### Optional but helpful

- example command
- expected diff shape
- rollback idea
- review checklist

### Ready anti-patterns

次は ready にしてはいけない。

- 「多分これだろう」で scope が曖昧
- task 名だけで中身がない
- blocked dependency が未解決
- “前にもやったから今回もOK” という過去承認依存
- 実行前提が docs 未整理
- user が明示的に禁止している操作を含む

---

## 5. Definition of Done

task が `done` と判断される条件。

### Required conditions

1. **Requested artifact exists**
   - 求められた文書・変更・結果が実在する

2. **Result matches scope**
   - 許可された範囲だけを変更している
   - 禁止された操作をしていない

3. **Verification was run**
   - 指定確認が実施済み
   - 例: `git status -sb`, `git diff --check`, tests, logs

4. **No unapproved side effects**
   - pushなし
   - PRなし
   - task mutationなし
   - Memory mutationなし
   - runtime mutationなし
   - external publishなし

5. **Outcome is reportable**
   - 何を作ったか
   - 何を確認したか
   - 何をしていないか
   - 未解決があるなら何か

### Done anti-patterns

- ファイルを書いたが確認していない
- draft を考えただけで保存していない
- 範囲外の変更が混ざっている
- 期待結果を示せない
- 「たぶん動く」で終える

---

## 6. Dispatcher Rules

dispatcher は workflow engine ではあるが approver ではない。

### Dispatcher may do

- `ready` task の候補を見つける
- dependency / claim / assignee の整合を見る
- 実行対象を絞る
- 既定ルールに沿って worker に渡す

### Dispatcher must not do

- `todo` / `blocked` を approval 扱いして dispatch する
- user approval を推測する
- mode のない task を mutation worker に渡す
- high-risk action を自動承認する
- Quality finding から task を自動dispatchする
- blocked task を勝手に unblock する
- Roadmap priority を authorization に変換する

### Dispatcher gating rule

dispatcher が task を動かせるのは、少なくとも以下が成立するときだけ。

- task が `ready`
- assignee / worker type が妥当
- mode が task の性質と一致
- high-risk action を含む場合は current approval が別にある
- policy違反がない

### Dispatcher failure behavior

条件が足りない場合の正しい動作:
- dispatchしない
- safe noop
- 必要なら「何が足りないか」を planner / human 向けに返す

---

## 7. Worker Rules

worker は bounded executor であり autonomous owner ではない。

### Worker may do

- 与えられた scope の実行
- 指定 mode 内での作業
- 許可された確認コマンド
- 結果報告
- ブロッカーの明示

### Worker must not do

- task scope を自己拡張する
- 新しい task を勝手に作る
- blocked task を自己判断で再開する
- push / PR / workflow rerun / external publish を無承認で行う
- Memory / Human Model / Constitution / Gate rules を無承認で変更する
- “やった方が良さそう” で dispatcher role を兼務する

### Worker escalation rule

worker は次の場合に止まり、承認または再計画へ返す。

- mode外の操作が必要になった
- task定義が曖昧だった
- 新しい high-risk action が必要になった
- dependency不足が発覚した
- policy違反の恐れがある

### Worker reporting rule

最低限、以下を返せること。

- 何をやったか
- 何を確認したか
- 何をしていないか
- どこで止まったか

---

## 8. Blocked Backlog Policy

blocked backlog は「価値がない」のではなく、「今は進めない」を意味する。

### Blocked task の扱い

blocked task は:
- inventory として保持する
- 依存や承認の不足を明示する
- planning / docs review の対象にはなりうる
- 実装着手対象にはしない

### Allowed actions around blocked tasks

許されることがある:
- read-only inspection
- dependency整理
- docs-only planning
- unblock条件の明文化
- risk整理

許されないこと:
- statusを勝手にreadyへ変更
- 実装を始める
- dispatcher dispatch
- worker起動による既成事実化

### Blocked backlog principle

> blocked backlog should remain visible, but not executable.

### Improvement candidate relationship

Quality / Continuous Evolution から生まれた改善候補は、最初から実装taskではない。

必要な流れ:
- finding
- candidate
- human review
- approved backlog item
- ready judgment
- execution

## 8.1 Planning Lane

Planning lane は、candidate / review / backlog / implementation の境界を見える化するための **review space** である。

Planning lane は次ではない。
- execution permission
- dispatcher route
- Kanban status変更ルール
- task creation rule

### 8.1.1 Purpose

Planning lane の目的は、候補をすぐ実装に滑らせず、review と planning の間で安全に整理することである。

Planning lane では、次を見える化する。
- candidate preview
- review verdict
- backlog との接続
- implementation との境界

### 8.1.2 Non-Goals

Planning lane は次を行わない。
- task creation
- ready化
- worker dispatch
- implementation permission の付与
- push / PR / workflow rerun の許可

### 8.1.3 Handoff Shape

Planning lane で扱う最小の流れ:
- Weekly Report
- candidate
- planning review
- backlog

ただし、次を常に分ける。
- review verdict != implementation permission
- docs completion != Kanban mutation
- backlog item existence != Planning Gate pass

### 8.1.4 Boundary Checks

Planning lane では次を固定する。
- candidate preview != task creation
- approval_required != approved
- auto_apply_allowed = false
- human review before backlog mutation
- human approval before implementation
- current user instruction wins

### 8.1.5 Minimal Examples

planning-only review の例:
- candidate を整理する
- docs構成案を比較する
- mutation せず human review を待つ

docs-only drafting の例:
- 指定docに planning lane の説明を追記する
- diff と boundary wording を確認する
- commit / push は行わない

status change を含まない例:
- backlog candidate の境界を説明する
- review結果を文章化する
- ready / running への変更は行わない

---

## 9. Mode and Gate Relationship

mode は「何をしてよいか」、Gate は「今やってよい状態か」を分ける。

### Core relationship

- **status** = task の位置
- **gate** = 実行可能性判断
- **mode** = 許可される操作範囲
- **approval** = 現在の高リスク許可

どれか一つだけでは不十分。

### Examples

#### planning-no-mutation-no-commit

許可:
- read-only確認
- planning draft 作成（チャット上）

禁止:
- file write
- git add / commit / push
- Kanban mutation
- worker dispatch

意味:
- Gate整理には使える
- 実装・保存には使えない

#### docs-only-no-commit

許可:
- 指定docの file write
- diff / status / check

禁止:
- git add / commit / push
- runtime code変更
- Kanban mutation

意味:
- docs化は可能
- local mutation は docs に限定

#### docs-only-local-commit-approved

許可:
- docs変更
- local commit

禁止:
- push
- PR
- runtime code変更（別途許可がない限り）

意味:
- commit はできる
- publish はできない

#### push-only

許可:
- 既存コミットの push verification
- dry-run
- push
- push後確認

禁止:
- file edits
- new commit
- Kanban mutation
- Memory mutation
- runtime changes

意味:
- push operation のみに絞る
- user の scope-bound workflow を守る

### Gate over mode

mode が file write を許していても、Gate上 blocked / approval不足なら進まない。

### Mode over intent expansion

“ついでにやる” は禁止。mode にない操作はしない。

---

## 10. Weekly Push Considerations

ユーザー運用では push は週一方針であり、Planning Gate から見ても high-risk / current approval required action として扱う。

### Push rule

push は以下が揃うまで行わない。

- current explicit push approval
- push-only などの明示mode
- 対象remote / branch が明確
- 事前確認が完了

### Pre-push expectations

最低限の例:

```bash
git status -sb
git push --dry-run origin main
```

### Post-push expectations

最低限の例:

```bash
git status -sb
git log --oneline origin/main..HEAD
git rev-list --count origin/main..HEAD
```

期待:
- 未送信コミットが 0

### Gate interpretation

- `ahead 1` は push authorization ではない
- local commit の存在も push authorization ではない
- weekly habit は原則であり、今回の current approval を代替しない

---

## 11. Examples

### Example 1: planning-only review

状況:
- task は `todo`
- mode は `planning-no-mutation-no-commit`

許可:
- read-only確認
- planning draft をチャットで整理

禁止:
- file write
- task status変更
- dispatch

判断:
- 正しい

---

### Example 2: docs-only foundation save

状況:
- mode は `docs-only-no-commit`
- 指定ファイルだけ保存許可

許可:
- `docs/product/hermes-foundation-v1.md` 作成
- `git status -sb`
- `git diff --check`

禁止:
- git add
- commit
- push
- 他docs変更

判断:
- 正しい

---

### Example 3: blocked task with tempting implementation

状況:
- task は `blocked`
- 実装アイデアは明確
- user approval はない

正しい動き:
- blocked reason を説明
- 必要なら docs-only で unblock条件を整理
- 実装しない

誤り:
- “簡単だから先にやる”

---

### Example 4: ready task but wrong mode

状況:
- task は `ready`
- mode は `review-only`
- file changeが必要

判断:
- 実行しない
- mode mismatch
- review結果だけ返す

---

### Example 5: quality finding

状況:
- Judge で低スコア
- 改善案が見えた

正しい動き:
- finding を report
- candidate として整理
- human review を待つ

誤り:
- そのまま rule変更
- そのまま task作成
- そのまま dispatch

---

### Example 6: weekly push temptation

状況:
- `main` が `origin/main` より ahead 1
- user は今 push を指示していない

判断:
- pushしない
- 必要なら push-only mode の依頼例を提示する

---

## 12. Open Questions

1. `ready` は Kanban status として明示管理するか、それとも planning judgment 層でのみ扱うか。
2. blocked reason の標準フォーマットを docs 化するか。
3. dispatcher が参照してよい gate metadata をどこまで明示するか。
4. high-risk action の分類表を別紙に分けるか。
5. weekly push review を Gate doc に残すか、Git workflow doc へ切り出すか。
6. Improvement Candidate から approved backlog への遷移テンプレートを別docにするか。
7. `done` の verification minimum を task種別ごとにテンプレ化するか。
8. runtime guard 実装に進む前に、どこまで docs-only examples を増やすべきか。

---

## 13. Next Recommended Task

次の自然な task は、Foundation pillar docs の流れとして:

```text
mode: docs-only-no-commit
Memory System Draft v0.1 を docs/product/memory-system-v1.md に保存する
```

理由:
- Planning Gate と強く接続する pillar
- `Memory is context, not authorization` を独立文書として固定できる
- Human Model と混線しやすい境界を先に明確にできる

代替候補:
- `docs/product/worker-architecture-v1.md`
- `docs/product/quality-framework-v1.md`

ただし、今回は task作成・Kanban mutation は行わない。

---

## Scope Note

この文書は Planning Gate Policy v1 Draft の保存であり、以下は行わない。

- Kanban mutation
- status変更
- task作成 / task完了
- dispatcher dispatch
- worker起動
- git add / commit / push
- workflow rerun
- PR作成
- Discord送信
- Cron化
- Hermes本体統合
- Memory mutation
- Human Model mutation
- Quality suppress behavior
- Constitution / Gate rules の自動変更
- runtime code変更
- 既存docs変更
