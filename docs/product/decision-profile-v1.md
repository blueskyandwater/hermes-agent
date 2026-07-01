# Decision Profile v1 Draft

## 1. Purpose

Decision Profile は、Hermes がユーザーの判断を **縛る** ための policy ではなく、**判断を支える参照軸** を整理するための文書である。

この文書の目的は、Hermes における Decision Profile の役割・境界・責務分離を明確にし、Decision Support / Human Model / Memory / Domain Model とどう関係するかを整理することにある。

Decision Profile が目指すもの:

- 判断時に参照すべき価値観や優先順位を見えやすくする
- ユーザーの長期志向と現在の指示を混同しない
- Domain evidence と value framing を分離する
- 高インパクト判断で、何を重く見るかを明示しやすくする
- あとから review / correction できる柔らかい判断補助軸を残す

中心原則:

> Decision Profile is a soft guide, not policy.

補足:

- Decision Profile は final decision を代行しない
- Decision Profile は current user instruction を上書きしない
- Decision Profile は user identity そのものではない
- Decision Profile は authorization source ではない
- この文書は runtime 実装を追加しない
- この文書は Human Model / Memory / Domain Model mutation を実行しない

---

## 2. Scope

この文書が扱う対象:

- Decision Profile の役割と境界
- values / priorities / constraints / risk tolerance の整理方針
- Decision Support からどう参照されるか
- Human Model / Memory / Domain Model との責務分離
- high-impact decisions における慎重な扱い
- profile freshness / correction / reviewability の原則

この文書が直接扱わない対象:

- ユーザーの全人格や identity の定義
- Domain-specific evidence の完全な整理
- 永続メモリ実装や storage schema
- policy engine / permission engine
- 自動実行 worker の dispatch 条件
- 最終決定を自動化するロジック

---

## 3. Non-goals

Decision Profile v1 の非目標。

### Non-goal 1: ユーザーの代わりに決めること

Decision Profile は framing を助けられても、決定主体にはならない。

### Non-goal 2: 過去のプロファイルで現在の意思を押し戻すこと

過去に蓄積された preference や long-term tendency があっても、現在の明示指示より優先してはならない。

### Non-goal 3: policy や constitution の代替になること

Decision Profile は soft guidance であり、禁止・許可・承認ルールそのものではない。

### Non-goal 4: Human Model の代替になること

Decision Profile は「この人は誰か」を定義しない。

### Non-goal 5: Domain Model の代替になること

Decision Profile は evidence layer ではない。根拠の強さや事実確認は Domain Model 側の責務である。

### Non-goal 6: stale profile を正しさとして固定すること

古い preference が現状とズレているなら、Profile は修正または保留されるべきであり、正解扱いしてはならない。

---

## 4. Decision Profile Boundaries

Decision Profile の境界は、以下のように整理される。

### 内側にあるもの

- ユーザーが重視しがちな価値観
- 長期的な優先順位
- 継続的な制約条件
- 典型的な risk tolerance の傾向
- 複数の選択肢を比べるときの framing 軸

### 外側にあるもの

- 実世界の事実認定そのもの
- 専門領域の根拠収集そのもの
- 承認・認可・実行許可
- その場の最新意図に反する固定ルール化
- 代行判断と断定的な指示

### 境界原則

1. Decision Profile は **判断のものさし** であって、命令ではない。
2. Decision Profile は **傾向** を表せても、必ずしも今回の結論を決めない。
3. Decision Profile は **支援文脈** だが、現在の user instruction に従属する。
4. Decision Profile は **長期参照軸** だが、stale なら弱めて扱う。
5. Decision Profile は **Memory や Domain evidence と組み合わさって初めて有用** になるが、それらを代替しない。

---

## 5. Decision Profile が扱うもの

Decision Profile が扱う主対象は、判断時の framing に関わる stable-ish な軸である。

### 5.1 Values

例:

- 自律性
- 継続性
- シンプルさ
- データ所有権
- 長期的な関係維持
- コスト効率
- 心理的納得感

Values は「何を良いと感じやすいか」を表す。

### 5.2 Priorities

例:

- 長期継続 > 短期最適化
- 可逆性 > 一発の最大効率
- 実運用の簡単さ > 理論上の最安値
- 進捗維持 > 完璧主義

Priorities は、複数の価値や条件が衝突したときの重みづけを助ける。

### 5.3 Constraints

例:

- 月額予算上限
- 時間や集中力の制約
- データローカル保存の志向
- upstream 非公開方針
- push 頻度に関する運用制約

Constraints は「望ましい」ではなく「外してはいけない／強く意識すべき」条件に近いが、Decision Profile 内ではなお soft framing として扱う。

### 5.4 Risk tolerance

例:

- コストの微増は許容するが、関係継続性は重視する
- 大きな irreversible change は避けたい
- 新規運用ルールの乱立は避けたい
- 高インパクト領域では慎重さを優先したい

Risk tolerance は、ユーザーがどの種の不確実性を嫌うかを示す。

### 5.5 Tradeoff framing

Decision Profile は以下のような比較軸を提供できる。

- speed vs confidence
- simplicity vs flexibility
- local ownership vs managed convenience
- short-term cost vs long-term continuity
- exploration vs stability

---

## 6. Decision Profile が扱わないもの

Decision Profile は便利だが、何でも入れてよい箱ではない。

### 6.1 事実そのもの

市場価格、病状、求人情報、ログ、法規制、研究結果などは Domain Model や Research の対象であり、Decision Profile に格納すべきではない。

### 6.2 承認・認可

「以前こう言っていたから今回も実行してよい」という authorization の根拠にしてはならない。

### 6.3 現在の明示指示に反する恒久ルール

ユーザーが今この場で「今回は例外でこうしたい」と言うなら、Decision Profile はその判断を拘束できない。

### 6.4 専門家の代替

医療・金融・法務・キャリアの重要判断で、Profile が専門助言の代替になることはない。

### 6.5 Identity の固定化

Decision Profile はユーザーの意思決定傾向を扱えても、「あなたはこういう人だ」と固定的に定義するためのものではない。

---

## 7. Relationship with Decision Support

Decision Support と Decision Profile の関係は密接だが、同一ではない。

### Decision Support の役割

- 選択肢を整理する
- tradeoffs を可視化する
- risks / next step / unknown を分離する
- high-impact で慎重さを上げる

### Decision Profile の役割

- その整理のときに参照する「重みづけの傾向」を提供する
- 何をユーザーが納得しやすいかの軸を補助する

### 関係原則

1. Decision Support が **構造** を作る。
2. Decision Profile が **重みづけのヒント** を与える。
3. どちらも final decision を代行しない。
4. Decision Support は Decision Profile を参照できても、従属しすぎてはならない。
5. current user instruction があれば、それが最優先になる。

言い換えると、Decision Support は「どう整理するか」、Decision Profile は「何を重く見がちか」を支える。

---

## 8. Relationship with Human Model

Human Model は support context であり、Decision Profile より広い。

### Human Model が含みうるもの

- コミュニケーション傾向
- 生活習慣
- 継続上のクセ
- 感情的な反応傾向
- 認知負荷への配慮点

### Decision Profile が含みうるもの

- 判断時に重視しやすい価値観
- リスクの取り方
- 長期優先順位
- 判断フレームの傾向

### 境界原則

- Human Model is support context, not identity.
- Decision Profile は Human Model の一部を参照してもよいが、同一視してはならない。
- Human Model から「説明の仕方」は得られても、「決定の中身」を固定してはならない。
- Human Model の傾向が見えても、今回の current intent を置き換えてはならない。

例:

- Human Model: 疲れているときは短い手順を好む
- Decision Profile: 可逆的な選択を好み、長期継続性を重視する

この2つは補完関係だが、役割は違う。

---

## 9. Relationship with Memory

Memory は context であり、authorization ではない。Decision Profile も同じ制約を共有する。

### Memory の役割

- durable facts を残す
- preferences や recurring conventions を保持する
- 毎回説明しなくてよい文脈を再利用する

### Decision Profile との違い

- Memory は事実や preference の保存が主
- Decision Profile はそれらを判断軸として整理した参照構造

### 例

Memory:

- ユーザーは upstream に PR を作らない方針
- ローカル保存とデータ所有権を重視する
- push は週一方針を取る

Decision Profile:

- 公開リスクを避ける傾向がある
- ownership / controllability を高く評価する
- 短期最適化より長期継続性を重視する

### 境界原則

1. Memory は raw context に近い。
2. Decision Profile は framing layer に近い。
3. どちらも「自動実行許可」にはならない。
4. stale memory から作られた profile は、そのまま使わず再確認が必要になる。

---

## 10. Relationship with Domain Model

Domain Model は evidence layer、Decision Profile は preference / framing layer である。

### Domain Model が担うもの

- facts
- constraints
- risks
- tradeoffs
- source quality
- domain-specific unknowns

### Decision Profile が担うもの

- 何をより重く見るか
- どの tradeoff が心理的に受け入れやすいか
- どのリスクを避けやすいか
- どの制約が長期的に重要か

### 関係原則

- Domain Model adds evidence, not orders.
- Decision Profile adds framing, not orders.
- Domain evidence が強くても final decision はユーザーに残る。
- Decision Profile があっても evidence 不足は補えない。

例:

- Domain Model: このクラウド構成は月額が安いが運用複雑性が高い
- Decision Profile: 多少高くても運用の単純さを取りやすい
- Decision Support: なら「安いが複雑」案と「高いが単純」案を比較して提示する

---

## 11. Values / Priorities / Constraints / Risk Tolerance の扱い

Decision Profile では、この4つを混ぜずに扱う。

### 11.1 Values

Values は「何が望ましいか」の方向。

例:

- 自律性
- 長期継続
- シンプルさ
- 納得感
- 可逆性

### 11.2 Priorities

Priorities は衝突時の重みづけ。

例:

- continuity > novelty
- reversible path > aggressive optimization
- one-console simplicity > absolute cheapest cloud

### 11.3 Constraints

Constraints は選択肢を狭める条件。

例:

- 予算上限
- データ所在の希望
- upstream / PR 制約
- push の頻度運用

### 11.4 Risk tolerance

Risk tolerance は、どんな失敗をどの程度まで許容するかの傾向。

例:

- 少額コスト増は許容できる
- 関係断絶やデータ喪失は嫌う
- 不可逆な変更は慎重に進めたい
- 高インパクト判断では保守側を取りやすい

### 運用原則

- Values を facts のように見せない
- Constraints を policy と誤認しない
- Risk tolerance を毎回の結論に自動変換しない
- Priorities の競合がある場合は、tradeoff として明示する

---

## 12. Soft Guide と Policy の違い

この区別は重要である。

### Soft guide の性質

- 例外を許容する
- 更新・修正されうる
- 現在の文脈で重みが変わる
- 「こうしがち」「こう考えやすい」を表す
- 説明責任を補助する

### Policy の性質

- 明示的な遵守ルールである
- 許可/禁止/承認条件に関わる
- 例外条件が別途定義される
- 実行判断に直接効くことがある

### Decision Profile が soft guide に留まる理由

1. ユーザーの判断は状況で変わりうる。
2. 過去傾向を現在に強制すると user agency を壊す。
3. values や priorities は domain facts と相互作用する。
4. 高インパクト判断ほど、profile の単純適用は危険になる。

### 重要な禁止

Decision Profile の内容を使って、以下のような扱いをしてはならない。

- 「前からそうなので今回もそれで確定」
- 「この profile があるので確認不要」
- 「この人はこういうタイプだからこの選択が正しい」

---

## 13. High-Impact Decisions での扱い

高インパクト領域では、Decision Profile の使い方をさらに慎重にする。

### 原則

- profile は framing に留める
- evidence と unknown を明確にする
- profile が current intent と衝突したら、衝突を明示する
- 強い誘導ではなく、選択肢の整理を優先する

### 13.1 Health

- 疲労、症状、継続性、安心感などの価値軸は参照できる
- ただし medical evidence や受診判断の代替にはならない
- 「以前こういう傾向だったから受診不要」といった使い方は禁止

### 13.2 Finance / Investment

- 長期志向、コスト感度、納得感、集中回避などの framing に使える
- ただし market facts や tax / legal / product-specific risk の代替にはならない
- 「この profile ならこの銘柄が正しい」と断定してはならない

### 13.3 Career / Work

- 成長機会、安定性、自律性、収益性、時間配分などの重みづけ整理に使える
- ただし current life situation や外部条件の変化を無視してはならない

### 13.4 Life decisions

- 居住、結婚、移住、大型投資、家族に関わる判断などでは、profile は補助に留める
- 長期価値観が見えても、現在の感情・事情・関係者要素を上書きしない

### 高インパクト時の最低限の出し方

少なくとも以下を分けて出す。

- Fact
- Unknown
- Value framing
- Main risks
- Reversible next step

---

## 14. Current User Instruction Wins

これは Decision Profile 運用の最重要原則の一つである。

### 原則

- 現在の明示指示が最優先
- profile は現在指示の補助にのみ使う
- current intent と profile がズレる場合、ズレを明示して current intent に従う

### なぜ必要か

1. ユーザーの判断は時間と状況で変わる
2. 過去傾向が正しくても、今回の目的は別かもしれない
3. 柔らかい profile を硬い rule にすると user agency が壊れる

### 例

- 普段は慎重でも、今回は speed を優先したい
- 普段は low-cost 重視でも、今回は continuity を優先したい
- 普段は local ownership 重視でも、今回は短期の managed convenience を取りたい

このとき Hermes は「過去傾向に反している」と叱るのではなく、差分を明示したうえで現在指示に従うべきである。

---

## 15. Profile Freshness / Review / Correction

Decision Profile は古びる。したがって freshness 管理が必要になる。

### stale になりうる理由

- ライフステージが変わる
- 予算や時間制約が変わる
- 新しい経験で risk tolerance が変わる
- 一時的な運用方針が終わる
- 過去の表現が粗すぎて誤解を生む

### freshness 原則

1. Profile は永遠の真実として扱わない。
2. 長期間参照されていても、重要判断では再確認余地を残す。
3. current instruction と矛盾したら stale 可能性を疑う。
4. repeated correction があれば profile 更新候補とみなす。

### review タイミングの例

- 高インパクト判断の前後
- 同じ種類の correction が複数回起きたとき
- 大きな生活・仕事・投資方針の変化が見えたとき
- 長期間使われていない profile を再活用するとき

### correction 原則

- correction は負けではなく正常運用
- 「以前の profile が間違い」ではなく「今の profile をより正確にする」視点で扱う
- 更新前提の柔らかい文書として維持する

---

## 16. Dangerous Examples

Decision Profile の危険な誤用例。

### 危険例 1: Profile を authorization に使う

> 「長期投資志向だから、この売買を実行してよい」

これは誤り。志向は実行許可ではない。

### 危険例 2: stale preference を current intent より優先する

> 「前にコスト重視と言っていたので、今回は安い案にします」

今回は continuity を重視したいかもしれない。現在指示を確認・尊重すべきである。

### 危険例 3: Human Model と混同して identity を固定化する

> 「あなたは慎重な人だから転職は避けるべき」

これは過度な人格化であり、支援を越えている。

### 危険例 4: Domain evidence 不足を profile で埋める

> 「この人はリスク耐性が高いので、詳細調査なしでこの投資案を勧める」

evidence 不足は profile で補えない。

### 危険例 5: soft guide を policy 化する

> 「Decision Profile に反するので、この案は採れません」

Decision Profile は veto engine ではない。

### 危険例 6: 高インパクト判断で誘導に使う

> 「あなたの価値観なら、もうこの選択で決まりです」

Hermes は choice architecture を整えても、決定の圧力をかけるべきではない。

---

## 17. Quality Framework へ渡す評価観点

Quality Framework では、Decision Profile 利用の質を以下で評価できる。

### A. Boundary correctness

- Decision Profile を policy として扱っていないか
- Decision Profile を authorization に使っていないか
- Human Model / Memory / Domain Model と混線していないか

### B. User agency preservation

- final decision がユーザーに残っているか
- 現在指示が最優先で扱われているか
- profile を使って誘導・断定していないか

### C. Freshness awareness

- stale 可能性を無視していないか
- correction の余地を残しているか
- 長期傾向と今回意図のズレを説明できているか

### D. Clarity of framing

- values / priorities / constraints / risk tolerance が分離されているか
- fact と value framing が混ざっていないか
- tradeoffs が見える形になっているか

### E. High-impact caution

- health / finance / career / life decisions で慎重さが上がっているか
- profile を短絡的な recommendation engine にしていないか

---

## 18. Worker Architecture へ渡す論点

Worker Architecture では、Decision Profile をどう扱うかについて以下の論点がある。

### 18.1 どの worker が参照できるか

候補:

- Planner: 強く参照しうる
- Decision Support 相当の整理 worker: 参照しうる
- Researcher: 原則として参照は最小限。evidence 収集に集中
- Executor: 参照しても authorization に使わない
- Reviewer: profile の誤用有無を評価できる

### 18.2 どの段階で注入するか

候補:

- framing 段階で注入
- evidence 収集の前提としては弱く注入
- execution phase では参照を制限

### 18.3 stale detection をどう扱うか

- repeated correction をどこで拾うか
- high-impact 時のみ review threshold を上げるか
- long-unused profile を自動で弱めるか

### 18.4 prompt への出し方

- identity 定義のように書かない
- soft guide と明示する
- current user instruction wins を明記する
- uncertainty や stale possibility を添える

### 18.5 logging / reviewability

- どの判断で profile を参照したか
- 参照した結果、どの framing が変わったか
- current intent と衝突があったか

---

## 19. Open Questions

Decision Profile v1 時点の未解決論点。

1. Decision Profile は Human Model の一部として持つべきか、独立文書として持つべきか。
2. values / priorities / constraints / risk tolerance の更新契機をどこまで formalize するか。
3. stale profile の自動弱化を runtime で扱うか、review process に留めるか。
4. high-impact decisions のときだけ追加確認ステップを mandatory にするか。
5. Planner / Researcher / Executor 間で、Decision Profile の見せ方を変えるべきか。
6. user-corrected preference を Memory へ保存する条件と、Decision Profile 更新条件をどう分けるか。
7. Decision Profile と Constitution の境界を、どこまで明文化するか。
8. Domain Model と Profile の衝突時に、どの表現フォーマットが最も誤解を減らすか。

---

## 20. Next Recommended Task

次に推奨されるタスクは、`docs/product/worker-architecture-v1.md` を作成し、

- Human Model
- Memory System
- Decision Support
- Domain Model
- Decision Profile

の5層が、どの worker / stage / review point で参照されるかを整理することである。

その次の候補は、`docs/product/quality-framework-v1.md` を作成して、これらの文書が品質評価でどう観測されるかを定義すること。
