# Foundation Pillar Map v1 Draft

## 1. Purpose

Foundation Pillar Map は、Hermes Foundation 文書群の**責務・依存関係・参照順・実装前の確認順**を一枚で見渡すための地図である。

この文書の目的は、各文書の内容を再定義することではない。むしろ、すでに存在する Foundation docs を次の観点で接続し直すことにある。

- それぞれの文書は何を担当するのか
- どの文書がどの文書の前提になるのか
- 実装前にどの順番で読むべきか
- 境界違反を防ぐにはどこを見ればよいか
- quality / evolution / backlog / report がどう接続するのか
- memory / human model / decision / worker / gate がどう分離されるのか

特に重要なのは、この地図自体が**実行許可を与える文書ではない**と明示することだ。

Foundation Pillar Map が目指すもの:

- Foundation docs 全体の責務の重なりを減らす
- 「どの文書を見ればよいか」の迷いを減らす
- 実装前 review の順番を明確にする
- 文書を authorization と誤解する事故を防ぐ
- quality / evolution / backlog / report の役割差分を明確にする
- human agency を壊さない

中心原則:

> Foundation docs guide; they do not authorize execution.

補足原則:

- Roadmap defines sequence, not permission
- Planning Gate prevents premature action
- Memory is context, not authorization
- Human Model supports the user, not defines the user
- Decision Profile is soft guide, not policy
- Domain Model adds evidence, not orders
- Worker Architecture defines boundaries
- Quality Framework evaluates behavior, not the user
- Continuous Evolution proposes reviewed refinement, not autonomous mutation
- Improvement Backlog is inventory, not authorization
- Weekly Quality Report observes and reports; it does not govern

この文書は:

- runtime 実装を追加しない
- Foundation docs の内容を自動統合しない
- Kanban mutation を行わない
- Memory / Human Model / Decision Profile mutation を行わない
- worker dispatch を行わない
- Constitution / Gate rules を自動変更しない
- 実装 approval を出さない

---

## 2. Document List

Foundation Pillar Map v1 で対象とする主要文書は次のとおり。

1. `docs/product/hermes-foundation-v1.md`
2. `docs/product/planning-gate-policy-v1.md`
3. `docs/product/memory-system-v1.md`
4. `docs/product/human-model-v1.md`
5. `docs/product/decision-support-v1.md`
6. `docs/product/domain-model-v1.md`
7. `docs/product/decision-profile-v1.md`
8. `docs/product/worker-architecture-v1.md`
9. `docs/product/quality-framework-v1.md`
10. `docs/product/continuous-evolution-v1.md`
11. `docs/product/improvement-backlog-v1.md`
12. `docs/product/weekly-quality-report-v1.md`

補助的に参照されうる文書:

- `docs/product/hermes-roadmap-v1.md`
- `docs/product/hermes-product-vision-v1.md`

この map では、上記文書を「全文書が同格に並ぶ集合」とは扱わない。

役割に応じて:

- 上位の方向づけ文書
- 実行前の制御文書
- context / user-understanding 文書
- execution boundary 文書
- evaluation 文書
- evolution / backlog / report 文書

として整理する。

---

## 3. Pillar Categories

Foundation docs は、次のカテゴリに分けて読むと混乱が少ない。

### 3.1 Orientation pillars

Hermes の全体方向と前提姿勢を定義する。

- `hermes-foundation-v1.md`
- `hermes-product-vision-v1.md`
- `hermes-roadmap-v1.md`

役割:

- Hermes は何を目指すのか
- 何を大切にするのか
- どの順番で育てるのか

注意:

- 方向を示すが、実装許可は出さない
- roadmap の順番は permission ではない

### 3.2 Control and gating pillars

早すぎる実装や無許可実行を防ぐ。

- `planning-gate-policy-v1.md`
- `worker-architecture-v1.md`

役割:

- いつ進めてよいかの gate を定義する
- worker / dispatcher / guard / reviewer の境界を分ける
- mode / approval / status / current instruction の優先順位を守る

注意:

- gate は阻止できるが、勝手に approve しない
- worker architecture は責務境界であって、自動起動規則ではない

### 3.3 Human and context pillars

ユーザー理解・長期文脈・意思決定支援の材料を整える。

- `human-model-v1.md`
- `memory-system-v1.md`
- `decision-profile-v1.md`
- `decision-support-v1.md`
- `domain-model-v1.md`

役割:

- user をどう理解するか
- 何を durable context として扱うか
- decisions をどう支えるか
- domain evidence をどう区別するか

注意:

- context は authorization ではない
- user model は user を固定しない
- decision support は user の決定を代行しない

### 3.4 Evaluation and learning pillars

Hermes の行動品質を観測し、改善候補を安全に扱う。

- `quality-framework-v1.md`
- `continuous-evolution-v1.md`
- `improvement-backlog-v1.md`
- `weekly-quality-report-v1.md`

役割:

- 品質評価の基準を持つ
- 改善論点を reviewable に扱う
- 候補を inventory として保持する
- 週次 report で可視化する

注意:

- quality finding は evidence であって permission ではない
- backlog は inventory であって実行許可ではない
- weekly report は report であって governance ではない
- continuous evolution は refinement proposal であって autonomous mutation ではない

---

## 4. Responsibility Map

各文書の責務を、何をするか / 何をしないかで整理する。

### 4.1 `hermes-foundation-v1.md`

**Does**

- Foundation 全体の土台を示す
- pillar の一覧と大枠の責務を整理する
- Hermes の trust / boundary / reviewability の基準を示す

**Does not**

- 実装許可を出す
- task を ready 化する
- runtime mutation を行う

### 4.2 `planning-gate-policy-v1.md`

**Does**

- 実装前の gate 条件を明確にする
- premature action を防ぐ
- approved / not approved の境界を保つ

**Does not**

- 実装の詳細仕様を書く
- worker 実装の責務境界を定義し切る
- quality finding だけで gate を通す

### 4.3 `memory-system-v1.md`

**Does**

- durable context の保持方針を定義する
- 保存対象 / 保存しない対象 / mutation 境界を整理する
- context retrieval の考え方を整える

**Does not**

- user の identity を固定する
- memory を permission source にする
- quality / backlog / report を代替する

### 4.4 `human-model-v1.md`

**Does**

- Hermes が user をどう支えるかの理解枠を示す
- user support に必要な stable traits / preferences / constraints を整理する

**Does not**

- user を定義しきる
- user の将来判断を拘束する
- approval を代行する

### 4.5 `decision-support-v1.md`

**Does**

- Hermes が decision をどう支援するかを示す
- framing / comparison / prioritization の支援境界を整理する

**Does not**

- 最終判断を下す
- policy engine になる
- user values を上書きする

### 4.6 `domain-model-v1.md`

**Does**

- domain-specific な evidence / constraints / concepts を整理する
- decision support や planning の材料を与える

**Does not**

- orders を出す
- implementation permission を出す
- worker dispatch を決める

### 4.7 `decision-profile-v1.md`

**Does**

- user の長期価値観・制約・判断基準を soft guide として整理する
- decision support の安定した参照軸を与える

**Does not**

- hard policy になる
- runtime 実行ルールを自動生成する
- current instruction を上書きする

### 4.8 `worker-architecture-v1.md`

**Does**

- worker / planner / executor / reviewer / guard / dispatcher の境界を定義する
- access と authorization を分離する
- bounded executor としての worker を定義する

**Does not**

- worker を自動起動する
- gate を bypass する
- context を approval に変換する

### 4.9 `quality-framework-v1.md`

**Does**

- Hermes の行動品質評価軸を定義する
- score / metrics / evidence / qualitative review の考え方を与える
- quality issue を観測可能にする

**Does not**

- user を評価する
- quality finding をそのまま implementation permission にする
- rule mutation を自動実行する

### 4.10 `continuous-evolution-v1.md`

**Does**

- 改善を reviewable に継続する枠組みを示す
- quality / report / backlog から refinement themes を受け取る
- reviewed refinement を提案する

**Does not**

- 自律 mutation を行う
- issue 発見だけで rule を増やす
- backlog を飛ばして implementation を承認する

### 4.11 `improvement-backlog-v1.md`

**Does**

- 改善候補を inventory として管理する
- one-off / repeated / regression / structural gap を分類する
- review 用の candidate pool を提供する

**Does not**

- authorization を出す
- auto-dispatch する
- auto-mutation する
- candidate を即 task 実行に変える

### 4.12 `weekly-quality-report-v1.md`

**Does**

- 週次で quality を見える化する
- repeated issue / regression candidate / violation summary を report する
- human review への handoff 情報を整える

**Does not**

- governance する
- task を自動作成する
- backlog を自動更新する
- CI rerun や worker dispatch を自動実行する

---

## 5. Dependency Map

Foundation docs の依存関係は、相互に全部が依存する網ではなく、なるべく一方向で読むべきである。

### 5.1 High-level dependency shape

```text
Product Vision / Roadmap
          ↓
Hermes Foundation
          ↓
Planning Gate
          ↓
Human Model / Memory System / Decision Profile / Domain Model / Decision Support
          ↓
Worker Architecture
          ↓
Quality Framework
          ↓
Weekly Quality Report
          ↓
Improvement Backlog
          ↓
Continuous Evolution
```

これは「時間順の実行フロー」を厳密に示すものではなく、**理解の依存関係**を示す。

### 5.2 Dependency principles

- Foundation は全体地図であり、多くの文書の入口になる
- Planning Gate は実行前判断の優先レイヤーである
- Human / Memory / Decision / Domain docs は context layer を形成する
- Worker Architecture は context layer を読んだ上で、実行境界を定義する
- Quality Framework は実行後の評価軸を提供する
- Weekly Quality Report は評価結果を定期 report に変換する
- Improvement Backlog は candidate inventory を保持する
- Continuous Evolution は review 済み refinement proposal を扱う

### 5.3 Forbidden dependency assumptions

次の誤解は避けなければならない。

- Quality Framework → implementation approval
- Weekly Quality Report → automatic task creation
- Improvement Backlog → automatic worker dispatch
- Memory System → authorization source
- Decision Profile → hard policy engine
- Worker Architecture → dispatch permission
- Continuous Evolution → autonomous mutation

### 5.4 Soft versus hard dependencies

**Harder reading dependency**

- `worker-architecture-v1.md` を読む前に `planning-gate-policy-v1.md` の理解が必要
- `weekly-quality-report-v1.md` を読む前に `quality-framework-v1.md` の理解が必要
- `improvement-backlog-v1.md` を読む前に `weekly-quality-report-v1.md` または `quality-framework-v1.md` の理解が望ましい
- `continuous-evolution-v1.md` を読む前に `quality-framework-v1.md` と `improvement-backlog-v1.md` の理解が望ましい

**Softer contextual dependency**

- `decision-support-v1.md` は `human-model-v1.md` / `decision-profile-v1.md` / `domain-model-v1.md` と接続して読むと意味が安定する
- `memory-system-v1.md` は `human-model-v1.md` と合わせて読むと mutation 境界が分かりやすい

---

## 6. Reading Order

実装前に Foundation docs を読む順番は、目的によって少し変わる。

### 6.1 Default reading order

1. `hermes-foundation-v1.md`
2. `planning-gate-policy-v1.md`
3. `human-model-v1.md`
4. `memory-system-v1.md`
5. `decision-profile-v1.md`
6. `domain-model-v1.md`
7. `decision-support-v1.md`
8. `worker-architecture-v1.md`
9. `quality-framework-v1.md`
10. `weekly-quality-report-v1.md`
11. `improvement-backlog-v1.md`
12. `continuous-evolution-v1.md`
13. `foundation-pillar-map-v1.md` を見直し用 index として使う

### 6.2 Fast reading order for implementation planning

1. `hermes-foundation-v1.md`
2. `planning-gate-policy-v1.md`
3. `worker-architecture-v1.md`
4. `quality-framework-v1.md`
5. 必要に応じて `memory-system-v1.md` / `human-model-v1.md` / `decision-profile-v1.md`

### 6.3 Fast reading order for quality review

1. `quality-framework-v1.md`
2. `weekly-quality-report-v1.md`
3. `improvement-backlog-v1.md`
4. `continuous-evolution-v1.md`
5. 必要に応じて `planning-gate-policy-v1.md`

### 6.4 Fast reading order for user-model-sensitive work

1. `human-model-v1.md`
2. `memory-system-v1.md`
3. `decision-profile-v1.md`
4. `decision-support-v1.md`
5. `planning-gate-policy-v1.md`

---

## 7. Implementation Decision Flow

実装前の判断は、Foundation docs を次の順序で参照すると安全である。

### Step 1: 方向確認

読む文書:

- `hermes-foundation-v1.md`
- 必要に応じて `hermes-product-vision-v1.md`
- 必要に応じて `hermes-roadmap-v1.md`

問い:

- これは Hermes の長期方向と矛盾しないか
- capability expansion ではなく trust refinement を壊していないか

### Step 2: 実行許可の有無確認

読む文書:

- `planning-gate-policy-v1.md`

問い:

- これは本当に今やってよいのか
- approval はあるか
- read-only なのか implementation なのか
- docs があることを permission と誤解していないか

### Step 3: context 参照境界確認

読む文書:

- `memory-system-v1.md`
- `human-model-v1.md`
- `decision-profile-v1.md`
- `domain-model-v1.md`
- `decision-support-v1.md`

問い:

- 何を read してよいか
- 何を mutate してはいけないか
- context を approval source と誤解していないか

### Step 4: execution boundary 確認

読む文書:

- `worker-architecture-v1.md`

問い:

- どの role が何をしてよいか
- dispatch / guard / review / execution を混同していないか
- bounded executor の範囲を超えていないか

### Step 5: quality impact 確認

読む文書:

- `quality-framework-v1.md`

問い:

- この変更でどの quality dimension が改善 / 悪化しうるか
- 測れるのか
- user を評価する設計になっていないか

### Step 6: post-change learning flow 確認

読む文書:

- `weekly-quality-report-v1.md`
- `improvement-backlog-v1.md`
- `continuous-evolution-v1.md`

問い:

- 結果をどこで観測するか
- 改善候補化はどう行うか
- 自動 mutation しない境界は守られているか

### Summary rule

> 実装前に読むべきなのは「何を作るか」だけではなく、「何をしてはいけないか」を定義する文書群である。

---

## 8. Boundary Flow

Foundation docs の境界フローは、「読む」「支える」「止める」「評価する」「提案する」を分けることに意味がある。

### 8.1 Boundary roles

- Foundation: 全体地図を与える
- Planning Gate: premature action を止める
- Memory / Human / Decision / Domain: context を支える
- Worker Architecture: 実行責務を分離する
- Quality Framework: 行動を評価する
- Weekly Quality Report: 評価を report に変換する
- Improvement Backlog: 候補を inventory として持つ
- Continuous Evolution: review 済み refinement を提案する

### 8.2 Boundary law

各レイヤーは隣接レイヤーの役割を奪ってはならない。

例:

- Memory が approval source になってはいけない
- Weekly Report が governance になってはいけない
- Improvement Backlog が dispatch queue になってはいけない
- Continuous Evolution が mutation engine になってはいけない
- Worker Architecture が current user instruction を上書きしてはいけない

### 8.3 Current instruction supremacy

すべての Foundation docs をまたいで重要なのは次の原則である。

> Current user instruction wins.

過去の docs・過去の candidate・過去の repeated issue・過去の report は context にはなるが、現在の禁止事項や mode より上位にはならない。

---

## 9. Quality / Evolution Flow

quality と evolution は近いが、同一ではない。

### 9.1 Quality flow

```text
Observed behavior
    ↓
Quality Framework で評価
    ↓
Weekly Quality Report で可視化
    ↓
Human review
```

### 9.2 Evolution flow

```text
Human-reviewed findings
    ↓
Improvement candidate として整理
    ↓
Improvement Backlog に在庫化
    ↓
Continuous Evolution で refinement themes を議論
    ↓
必要なら別途 approval を経て implementation planning へ
```

### 9.3 Key separation

- Quality Framework は評価軸
- Weekly Quality Report は定期 report
- Improvement Backlog は在庫
- Continuous Evolution は review された改善論点の整理と refinement proposal

この4つは連携するが、どれも単独で実装 authorization にはならない。

---

## 10. Memory / Human Model / Decision Flow

ユーザー理解まわりの文書は、互いに近いが責務が異なる。

### 10.1 Flow shape

```text
Human Model
   ↓
Memory System
   ↓
Decision Profile
   ↓
Domain Model
   ↓
Decision Support
```

これは厳密な runtime pipeline ではなく、**理解の積み重ね順**を示す。

### 10.2 Responsibility split

**Human Model**
- user をどう支えるかの理解枠
- user を固定しない

**Memory System**
- durable context の管理
- authorization にしない

**Decision Profile**
- 長期判断の soft guide
- policy にしない

**Domain Model**
- evidence / constraints / concepts
- orders にしない

**Decision Support**
- 判断を助ける framing
- final decision を代行しない

### 10.3 Mutation caution

この領域は特に mutation 境界が重要である。

- user support のための理解と、user identity の固定は違う
- context retention と implicit policy generation は違う
- decision support と decision substitution は違う

---

## 11. Worker / Gate / Quality Flow

実行系の安全性は、worker だけを見ても足りない。gate と quality を同時に見る必要がある。

### 11.1 Flow shape

```text
Current instruction
    ↓
Planning Gate
    ↓
Worker Architecture
    ↓
Observed behavior
    ↓
Quality Framework
    ↓
Weekly Quality Report
```

### 11.2 Why this matters

- Planning Gate がないと premature action が起きる
- Worker Architecture がないと role confusion が起きる
- Quality Framework がないと「動いたかどうか」しか見なくなる
- Weekly Quality Report がないと trend と repeated issue が埋もれる

### 11.3 Non-equivalences

次のものは同じではない。

- gate pass ≠ quality success
- quality finding ≠ implementation approval
- worker capability ≠ worker permission
- report visibility ≠ governance right

---

## 12. Docs That Authorize Nothing

以下の文書は、存在していても単独では何も authorize しない。

- `hermes-foundation-v1.md`
- `hermes-product-vision-v1.md`
- `hermes-roadmap-v1.md`
- `human-model-v1.md`
- `memory-system-v1.md`
- `decision-profile-v1.md`
- `decision-support-v1.md`
- `domain-model-v1.md`
- `quality-framework-v1.md`
- `continuous-evolution-v1.md`
- `improvement-backlog-v1.md`
- `weekly-quality-report-v1.md`
- `foundation-pillar-map-v1.md`

補足:

`planning-gate-policy-v1.md` は authorization を直接発行する文書というより、**authorization の欠如を見抜き、premature action を止める文書**として理解すべきである。

### Practical rule

> Documentation presence is not execution permission.

### Common failure mode

- 「roadmap にあるからやってよい」
- 「backlog にあるから実装してよい」
- 「weekly report に出たから直してよい」
- 「memory にあるからそのまま決めてよい」

これらはすべて誤りである。

---

## 13. Docs to Read Before Implementation

実装前は最低でも次を読む。

### Minimum set

1. `docs/product/hermes-foundation-v1.md`
2. `docs/product/planning-gate-policy-v1.md`
3. `docs/product/worker-architecture-v1.md`
4. `docs/product/quality-framework-v1.md`

### Conditional set

対象によって追加で読む。

- Memory を読む / 触る可能性がある → `memory-system-v1.md`
- User understanding に触れる → `human-model-v1.md`
- Decision support に触れる → `decision-profile-v1.md` / `decision-support-v1.md`
- Domain reasoning を使う → `domain-model-v1.md`
- Quality learning loop に影響する → `weekly-quality-report-v1.md` / `improvement-backlog-v1.md` / `continuous-evolution-v1.md`

### Rule

> 実装対象の機能文書だけではなく、境界文書も読む。

---

## 14. Docs to Read Before Memory or Human Model Mutation

Memory / Human Model mutation は、特に user agency を傷つけやすいので慎重であるべき。

読む文書:

1. `docs/product/human-model-v1.md`
2. `docs/product/memory-system-v1.md`
3. `docs/product/decision-profile-v1.md`
4. `docs/product/planning-gate-policy-v1.md`
5. 必要に応じて `docs/product/decision-support-v1.md`

確認する問い:

- これは durable fact か
- これは user identity を固定する書き方ではないか
- current instruction より過去の記録を優先していないか
- mutation permission は本当にあるか
- support のための context と hidden policy を混同していないか

### Rule

> Memory and Human Model may inform support, but must not silently redefine the user.

---

## 15. Docs to Read Before Worker Dispatch

worker dispatch 前に見るべき文書:

1. `docs/product/planning-gate-policy-v1.md`
2. `docs/product/worker-architecture-v1.md`
3. `docs/product/hermes-foundation-v1.md`
4. 必要に応じて `docs/product/quality-framework-v1.md`

確認する問い:

- dispatch してよい approval があるか
- mode は何か
- worker は bounded executor として収まっているか
- planner / executor / reviewer / guard の役割を取り違えていないか
- current user instruction を上書きしていないか

### Rule

> Worker availability is not dispatch permission.

---

## 16. Docs to Read Before Quality/Evolution Changes

quality or evolution まわりを変える前に見る文書:

1. `docs/product/quality-framework-v1.md`
2. `docs/product/weekly-quality-report-v1.md`
3. `docs/product/improvement-backlog-v1.md`
4. `docs/product/continuous-evolution-v1.md`
5. `docs/product/planning-gate-policy-v1.md`
6. 必要に応じて `docs/product/worker-architecture-v1.md`

確認する問い:

- これは evaluation 変更なのか governance 変更なのか
- report と authorization を混同していないか
- backlog を dispatch queue 化していないか
- continuous evolution を mutation engine 化していないか
- rule bloat を増やしていないか

### Rule

> Quality and evolution layers should improve reviewability, not automate authority.

---

## 17. Dangerous Misunderstandings

Foundation Pillar Map が特に防ぎたい危険な誤解を列挙する。

### Misunderstanding 1: roadmap にあるから今やってよい

誤り。

Roadmap は順番を示す。permission は示さない。

### Misunderstanding 2: Planning Gate を通るのは docs があるから

誤り。

docs の存在は条件の一つたりえても、approval の代替にはならない。

### Misunderstanding 3: Memory があるから自動判断してよい

誤り。

Memory は context であって authorization source ではない。

### Misunderstanding 4: Human Model が user を定義する

誤り。

Human Model は support のための理解枠であり、user identity の固定化文書ではない。

### Misunderstanding 5: Decision Profile は policy である

誤り。

Decision Profile は soft guide であり、hard rule engine ではない。

### Misunderstanding 6: Domain Model が orders を出す

誤り。

Domain Model は evidence を増やす。命令しない。

### Misunderstanding 7: Worker Architecture が dispatch を正当化する

誤り。

worker が存在しても、dispatch permission があるとは限らない。

### Misunderstanding 8: Quality Framework の finding は implementation permission である

誤り。

quality finding は evidence にすぎない。

### Misunderstanding 9: Weekly Quality Report は governance である

誤り。

report は report であり、統治権ではない。

### Misunderstanding 10: Improvement Backlog は task queue である

誤り。

backlog は inventory であり、dispatch queue ではない。

### Misunderstanding 11: Continuous Evolution は自律改善機構である

誤り。

reviewed refinement proposal であって、自動 mutation ではない。

### Misunderstanding 12: Foundation Pillar Map 自体が implementation checklist を代替する

誤り。

この文書は地図であって、対象実装の仕様書でも gate pass でもない。

---

## 18. Open Questions

Foundation Pillar Map v1 の時点で残る論点:

1. `hermes-product-vision-v1.md` と `hermes-foundation-v1.md` の責務差分を、今後どこまで明示的に分離するか。
2. `hermes-roadmap-v1.md` を Foundation 本体の pillar 扱いにするか、補助文書扱いのままにするか。
3. `decision-support-v1.md` と `decision-profile-v1.md` の境界を、今後 provider / runtime に落とす前にどの粒度で固定するか。
4. `weekly-quality-report-v1.md` と `improvement-backlog-v1.md` の handoff schema を、文書間参照だけで足りるのか、別 interface doc が必要か。
5. `continuous-evolution-v1.md` が扱う refinement theme の粒度を、 rule / workflow / prompt / scoring のどこまで含めるか。
6. worker / gate / quality の接続を、将来の implementation readiness review でどこまで checklist 化するか。
7. Foundation docs 群の index をこの Pillar Map だけで足りるとするか、それとも separate glossary / dependency graph artifact を追加するか。

---

## 19. Next Recommended Task

次に作ると接続がさらに明確になる候補は次の3つ。

### Option A: Foundation Reading Paths v1

目的別に「どの依頼で何を何分で読むか」を短く整理する。

向いている理由:

- 実装前の迷いをさらに減らせる
- docs index としての実用性が高い
- Pillar Map を運用面に落としやすい

### Option B: Quality-to-Backlog Handoff v1

Weekly Quality Report → Improvement Backlog の handoff 境界だけを切り出して、report と candidate inventory の差分をより厳密にする。

向いている理由:

- report / candidate / task の混同をさらに減らせる
- no auto-mutation の境界を強化できる

### Option C: Implementation Readiness Review v1

実装前レビューの読み順・確認項目・禁止ショートカットをまとめる。

向いている理由:

- Planning Gate と Worker Architecture の運用接続が良くなる
- docs が増えた分の review burden を軽くできる

現時点での推奨は Option C である。

理由:

- Foundation docs 群はかなり揃ってきた
- 次のボトルネックは「どれをどう見て実装判断に入るか」の運用整理になりやすい
- Planning Gate / Worker Architecture / Quality Framework の接続を一段実務化できる

### Final reminder

> Foundation Pillar Map helps humans and agents navigate the docs. It does not grant permission to act.
