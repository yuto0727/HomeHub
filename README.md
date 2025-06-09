# スマートリモコンシステム

Alexa 対応スマトーリモコン機能の統合コントローラー
基本構成は NodeRed + Node-RED Alexa Home Skill Bridge
IR 送受信には pigpio 使用

## Raspi の設定について

### Wifiが切れる問題
参考：https://miyagadget.page/blog/2025/03/03/raspberrypi-wifi/


### ログファイルの肥大化防止

参考：https://note.com/puerh_tea_/n/n44f86d3a062e

```bash
# 既存ログファイルの削除
sudo find /var/log/ -type f -name \* -exec cp -f /dev/null {} \;
```

```bash
# ルールの変更
sudo nano /etc/rsyslog.conf

#以下、変更点
###############
#### RULES ####
###############

#
# First some standard log files.  Log by facility.
#
auth,authpriv.*			/var/log/auth.log
*.*;auth,authpriv.none		-/var/log/syslog
#cron.*				/var/log/cron.log
#daemon.*			-/var/log/daemon.log
kern.*				-/var/log/kern.log
#lpr.*				-/var/log/lpr.log
#mail.*				-/var/log/mail.log
user.*				-/var/log/user.log

#
# Logging for the mail system.  Split it up so that
# it is easy to write scripts to parse these files.
#
#mail.info			-/var/log/mail.info
#mail.warn			-/var/log/mail.warn
#mail.err			/var/log/mail.err

#
# Some "catch-all" log files.
#
#*.=debug;\
#	auth,authpriv.none;\
#	news.none;mail.none	-/var/log/debug
*.=info;*.=notice;*.=warn;\
	auth,authpriv.none;\
	cron,daemon.none;\
	mail,news.none		-/var/log/messages

#
# Emergencies are sent to everybody logged in.
#
*.emerg				:omusrmsg:*
```

```bash
# ローテーション周期の変更
sudo nano /etc/logrotate.conf
# 2weekとか？
```
