import os
import random
import shutil

# 输入文件夹路径和划分比例
folder_path = './labels/'
train_ratio = 0.8

# 检查文件夹是否存在
if not os.path.exists(folder_path):
    print("文件夹不存在！")
    exit()

# 获取所有png和txt文件
png_files = [file for file in os.listdir(folder_path) if file.endswith(".png")]
txt_files = [file for file in os.listdir(folder_path) if file.endswith(".txt")]

# 检查文件数量是否相等
if len(png_files) != len(txt_files):
    print("图片和标签数量不匹配！")
    exit()

# 打乱文件顺序
random.shuffle(png_files)

# 划分训练集和验证集
train_size = int(len(png_files) * train_ratio)
train_png = png_files[:train_size]
train_txt = [file.replace(".png", ".txt") for file in train_png]
val_png = png_files[train_size:]
val_txt = [file.replace(".png", ".txt") for file in val_png]

# 创建文件夹和子文件夹
if not os.path.exists("images/train"):
    os.makedirs("images/train")
if not os.path.exists("images/val"):
    os.makedirs("images/val")
if not os.path.exists("labels/train"):
    os.makedirs("labels/train")
if not os.path.exists("labels/val"):
    os.makedirs("labels/val")

# 复制文件到目标文件夹
for file in train_png:
    shutil.copy(os.path.join(folder_path, file), "images/train")
for file in train_txt:
    shutil.copy(os.path.join(folder_path, file), "labels/train")
for file in val_png:
    shutil.copy(os.path.join(folder_path, file), "images/val")
for file in val_txt:
    shutil.copy(os.path.join(folder_path, file), "labels/val")


print("处理完成！")