import os
import random

# 素材输出目录
output_dir = os.path.join(os.path.dirname(__file__), "files")
os.makedirs(output_dir, exist_ok=True)

# 1. 空TXT文件
with open(os.path.join(output_dir, "empty.txt"), "w", encoding="utf-8") as f:
    f.write("")

# 2. 超过10MB的超大TXT文件（约12MB）
with open(os.path.join(output_dir, "oversize_file.txt"), "w", encoding="utf-8") as f:
    # 每行100字符，写12万行，约12MB
    line = "这是测试超大文件的填充内容，用来验证文件大小拦截逻辑。" * 3 + "\n"
    for _ in range(120000):
        f.write(line)

# 3. 错误格式文件（伪装成jpg/docx，实际是文本）
with open(os.path.join(output_dir, "fake_image.jpg"), "w", encoding="utf-8") as f:
    f.write("这不是真正的图片，用来测试格式校验")
with open(os.path.join(output_dir, "fake_doc.docx"), "w", encoding="utf-8") as f:
    f.write("这不是真正的Word文档，用来测试格式校验")

# 4. 超长输入文本（1200字）
long_text = "测试超长输入问题" + "。这是重复填充的内容，用来验证输入长度拦截" * 200
with open(os.path.join(output_dir, "long_input.txt"), "w", encoding="utf-8") as f:
    f.write(long_text)

# 6. GBK编码的TXT文件
with open(os.path.join(output_dir, "gbk_encoding.txt"), "w", encoding="gbk") as f:
    f.write("这是GBK编码的文件，用来测试编码异常兜底。")

# 9. 特殊字符文本
special_text = "😀😁😂🤣😃😄😅😆😉😊😋😎😍😘🥰😗😙😚🙂🤗🤩🤔🤨😐😑😶🙄😏😣😥😮🤐😯😪😫🥱😴😌😛😜😝🤤😒😓😔😕🙃🤑😲🙁😖😞😟😤😢😭😦😧😨😩🤯😬😰😱🥵🥶😳🤪😵🥴😠😡🤬🥺😷🤒🤕🤑🤠"
special_text += "\n!@#$%^&*()_+-=[]{}|;':\",./<>?`~"
special_text += "\n测试特殊符号、emoji混合输入是否正常"
with open(os.path.join(output_dir, "special_chars.txt"), "w", encoding="utf-8") as f:
    f.write(special_text)

print(f"✅ 所有测试素材已生成，路径：{output_dir}")
