"""
种子脚本：通过 webnovel.py 将设定集中的已知实体导入 index.db
"""
import subprocess, json, sys, pathlib

ROOT = pathlib.Path(r"H:\Code\mynovel")
WEB_CLI = [sys.executable, str(ROOT / ".opencode" / "scripts" / "webnovel.py"), "--project-root", str(ROOT)]

def run_index(*args):
    """Run `webnovel.py --project-root ROOT index <args>`"""
    cmd = WEB_CLI + ["index"] + list(args)
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        err = (r.stderr or r.stdout).strip()
        print(f"  ERR: {err[:120]}")
    return r

def upsert_entity(eid, etype, name, tier="重要", desc="", first=0, last=0, protagonist=False):
    data = json.dumps({
        "id": eid, "type": etype, "canonical_name": name,
        "tier": tier, "desc": desc,
        "current": {}, "first_appearance": first, "last_appearance": last,
        "is_protagonist": protagonist, "is_archived": False
    }, ensure_ascii=False)
    return run_index("upsert-entity", "--data", data)

def upsert_relationship(from_e, to_e, rtype, desc, chapter=0):
    data = json.dumps({
        "from_entity": from_e, "to_entity": to_e,
        "type": rtype, "description": desc, "chapter": chapter
    }, ensure_ascii=False)
    return run_index("upsert-relationship", "--data", data)

print("=== Seeding entities ===\n")

# ========= 主角 =========
upsert_entity("shen_an", "角色", "沈安", "核心", "窥痕境初痕（表面），前执痕。沈氏子弟，送进砥砺宗。躺平即是修炼。", 1, 0, True)

# ========= 沈氏家族 =========
upsert_entity("shen_huaiyuan", "角色", "沈怀远", "重要", "沈氏戒律长老，试过教训儿子反被打败", 1, 0)
upsert_entity("shen_chongwu", "角色", "沈崇武", "重要", "沈氏大长老，推动逐出沈安", 1, 0)
upsert_entity("shen_shouzhuo", "角色", "沈守拙", "重要", "沈氏族中老实人，欠沈安两顿酒", 1, 0)
upsert_entity("shen_qingluo", "角色", "沈青萝", "重要", "沈氏天才少女，绘制沈安每日活动轨迹图", 1, 0)
upsert_entity("shen_xiaohe", "角色", "沈小禾", "重要", "沈守拙之妹，拜沈安为师学道痕", 1, 0)
upsert_entity("shen_shi", "世族", "沈氏家族", "重要", "青石城戒律世家，与谷氏隔山采脉三百年", 1, 0)

# ========= 砥砺宗 =========
upsert_entity("tieli", "角色", "铁骊", "重要", "砥砺宗宗主，从必须磨动到发现不对劲", 1, 0)
upsert_entity("wen_xiaolu", "角色", "温小鹿", "重要", "砥砺宗二师姐，沈安的沉默同盟", 1, 0)
upsert_entity("tiesiyuan", "角色", "铁思源", "次要", "铁氏包装的天才少年", 1, 0)
upsert_entity("dili_zong", "宗门", "砥砺宗", "重要", "铁氏把持，铁脊航线崛起于近百年。宗训：天道酬勤。", 1, 0)

# ========= 云隐宗 =========
upsert_entity("yunyin_zong", "宗门", "云隐宗", "重要", "苍渊老牌宗派，隐世悟道数百年。道痕理解最深。", 1, 0)
upsert_entity("liu_shixiong", "角色", "柳师兄", "重要", "云隐宗弟子，沈安的第一个非家族朋友", 1, 0)
upsert_entity("neigui_zhanglao", "角色", "内鬼长老", "次要", "云隐宗长老，与影阁秘密交易", 1, 0)
upsert_entity("yunyin_zongzhu", "角色", "云隐宗宗主", "重要", "暗中保护沈安", 1, 0)

# ========= 玉华阁 =========
upsert_entity("yuhua_ge", "宗门", "玉华阁", "重要", "全女宗门，苏锦年暗线创立。以举报闻名，暗藏牵痕术。", 1, 0)
upsert_entity("yuge_zhizhu", "角色", "玉阁之主", "次要", "玉华阁对外话语权掌者，从不道歉只换话题", 1, 0)

# ========= 玄霄势力 =========
upsert_entity("xiao_changhe", "角色", "萧长河", "核心", "萧氏丹阁，沈溪风兄弟，道契创造者。修为顶点才在老婆面前像个初学者。", 1, 0)
upsert_entity("su_jinnian", "角色", "苏锦年", "核心", "萧长河之妻，暗线核心。怕纪元归零→计划一切→亲手推开了唯一的解法。", 1, 0)
upsert_entity("li_huai", "角色", "厉淮", "重要", "天律司第七执事，被沈溪风救过命。表面威严追捕，暗中拼命放水。", 1, 0)
upsert_entity("jian_lao", "角色", "鉴老", "重要", "巡天鉴器灵，黑历史被沈安捏着，暗中帮忙", 1, 0)
upsert_entity("shang_hen", "角色", "拭痕", "重要", "沈溪风仙器笔，二十三连败酒桌赌局被迫认爹", 1, 0)
upsert_entity("xuntian_jian", "法宝", "巡天鉴", "重要", "萧长河仙器，扫描天痕之脉定位沈安", 1, 0)
upsert_entity("xiao_shi", "玄霄势力", "萧氏丹阁", "重要", "玄霄炼丹世家", 1, 0)

# ========= 镇域司 =========
upsert_entity("zhenyu_si", "势力", "镇域司", "重要", "苍渊仲裁机构，端着一碗永远端不平的水", 1, 0)
upsert_entity("cao_sizheng", "角色", "曹司正", "次要", "镇域司长官，不允许违规发生在他看得见的地方", 1, 0)
upsert_entity("xu_zhishi", "角色", "许执事", "次要", "镇域司调查处，真的想秉公执法的年轻人", 1, 0)

# ========= 星汉阁 =========
upsert_entity("xinghan_ge", "宗门", "星汉阁", "重要", "陆川创立，周天星痕吞噬砥砺宗航线份额", 1, 0)
upsert_entity("lu_chuan", "角色", "陆川", "次要", "星汉阁创始人，被铁骊赶走才建出了更快的航线", 1, 0)

# ========= 新增势力 =========
upsert_entity("tuilu", "地下之络", "蜕庐", "重要", "苍渊最大中立商会，岩壁总账记录所有交易。门楣刻蝉蜕。", 1, 0)
upsert_entity("cen_buyan", "角色", "蜕庐主人·岑不言", "重要", "两百年不提问，只等人开口。手指叩桌——进制换算节奏。", 1, 0)
upsert_entity("yexiao", "地下之络", "夜鸮", "重要", "苍渊最古暗杀之络，无据点无名单。只接有资格的单。", 1, 0)
upsert_entity("yinge", "地下之络", "影阁", "重要", "苍渊情报交易之络，贩售你的需要——你不需要它不卖。", 1, 0)

# ========= 世家 =========
upsert_entity("fengjin_gu", "世族", "焚金谷·谷氏", "重要", "青石城西铸器世家，炉子四十年没熄。与沈氏隔山采脉三百年。", 1, 0)
upsert_entity("gu_fentian", "角色", "谷焚天", "重要", "焚金谷谷主，刻痕境。年年在沈氏族会喝完茶说'明年我还来'。", 1, 0)
upsert_entity("qinghe_cui", "世族", "清河崔氏", "重要", "以辨痕立族，清鉴帖传家。能辨真伪不能辨趋势。盲区养活了牵痕术。", 1, 0)

# ========= 学宫 =========
upsert_entity("qingshi_xuegong", "学府", "青石学宫", "重要", "苍渊平民公学，来者不拒束脩随缘。造假事件后更近关门。", 1, 0)
upsert_entity("kouming_tang", "学府", "叩鸣堂", "重要", "苍渊北域私立学宫。新生先敲钟——据说钟声辨根骨。从不造假，因为只有座满之后的人才收。", 1, 0)
upsert_entity("zhou_gongzhu", "角色", "周宫主", "次要", "青石学宫第三代宫主，为维持学宫包装纪秋萤", 1, 0)
upsert_entity("ji_qiuying", "角色", "纪秋萤", "次要", "青石学宫女弟子，塌楼的被包装天才", 1, 0)

# ========= 虚海 =========
upsert_entity("yun_du", "角色", "云渡", "重要", "渡舟人少女，唯一的礼物派送员。沈安的女=麻烦等式的唯一裂痕。", 1, 0)
upsert_entity("lao_saogong", "角色", "老艄公", "次要", "渡舟人，你知道你是谁所以一句话没多问。", 1, 0)

# ========= 地点 =========
upsert_entity("loc_qingshi", "地点", "青石城", "重要", "沈氏与谷氏共存之城", 1, 0)
upsert_entity("loc_tieji", "地点", "铁脊山脉", "重要", "砥砺宗所在，飞舟航线枢纽", 1, 0)
upsert_entity("loc_yunwu", "地点", "云雾山脉", "重要", "云隐宗所在，道痕枢点最密之处", 1, 0)
upsert_entity("loc_cangyuan", "地点", "苍渊", "核心", "道痕体系发源地，灵气稀薄，法则最松", 1, 0)

print("\n=== Entities done. Now seeding relationships ===\n")

# ========= 核心关系 =========
upsert_relationship("shen_an", "shen_huaiyuan", "父子", "沉默中互相理解", 1)
upsert_relationship("shen_an", "shen_shouzhuo", "欠债", "两顿酒", 1)
upsert_relationship("shen_an", "shen_qingluo", "互相研究", "日轨交换", 1)
upsert_relationship("shen_an", "shen_xiaohe", "师徒", "教道痕", 1)
upsert_relationship("shen_an", "tieli", "博弈", "从磨不动到发现不对劲", 1)
upsert_relationship("shen_an", "wen_xiaolu", "沉默同盟", "不说话=最舒服", 1)
upsert_relationship("shen_an", "liu_shixiong", "朋友", "第一个非家族朋友", 1)
upsert_relationship("shen_an", "xiao_changhe", "前世兄弟", "四百年追逃", 1)
upsert_relationship("shen_an", "shang_hen", "父子(被动)", "酒桌认爹", 1)
upsert_relationship("shen_an", "jian_lao", "交易", "黑历史换暗中放水", 1)
upsert_relationship("shen_an", "yun_du", "被送礼物", "躲不掉", 1)
upsert_relationship("shen_huaiyuan", "tieli", "旧识", "青石学宫同窗", 1)
upsert_relationship("shen_huaiyuan", "gu_fentian", "旧识", "同窗/隔着矿山", 1)
upsert_relationship("shen_chongwu", "shen_huaiyuan", "对立", "族内权力之争", 1)
upsert_relationship("shen_shi", "fengjin_gu", "同城对立", "隔山采脉三百年", 1)
upsert_relationship("xiao_changhe", "su_jinnian", "夫妻", "被拿捏", 1)
upsert_relationship("su_jinnian", "yuhua_ge", "暗线创立", "抹去姓名的创始人", 1)
upsert_relationship("dili_zong", "xinghan_ge", "竞争", "飞舟 vs 天痕", 1)
upsert_relationship("dili_zong", "yunyin_zong", "同源对立", "隐世 vs 入世", 1)
upsert_relationship("yunyin_zong", "qinghe_cui", "师徒输送", "改良清鉴帖", 1)
upsert_relationship("yunyin_zong", "kouming_tang", "师徒输送", "推荐旁听", 1)
upsert_relationship("fengjin_gu", "dili_zong", "供应商", "铸造飞舟配件", 1)
upsert_relationship("qinghe_cui", "zhenyu_si", "充任", "辨痕者在调查处", 1)
upsert_relationship("yuhua_ge", "zhenyu_si", "偏袒", "举报→喝茶", 1)
upsert_relationship("tuilu", "yinge", "暗争", "知道过去多少 vs 知道今天谁想买", 0)
upsert_relationship("yinge", "yexiao", "业务合作", "卖消息→执行", 0)
upsert_relationship("yexiao", "shen_chongwu", "旧日交易", "暗线伏笔", 0)
upsert_relationship("yinge", "neigui_zhanglao", "交易", "倒卖信息", 1)
upsert_relationship("qingshi_xuegong", "kouming_tang", "竞争", "来者不拒 vs 今年座满", 1)
upsert_relationship("qingshi_xuegong", "shen_shi", "旧址", "沈氏捐赠", 1)
upsert_relationship("shen_shi", "loc_qingshi", "坐落", "沈氏立族青石城", 1)
upsert_relationship("dili_zong", "loc_tieji", "坐落", "砥砺宗立宗铁脊山脉", 1)
upsert_relationship("yunyin_zong", "loc_yunwu", "坐落", "云隐宗隐于云雾山脉", 1)
upsert_relationship("shen_an", "loc_qingshi", "故土", "青石柱下", 1)

print("\n=== DONE ===")
