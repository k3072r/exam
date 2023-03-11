# 某会社様　プログラミング試験課題

```
python app.py n m t
```
にて実行します。
同ディレクトリ内の log.txt の内容を読み込み、結果を出力します。

```
python tests.py
```
とするとテストを実施します。
入力データ・期待される出力・テストの意図　はtest.py内に記述しています。


## 設問1

ログファイルを読み込み、「各行をコンマで分割したものを要素にもつリスト」のリストに変換します。
（以下、「各行をコンマで分割したものを要素にもつリスト」を「ログ」とします。）

ログのリストを```parse_logs_all```関数に渡し、その中で
各サーバごとのログのリストに分け、```check_failure_a_server```に渡します。

```check_failure_a_server```ではログを時刻昇順にし、
応答結果を見て行き、故障状態を割り出してアドレスと期間のタプルを返します。
このアドレスと期間を出力し、設問1の解答となります。


## 設問2

```check_failure_a_server```内で故障状態を```ifFailure```変数で管理しており、真偽値を入れていましたが、
それを整数にしてnと比較するようにしました。


## 設問3

```check_failure_a_server```と同様に```check_overload_a_server```関数を定義し、
過負荷状態を検知するようにしました。
ループを2回回すことになりますが、
failureとoverloadを同時に検知するのはコードが煩雑になりそうなので避けました。