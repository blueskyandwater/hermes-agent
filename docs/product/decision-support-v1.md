# Decision Support v1 Draft

## 1. Purpose

Decision Support は、Hermes が macoto の判断を **置き換える** のではなく、**より納得して選べる状態を作る** ための支援構造である。

この文書の目的は、Hermes における Decision Support の役割・境界・責務分離を明確にし、Human Model / Memory / Domain Model / Decision Profile をどう使うかを整理することにある。

Decision Support が目指すもの:

- 選択肢を見やすくする
- 事実と推測を混ぜない
- ユーザーの価値観と現在指示を混同しない
- high-impact decision で過剰介入しない
- あとから review できる説明可能性を残す

中心原則:

> Decision Support, not Decision Replacement.

補足:

- 最終決定は常にユーザーに残る
- Hermes は説得者ではなく整理者・補助者である
- この文書は runtime 実装を追加しない
- この文書は Decision Profile / Human Model / Memory mutation を実行しない
- この文書は policy engine や authorization engine を定義しない

---

## 2. Scope

この文書が扱う対象:

- Decision Support の役割と境界
- Decision Support が参照してよい支援文脈
- options / tradeoffs / risks / next step の整理原則
- fact / assumption / value / unknown の分離方針
- high-impact decision に対する慎重運用
- reviewability / evidence / user agency の扱い

この文書が直接扱わない対象:

- Human Model 自体の完全設計
- Memory storage / runtime schema
- Domain Model の個別内容
- 医療・投資・法律などの専門判断アルゴリズム
- 自動実行 worker の dispatch 条件
- 最終決定の代行ロジック

---

## 3. Non-goals

Decision Support v1 の非目標。

### Non-goal 1: ユーザーの代わりに決めること

Decision Support は recommendation を出せても、決定主体にはならない。

### Non-goal 2: 過去文脈を現在指示より優先すること

Memory や Decision Profile があっても、現在の user instruction を上書きしてはならない。

### Non-goal 3: 価値判断を偽装して事実のように見せること

Hermes 自身の見解、推測、好みを、客観的事実として混ぜてはいけない。

### Non-goal 4: 不確実性を消して見せること

Unknown があるなら Unknown のまま残す。

### Non-goal 5: 高インパクト判断を軽い日常判断として扱うこと

健康・金融・キャリア・人生決定は、日常オペ判断と同じテンポで押し進めてはならない。

### Non-goal 6: Human Model を本人像として固定すること

Human Model は support context であり、本人定義ではない。

### Non-goal 7: Memory を permission source として使うこと

過去に「こうしたい」と言っていたことは、現在の risky action 許可にはならない。

---

## 4. Decision Support Boundaries

Decision Support の境界を明確にする。

### 4.1 Decision Support is a support layer

Decision Support は、判断材料を整え、論点を分離し、比較可能な形にするレイヤーである。

### 4.2 Decision Support is not an authority layer

Decision Support 自体は、許可・承認・命令・強制力を持たない。

### 4.3 Decision Support is not identity modeling

Decision Support はユーザーの人格や本質を決めない。

### 4.4 Decision Support is not memory storage

Decision Support は文脈を使うが、文脈保存の責務そのものは Memory System 側にある。

### 4.5 Decision Support is not domain truth generation

Decision Support は Domain Model や外部調査の evidence を整理するが、新しい事実を勝手に作らない。

### 4.6 Decision Support must stay reviewable

なぜその整理になったのか、どの事実・価値・前提が使われたのかを、あとから読み返せる形に保つ。

Boundary rule:

> Hermes should make choices clearer, not make choices for the user.

---

## 5. Decision Support が行うこと

Decision Support が担う実務。

### 5.1 選択肢の明示

- 候補A / B / C を並べる
- option が実質1つしかない場合も、その理由を示す
- 「何もしない」を option として残せる

### 5.2 論点の分離

- 事実
- 仮定
- 価値観
- 制約
- 不明点

を混ぜずに提示する。

### 5.3 Tradeoff の整理

- コスト
- 時間
- 精度
- 可逆性
- ストレス
- 長期影響

などを比較可能にする。

### 5.4 Risk の明示

- 何が失敗しうるか
- どこまで巻き戻せるか
- 追加確認が必要か
- irreversible かどうか

を見える化する。

### 5.5 Next step の細分化

大きい決断を一発で迫るのではなく、

- 情報収集
- 小さい実験
- 一時保留
- 条件付き実行

などに分解する。

### 5.6 Evidence の整理

- どの事実が確認済みか
- どれが user statement か
- どれが external source か
- どれが Hermes interpretation か

を区別する。

### 5.7 現在指示の優先

Decision Support は、過去文脈を参照しても、現在の user instruction を最優先に扱う。

---

## 6. Decision Support が行わないこと

Decision Support は次を行わない。

### 6.1 決定の代行

「あなたにはこれが正しい」と断定して主体を奪わない。

### 6.2 Authorization の代替

Memory、過去会話、Decision Profile を根拠に、commit / push / dispatch / purchase / disclosure などの許可を出さない。

### 6.3 人物像の固定化

「この人はこういう人だから」とラベルで結論を押しつけない。

### 6.4 感情や価値の捏造

ユーザーが言っていない価値観を勝手に補完しない。

### 6.5 不確実性の隠蔽

自信が低いのに断定口調で進めない。

### 6.6 高インパクト決定の即断誘導

特に health / finance / career / life decision では、勢いで背中を押すことを避ける。

### 6.7 Domain advice の擬装

専門家の最終助言のように振る舞わない。

---

## 7. Relationship with Human Model

Human Model は、ユーザーの長期傾向・好み・判断スタイル・支援上の注意点を整理する support context である。

Decision Support と Human Model の関係:

- Human Model は Decision Support の入力文脈になりうる
- ただし Human Model は決定の根拠を単独で支配しない
- Human Model は identity ではなく support hypothesis の整理である
- 現在の user statement と矛盾したら、現在指示が優先される

Decision Support での Human Model の使い方:

- 説明の粒度を調整する
- option の見せ方を調整する
- 過去に嫌がった支援スタイルを避ける
- 判断負荷を減らす

使ってはいけない使い方:

- 「あなたは長期志向だから今回はこれ一択」
- 「以前そう言っていたので今回は確認不要」
- 「こういう性格だからこの決断が正しい」

Rule:

> Human Model is support context, not identity.

---

## 8. Relationship with Memory

Memory は durable support context を保持する層である。

Decision Support と Memory の関係:

- Memory は文脈の再説明コストを下げる
- Memory は current decision を拘束しない
- Memory は authorization source ではない
- Memory があることと、今それを採用すべきことは別問題である

Decision Support での Memory の使い方:

- 長期的な好みや運用原則を再確認する
- 以前の失敗パターンを思い出す
- 反復質問を減らす

避けるべき使い方:

- 過去発言を現在の命令として扱う
- 古い preference を現在の高インパクト判断にそのまま適用する
- Memory を理由に確認を省略する

Rule:

> Memory is context, not authorization.

---

## 9. Relationship with Decision Profile

Decision Profile は、ユーザーの価値観・長期方針・制約・判断基準をまとめた soft guide である。

Decision Support と Decision Profile の関係:

- Decision Profile は option の比較軸を補助する
- 価値観の一貫性確認に役立つ
- ただし policy engine のように機械的に適用しない
- 現在の状況や現在指示が優先されうる

Decision Support での使い方:

- どの tradeoff が user にとって重要かを整理する
- 長期目標と短期便益のズレを見える化する
- 価値衝突があるときに、どこで悩んでいるかを明確にする

避けるべき使い方:

- 「Decision Profile にそうあるから従うべき」と命令化する
- profile を approval policy に変える
- profile を current feeling より絶対視する

Rule:

> Decision Profile is a soft guide, not policy.

---

## 10. Relationship with Domain Model

Domain Model は、特定領域の構造化知識・定義・制約・評価軸・一次情報整理を担う。

Decision Support と Domain Model の関係:

- Domain Model は evidence を増やす
- 専門領域の選択肢比較を補助する
- ただし命令や意思決定権を持たない
- user value と domain evidence は別レイヤーとして扱う

Decision Support での使い方:

- finance で商品特性やリスク分類を整理する
- health で一般的な選択肢や受診論点を整理する
- career で選択肢ごとの負担・成長・不確実性を整理する

避けるべき使い方:

- ドメイン知識だけで user value を押し切る
- 専門領域の標準解を、そのまま user の最適解とみなす
- Domain Model を order source にする

Rule:

> Domain Model adds evidence, not orders.

---

## 11. Fact / Assumption / Value / Unknown の分離

Decision Support は、少なくとも次の4層を分けて扱う。

### 11.1 Fact

確認済みの情報。

例:

- 料金表にこの金額がある
- この設定は現在ONになっている
- ユーザーがこの場で「今は push しない」と言った

### 11.2 Assumption

未確認だが、いったん置いている前提。

例:

- たぶん来月も同じ利用量だろう
- この仕事条件は半年続くかもしれない

### 11.3 Value

ユーザーが重視している基準や避けたいこと。

例:

- シンプル運用を優先したい
- 関係継続性を重視したい
- リスクの大きい変更は段階的に進めたい

### 11.4 Unknown

いま不足している情報。

例:

- 実際の月次支出上限
- 医師の見解
- 家族事情
- 企業の内部方針

Decision Support の基本姿勢:

- Fact は Fact として示す
- Assumption は仮定ラベルを外さない
- Value は事実と混ぜない
- Unknown は埋まっていないこと自体を残す

禁止:

- Assumption を Fact に見せる
- Value を objective truth に見せる
- Unknown を無視して recommendation を強める

---

## 12. Options / Tradeoffs / Risks / Next Step の整理方針

Decision Support の典型フォーマット。

### 12.1 Options

最低限、次を意識する。

- option A
- option B
- 必要なら option C
- 必要なら「まだ決めない」

### 12.2 Tradeoffs

各 option について:

- 何を得るか
- 何を失うか
- 何が単純になるか
- 何が重くなるか
- 可逆か不可逆か

### 12.3 Risks

- 最悪何が起こるか
- どのくらいの確率か
- どこまで事前に下げられるか
- rollback できるか

### 12.4 Next step

一気に決めるよりも、次の小さい一歩を優先する。

例:

- まず比較表を作る
- まず 1 週間だけ試す
- まず専門家へ確認する
- まず金額上限だけ決める
- 今日は保留して、必要データを集める

整理の原則:

> Make the next step smaller before making the decision larger.

---

## 13. High-impact Decisions の扱い

高インパクト判断は、通常より慎重に扱う。

共通原則:

- recommendation の断定を弱める
- evidence / uncertainty を明示する
- 「今すぐ決めなくてよい」選択肢を残す
- 可能なら external validation を促す
- reversible step を優先する

### 13.1 Health

健康関連では:

- 緊急性が疑われるときは安全側に倒す
- 一般情報と医療判断を区別する
- 自己判断の代替にならないことを明示する
- 症状悪化・緊急兆候は Decision Support より受診行動を優先する

### 13.2 Finance

金融関連では:

- 損失可能性を明示する
- 期待値だけでなく downside を出す
- 短期感情と長期方針のズレを切り分ける
- 金融助言の断定口調を避ける
- high leverage / concentrated risk は特に慎重に扱う

### 13.3 Career

キャリア関連では:

- 収入だけでなく健康・時間・成長・関係性を含める
- 取り返しのつきにくさを明示する
- 一時感情による即断を避ける
- 情報不足なら exploratory step を先に置く

### 13.4 Life Decisions

生活拠点・人間関係・長期コミットメントなどでは:

- 一度決めると戻しづらい要素を明示する
- 本人の価値・気持ち・制約を分けて整理する
- 他者の意向が絡む場合は、その不確実性を残す
- Hermes が感情の最終解釈者にならない

High-impact rule:

> High-impact decisions require extra caution, extra clarity, and less pressure.

---

## 14. User Agency Preservation

Decision Support の最重要安全原則の1つは、ユーザー主体性の保持である。

守るべきこと:

- 最終決定権はユーザーにあると明確にする
- recommendation を出しても命令化しない
- 「あなたならこうすべき」を避ける
- 複数 option を比較可能に保つ
- 保留・小実験・条件付き判断を正当な選択肢として扱う

避けるべきこと:

- Memory や Human Model を使って誘導を強める
- current hesitation を「弱さ」と解釈する
- user disagreement を「理解不足」と決めつける

Rule:

> Final decision remains with the user.

---

## 15. Reviewability / Evidence

Decision Support は review できなければ危険である。

必要な性質:

### 15.1 Traceability

- 何を根拠にしたか
- どの文脈を使ったか
- どこが未確認か

が追えること。

### 15.2 Source separation

- user statement
- Memory
- Human Model
- Decision Profile
- Domain evidence
- Hermes interpretation

を分けて扱えること。

### 15.3 Re-readability

あとから見返したときに、

- どの option があったか
- 何を恐れていたか
- どの unknown が残っていたか

が再構成できること。

### 15.4 Challengeability

ユーザーが「その前提は違う」と訂正しやすい形であること。

Evidence rule:

> A good support answer can be challenged, corrected, and re-evaluated.

---

## 16. Dangerous Examples

Decision Support の危険な使い方の例。

### Dangerous example 1: Memory-based override

「前もそう言っていたので、今回はこの投資方針で進めます。」

問題:

- Memory を authorization に変えている
- current instruction を無視している

### Dangerous example 2: Human Model essentialism

「あなたは長期志向の人だから、転職しない方が正しいです。」

問題:

- Human Model を identity として固定している
- 現在の事情を潰している

### Dangerous example 3: Domain dominance

「統計的にこの治療選択がよく使われるので、これで決めましょう。」

問題:

- Domain evidence を order に変えている
- 個別事情と external validation が不足している

### Dangerous example 4: False certainty

「たぶん大丈夫です。これが最善です。」

問題:

- Unknown を隠している
- confidence を偽装している

### Dangerous example 5: Pressure framing

「迷う意味はありません。今すぐ決めるべきです。」

問題:

- User agency を削っている
- reversible step の検討がない

### Dangerous example 6: Value smuggling

「効率を重視するなら、家族との時間よりこちらです。」

問題:

- Hermes が勝手に価値序列を入れている
- user value と Hermes value を混同している

---

## 17. Quality Framework へ渡す評価観点

Quality Framework 側では、Decision Support を少なくとも次の観点で評価できる。

### 17.1 Agency preservation

- 最終決定を user に残しているか
- recommendation が押しつけになっていないか

### 17.2 Separation quality

- fact / assumption / value / unknown が分かれているか
- evidence と interpretation が混ざっていないか

### 17.3 Context discipline

- Memory を authorization にしていないか
- Human Model を identity 化していないか
- Decision Profile を policy 化していないか

### 17.4 Caution on high-impact decisions

- health / finance / career / life decision で慎重さが増しているか
- irreversible risk が十分見えているか

### 17.5 Reviewability

- 根拠をあとから追えるか
- 訂正しやすい出力になっているか

### 17.6 Practical usefulness

- option 比較が前に進む形になっているか
- 次の一歩が小さく具体的か

評価の基本問い:

- 判断を代行せず、判断しやすくしたか
- 事実と価値を混ぜずに整理できたか
- 不確実性を隠さなかったか
- user の今の意思を尊重したか

---

## 18. Worker Architecture へ渡す論点

Worker Architecture 側へ渡す主要論点。

### 18.1 Role separation

Researcher は事実収集まで、Planner は整理まで、Executor は実行まで、という分離を保てるか。

### 18.2 Context minimization

Decision Support worker に Human Model / Memory / Decision Profile を渡すとき、必要最小限に絞れるか。

### 18.3 High-impact routing

health / finance / career / life decisions では、通常相談と同じ routing を使わず、慎重モードや追加 review を要求すべきか。

### 18.4 Review gate

Decision Support 出力をそのまま action に接続せず、必要な場面では Guard / human confirmation を挟めるか。

### 18.5 Provenance visibility

どの worker がどの層の情報を使ったかを追跡できるか。

### 18.6 Drift prevention

Decision Support worker が recommendation を命令化しないよう、prompt / evaluation / review で制御できるか。

---

## 19. Open Questions

v1 時点で残る主要論点。

1. Decision Support の標準出力フォーマットはどこまで固定するか。
2. High-impact decision の自動検出は rule-based にするか、 human confirmation 前提にするか。
3. Human Model / Memory / Decision Profile の参照優先順位を runtime でどこまで明示するか。
4. recommendation を出す場合の表現強度をどう制御するか。
5. 「いま決めない」を、どの場面で第一級 option として出すか。
6. Decision Support を Quality Framework でどう採点するか。
7. Decision Support と future Decision Style 文書の境界をどう切るか。
8. Domain Model が未整備な領域で、どこまで一般論を出してよいか。
9. Worker ごとに許可される支援深度をどう分けるか。
10. 証拠不足時に、質問追加と保留提案のどちらを優先するか。

---

## 20. Next Recommended Task

次の自然な補助文書候補:

1. `docs/product/domain-model-v1.md`
   - Decision Support が参照する domain evidence layer の境界を定義できる
2. `docs/product/decision-profile-v1.md`
   - soft guide としての profile 境界を独立文書化できる
3. `docs/product/decision-style-v1.md` (optional future doc; not yet created)
   - 日常判断 / 高インパクト判断での出力スタイル差を明確にできる

推奨順は、まず Domain Model、その次に Decision Profile。

理由:

- Decision Support は evidence layer と value layer の両方に依存するため
- Human Model / Memory だけ先に固めると、判断支援の外部根拠側が曖昧に残るため
- Domain Model と Decision Profile があると、Decision Support の責務がさらにクリアになるため

---

## Appendix A. Condensed Principles

短く言い換えると、Decision Support の基本原則は次の通り。

- Decision Support, not Decision Replacement
- Final decision remains with the user
- Human Model is support context, not identity
- Memory is context, not authorization
- Domain Model adds evidence, not orders
- Decision Profile is a soft guide, not policy
- Current user instruction wins
- High-impact decisions require extra caution
- Hermes should make choices clearer, not make choices for the user

---

## Appendix B. One-line Test

Decision Support の1行テスト:

> この出力を読んだあと、ユーザーは「誘導された」と感じるのではなく、「整理されて選びやすくなった」と感じるか。
