# nahida

让智慧之神指引你吧。

本项目基于项目`Iridium-py`开发，由两部分组成。

`realtime_damage_shower`：在游戏中触发战斗时，能自动实时显示当前队伍角色的伤害占比和全队DPS。

`Nahida`：自动记录战斗期间的收发数据包，结束后统一分析，得到包含武器，角色面板，dps及变化情况，能量变化等信息的图片。

两部分互相独立，以满足不同人群的需要。

## 使用

### 方式1.自行安装

(1)参见[scapy](https://github.com/secdev/scapy)安装scapy

(2)安装matplotlib

``` python
pip install matplotlib
```

### 方式2.下载嵌入式包

https://www.aliyundrive.com/s/H92QJFwjcHN  提取码: cx88

自解压包，因此后缀为exe。

可能需要安装npcap

## 项目安全性

除非米哈游发则公告禁止使用，不然本项目完全不干扰客户端和服务端间的通信， 只是从本机网卡中获取数据，毫无封号理由。

## 项目风险

随时有可能遭到米哈游的dmca，且用且珍惜。

关键文件`WindSeedClientNotify`,即本项目中的`plaintext.bin`周期性停发，且随版本改变。可以使用`Iridium-py`获取`AvatarDataNotify`,`FinishedParentQuestNotify`,`GetAllMailResultNotify`等较长数据包作替代。

proto混淆，等待项目`Iridium-py`更新。

## 备注

请在网络良好条件下使用。

最近较忙，若使用出现问题希望直接提Pull request, 提issue当然也可以。

欢迎性能优化， 项目美化，功能扩展等PR。

## 致谢

* [grasscutter](https://github.com/Grasscutters/Grasscutter)

* [GrasscutterCommandGenerator](https://github.com/jie65535/GrasscutterCommandGenerator)

* [Iridium-py](https://github.com/c2c3vsfac/Iridium-py-release)
