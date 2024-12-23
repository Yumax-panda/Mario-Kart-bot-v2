# 交流戦 bot

本botはマリオカート8デラックスのチーム活動をサポートする機能を備えたbotになります。

## 機能


本botの主な機能は以下の通りです。


- プレイヤーの一括検索
- 交流戦の挙手
- 戦績管理
- フレンド申請

MK8DX 150cc Loungeのデータは[MK8DX 150cc Leaderboard](https://www.mk8dx-lounge.com/Leaderboard)より取得しています。

## 特徴


#### **複数アカウントの連携**

本botはラウンジサーバーに参加しているDiscordアカウントのIDを連携させることによって、ラウンジサーバーに加入していないアカウントでもラウンジのデータを参照できるようになっています。

#### **広範囲の検索**

プレイヤーの検索にはDiscord IDやNintendo Switchのフレンドコード、ラウンジ名などが使用できますが、これはbotにより自動で判別されるため、入力が簡単でありながら多くの要素で検索することが可能です。


#### **英語と日本語の対応**

スラッシュコマンドやヘルプは言語対応しており、使用者の言語に応じて表示が変わります。


#### **ロールとの連携**

Discordサーバー内のロール（役職）と連携した機能を実装しているため、サーバーごとにより自由な使い方が実現できます。



## 謝辞


本botの作成にあたり、以下のプログラムを参考にさせていただきました。

- [mkbot.py](https://github.com/sheat-git/mkbot.py)


## 使用方法

 [招待リンク](https://discordapp.com/api/oauth2/authorize?client_id=1038322985146273853&permissions=854027660408&scope=bot%20applications.commands)から各自サーバーへ本botを招待してください。また、コマンドの確認はサーバー内にて`/help`と入力することで確認できます。
