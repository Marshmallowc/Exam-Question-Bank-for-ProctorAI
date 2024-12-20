import json
import re
import tkinter as tk
import uuid
from tkinter import filedialog, messagebox, ttk
import cv2
import datetime
import pandas as pd
import mysql.connector
import face_recognition
import os
import numpy as np
import math
# 上传图片的函数
from PIL import Image
import numpy as np4

# 存储所有人脸编码的列表
encodings = []

# 数据库配置
db_config = {
    'host': 'localhost',
    'user': 'mysql-container',
    'password': "123456",
    'database': "xzs",
    'charset': 'utf8mb4'  # 或者其他适合的字符集
}




def create_connection():
    connection = mysql.connector.connect(**db_config)
    return connection

# 定义安全文件名的函数
def safe_file_name(file_path):
    base_name = os.path.basename(file_path)
    return base_name.encode('utf-8').decode('utf-8')

# 定义提取信息的函数
def extract_info(file_name):
    base_name = os.path.splitext(file_name)[0]  # 去掉文件扩展名
    stuNo = ""
    count_no = 0

    for ch in base_name:
        if (ch >= '0' and ch <= '9') or (ch >= '65' and ch <= "90") or (ch >= "97" and ch <= "122"):
            stuNo += ch
            count_no += 1
        else : break

    stuName = base_name[count_no:]
    print(f"在extract_info中提取到的信息分别为{stuNo}和{stuName}")

    return stuNo, stuName



def insert_face_encode(connection, stuName, stuNo, face_encoding):
    insert_query = """
    INSERT INTO t_face_encoding (face_name, stuNo, encoding)
    VALUES (%s, %s, %s)
    """
    cursor =connection.cursor()
    encoding_bolb = np.array(face_encoding).tobytes() # 转换为字节存储
    cursor.execute(insert_query, (stuName, stuNo, encoding_bolb))
    connection.commit()
    print(f"{stuNo} {stuName} 成功插入数据库")

def upload_images():
    file_paths = filedialog.askopenfilenames(filetypes=[("Image files", "*.jpg;*.jpeg;*.png")])
    if file_paths:
        for file_path in file_paths:
            # 使用 Pillow 读取图像
            image = Image.open(file_path)
            image = np.array(image)  # 转换为 NumPy 数组

            face_encoding = encode_face(image)
            encodings.append(face_encoding)

            # 提取文件名并打印
            file_name = os.path.basename(file_path)  # 获取文件名
            stuNo, stuName = extract_info(file_name)

            if len(face_encoding) == 0:
                print(f"{stuNo}{stuName}的图片加载失败")
                continue

            # 开始导入数据库
            # 1.连接数据库
            connection = create_connection()

            # 2.插入数据库
            insert_face_encode(connection, stuName, stuNo, face_encoding)

    messagebox.showinfo("Success", f"图片导入完成")

count_encode = 0
def encode_face(image):
    global count_encode
    count_encode += 1
    encoding =face_recognition.face_encodings(image)
    if len(encoding) > 0:
        # print(f'第{count_encode}次解码成功')
        return encoding[0]
    else :
        print(f"第{count_encode}次失败，图片不符合要求")
        return None

# 上传题库
#   t_question:
#       id,
#       question_type,
#       subject_id = 1,
#       score,
#       grade_level = 1,
#       difficult,
#       correct,
#       info_text_content_id,
#       create_user = 2,
#       status = 1,
#       create_time = new Date(),
#       deleted = 0x00,
#       knowledge_points
# question_type（文件）
# score（文件）
# difficult（文件）
# correct（文件）
# knowledge_points(文件)

#   t_text_content
#       id,
#       content,
#       create_time = new Date()
# content(文件）


# 文件中必须包含：
#   1.question_type
#   2.score
#   3.difficult
#   4.correct
#   5.knowledge_points
#   6.content

# 1:单选题(question_type=1)
#   格式：{"titleContent":"?????","analyze":"none","questionItemObjects":[{"prefix":"A","content":"?","score":null,"itemUuid":null},{"prefix":"B","content":"?","score":null,"itemUuid":null},{"prefix":"C","content":"?","score":null,"itemUuid":null},{"prefix":"D","content":"??","score":null,"itemUuid":null}],"correct":"D"}
#       "analyze" : "none"
#       "questionItemObjects" : [{"prefix": "A", "content": "x", "score": null, "itemUuid": null}], "correct":"D"}
#       1. 获取每个选项的内容
#       2. 获取除了ABCD内容外的题目内容
#       3. 转换格式
# 2.多选题(question_type=2)
#   格式：{"titleContent":"?????","analyze":"none","questionItemObjects":[{"prefix":"A","content":"a","score":null,"itemUuid":null},{"prefix":"B","content":"<p>b</p>","score":null,"itemUuid":null},{"prefix":"C","content":"<p class=\"ueditor-p\">c</p>","score":null,"itemUuid":null},{"prefix":"D","content":"d","score":null,"itemUuid":null}],"correct":""}
#
# 3.判断题(question_type=3)
#   格式：{"titleContent":"?????????","analyze":"?","questionItemObjects":[{"prefix":"A","content":"?","score":null,"itemUuid":null},{"prefix":"B","content":"?","score":null,"itemUuid":null}],"correct":"A"}
# 4.填空题(question_type=4)
#   格式：{"titleContent":"????????<span class=\"gapfilling-span 147a9808-6851-4ba3-b76e-6f77cadf5ab5\">1</span>","analyze":"none","questionItemObjects":[{"prefix":"1","content":"???","score":30,"itemUuid":"147a9808-6851-4ba3-b76e-6f77cadf5ab5"}],"correct":""}
# 5.简答题(question_type=5)
#   格式：{"titleContent":"<p>??????????????</p>","analyze":"none","questionItemObjects":[],"correct":"<p>xuxingaga</p>"}
import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import json
import re

def upload_tests():
    print("开始上传题库")

    # 创建一个Tkinter窗口用于文件选择
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口

    # 打开文件选择对话框
    file_name = filedialog.askopenfilename(
        title="选择Excel文件",
        filetypes=(("Excel文件", "*.xlsx;*.xls"), ("所有文件", "*.*"))
    )

    if not file_name:
        messagebox.showerror("错误", "未选择文件")
        return

    # 读取Excel文件内容
    try:
        raw_data = pd.read_excel(file_name)
    except Exception as e:
        messagebox.showerror("错误", f"无法读取文件：{e}")
        return

    # 假设你知道列名
    glb_question_types = list(raw_data['题目类型'])
    glb_scores = list(raw_data['分数'])
    glb_difficults = list(raw_data['难度'])
    glb_corrects = list(raw_data['答案'])
    glb_knowledge_points = list(raw_data['知识点'])
    glb_contents = list(raw_data['内容'])

    knowledge_str = [str(item) for item in glb_knowledge_points]
    glb_corrects_str = [str(item) for item in glb_corrects]

    for qtype, score, difficult, correct, knowledge, content in zip(glb_question_types, glb_scores, glb_difficults, glb_corrects_str, knowledge_str, glb_contents):
        # 插入t_text_content并记录插入的id
        print(knowledge)
        print(type(knowledge))

        # 根据type生成t_text_content中的content
        if qtype >= 1 and qtype <= 5:
            correct_tmp = ""
            if qtype == 2:
                for i, ch in enumerate(correct):
                    correct_tmp += ch
                    if i != len(correct) - 1:
                        correct_tmp += ","
                correct = correct_tmp
            print(correct)

            question_content = extract_question(content, qtype)
            options = re.findall(r'([A-D]\.\s*.*)', content)
            if len(options) == 0:
                print("开始匹配第二次")
                options = re.findall(r'([A-D]．\s*.*)', content)

            question_item_objects = []
            question_data = {}
            if qtype < 4:
                for option in options:
                    prefix = option[0]
                    choice_content = option[2:]
                    question_item_objects.append({
                        "prefix": prefix,
                        "content": choice_content,
                        "score": None,
                        "itemUuid": None
                    })

                question_data = {
                    "titleContent": question_content,
                    "analyze": "none",
                    "questionItemObjects": question_item_objects,
                    "correct": correct
                }
            elif qtype == 4:
                result = replace_gaps(content, score, correct)
                question_data = result
            elif qtype == 5:
                result = {
                    "titleContent": content,
                    "analyze": "none",
                    "questionItemObjects": [],
                    "correct": correct
                }
                question_data = result

            json_output = json.dumps(question_data, ensure_ascii=False, indent=4)
            print(json_output)

            # 插入数据库
            connection = create_connection()
            current_id = insert_question(connection, json_output)
            insert_t_question(connection, qtype, score, difficult, correct, current_id, knowledge)
        else:
            messagebox.showerror("错误", "题目类型错误")
    messagebox.showinfo("成功", "成功插入数据库")


def insert_t_question(connection, qtype, score, difficult, correct, current_id, knowledge):
    current_datetime = datetime.datetime.now()
    insert_query = """
    INSERT INTO t_question (question_type, subject_id, score, grade_level, difficult, correct, info_text_content_id, create_user, status, create_time, deleted, knowledge_points)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor = connection.cursor()
    print(f"({qtype})")
    cursor.execute(insert_query, (qtype, 1, score * 10, 1, difficult, correct, current_id, 2, 1, current_datetime, False, knowledge))
    connection.commit()
    print("t_question数据表插入成功")
    cursor.close()

def replace_numbers_in_spans(title_content):
    # 用于记录当前数字的递增值
    current_number = 1

    def replace_func(match):
        nonlocal current_number  # 允许修改外部变量
        # 获取原始的 span 标签
        span_tag = match.group(0)
        # 获取标签内的内容，并将其替换为当前数字
        new_span_tag = span_tag.replace(match.group(2), str(current_number))
        # 递增数字
        current_number += 1
        return new_span_tag  # 返回替换后的 span 标签

    # 使用正则表达式找到所有 <span> 标签并替换其中的数字
    updated_content = re.sub(r'(<span[^>]*>)(\d+)(</span>)', replace_func, title_content)

    # 返回更新后的内容
    return updated_content

def replace_gaps(content, score, correct):
    # 定义一个生成唯一UUID的函数
    def generate_uuid():
        return str(uuid.uuid4())

    # 匹配下划线
    def replace_match(match):
        print("来到replace_match了")
        gap_length = len(match.group(0))  # 获取下划线的长度
        unique_id = generate_uuid()  # 生成唯一ID
        # 生成格式化的字符串
        return f'<span class="gapfilling-span {unique_id}">{gap_length}</span>'

    # 使用正则表达式替换下划线
    new_content = re.sub(r'_+', replace_match, content)

    # 生成最终的JSON格式
    # title_content = new_content.replace(" ", "?")  # 假设用?替换空格
    title_content = replace_numbers_in_spans(new_content)
    analyze = "none"

    # 获取替换后的填空数量
    gaps = re.findall(r'<span class="gapfilling-span .*?">.*?</span>', new_content)
    print(f"这里是gaps = {gaps} 和它的count = {gaps.count}")
    question_item_objects = []

    # 计算填空的数量
    count_gaps = 0
    for i, gap in enumerate(gaps):
        count_gaps += 1
    print(f"这里的count_gaps = {count_gaps}")

    answer = [ans.strip() for ans in re.split(r'[，,]', correct)]

    for i, gap in enumerate(gaps):
        print("我进来啦啦啦啦啦啦啦啦")
        prefix = str(i + 1)  # 填空题编号
        item_uuid = gap.split('"')[1]  # 从span中提取UUID
        question_item_objects.append({
            "prefix": i + 1,
            "content": answer[i],
            "score": score * 10 / count_gaps,
            "itemUuid": item_uuid
        })

    result = {
        "titleContent": title_content,
        "analyze": analyze,
        "questionItemObjects": question_item_objects,
        "correct": correct  # 这里可以添加正确答案
    }

    return result
def insert_question(connection, json_output):
    # 获取当前日期和时间
    current_datetime = datetime.datetime.now()
    insert_query = """
        INSERT INTO t_text_content (content, create_time)
        VALUES (%s, %s)
        """

    cursor = connection.cursor()
    try:
        cursor.execute(insert_query, (json_output, current_datetime))
        connection.commit()

        # 获取插入记录的ID
        inserted_id = cursor.lastrowid  # 获取最后插入的ID
        # print(f"{json_output} {current_datetime} 成功插入数据库, ID: {inserted_id}")

        return inserted_id  # 如果需要返回这个ID，可以选择返回
    except Exception as e:
        connection.rollback()  # 发生错误时回滚
        print(f"插入失败: {e}")
    finally:
        cursor.close()  # 关闭游标

def match_face(encoding, encodings):
    # 使用face_recognition库的比较功能
    if encoding is not None and encodings:
        # 计算与已知编码的距离
        distances = face_recognition.face_distance(encodings, encoding)
        threshold = 0.35  # 调整阈值以提高准确性
        matches = distances < threshold  # 返回布尔数组，指示是否匹配
        return True in matches  # 如果有任何匹配，返回True
    return False  # 如果没有编码或已知编码为空，则返回False

def extract_question(content, qtype):
    # 使用正则表达式匹配题目部分，匹配到（）。为止
    match = re.search(r'^(.*?（）。)', content, re.DOTALL)
    if match == None:
        match = re.search(r'^(.*?。)', content, re.DOTALL)
    if match == None:
        match = re.search(r'^(.*?（）)', content, re.DOTALL)

    if match:
        return match.group(1).strip()  # 提取题目部分并去除前后空格
    else:
        return None  # 如果没有匹配到，返回None
# def test_face():
#     global encodings
#     print("开始测试人脸")
#
#     # 打开摄像头
#     cap = cv2.VideoCapture(0)
#
#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             print("无法读取摄像头")
#             break
#
#         # 进行人脸检测
#         face_encoding = encode_face(frame)  # 生成当前捕获人脸的编码
#         # print(f"当前的人脸编码 {face_encoding}")
#
#         if match_face(face_encoding, encodings):  # 检查编码是否存在
#             cv2.putText(frame, "Matched!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
#         else:
#             cv2.putText(frame, "Not Matched", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
#
#         cv2.imshow("Face Recognition", frame)
#
#         if cv2.waitKey(1) & 0xFF == ord('q'):  # 按 'q' 键退出
#             break
#
#     cap.release()
#     cv2.destroyAllWindows()

# 测试按钮
# test = ttk.Button(root, text="test", command=test_face)
# test.pack(pady=20)

# 创建图形化界面




root = tk.Tk()
root.title("Face Upload")
root.geometry("400x300")
root.configure(bg="#f0f0f0")

# 样式
style = ttk.Style()
style.configure("TButton", font=("Arial", 12), padding=10)
style.configure("TLabel", font=("Arial", 14), background="#f0f0f0")

# 标题
label = ttk.Label(root, text="考试系统数据管理系统", font=("Arial", 16), background="#f0f0f0")
label.pack(pady=20)

# 人脸按钮
upload_button = ttk.Button(root, text="上传人脸图片", command=upload_images)
upload_button.pack(pady=20)

# 题库按钮
test_button = ttk.Button(root, text="上传题库文件", command=upload_tests)
test_button.pack(pady=20)

# 运行
root.mainloop()