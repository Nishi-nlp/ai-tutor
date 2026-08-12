# Mastery Policy — 7日版 Version 1

## 目的

`la.linear_combination`の回答結果を、説明可能で再現可能なMastery Scoreへ
変換する。Masteryは理解度そのものではなく、保存された回答履歴からの推定値である。

## 回答評価

| 評価 | score |
|---|---:|
| 完全正解 | `1.00` |
| 軽微なミス | `0.75` |
| 部分正解 | `0.40` |
| 不正解 | `0.00` |

7日版では固定回答または数値問題を決定的なロジックで評価する。
LLMによる採点は行わない。

## ヒント係数

| 最大使用レベル | 内容 | coefficient |
|---:|---|---:|
| 0 | なし | `1.00` |
| 1 | 着目点 | `0.90` |
| 2 | 使用する概念 | `0.75` |
| 3 | 途中式または強い誘導 | `0.55` |

4段階以上のヒントを実装する場合も、係数は明示してテストを追加する。

## evidence

```text
evidence = score × hint_coefficient
```

回答時間と問題難易度はVersion 1の計算に使用しない。

## Mastery更新

初期値は`0.20`とする。

```text
evidence >= current_mastery の場合:
new_mastery = current_mastery + 0.35 × (evidence - current_mastery)

evidence < current_mastery の場合:
new_mastery = current_mastery + 0.15 × (evidence - current_mastery)

new_mastery = clamp(new_mastery, 0, 1)
```

DBには丸め前の値を保存し、表示時だけ丸める。更新はAttempt保存と同一の
トランザクションで行う。

## 状態

| 状態 | 条件 |
|---|---|
| 未学習 | Attemptがない |
| 学習中 | Attemptがあり、Masteryが`0.85`未満 |
| 習得 | Masteryが`0.85`以上、かつヒントなし完全正解が1回以上 |

7日版は問題形式が限定されるため、「異なる2種類以上の問題形式で成功」は
習得条件に含めない。要復習状態と復習日計算も対象外とする。

## 保存項目

- KC ID、Question ID、回答
- score、評価ラベル、評価理由
- 最大ヒントレベル、ヒント係数、evidence
- 更新前後のMastery
- 回答日時、計算方式`mastery-v1`

## 必須テスト

- 各評価とヒントレベルのevidence
- 上昇係数`0.35`と下降係数`0.15`
- 0〜1へのclamp
- 初回Attemptと複数Attempt
- Attempt保存とMastery更新の原子性
