import base64
import threading
from scapy.all import sniff
import json
import parse_proto as pp
import time
import os
import re


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


def get_proto_name_by_id(i_id):
    try:
        proto_name = d_pkt_id[str(i_id)]
        return proto_name
    except KeyError as e:
        print(e)
        return False


def sniff_(iface_):
    sniff(iface=iface_, count=0, filter="udp port 22102||22101", prn=package_handle)


def parse(decrypt_key):
    i = 0
    f_decrypt_data = open(now_time + "战斗数据.txt", "w", encoding="utf-8")
    print("纳西妲工作正常，战斗数据将保存在文件 %s战斗数据.txt 中, 请使用虚空分析" % now_time)
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
            ts, b_data = packet[i]
            i += 1
            b_data = xor(b_data, decrypt_key)
            packet_id = get_packet_id(b_data)
            proto_name = get_proto_name_by_id(packet_id)
            b_data = remove_magic(b_data)
            if proto_name:
                if packet_id == 42:  # UnionCmdNotify
                    union_list = []
                    try:
                        data = pp.parse(b_data, str(packet_id))
                        for union_data in data["cmd_list"]:
                            each_data = pp.parse(base64.b64decode(union_data["body"]),
                                                 str(union_data["message_id"]))
                            if 'invokes' in each_data:
                                if 'argument_type' in each_data["invokes"][0]:
                                    argument_type = each_data["invokes"][0]['argument_type']
                                    if argument_type == 'ABILITY_INVOKE_ARGUMENT_META_TRIGGER_ELEMENT_REACTION':
                                        if 'ability_data' in each_data["invokes"][0]:
                                            each_data["invokes"][0]['ability_data'] = pp.parse(
                                                base64.b64decode(each_data["invokes"][0]['ability_data']),
                                                union_cmd[argument_type])
                                        union_list.append({"AbilityInvocationsNotify": each_data})
                            elif 'invoke_list' in each_data:
                                if 'argument_type' in each_data["invoke_list"][0]:
                                    argument_type = each_data["invoke_list"][0]['argument_type']
                                    if argument_type == 'COMBAT_TYPE_ARGUMENT_EVT_BEING_HIT':
                                        each_data["invoke_list"][0]['combat_data'] = pp.parse(
                                            base64.b64decode(each_data["invoke_list"][0]['combat_data']),
                                            union_cmd[argument_type])
                                        union_list.append({"CombatInvocationsNotify": each_data})
                        if union_list:
                            f_decrypt_data.write("%d UnionCmdNotify %s\n" % (ts, union_list))
                    except Exception:
                        print("%s Error" % proto_name)
                elif packet_id == 354:  # CombatInvocationsNotify
                    try:
                        data = pp.parse(b_data, str(packet_id))
                        combat_list = []
                        for invoke in data["invoke_list"]:
                            if 'argument_type' in invoke:
                                argument_type = invoke['argument_type']
                                if argument_type == 'COMBAT_TYPE_ARGUMENT_BEING_HEALED_NTF':
                                    invoke['combat_data'] = pp.parse(
                                        base64.b64decode(invoke['combat_data']), union_cmd[argument_type])
                                    combat_list.append(invoke)
                        if combat_list:
                            f_decrypt_data.write("%d CombatInvocationsNotify %s\n" % (ts, data))
                    except Exception:
                        print("%s Error" % proto_name)
                elif packet_id in [1728, 400, 243, 1243, 139, 976]:
                    try:
                        data = pp.parse(b_data, str(packet_id))
                        f_decrypt_data.write("%d %s %s\n" % (ts, proto_name, data))
                    except Exception:
                        print("%s Error" % proto_name)


def handle_kcp():
    i = 0
    packet_head = b""
    id_key = b""
    xor_key = b""
    special_sn = 0
    sn_ts_map = {}
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
            if packet_head:
                if not id_key:
                    if len(data) > 70:
                        flag = data[70:74]
                        if (not flag.startswith(b"$\x8f")) and data.startswith(packet_head):
                            id_key = xor(flag, b"Eg\x00\x9c'")  # PlayerLoginReq
                        else:
                            continue
                    else:
                        continue
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
                                if packt_id in [1728, 400, 243, 42, 1243, 139, 354, 976]:
                                    ts = int.from_bytes(data[12:16], byteorder="little", signed=False)
                                    packet.append((ts, data[28:28 + length]))
                                handled_without_kcp_packet.append((sn, una))
                            skip = True
                        else:
                            skip = False
                            if head.startswith(b"\x45\x67"):
                                packt_id = get_packet_id(head)
                                if not xor_key:
                                    if packt_id == 1157:  # WindSeedClientNotify
                                        special_sn = sn + frg
                                if packt_id in [1728, 1157, 400, 243, 42, 1243, 139, 354, 976]:
                                    if sn + frg not in handled_kcp_packet:
                                        ts = int.from_bytes(data[12:16], byteorder="little", signed=False)
                                        sn_ts_map[sn + frg] = ts
                                        if sn + frg not in kcp:
                                            kcp[sn + frg] = {frg: data[28: 28 + length]}
                                        else:
                                            kcp[sn + frg][frg] = data[28: 28 + length]
                                    else:
                                        skip = True
                                else:
                                    handled_kcp_packet.append(sn + frg)
                                    skip = True
                            else:
                                if sn + frg in kcp:
                                    if frg in kcp[sn + frg]:
                                        skip = True
                                    else:
                                        kcp[sn + frg][frg] = data[28: 28 + length]
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
                            if key1 == special_sn:
                                offset = len(b_data) - len(windseed_text)
                                full_key = xor(b_data[offset:], windseed_text)
                                keys = [full_key[i: i + 4096] for i in range(4096 - offset, len(full_key), 4096)]
                                xor_key = max(set(keys), key=keys.count)
                                if keys.count(xor_key) < 2:
                                    print("请重试")
                                    os.exit(-1)
                                pkg_parser = threading.Thread(target=parse, args=(xor_key,))
                                pkg_parser.start()
                            packet.append((sn_ts_map[key1], b_data))
                            handled_kcp_packet.append(key1)
                            del kcp[key1]
                            break
            else:
                if len(data) > 20:
                    packet_head = data[:2]


def read_windseed():
    with open("./plaintext.bin", "rb") as f:
        b_windseed = f.read()
    return b_windseed


def read_json(file):
    with open(file, "r", encoding="utf-8") as f:
        text = json.load(f)
    return text


config = read_json("./nahida_config.json")
windseed_text = read_windseed()
union_cmd = read_json("./ucn_id.json")
d_pkt_id = read_json("./packet_id.json")
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
    with open("./nahida_config.json", "w", encoding="utf-8") as f:
        config["device_name"] = dev
        json.dump(config, f, indent=1)
lock = threading.Lock()
now_time = time.strftime("%m{}%d{}%H{}%M{}").format("月", "日", "时", "分")
sniffer = threading.Thread(target=sniff_, args=(dev,))
kcp_handler = threading.Thread(target=handle_kcp)
sniffer.start()
kcp_handler.start()
