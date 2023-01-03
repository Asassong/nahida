# nahida

This project is developed based on `Iridium-py`.

It sniffs special packages when you combat in game, acquire team info, damage, energy etc. 

## Usage

(1)Install [scapy](https://github.com/secdev/scapy)

(2)Install matplotlib

``` python
pip install matplotlib
```

(3)Download this project and open `config.json`.

```json
{
 "device_name": "\\Device\\NPF_{}",  // it can use the name instead which has ipv4,ipv6 etc. after typing ipconfig in cmd
 "language": "chs"  // if you dont's know Chinese, you can modify it to "en"
}
```

## Safety

Unless MiHoYo/HoYoverse issues a proclamation against it, it's perfectly safe.

## Risk

MiHoYo's dmca.

Key file `WindSeedClientNotify`,whose name is `plaintext.bin` in this project，is version-dependent and unpunctual。You can use `Iridium-py` to get the plaintext of `AvatarDataNotify`,`FinishedParentQuestNotify`,`GetAllMailResultNotify` etc. as an alternative。

MiHoYo shuffle the proto.Please wait or study by yourselves.

## Other

**Please use it in good network condition.**

## Contributing

I would probably work on Akasha2.0, which would contains ability(or call it buff) and skills etc.If you are instrested in them, please contact.

## Credits

* [grasscutter](https://github.com/Grasscutters/Grasscutter)

* [GrasscutterCommandGenerator](https://github.com/jie65535/GrasscutterCommandGenerator)

* [Iridium-py](https://github.com/c2c3vsfac/Iridium-py-release)
