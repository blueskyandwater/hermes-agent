# Domain Model v1 Draft

## 1. Purpose

Domain Model は、Hermes が投資・健康・仕事・開発・運用などの **領域ごとの判断材料** を扱うための evidence layer である。

この文書の目的は、Domain Model の役割・境界・責務分離を明確にし、Decision Support / Human Model / Memory / Decision Profile とどう関係するかを整理することにある。

Domain Model が目指すもの:

- 領域ごとの facts / constraints / risks / tradeoffs を整理する
- 高インパクト領域で evidence 基準を強める
- ユーザー理解とドメイン知識を混同しない
- 過去文脈を authorization に変質させない
- あとから review できる説明可能性を残す

中心原則:

> Domain Model adds evidence, not orders.

補足:

- Domain Model は user identity を定義しない
- Domain Model は final decision を代行しない
- Domain Model は Human Model を上書きしない
- Domain Model は Decision Support の代替ではない
- この文書は runtime 実装を追加しない
- この文書は Memory / Human Model / Decision Profile mutation を実行しない

---

## 2. Scope

この文書が扱う対象:

- Domain Model の役割と境界
- Domain Model が保持・参照してよい情報の種類
- evidence / constraints / risks / tradeoffs の整理方針
- high-impact domains に対する慎重運用
- Decision Support / Human Model / Memory / Decision Profile との責務分離
- reviewability / source requirements / user agency preservation

この文書が直接扱わない対象:

- 個別ドメインの完全な専門知識体系
- 医療・投資・法律などの専門資格を要する最終判断
- runtime の DB schema や prompt assembly 実装
- 認可・承認・policy engine
- 自動 execution worker の dispatch 条件
- ユーザーの価値観そのものの定義

---

## 3. Non-goals

Domain Model v1 の非目標。

### Non-goal 1: ユーザーの代わりに決めること

Domain Model は recommendation の根拠を増やせても、決定主体にはならない。

### Non-goal 2: ドメイン知識でユーザーの価値観を上書きすること

Domain knowledge が豊富でも、「何を優先するか」はユーザーの領域である。

### Non-goal 3: Human Model の代替

Domain Model は「この人がどういう人か」を定義しない。

### Non-goal 4: Memory の代替

Domain Model は durable user facts の保存場所ではない。

### Non-goal 5: 不確実性を隠すこと

根拠が弱いなら、弱いと明示する。Unknown は Unknown のまま残す。

### Non-goal 6: authority source になること

Domain Model に「こう書いてある」ことは、push・mutation・高リスク行為の許可にはならない。

### Non-goal 7: current instruction を過去ルールで打ち消すこと

現在の user instruction が明示されているとき、過去の domain guidance を優先してはならない。

---

## 4. Domain Model Boundaries

Domain Model の境界は、**何をドメイン文脈として扱ってよいか** と **何を扱ってはいけないか** を分けることで成立する。

### 4.1 Domain Model is domain context

Domain Model は、特定の領域で判断に必要な共通知識・制約・注意点・評価軸を整理する層である。

例:

- 投資領域のリスク要因、税・流動性・時間軸
- 健康領域の慎重姿勢、症状悪化時の受診誘導
- 仕事領域の選択肢比較、影響範囲、機会費用
- 開発領域の変更影響、テスト、ロールバック性
- 運用領域の可観測性、権限、障害半径

### 4.2 Domain Model is not user identity

Domain Model は「この領域では一般に何を見るべきか」を扱うが、「このユーザーは本質的にこういう人だ」は扱わない。

### 4.3 Domain Model is not Decision Support itself

Domain Model は evidence を供給するが、選択肢の提示順・価値観との統合・最終整理は Decision Support 側の責務である。

### 4.4 Domain Model is not Memory

Domain Model はドメイン一般の知識・判断枠組みを扱う。個人の correction / preference / durable fact は Memory 側に置く。

### 4.5 Domain Model is not authorization

Domain Model は caution を強めたり根拠を補ったりするが、実行権限を付与しない。

Boundary rule:

> Domain context can inform a recommendation, but cannot authorize an action.

---

## 5. Domain Model が扱うもの

Domain Model が扱ってよい情報の中心は、**領域に依存する判断材料** である。

### 5.1 Evidence

- 公式情報
- 一次情報
- 技術仕様
- 観測されたログや数値
- 検証済みのリスク要因
- 一般的に妥当な比較軸

### 5.2 Constraints

- 法規制
- セキュリティ制約
- 予算制約
- 時間制約
- 可用性制約
- 専門性の限界

### 5.3 Risks

- 誤判断コスト
- 実行失敗コスト
- 遅延コスト
- 可逆性の低さ
- 安全性リスク
- reputational / financial / operational impact

### 5.4 Tradeoffs

- speed vs safety
- cost vs quality
- local optimum vs long-term resilience
- certainty vs timeliness
- automation vs human review

### 5.5 Domain-specific heuristics

厳密な法則ではなく、領域内で役立つ整理原則は Domain Model に含めてよい。

例:

- 投資では expected return だけでなく downside / liquidity / concentration を見る
- 健康では軽視より受診側に倒す安全バイアスを持つ
- 運用では restart より前に observability を確認する
- 開発では変更前に target verification を行う

ただし heuristic は rule や order ではない。

---

## 6. Domain Model が扱わないもの

### 6.1 User identity

- 性格の断定
- 人格ラベル
- 「この人ならこうするはず」という固定像

### 6.2 Personal durable memory

- 好み
- 長期 correction
- 固有の運用習慣
- ユーザー固有の禁止事項

これらは Memory または Decision Profile 側の責務である。

### 6.3 Final choice

Domain Model は結論候補を補助できるが、最終決定を下さない。

### 6.4 Hidden control logic

- user manipulation
- 無断の risk escalation
- 説明のない routing bias
- 根拠のない「おすすめだから従うべき」圧力

### 6.5 Overclaimed expertise

- 医師の診断の代行
- 投資顧問の断定
- 法律判断の断定
- 人事判断の断定

---

## 7. Relationship with Decision Support

Decision Support と Domain Model は近いが別レイヤーである。

### 7.1 Domain Model provides evidence structure

Domain Model は、何が evidence で、何が constraint で、何が risk かを整理する。

### 7.2 Decision Support synthesizes across layers

Decision Support は、Domain Model の evidence を Human Model / Memory / Decision Profile / current instruction と並べて、比較しやすい形にまとめる。

### 7.3 Domain Model should not choose for Decision Support

Domain Model は options を 1 つに絞り込む authority ではない。候補を見やすくしても、価値判断の統合は Decision Support 側に残す。

### 7.4 Escalation in high-impact cases

高インパクト領域では、Decision Support は Domain Model の caution を強く参照するが、それでも最終判断はユーザーに残る。

整理すると:

- Domain Model = domain evidence layer
- Decision Support = decision organization layer

---

## 8. Relationship with Human Model

Human Model は「このユーザーにどう支えるとよいか」の理解レイヤーであり、Domain Model は「この領域で何を見るべきか」の知識レイヤーである。

### 8.1 Different questions

- Human Model: このユーザーはどういう支援だと動きやすいか
- Domain Model: この領域では何が重要な判断材料か

### 8.2 No override rule

Domain Model は Human Model を上書きしない。

例:

- Domain Model が caution-heavy でも、Human Model が「短い選択肢提示を好む」なら、伝え方は短くできる
- ただし、伝え方を短くしても caution 自体を消してよいわけではない

### 8.3 Support style vs evidence style

Human Model は提示スタイルに影響しうる。Domain Model は中身の evidence quality に影響する。

---

## 9. Relationship with Memory

Memory は user-specific durable context、Domain Model は domain-specific evidence context である。

### 9.1 Memory is personal context

Memory に入るもの:

- ユーザーの継続的な好み
- 修正された事実
- 固有の禁止事項
- 運用上の安定した前提

### 9.2 Domain Model is not a place for personal preferences

例:

- 「このユーザーは upstream に PR を出さない」→ Memory / Decision Profile
- 「PR 前には diff と status を確認する」→ domain/engineering heuristic になりうる

### 9.3 Memory is context, not authorization

Memory に「この人は普段こうする」と書いてあっても、危険操作の許可にはならない。

この原則は Domain Model と組み合わせても変わらない。

---

## 10. Relationship with Decision Profile

Decision Profile は、ユーザーの価値観・長期方針・制約・判断基準を表す soft guide である。

### 10.1 Decision Profile answers "what matters"

例:

- 長期継続を優先する
- データ所有権を重視する
- 単純さを好む
- 対話の中断リスクを避ける

### 10.2 Domain Model answers "what is materially relevant in this domain"

例:

- 投資なら concentration risk と time horizon が重要
- 健康なら red flag symptoms を見落とさない
- 運用なら rollback と observability が重要

### 10.3 Soft guide, not policy

Decision Profile も Domain Model も、current user instruction より上位の命令にはならない。

---

## 11. Evidence / Constraints / Risks / Tradeoffs の扱い

Domain Model は、単に情報を列挙するだけでは不十分で、情報の種類を分けて扱う必要がある。

### 11.1 Evidence

Evidence は、観測・仕様・一次情報・計測など、比較的検証可能な材料。

表示例:

- Fact
- Source
- Confidence
- Timestamp / freshness
- Missing context

### 11.2 Constraints

Constraints は、取りうる選択肢を制限する条件。

例:

- 予算上できない
- 権限上できない
- 時間内に安全確認できない
- 外部専門家レビューが必要

### 11.3 Risks

Risk は、「何が悪化しうるか」を表す。

例:

- 元本毀損
- 症状悪化
- キャリア機会損失
- 障害波及
- データ損失

### 11.4 Tradeoffs

Tradeoff は、複数の良いもの / 悪いものの両立不能性を示す。

例:

- 速さを取ると安全余裕が減る
- コストを下げると保守性が落ちる
- 集中投資は upside と downside の両方を増やす

### 11.5 Separation rule

Domain-specific advice では、少なくとも次を分離して表示できるのが望ましい。

- Fact
- Assumption
- Risk
- Constraint
- Value-sensitive point
- Unknown

---

## 12. High-impact Domains の扱い

高インパクト領域では、Domain Model は強い caution を持つべきである。

### 12.1 Finance / Investment

重点:

- downside risk
- liquidity
- concentration
- tax / fee impact
- time horizon mismatch
- information source quality

原則:

- 短期の熱量を長期方針と混同しない
- 期待リターンだけで押し切らない
- uncertainty を見せる
- final allocation decision はユーザーに残す

### 12.2 Health

重点:

- red flags
- symptom progression
- safety-first bias
- 緊急性
- 専門家相談の必要性

原則:

- 診断の代行をしない
- 危険サインでは受診・相談を優先する
- reassurance を事実以上に盛らない

### 12.3 Career / Work

重点:

- opportunity cost
- reputation
- learning value
- burnout risk
- reversibility
- timeline sensitivity

原則:

- 外形的成功指標だけで押さない
- ユーザーの価値観・生活条件・長期目標との整合を見る

### 12.4 Engineering / Operations

重点:

- blast radius
- rollbackability
- observability
- test coverage
- permissions
- data loss risk

原則:

- 推測で production action しない
- 変更前に確認、変更後に検証
- 危険操作では explicit approval を要求する

### 12.5 Life decisions

重点:

- irreversible impact
- identity entanglement
- long-term consequences
- emotional state
- social/financial coupling

原則:

- その場の勢いで断定支援しない
- option framing を丁寧にする
- 「今決めない」という選択肢も残す

---

## 13. Domain-specific Caution

Domain Model は、領域ごとに caution strength が異なってよい。

### 13.1 Low-impact domains

日常の軽微な判断では、迅速性を重視してもよい。

### 13.2 Medium-impact domains

一定の確認と代替案提示が望ましい。

### 13.3 High-impact domains

高インパクト領域では、次を強める。

- source quality requirement
- fact/assumption separation
- uncertainty disclosure
- user agency reminder
- explicit caution
- defer / get expert help option

### 13.4 Caution is not paralysis

慎重さは必要だが、無限に先送りすることが正解とは限らない。

Hermes の役割は、

- いま決める
- 追加確認してから決める
- 専門家に繋ぐ
- 今は決めない

という複数の正当な選択肢を見やすくすることである。

---

## 14. User Agency Preservation

Domain Model が強くなりすぎると、Hermes が「正しい答え」を押しつける危険がある。

それを防ぐ原則:

### 14.1 Final decision remains with the user

最終判断は常にユーザーに残る。

### 14.2 Evidence is not a command

根拠が強くても、それは命令ではない。

### 14.3 Present options, not hidden coercion

選択肢を出すときは、比較可能性を高める。圧をかける hidden framing は避ける。

### 14.4 Current instruction wins

過去のドメイン知見より、現在の明示的指示を優先する。

### 14.5 Allow disagreement

ユーザーが evidence を見た上で別の選択をしても、その主体性を侵害しない。

---

## 15. Reviewability / Source Requirements

Domain Model は review 可能であるべきで、特に高インパクト領域では source quality が重要になる。

### 15.1 Preferred source order

原則:

1. 公式情報
2. 一次情報
3. 信頼できる技術資料
4. コミュニティ知見
5. SNS / rumor

### 15.2 Mark source class

可能なら各主張に以下を付ける。

- source class
- freshness
- confidence
- missing context

### 15.3 Separate Fact / Unknown / Opinion / Rumor

Research 系と接続する場合、この区別は特に重要。

### 15.4 Review trail

あとから「なぜその caution だったのか」を追えるように、最低限の provenance を残す設計が望ましい。

---

## 16. Dangerous Examples

### Dangerous example 1: 投資確信の押しつけ

悪い例:

> この銘柄は将来性が高いので、今すぐ比率を上げるべきです。

問題:

- evidence と value judgment が混ざっている
- downside / concentration / liquidity が抜けている
- final decision を奪っている

望ましい形:

> 成長期待の材料はある。一方で集中リスクと時間軸の確認が必要。増やす / 現状維持 / 追加調査の3案で比較できる。

### Dangerous example 2: 健康不安の過小評価

悪い例:

> たぶん大丈夫です。様子見でOKです。

問題:

- 根拠不明
- red flag を見落とす危険
- reassurance bias

望ましい形:

> 断定はできない。もし症状の悪化、持続、強い痛み、呼吸・意識の異常があれば受診優先。軽症でも不安が強ければ相談先を使う。

### Dangerous example 3: 開発運用での過信

悪い例:

> 前も大丈夫だったので本番で直接直していいです。

問題:

- Domain Model と Memory を authorization に誤用している
- rollback / blast radius / observability を無視している

望ましい形:

> 前例は参考にはなるが、今回の権限・影響範囲・戻し手順の確認は別途必要。

### Dangerous example 4: キャリア判断の単一指標化

悪い例:

> 年収が高いのでこの選択が最善です。

問題:

- 価値軸の単純化
- burnout / learning / optionality を無視

望ましい形:

> 年収面では有利だが、学習機会・継続性・負荷も比較軸。何を優先するかはユーザー側の価値判断。

---

## 17. Quality Framework へ渡す評価観点

Quality Framework に渡すとよい観点:

### 17.1 Evidence clarity

- evidence が明示されているか
- source quality が適切か
- fact と assumption が分離されているか

### 17.2 Boundary respect

- Domain Model が user identity を定義していないか
- Decision Support を置き換えていないか
- authorization source に化けていないか

### 17.3 High-impact caution

- 高インパクト領域で caution が弱すぎないか
- 専門家相談や defer option を適切に残しているか

### 17.4 User agency

- 最終判断がユーザーに残っているか
- hidden coercion がないか

### 17.5 Reviewability

- なぜその整理になったか後追いできるか
- source / unknown / risk が見えるか

---

## 18. Worker Architecture へ渡す論点

Worker Architecture へ渡す論点:

### 18.1 Separation of responsibilities

- Researcher は domain evidence を集める
- Planner / Decision Support は選択肢整理を行う
- Executor は domain evidence を approval の代わりに使わない

### 18.2 Injection boundaries

- どの worker が Domain Model を参照できるか
- 参照しても mutation 権限には変換されないこと

### 18.3 High-impact routing

- finance / health / life decisions では caution-heavy presentation に切り替えるか
- どの条件で expert-help / defer option を前面に出すか

### 18.4 Provenance visibility

- worker 出力に source class や uncertainty を含めるか
- downstream worker が domain evidence を断定に変えない guard が必要か

### 18.5 Review loop

- Domain Model に基づく提案が過剰断定だった場合、どこで修正フィードバックを返すか

---

## 19. Open Questions

未解決論点:

1. Domain Model は domain ごとに独立文書化するか、それとも共通 schema の下に複数 profile を持つか。
2. 高インパクト領域の閾値を runtime でどう判定するか。
3. source freshness をどこまで厳密に扱うか。
4. domain-specific heuristic と user-specific preference の境界をどう実装で守るか。
5. research output から Domain Model に昇格させる条件を何にするか。
6. Domain Model と Decision Profile の conflict を runtime でどう表現するか。
7. engineering / operations の安全原則を Domain Model に入れる範囲と、実行 guard に入れる範囲をどう分けるか。

---

## 20. Next Recommended Task

次に自然なのは、`docs/product/decision-profile-v1.md` を作成して、

- Domain Model が扱う domain evidence
- Human Model が扱う support-relevant patterns
- Memory が扱う durable personal context
- Decision Support が扱う decision organization
- Decision Profile が扱う values / constraints / long-term principles

の5層の境界を明文化することである。

その次の候補は、`docs/product/worker-architecture-v1.md` を作成して、これらの文書が実際にどの worker / layer に注入されるべきかを整理すること。
