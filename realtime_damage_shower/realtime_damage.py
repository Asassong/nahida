import base64
import threading
from scapy.all import sniff
import json
import parse_proto
import time
from matplotlib import pyplot as plt
import matplotlib
from multiprocessing import Process, Pipe
import os
import re


class Avatar:
    def __init__(self):
        self.avatar_name = ""
        self.avatar_id = 0
        self.entity_id = 0
        self.guid = 0

    @property
    def avatar_id(self):
        return self.avatar_id

    @avatar_id.setter
    def avatar_id(self, value):
        if value != 0:
            self.avatar_name = avatar_id_list[value]


class Gadget:
    def __init__(self):
        self.owner_id = 0

    def set_owner_id(self, value):
        if value > 800000000:
            self.owner_id = gadget_obj_dict[value].owner_id
        else:
            self.owner_id = value


def package_handle(data):
    sniff_datas.append(bytes(data))


def xor(b_data, b_key):
    decrypt_data = b""
    for j in range(len(b_data)):
        decrypt_data += (b_data[j] ^ b_key[j % len(b_key)]).to_bytes(1, byteorder="big", signed=False)
    return decrypt_data


def remove_magic(b_data):
    try:
        cut1 = b_data[6]
        cut2 = b_data[5]
        b_data = b_data[8 + 2:]
        b_data = b_data[:len(b_data) - 2]
        b_data = b_data[cut2:]
        return b_data[cut1:]
    except IndexError as e:
        print(e)


def get_packet_id(b_data):
    packet_id = int.from_bytes(b_data[2:4], byteorder="big", signed=False)
    return packet_id


def read_packet_id():
    f = open("packet_id.json", "r")
    d_packet_id = json.load(f)
    f.close()
    return d_packet_id


def sniff_(iface_):
    sniff(iface=iface_, count=0, filter="udp port 22102||22101", prn=package_handle)


def find_key():
    i = 0
    head = ""
    have_got_id_key = False
    have_got_data_key = False
    d_windseed = {}
    encrypted_windseed = b""
    while True:
        if i <= len(sniff_datas) - 1:
            b_data = sniff_datas[i]
            b_data = b_data[42:]
            i += 1
            if have_got_data_key and have_got_id_key:
                frg = b_data[9]
                sn = int.from_bytes(b_data[16:20], byteorder="little", signed=False)
                if frg + sn == first_frg + first_sn:
                    if frg not in d_windseed:
                        d_windseed[frg] = b_data[28:]
                    else:
                        continue
                    frgs = list(d_windseed.keys())
                    if frgs[0] + 1 == len(frgs):
                        sorted_frgs = sorted(d_windseed.items(), key=lambda x: x[0], reverse=True)
                        t_data = list(zip(*sorted_frgs))[1]
                        for frg_data in t_data:
                            encrypted_windseed += frg_data
                        get_seed = False
                        offset = len(encrypted_windseed) - len(windseed_text)
                        full_key = xor(encrypted_windseed[offset:], windseed_text)
                        keys = [full_key[i: i + 4096] for i in range(4096 - offset, len(full_key), 4096)]
                        decrypted_key = max(set(keys), key=keys.count)
                        if keys.count(decrypted_key) > 1:
                            get_seed = True
                            print("get key")
                        if get_seed:
                            pkg_parser = threading.Thread(target=parse_, args=(decrypted_key,))
                            kcp_dealing = threading.Thread(target=handle_kcp, args=(id_key,))
                            pkg_parser.start()
                            kcp_dealing.start()
                            break
                        else:
                            print("请重试")
                            exit()
            else:
                if not head:
                    if len(b_data) > 20:
                        head = b_data[:2]
                    else:
                        continue
                if len(b_data) > 20:
                    if not have_got_id_key:
                        b_data = b_data[28:]
                        if b_data.startswith(b"$\x8f") or b_data.startswith(head):
                            continue
                        else:
                            id_key = xor(b_data[:4], b"Eg\x00\x9c")
                            if id_key:
                                have_got_id_key = True
                    else:
                        packet_id = xor(b_data[28:32], id_key)
                        if packet_id == b"\x45\x67\x04\x85":
                            first_frg = b_data[9]
                            first_sn = int.from_bytes(b_data[16:20], byteorder="little", signed=False)
                            have_got_data_key = True
                            d_windseed[first_frg] = b_data[28:]


def parse_(decrypt_key):
    avatar_obj_dict = {}
    combat_start_time = 0
    total_damage = 0
    i = 0
    while True:
        if i <= len(packet) - 1:
            get = False
            try:
                if i >= 50:
                    get = lock.acquire()
                    for j in range(50):
                        packet.pop(0)
                    i -= 50
            finally:
                if get:
                    lock.release()
            b_data = packet[i]
            i += 1
            b_data = xor(b_data, decrypt_key)
            packet_id = get_packet_id(b_data)
            b_data = remove_magic(b_data)
            if packet_id == 1728:  # SceneTeamUpdateNotify
                data = parse_proto.parse(b_data, str(packet_id))
                for guid, avatar_obj in avatar_obj_dict.items():
                    del avatar_obj
                avatar_obj_dict = {}
                damage_dict.clear()
                send_pipe.send(("clear", 0))
                combat_start_time = 0
                total_damage = 0
                for scene_info in data['scene_team_avatar_list']:
                    info = scene_info['scene_entity_info']
                    if info['entity_type'] == 'PROT_ENTITY_TYPE_AVATAR':
                        avatar = info['avatar']
                        avatar_id = avatar['avatar_id']
                        avatar_guid = avatar['guid']
                        avatar_obj_dict.update({avatar_guid: Avatar()})
                        avatar_obj_dict[avatar_guid].avatar_id = avatar_id
                        damage_dict.update({avatar_obj_dict[avatar_guid].avatar_name: 0})
                send_pipe.send(("update", list(damage_dict.keys())))  # 不写这个就会直到下一次伤害才更新图，没搞明白
            elif packet_id == 400:  # EvtCreateGadgetNotify
                data = parse_proto.parse(b_data, str(packet_id))
                entity_id = data['entity_id']
                gadget_obj_dict.update({entity_id: Gadget()})
                gadget_obj_dict[entity_id].set_owner_id(data['prop_owner_entity_id'])
            elif packet_id == 243:  # SceneEntityAppearNotify
                data = parse_proto.parse(b_data, str(packet_id))
                for entity in data['entity_list']:
                    if entity['entity_type'] == 'PROT_ENTITY_TYPE_AVATAR':
                        if entity["entity_id"] not in avatar_entity_to_guid_map:
                            avatar = entity['avatar']
                            avatar_entity_to_guid_map.update({entity["entity_id"]: avatar["guid"]})
                            avatar_obj_dict[avatar["guid"]].entity_id = entity["entity_id"]
            elif packet_id == 42:  # UnionCmdNotify
                try:
                    data = parse_proto.parse(b_data, str(packet_id))
                    send_flag = False
                    for union_data in data["cmd_list"]:
                        if union_data["message_id"] == 354:  # CombatInvocationsNotify
                            each_data = parse_proto.parse(base64.b64decode(union_data["body"]),
                                                 str(union_data["message_id"]))
                            if 'invoke_list' in each_data:
                                argument_type = each_data["invoke_list"][0]['argument_type']
                                if argument_type == 'COMBAT_TYPE_ARGUMENT_EVT_BEING_HIT':
                                    combat_data = parse_proto.parse(
                                        base64.b64decode(each_data["invoke_list"][0]['combat_data']),
                                        union_cmd[argument_type])
                                    attack_result = combat_data["attack_result"]
                                    try:
                                        attacker_entity_id = attack_result["attacker_id"]
                                        attackee = attack_result['defense_id']
                                        if str(attackee).startswith("33"):
                                            if str(attacker_entity_id).startswith("88"):
                                                attacker_entity_id = gadget_obj_dict[attacker_entity_id].owner_id
                                            if str(attacker_entity_id).startswith("16"):
                                                attacker = avatar_obj_dict[avatar_entity_to_guid_map[attacker_entity_id]].avatar_name
                                                if "damage" in attack_result:
                                                    damage = attack_result["damage"]
                                                    attack_time = attack_result["attack_timestamp_ms"]
                                                    if combat_start_time == 0:
                                                        combat_start_time = attack_time
                                                    elif combat_start_time > attack_time:
                                                        combat_start_time = attack_time
                                                    combat_duration = attack_time - combat_start_time
                                                    # print(combat_duration, attacker, damage)
                                                    damage_dict[attacker] += damage
                                                    total_damage += damage
                                                    send_flag = True
                                    except KeyError as e:
                                        print("存在未知字典键%s" % e)
                                        print(attack_result)
                    if send_flag:
                        damage_list = list(damage_dict.values())
                        damage_ratio = [round(r / total_damage * 100, 4) for r in damage_list]
                        if combat_duration == 0:
                            dps = total_damage
                        else:
                            dps = int(total_damage * 1000 / combat_duration)
                        send_pipe.send(("draw", (list(damage_dict.keys()), damage_ratio, dps)))
                        # send_pipe.send(("flash", 0))
                except Exception as e:
                    print("未知异常%s" % e)


def handle_kcp(id_key):
    i = 6
    while True:
        if i <= len(sniff_datas) - 1:
            get = False
            try:
                if i >= 100:
                    get = lock.acquire()
                    for j in range(100):
                        sniff_datas.pop(0)
                    i -= 100
            finally:
                if get:
                    lock.release()
            data = sniff_datas[i]
            i += 1
            data = data[42:]
            skip = False
            while len(data) != 0:
                length = int.from_bytes(data[24:28], byteorder="little", signed=False)
                if length == 0:
                    data = data[28:]
                    continue
                else:
                    head = xor(data[28:32], id_key)
                    frg = data[9]
                    sn = int.from_bytes(data[16:20], byteorder="little", signed=False)
                    if head.startswith(b"\x45\x67") and frg == 0:
                        packt_id = get_packet_id(head)
                        una = int.from_bytes(data[20:24], byteorder="little", signed=False)
                        if (sn, una) not in handled_without_kcp_packet:
                            if packt_id in [1728, 42, 400, 243]:
                                packet.append(data[28:28 + length])
                            handled_without_kcp_packet.append((sn, una))
                        skip = True
                    else:
                        skip = False
                        if head.startswith(b"\x45\x67"):
                            packt_id = get_packet_id(head)
                            if packt_id in [1728, 42, 400, 243]:
                                if sn + frg not in handled_kcp_packet:
                                    if sn + frg not in kcp:
                                        kcp[sn + frg] = {frg: data[28: 28 + length]}
                                    else:
                                        kcp[sn + frg][frg] = data[28: 28 + length]
                                else:
                                    skip = True
                            else:
                                handled_kcp_packet.append(sn + frg)
                                skip = True
                            # {245:{36:data}}, 284:{:}}
                        else:
                            if sn + frg in kcp:
                                if frg in kcp[sn + frg]:
                                    skip = True
                                else:
                                    kcp[sn + frg][frg] = data[28: 28 + length]
                            else:
                                if sn + frg not in handled_kcp_packet:
                                    kcp[sn + frg] = {frg: data[28: 28 + length]}
                    offset = length + 28
                    data = data[offset:]
            if not skip:
                for key1, value1 in kcp.items():
                    frgs = list(value1.keys())
                    if len(frgs) == frgs[0] + 1:
                        sorted_dict = sorted(value1.items(), key=lambda x: x[0], reverse=True)
                        t_data = list(zip(*sorted_dict))[1]
                        b_data = b""
                        for frg_data in t_data:
                            b_data += frg_data
                        packet.append(b_data)
                        handled_kcp_packet.append(key1)
                        del kcp[key1]
                        break


def show_damage(pipe):
    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
    plt.rcParams['axes.unicode_minus'] = False
    matplotlib.use("TkAgg")
    fig = plt.figure(figsize=(1.5, 1))
    mngr = plt.get_current_fig_manager()
    mngr.window.wm_geometry("+10+500")
    fig.canvas.toolbar.pack_forget()
    win = plt.gcf().canvas.manager.window
    win.attributes("-transparentcolor", "white")
    fig.canvas.manager.window.overrideredirect(1)
    plt.ion()
    plt.xlim(0, 1)
    while True:
        if pipe.poll():
            state, recv_data = pipe.recv()
            if state == "draw":
                attacker, damage_ratio, dps = recv_data
                plt.cla()
                plt.axis("off")
                plt.barh(attacker, damage_ratio, color="#2da4e4")
                for location_index, value in enumerate(damage_ratio):
                    plt.text(0, - 0.2 + location_index * 1, attacker[location_index] + "%.2f%%" % damage_ratio[location_index]
                             , fontdict={"color": "red"})
                    location_index += 1
                plt.text(0, -1, "DPS:%d" % dps, fontdict={"weight": "bold"})
                plt.pause(0.001)
                plt.ioff()
            elif state == "clear":
                plt.clf()
                plt.axis("off")
                plt.pause(0.001)
                plt.ioff()
            elif state == "update":
                avatar_name = recv_data
                damage = [0]*len(avatar_name)
                plt.clf()
                plt.axis("off")
                plt.barh(avatar_name, damage, color="#2da4e4")
                plt.pause(0.001)
                plt.ioff()


def read_windseed():
    f = open("plaintext.bin", "rb")
    b_windseed = f.read()
    f.close()
    return b_windseed


def read_config():
    f = open("config.json", "r")
    return json.load(f)


def read_union_cmd():
    f = open("ucn_id.json", "r")
    return json.load(f)


if __name__ == '__main__':
    recv_pipe, send_pipe = Pipe(False)
    show = Process(target=show_damage, args=(recv_pipe,))
    show.start()
    config = read_config()
    windseed_text = read_windseed()
    union_cmd = read_union_cmd()
    d_pkt_id = read_packet_id()
    sniff_datas = []
    packet = []
    handled_without_kcp_packet = []
    handled_kcp_packet = []
    kcp = {}
    dev = config["device_name"]
    if dev == "\\Device\\NPF_{}":
        with os.popen("getmac", "r") as c:
            text = c.read()
        iface = re.findall("(?<=_{).*?(?=})", text)[0]
        dev = "\\Device\\NPF_{%s}" % iface
        with open("config.json", "w", encoding="utf-8") as f:
            config["device_name"] = dev
            json.dump(config, f, indent=1)
    skip_packet = config["skip_packet_id"]
    avatar_id_list = {10000002: "神里绫华", 10000003: "琴", 10000005: "旅行者", 10000006: "丽莎", 10000007: "旅行者",
                      10000014: "芭芭拉", 10000015: "凯亚", 10000016: "迪卢克", 10000020: "雷泽", 10000021: "安柏",
                      10000022: "温迪", 10000023: "香菱", 10000024: "北斗", 10000025: "行秋", 10000026: "魈",
                      10000027: "凝光",
                      10000029: "可莉", 10000030: "钟离", 10000031: "菲谢尔", 10000032: "班尼特", 10000033: "达达利亚",
                      10000034: "诺艾尔", 10000035: "七七", 10000036: "重云", 10000037: "甘雨", 10000038: "阿贝多",
                      10000039: "迪奥娜", 10000041: "莫娜", 10000042: "刻晴", 10000043: "砂糖", 10000044: "辛焱",
                      10000045: "罗莎莉亚", 10000046: "胡桃", 10000047: "枫原万叶", 10000048: "烟绯", 10000049: "宵宫",
                      10000050: "托马", 10000051: "优菈", 10000052: "雷电将军", 10000053: "早柚",
                      10000054: "珊瑚宫心海",
                      10000055: "五郎", 10000056: "九条裟罗", 10000057: "荒泷一斗", 10000058: "八重神子",
                      10000059: "鹿野院平藏", 10000060: "夜兰", 10000062: "埃洛伊", 10000063: "申鹤", 10000064: "云堇",
                      10000065: "久岐忍", 10000066: "神里绫人", 10000067: "柯莱", 10000068: "多莉", 10000069: "提纳里",
                      10000070: "妮露", 10000071: "赛诺", 10000072: "坎蒂丝", 10000073: "纳西妲", 10000074: "莱依拉",
                      10000075: "流浪者", 10000076: "珐露珊"}
    gadget_obj_dict = {}
    avatar_entity_to_guid_map = {}
    damage_dict = {}
    lock = threading.Lock()
    now_time = time.strftime("%Y%m%d%H%M%S")
    sniffer = threading.Thread(target=sniff_, args=(dev,))
    key_finder = threading.Thread(target=find_key)
    sniffer.start()
    key_finder.start()




