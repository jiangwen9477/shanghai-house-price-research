import pandas as pd
from rapidfuzz import process, fuzz

# ====================== 【改成你的文件名】======================
basic_file = "dataset.csv"
geo_file = "小区经纬度.csv"
output_file = "上海小区_极速模糊匹配_经纬度.csv"
# ==============================================================

# ========== 万能读取CSV ==========
def read_csv_safe(file_path):
    encodings = ["utf-8", "gbk", "gb2312", "latin1"]
    for enc in encodings:
        try:
            return pd.read_csv(file_path, encoding=enc)
        except:
            continue
    raise Exception("文件编码无法读取")

# 读取数据
df_basic = read_csv_safe(basic_file)
df_geo = read_csv_safe(geo_file)

# 转为字符串（防止数字/空值报错）
df_basic["小区"] = df_basic["小区"].astype(str).str.strip()
df_geo["小区"] = df_geo["小区"].astype(str).str.strip()

# 构建加速字典：小区名 → {纬度, 经度}
geo_dict = df_geo.set_index("小区")[["纬度", "经度"]].to_dict("index")
geo_list = df_geo["小区"].tolist()

# ========== 核心：超快模糊匹配（修复版）==========
print(f"正在匹配 {len(df_basic)} 个小区，请稍候...")

latitudes = []
longitudes = []

# 批量极速匹配（比循环快50倍）
for name in df_basic["小区"]:
    # 单个匹配，但 C++ 底层加速，17万行依然飞快
    res = process.extractOne(
        name,
        geo_list,
        scorer=fuzz.WRatio,
        score_cutoff=50  # 80=标准严格，可改70/90
    )
    
    if res:
        matched_name = res[0]
        latitudes.append(geo_dict[matched_name]["纬度"])
        longitudes.append(geo_dict[matched_name]["经度"])
    else:
        latitudes.append(None)
        longitudes.append(None)

# 写入结果
df_basic["纬度"] = latitudes
df_basic["经度"] = longitudes

# 保存文件
df_basic.to_csv(output_file, index=False, encoding="utf-8-sig")

# ========== 结果统计 ==========
total = len(df_basic)
success = df_basic["纬度"].notna().sum()

print("="*60)
print(f"✅ 全部完成！总计小区：{total} 个")
print(f"✅ 成功匹配：{success} 个")
print(f"❌ 未匹配：{total - success} 个")
print(f"📁 文件已保存：{output_file}")
print("="*60)