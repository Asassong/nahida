import json
import os
import sys
from PIL import Image, ImageDraw, ImageFont
from matplotlib import pyplot as plt
import matplotlib
from tkinter import filedialog, Tk


class Avatar:
    def __init__(self):
        self.avatar_name = ""
        self.avatar_id = 0
        self.entity_id = 0
        self.guid = 0
        self.level = 0
        self.fight_prop = {}
        self.draw_fight_prop = {}
        self.weapon = Weapon()
        self.reliquaries = []
        self.skill_map = {}
        self.skill_level = {}

    @property
    def avatar_id(self):
        return self.avatar_id

    @avatar_id.setter
    def avatar_id(self, value):
        if value != 0:
            self.avatar_name = avatar_id_dict[value]


class Gadget:
    def __init__(self):
        self.owner_id = 0

    def set_owner_id(self, value):
        if value > 800000000:
            self.owner_id = gadget_obj_dict[value].owner_id
        else:
            self.owner_id = value


class Monster:
    def __init__(self):
        self.entity_id = 0
        self.monster_name = ""


class Weapon:
    def __init__(self):
        self.name = ""
        self.level = 0
        self.refinement = 0


def read_json(file):
    with open(file, "r", encoding="utf-8") as json_file:
        text = json.load(json_file)
    convert_dict = {int(str_id): id_value for str_id, id_value in text.items()}
    return convert_dict


def cal_dps(damage_time_dict):
    attack_time = sorted(damage_time_dict)
    attack_time0 = attack_time[0]
    team_damage = 0
    pre_time = attack_time0
    i = 1
    attack_time_8 = [0]
    dps = [round(damage_time_dict[attack_time0], 0)]
    for time_ in attack_time[1:]:
        team_damage += damage_time_dict[time_]
        if not i % 8:
            attack_time_8.append(round((time_ - attack_time0)/1000, 2))
            dps.append(round(team_damage * 1000 / (time_ - pre_time), 0))
            pre_time = time_
            team_damage = 0
        i += 1
    return attack_time_8, dps


def deal_stamina(stamina_dict):
    sorted_stamina = sorted(stamina_dict)
    sorted_stamina0 = combat_start_time
    sorted_stamina_end = sorted_stamina[-1]
    time_ = []
    stamina = []
    for i, stamina_ in enumerate(sorted_stamina):
        time_.append(round((stamina_ - sorted_stamina0)/1000, 2))
        stamina.append(round(stamina_dict[stamina_]/100, 0))
        if stamina_dict[stamina_] == 24000:
            if stamina_ != sorted_stamina_end:
                time_.append(round((sorted_stamina[i + 1] - sorted_stamina0 - 10)/1000, 2))
                stamina.append(240)
    return time_, stamina


def deal_energy(energy_dict):
    max_energy = {}
    for avatar in avatar_obj_dict.values():
        for element_energy in ['火元素能量上限', '雷元素能量上限', '水元素能量上限', '草元素能量上限', '风元素能量上限',
                               '冰元素能量上限', '岩元素能量上限']:
            if element_energy in avatar.fight_prop:
                max_energy.update({avatar.avatar_name: avatar.fight_prop[element_energy]})
                break
    sorted_energy0 = combat_start_time
    avatar_energy_tuple = {}
    for avatar in list(max_energy.keys()):
        if avatar in energy_dict:  # 当队伍中角色从没使用过元素爆发时，不绘制
            energy_time_dict = energy_dict[avatar]
            sorted_energy = sorted(energy_time_dict)
            sorted_energy_end = sorted_energy[-1]
            avatar_max_energy = max_energy[avatar]
            time_ = []
            energy = []
            if sorted_energy != sorted_energy[0]:
                time_.append(0)
                energy.append(energy_time_dict[sorted_energy[0]])
            for i, energy_ in enumerate(energy_time_dict):
                time_.append(round((energy_ - sorted_energy0)/1000, 2))
                energy.append(energy_time_dict[energy_])
                if energy_time_dict[energy_] == avatar_max_energy:
                    if energy_ != sorted_energy_end:
                        time_.append(round((sorted_energy[i + 1] - sorted_energy0 - 10)/1000, 2))
                        energy.append(avatar_max_energy)
            avatar_energy_tuple.update({avatar: (time_, energy)})
    return avatar_energy_tuple


def draw(combat_duration):
    # 队伍配置 dps时序 能量时序 体力时序 战斗综合（暴击，反应率，总伤害，伤害占比，战斗时间）
    img = Image.open("akasha.png")
    copy_img = img.copy()
    fnt = ImageFont.truetype("simhei.ttf", 24)
    avatar_info_color = (37, 111, 55, 255)
    painter = ImageDraw.Draw(copy_img)
    x_px = 49
    y_px = 44
    for avatar in avatar_obj_dict.values():
        painter.text((x_px, y_px), "%s %d级" % (avatar.avatar_name, avatar.level), font=fnt, fill=avatar_info_color)
        y_px += 24
        painter.text((x_px, y_px), "%s %d级 精炼%d" % (avatar.weapon.name, avatar.weapon.level, avatar.weapon.refinement)
                     , font=fnt, fill=avatar_info_color)
        y_px += 24
        painter.text((x_px, y_px),
                     "a: %d e: %d q:%d" % (avatar.skill_level["a"], avatar.skill_level["e"], avatar.skill_level["q"])
                     , font=fnt, fill=avatar_info_color)
        y_px += 24
        for reliquary in avatar.reliquaries:
            painter.text((x_px, y_px), "%s" % reliquary, font=fnt, fill=avatar_info_color)
            y_px += 24
        for draw_fight_prop_id in [2000, 2001, 2002, 20, 22, 23, 28, 40, 41, 42, 43, 44, 45, 46, 30, 26]:
            if draw_fight_prop_id in avatar.draw_fight_prop:
                if draw_fight_prop_id in [2000, 2001, 2002, 28]:
                    painter.text((x_px, y_px), "%s: %d" % (draw_fight_prop_dict[draw_fight_prop_id],
                                 round(avatar.draw_fight_prop[draw_fight_prop_id], 0)), font=fnt,
                                 fill=avatar_info_color)
                else:
                    painter.text((x_px, y_px), "%s: %.1f%%" % (draw_fight_prop_dict[draw_fight_prop_id],
                                                           round((avatar.draw_fight_prop[draw_fight_prop_id]*100), 3)),
                                 font=fnt, fill=avatar_info_color)
                y_px += 24
        y_px = 44
        x_px += 360
    x_px = 98
    y_px = 664
    painter.text((x_px, y_px), "战斗时间:%.2fs    总伤害: %d" % (combat_duration/1000, total_damage), font=fnt,
                 fill=avatar_info_color)
    x_px = 216
    y_px = 729
    painter.text((x_px, y_px), "实际暴击率", font=fnt, fill=avatar_info_color)
    x_px += 142
    painter.text((x_px, y_px), "反应率", font=fnt, fill=avatar_info_color)
    x_px += 142
    painter.text((x_px, y_px), "伤害占比", font=fnt, fill=avatar_info_color)
    x_px = 86
    y_px = 800
    for avatar in avatar_obj_dict.values():
        avatar_name = avatar.avatar_name
        if avatar_name in avatar_hit_times:
            hit_times = avatar_hit_times[avatar_name]
        else:
            hit_times = 0
        if avatar_name in avatar_trigger_reaction_times:
            trigger_reaction_times = avatar_trigger_reaction_times[avatar_name]
        else:
            trigger_reaction_times = 0
        if avatar_name in avatar_crit_times:
            crit_times = avatar_crit_times[avatar_name]
        else:
            crit_times = 0
        if avatar_name in avatar_damage_dict:
            damage = avatar_damage_dict[avatar_name]
        else:
            damage = 0
        painter.text((x_px, y_px), "%s" % avatar_name, font=fnt, fill=avatar_info_color)
        x_px += 140
        painter.text((x_px, y_px), "%.2f%%" % (crit_times * 100 / hit_times) if hit_times != 0 else "0", font=fnt, fill=avatar_info_color)
        x_px += 140
        painter.text((x_px, y_px), "%.2f%%" % (trigger_reaction_times * 100 / hit_times) if hit_times != 0 else "0", font=fnt,
                     fill=avatar_info_color)
        x_px += 140
        painter.text((x_px, y_px), "%.2f%%" % (damage * 100 / total_damage) if total_damage != 0 else "0", font=fnt, fill=avatar_info_color)
        x_px = 86
        y_px += 72
    matplotlib.use("TkAgg")
    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
    plt.rcParams['axes.unicode_minus'] = False
    fig = plt.figure(figsize=(6, 6))
    damage_time_from_0, matching_time_damage = cal_dps(time_damage_dict)
    plt.title("DPS时序图")
    plt.plot(damage_time_from_0, matching_time_damage)
    fig.canvas.draw()
    pil_damage = Image.frombytes('RGB', fig.canvas.get_width_height(), fig.canvas.tostring_rgb())
    copy_img.paste(pil_damage, (770, 600))
    plt.clf()
    stamina_time_from_0, matching_time_stamina = deal_stamina(stamina_time_dict)
    plt.title("体力时序图")
    plt.plot(stamina_time_from_0, matching_time_stamina)
    fig.canvas.draw()
    pil_stamina = Image.frombytes('RGB', fig.canvas.get_width_height(), fig.canvas.tostring_rgb())
    copy_img.paste(pil_stamina, (65, 1284))
    plt.clf()
    avatar_energy_time_map = deal_energy(avatar_energy_time_dict)
    plt.title("能量时序图")
    for avatar in avatar_obj_dict.values():
        if avatar.avatar_name in avatar_energy_time_map:  # 防止队伍角色能量满却一直未使用元素爆发
            time_, energy = avatar_energy_time_map[avatar.avatar_name]
            plt.plot(time_, energy, label=avatar.avatar_name)
    plt.legend()
    fig.canvas.draw()
    pil_energy = Image.frombytes('RGB', fig.canvas.get_width_height(), fig.canvas.tostring_rgb())
    copy_img.paste(pil_energy, (785, 1284))
    copy_img.save("%s\\%s\\%s分析%s.png" % (file_path, file_name_without_ext, file_name_without_ext, combat_round))


avatar_id_dict = read_json("avatar.json")
weapon_id_dict = read_json("weapon.json")
reliquary_id_dict = read_json("reliquary.json")
monster_id_dict = read_json("monster.json")
fight_prop_dict = read_json("fight_prop.json")
draw_fight_prop_dict = read_json("draw_fight_prop.json")
element_id_dict = read_json("element.json")
element_reaction_id_dict = read_json("element_reaction.json")
root = Tk()
root.withdraw()  # 隐藏主窗口，只弹出打开文件对话框
nahida_file = filedialog.askopenfilename()
file_name = os.path.split(nahida_file)[1]
file_name_without_ext = os.path.splitext(file_name)[0]
file_path = os.getcwd()
if os.path.exists("%s\\%s" % (file_path, file_name_without_ext)):
    print("%s 文件夹已存在" % file_name_without_ext)
    sys.exit()
else:
    os.mkdir("%s\\%s" % (file_path, file_name_without_ext))
f = open(nahida_file, "r", encoding="utf-8")
lines = f.readlines()
sorted_data = []
for line in lines:
    ts, packet_name, data = line.split(" ", 2)
    sorted_data.append((int(ts), packet_name, eval(data)))
# sorted_data = sorted(sorted_data, key=lambda x: x[0])  # 排序会出错，可能是网卡了导致kcp重传导致
avatar_obj_dict = {}
gadget_obj_dict = {}
monster_obj_dict = {}
monster_name_list = []
avatar_entity_to_guid_map = {}
combat_start = False
combat_start_time = 0
attack_time_exactly = 0
avatar_hit_times = {}
avatar_trigger_reaction_times = {}
avatar_crit_times = {}
avatar_energy_time_dict = {}
avatar_damage_dict = {}
time_damage_dict = {}
stamina_time_dict = {}
total_damage = 0
assume_end_time = 0
all_combat_text = open("%s\\%s\\%s分析.txt" % (file_path, file_name_without_ext, file_name_without_ext), "w", encoding="utf-8")
combat_round = 1

for line in sorted_data:
    ts, packet_name, data = line
    if packet_name == "SceneTeamUpdateNotify":
        if combat_start:
            combat_end_time = assume_end_time
            draw(combat_end_time-combat_start_time)
            combat_round += 1
            all_combat_text.close()
            all_combat_text = open(
                "%s\\%s\\%s分析%s.txt" % (file_path, file_name_without_ext, file_name_without_ext, combat_round),
                "w", encoding="utf-8")
            combat_start_time = 0
            attack_time_exactly = 0
            avatar_hit_times = {}
            avatar_trigger_reaction_times = {}
            avatar_crit_times = {}
            avatar_damage_dict = {}
            time_damage_dict = {}
            stamina_time_dict = {}
            total_damage = 0
        combat_start = False
        for guid, avatar_obj in avatar_obj_dict.items():
            del avatar_obj
        avatar_obj_dict = {}
        for scene_info in data['scene_team_avatar_list']:
            info = scene_info['scene_entity_info']
            if info['entity_type'] == 'PROT_ENTITY_TYPE_AVATAR':
                avatar = info['avatar']
                avatar_id = avatar['avatar_id']
                avatar_guid = avatar['guid']
                avatar_obj_dict.update({avatar_guid: Avatar()})
                for prop in info["prop_list"]:
                    if prop["type"] == 4001:
                        avatar_obj_dict[avatar_guid].level = prop['prop_value']["val"]  # 或者ival，暂不清楚
                        break
                fight_props = info['fight_prop_list']
                for fight_prop in fight_props:
                    if len(fight_prop) != 1:
                        avatar_obj_dict[avatar_guid].fight_prop.update(
                            {fight_prop_dict[fight_prop['prop_type']]: fight_prop['prop_value']})
                        if fight_prop['prop_type'] in draw_fight_prop_dict:
                            avatar_obj_dict[avatar_guid].draw_fight_prop.update(
                                {fight_prop['prop_type']: fight_prop['prop_value']})
                avatar_obj_dict[avatar_guid].avatar_id = avatar_id
                weapon = avatar["weapon"]
                avatar_obj_dict[avatar_guid].weapon.name = weapon_id_dict[weapon['item_id']]
                avatar_obj_dict[avatar_guid].weapon.level = weapon["level"]
                if 'affix_map' in weapon:
                    avatar_obj_dict[avatar_guid].weapon.refinement = weapon['affix_map'][0][100000 + weapon['item_id']] + 1
                else:
                    avatar_obj_dict[avatar_guid].weapon.refinement = 1
                if 'reliquary_list' in avatar:
                    reliquaries = avatar['reliquary_list']
                    reliquaries_name = []
                    for reliquary in reliquaries:
                        reliquary_name = reliquary_id_dict[reliquary['item_id']]
                        reliquaries_name.append(reliquary_name)
                    avatar_obj_dict[avatar_guid].reliquaries = reliquaries_name
                skills = avatar['skill_level_map']
                skill_dict = {}
                for skill in skills:
                    skill_dict.update(skill)
                sorted_skill = sorted(skill_dict)
                avatar_obj_dict[avatar_guid].skill_map = {sorted_skill[0]: "a", sorted_skill[1]: "e",
                                                          sorted_skill[2]: "q"}
                skill_map = {"a": skill_dict[sorted_skill[0]], "e": skill_dict[sorted_skill[1]],
                             "q": skill_dict[sorted_skill[2]]}
                if 'proud_skill_extra_level_map' in avatar:
                    for extra_skill in avatar['proud_skill_extra_level_map']:
                        for key, value in extra_skill.items():
                            if str(key).endswith("32"):
                                skill_map["e"] += value
                            elif str(key).endswith("39"):
                                skill_map["q"] += value
                            else:
                                skill_map["a"] += value
                avatar_obj_dict[avatar_guid].skill_level = skill_map
    elif packet_name == "EvtCreateGadgetNotify":
        entity_id = data['entity_id']
        gadget_obj_dict.update({entity_id: Gadget()})
        gadget_obj_dict[entity_id].set_owner_id(data['prop_owner_entity_id'])
    elif packet_name == "SceneEntityAppearNotify":
        for entity in data['entity_list']:
            if entity['entity_type'] == 'PROT_ENTITY_TYPE_MONSTER':
                monster_obj_dict.update({entity['entity_id']: Monster()})
                monster_obj_dict[entity['entity_id']].entity_id = entity['entity_id']
                if entity["monster"]["monster_id"] in monster_id_dict:
                    monster = monster_id_dict[entity["monster"]["monster_id"]]
                else:
                    monster = "未知怪物"
                num = 1
                while monster + str(num) in monster_name_list:
                    num += 1
                monster_obj_dict[entity['entity_id']].monster_name = monster + str(num)
                monster_name_list.append(monster + str(num))
            elif entity['entity_type'] == 'PROT_ENTITY_TYPE_AVATAR':
                if entity["entity_id"] not in avatar_entity_to_guid_map:
                    avatar = entity['avatar']
                    avatar_entity_to_guid_map.update({entity["entity_id"]: avatar["guid"]})
                    avatar_obj_dict[avatar["guid"]].entity_id = entity["entity_id"]
                avatar_guid = entity['avatar']["guid"]
                if combat_start_time:
                    all_combat_text.write("%.2fs %s登场\n" % ((ts-combat_start_time)/1000, avatar_obj_dict[avatar_guid].avatar_name))
                else:
                    all_combat_text.write(
                        "0s 当前场上角色%s\n" % avatar_obj_dict[avatar_guid].avatar_name)
                for prop in entity['fight_prop_list']:
                    if len(prop) != 1:
                        avatar_obj_dict[avatar_guid].fight_prop.update(
                            {fight_prop_dict[prop['prop_type']]: prop['prop_value']})
    elif packet_name == "UnionCmdNotify":
        for union_data in data:
            if 'CombatInvocationsNotify' in union_data:
                invoke = union_data['CombatInvocationsNotify']['invoke_list'][0]
                if invoke["argument_type"] == 'COMBAT_TYPE_ARGUMENT_EVT_BEING_HIT':
                    assume_end_time = ts
                    attack_result = invoke['combat_data']["attack_result"]
                    try:
                        attacker_entity_id = attack_result["attacker_id"]
                        attack_time = attack_result["attack_timestamp_ms"]
                        if attack_time_exactly == 0:
                            attack_time_exactly = attack_time
                        elif attack_time < attack_time_exactly:
                            attack_time_exactly = attack_time
                        attackee = attack_result['defense_id']
                        if str(attackee).startswith("33"):
                            if not combat_start:
                                combat_start = True
                                combat_start_time = ts
                                all_combat_text.write("战斗开始\n")
                            if str(attacker_entity_id).startswith("88"):
                                attacker_entity_id = gadget_obj_dict[attacker_entity_id].owner_id
                            if str(attacker_entity_id).startswith("16"):
                                attacker = avatar_obj_dict[avatar_entity_to_guid_map[attacker_entity_id]].avatar_name
                            else:
                                continue
                            attackee_name = monster_obj_dict[attackee].monster_name
                            if "damage" in attack_result:
                                damage = attack_result["damage"]
                                if attacker not in avatar_hit_times:
                                    avatar_hit_times[attacker] = 0
                                avatar_hit_times[attacker] += 1
                                apply_element = False
                                crit = False
                                total_damage += damage
                                if attacker not in avatar_damage_dict:
                                    avatar_damage_dict[attacker] = 0
                                avatar_damage_dict[attacker] += damage
                                if attack_time in time_damage_dict:
                                    time_damage_dict[attack_time] += damage
                                else:
                                    time_damage_dict[attack_time] = damage
                                if 'element_durability_attenuation' in attack_result:
                                    apply_element = True
                                if "is_crit" in attack_result:
                                    crit = True
                                    if attacker not in avatar_crit_times:
                                        avatar_crit_times[attacker] = 0
                                    avatar_crit_times[attacker] += 1
                                if "element_type" in attack_result:
                                    element_type = element_id_dict[attack_result["element_type"]]
                                    all_combat_text.write("%.2fs %s对%s造成%d点%s元素伤害,该伤害%s, %s\n" % (
                                                         (ts-combat_start_time)/1000, attacker,
                                                          attackee_name, int(damage), element_type,
                                                          "暴击" if crit else "未暴击",
                                                          "造成元素附着" if apply_element else "未造成附着"))
                                else:
                                    all_combat_text.write("%.2fs %s对%s造成%d点物理伤害,该伤害%s\n" % ((ts-combat_start_time)/1000, attacker, attackee_name,
                                                          int(damage), "暴击" if crit else "未暴击"))
                            else:
                                all_combat_text.write("%.2fs %s对%s造成无效伤害\n" % ((ts-combat_start_time)/1000, attacker, attackee_name))
                    except KeyError:
                        pass
            if 'AbilityInvocationsNotify' in union_data:
                invoke = union_data['AbilityInvocationsNotify']['invokes'][0]
                if invoke["argument_type"] == 'ABILITY_INVOKE_ARGUMENT_META_TRIGGER_ELEMENT_REACTION':
                    if not combat_start:
                        combat_start = True
                        combat_start_time = ts
                        all_combat_text.write("战斗开始\n")
                    # 17: '火元素扩散', 18: '水元素扩散', 19: '雷元素扩散', 20: '冰元素扩散', 21: '风火湮灭',
                    # 22: '风水湮灭', 23: '风雷湮灭', 24: '风冰湮灭'
                    # 附火：对燃烧状态实体施加火附着称为附火（无论是燃烧反应自挂火还是角色再次上火）
                    # 湮灭： 触发风元素反应时，有一极短的风火/水/冰/雷共存，将从共存到风元素消失的过程称为湮灭。通常和扩散同时发生。
                    # 但在打无相之风时，当核心缩回壳子，有概率出现未跳出扩散和伤害数字的情况，此时只出现了湮灭反应。
                    element_reaction = invoke["ability_data"]
                    trigger_on = invoke["entity_id"]
                    trigger_entity = element_reaction['trigger_entity_id']
                    if str(trigger_on).startswith("33"):
                        entity_name = monster_obj_dict[trigger_on].monster_name
                    elif str(trigger_on).startswith("16"):
                        entity_name = avatar_obj_dict[avatar_entity_to_guid_map[trigger_on]].avatar_name
                    else:
                        continue
                    element_reaction_type = element_reaction["element_reaction_type"]
                    if str(trigger_entity).startswith("16"):
                        try:  # 防止上一队伍残留
                            trigger_avatar = avatar_obj_dict[avatar_entity_to_guid_map[trigger_entity]].avatar_name
                        except KeyError:
                            continue
                        if trigger_avatar not in avatar_trigger_reaction_times:
                            avatar_trigger_reaction_times[trigger_avatar] = 0
                        avatar_trigger_reaction_times[trigger_avatar] += 1
                    elif str(trigger_entity).startswith("88"):
                        trigger_avatar_id = gadget_obj_dict[trigger_entity].owner_id
                        if str(trigger_avatar_id).startswith("16"):
                            try:
                                trigger_avatar = avatar_obj_dict[avatar_entity_to_guid_map[trigger_avatar_id]].avatar_name
                            except KeyError:
                                continue
                            if trigger_avatar not in avatar_trigger_reaction_times:
                                avatar_trigger_reaction_times[trigger_avatar] = 0
                            if element_reaction_type not in [4, 5, 10, 11, 13, 14, 21, 22, 23, 24, 26, 32]:
                                avatar_trigger_reaction_times[trigger_avatar] += 1
                        elif trigger_on == trigger_avatar_id:
                            trigger_avatar = monster_obj_dict[trigger_on].monster_name
                        else:
                            continue
                    else:
                        continue
                    if element_reaction_type in element_reaction_id_dict:
                        if element_reaction_type in [4, 5, 10, 11, 13, 14, 15, 26, 32]:
                            all_combat_text.write("%.2fs %s为%s施加了%s\n" % (
                                (ts-combat_start_time) / 1000, trigger_avatar, entity_name, element_reaction_id_dict[element_reaction_type]))
                        elif element_reaction_type in [17, 18, 19, 20, 21, 22, 23, 24]:
                            all_combat_text.write("%.2fs %s对%s触发了%s反应\n" % (
                                (ts-combat_start_time) / 1000, trigger_avatar, entity_name, element_reaction_id_dict[element_reaction_type]))
                        else:
                            element_reactor_type = element_reaction["element_reactor_type"]
                            element_source_type = element_reaction['element_source_type']
                            if element_reactor_type in element_id_dict:
                                if element_source_type in element_id_dict:
                                    all_combat_text.write("%.2fs %s对%s触发了%s%s%s反应\n" % ((ts-combat_start_time) / 1000,
                                                                                              trigger_avatar, entity_name, element_id_dict[element_source_type],
                                                                                              element_id_dict[element_reactor_type],
                                                                                              element_reaction_id_dict[element_reaction_type]))
                                else:
                                    print("存在未发现元素类型%s" % element_source_type)
                            else:
                                print("存在未发现元素类型%s" % element_reactor_type)
                    else:
                        print("发现未知元素反应类型%d" % element_reaction_type)
    elif packet_name == "AvatarFightPropUpdateNotify":
        guid = data['avatar_guid']
        if guid in avatar_obj_dict:  # 上一个队伍会遗留
            avatar = avatar_obj_dict[guid]
            update_fight_props = data['fight_prop_map']
            for prop in update_fight_props:
                for key, value in prop.items():
                    prop_name = fight_prop_dict[key]
                    if key in [1000, 1001, 1002, 1003, 1004, 1005, 1006]:
                        if avatar.avatar_name not in avatar_energy_time_dict:
                            avatar_energy_time_dict[avatar.avatar_name] = {}
                        avatar_energy_time_dict[avatar.avatar_name].update({ts: value})
                    if prop_name in avatar.fight_prop:
                        if avatar.fight_prop[prop_name] != value:
                            if value >= 5:
                                all_combat_text.write("%.2fs %s的%s由%d变化为%d\n" % ((ts-combat_start_time)/1000 if combat_start_time else 0, avatar.avatar_name, prop_name, avatar.fight_prop[prop_name], value))
                            else:
                                all_combat_text.write("%.2fs %s的%s由%.2f变化为%.2f\n" % ((ts-combat_start_time)/1000 if combat_start_time else 0, avatar.avatar_name, prop_name, avatar.fight_prop[prop_name], value))
                            avatar.fight_prop[prop_name] = value
                    else:
                        all_combat_text.write("%.2fs %s的%s由0变化为%d\n" % ((ts-combat_start_time)/1000 if combat_start_time else 0, avatar.avatar_name, prop_name, value))
                        avatar.fight_prop[prop_name] = value
    elif packet_name == "PlayerPropNotify":
        for prop_map in data['prop_map']:
            if 10011 in prop_map:
                stamina_time_dict.update({ts: prop_map[10011]["val"]})
                if combat_start_time:
                    all_combat_text.write("%.2fs 当前体力为%.2f\n" % ((ts-combat_start_time)/1000, prop_map[10011]["val"]/100))
                else:
                    all_combat_text.write(
                        "0s 当前体力为%.2f\n" % (prop_map[10011]["val"] / 100))
    # elif packet_name == "ChangeAvatarRsp":
    #     # print("切换角色%s" % avatar_obj_dict[data['cur_guid']].avatar_name)
    elif packet_name == "CombatInvocationsNotify":
        for invoke in data['invoke_list']:
            if invoke['argument_type'] == 'COMBAT_TYPE_ARGUMENT_BEING_HEALED_NTF':
                combat_data = invoke['combat_data']
                if 'real_heal_amount' in combat_data:
                    target_id = combat_data["target_id"]
                    heal_amount = combat_data['real_heal_amount']
                    healer = combat_data['source_id']
                    if str(healer).startswith("16"):
                        heal_avatar = avatar_obj_dict[avatar_entity_to_guid_map[healer]].avatar_name
                    elif str(healer).startswith("88"):
                        heal_avatar_id = gadget_obj_dict[healer].owner_id
                        if str(heal_avatar_id).startswith("16"):
                            heal_avatar = avatar_obj_dict[avatar_entity_to_guid_map[heal_avatar_id]].avatar_name
                    else:
                        continue
                    if str(target_id).startswith("16"):
                        target_avatar = avatar_obj_dict[avatar_entity_to_guid_map[target_id]].avatar_name
                        all_combat_text.write("%.2fs %s为%s治疗了%d血量\n" % ((ts-combat_start_time)/1000, heal_avatar, target_avatar, int(heal_amount)))
    elif packet_name == "DungeonChallengeBeginNotify":
        combat_start = True
        combat_start_time = ts
        all_combat_text.write("战斗开始\n")
    # elif line.startswith("EvtDoSkillSuccNotify"):  # 先跳过
    #     new_line = line.replace("EvtDoSkillSuccNotify ", "")
    #     new_line = eval(new_line)
    #     skill = new_line['skill_id']
    #     avatar = avatar_obj_dict[avatar_entity_to_guid_map[new_line['caster_id']]]
    #     print("%s使用了%s" % (avatar.avatar_name, avatar.skill_map[skill]))
all_combat_text.close()
# if combat_start:  # 中途退出未接收SceneTeamUpdateNotify使用
#     draw(assume_end_time - combat_start_time)
