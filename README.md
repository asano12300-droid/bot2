# bot2
discordbotを作成するツールです。そして作成例です

## 使用条件
os: linux<br>
destribution: ubuntu, debian</br>
仮想環境: uv (現在、debianで公開されていないpython3.15を使用しているため)

## 使い方
1.クローンしてください
```
git clone https://github.com/asano12300-droid/bot2/commits/{version}
```
2.クローンしたフォルダーに入ります
```
cd bot2
```
3.`install.sh`を起動させます
```
sh install.sh
```

## 使用しているモジュール
使用しているモジュールは13個です。
### 1.外部モジュール
|No.|モジュール名|必須|
|-|-|-|
|1|py-cord|Yes|
|2|python-dotenv|Yes|
|3|sympy|Yes|
|4|matplotlib|Yes|
|5|requests|No|
|6|deep_translator|No|
### 2.内部モジュール
|No.|モジュール名|必須|
|-|-|-|
|7|os|Yes|
|8|time|Yes|
|9|datetime|Yes|
|10|importlib|Yes|
|11|pkgutil|Yes|
|12|random|Yes|
|13|io|Yes|

