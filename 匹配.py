import pandas as pd
from rapidfuzz import process, fuzz

# ====================== 【改成你的文件名】======================
basic_file = "dataset.csv"
geo_file = "小区经纬度.csv"
output_file = "上海小区_光速匹配_经纬度.csv"
# ==============================================================

# ========== 万能读取CSV ==========
def read_csv_safe(file_path):
    for enc in ["utf-8", "gbk", "gb2312"]:
        try:
            return pd.read_csv(file_path, encoding=enc)
        except:
            continue
    raise Exception("文件编码错误")

# 读取数据
df_basic = read_csv_safe(basic_file)
df_geo = read_csv_safe(geo_file)

# 清洗名称
df_basic["小区"] = df_basic["小区"].astype(str).str.strip()
df_geo["小区"] = df_geo["小区"].astype(str).str.strip()

# ========== 【核心黑科技：只匹配唯一值！】==========
# 1. 取出基本表里 唯一的小区名（可能只有几千个，而不是17万）
unique_names = df_basic["小区"].unique()
geo_list = df_geo["小区"].tolist()
geo_map = df_geo.set_index("小区")[["纬度", "经度"]].to_dict("index")

print(f"总数据行数：{len(df_basic)}")
print(f"唯一小区数量：{len(unique_names)}")
print("开始极速匹配...")

# 2. 只匹配 唯一小区（超快！）
match_result = {}
for name in unique_names:
    res = process.extractOne(
        name, geo_list,
        scorer=fuzz.WRatio,
        score_cutoff=50
    )
    if res:
        match_result[name] = geo_map[res[0]]
    else:
        match_result[name] = {"纬度": None, "经度": None}

# 3. 映射回17万行数据（秒级完成）
df_basic["纬度"] = df_basic["小区"].map(lambda x: match_result[x]["纬度"])
df_basic["经度"] = df_basic["小区"].map(lambda x: match_result[x]["经度"])

# ========== 保存结果 ==========
df_basic.to_csv(output_file, index=False, encoding="utf-8-sig")

# 统计
total = len(df_basic)
success = df_basic["纬度"].notna().sum()
print("="*60)
print(f"✅ 光速完成！总小区行数：{total}")
print(f"✅ 唯一小区：{len(unique_names)}")
print(f"✅ 匹配成功：{success} 行")
print(f"📁 文件已保存：{output_file}")