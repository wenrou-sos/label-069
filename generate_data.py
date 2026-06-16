import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import os

random.seed(42)
np.random.seed(42)

os.makedirs('data', exist_ok=True)

categories = ['文学', '社科', '科技', '少儿', '教辅']
channels = ['线上电商', '线下书店', '馆配']
age_groups = ['18-25', '26-35', '36-45', '46-55', '55+']
genders = ['男', '女']
price_ranges = ['20-50', '50-100', '100+']

book_titles = {
    '文学': ['百年孤独', '红楼梦', '活着', '平凡的世界', '围城', '三体', '夜晚的潜水艇', '秋园', '文城', '长安的荔枝'],
    '社科': ['人类简史', '未来简史', '原则', '思考，快与慢', '乌合之众', '影响力', '枪炮、病菌与钢铁', '自私的基因', '万历十五年', '乡土中国'],
    '科技': ['深度学习', '算法导论', '代码大全', '设计模式', '重构', '程序员修炼之道', '计算机程序的构造和解释', '编程珠玑', '人月神话', '浪潮之巅'],
    '少儿': ['小王子', '哈利波特', '夏洛的网', '窗边的小豆豆', '草房子', '狼王梦', '青铜葵花', '了不起的狐狸爸爸', '皮皮鲁传', '葫芦兄弟'],
    '教辅': ['高等数学', '线性代数', '大学英语', 'C++程序设计', '数据结构', '计算机网络', '操作系统', '数据库原理', '软件工程', '考研英语']
}

def generate_isbn():
    return '978' + ''.join([str(random.randint(0, 9)) for _ in range(10)])

books = []
isbn_list = []
for category, titles in book_titles.items():
    base_price = {'文学': 55, '社科': 65, '科技': 85, '少儿': 45, '教辅': 58}[category]
    for i, title in enumerate(titles):
        isbn = generate_isbn()
        isbn_list.append(isbn)
        price = round(base_price + random.uniform(-15, 25), 2)
        books.append({
            'ISBN': isbn,
            '书名': title,
            '作者': f'{random.choice(["张", "李", "王", "刘", "陈", "杨", "黄", "赵"])}{random.choice(["明", "华", "强", "丽", "军", "芳", "伟", "静"])}',
            '品类': category,
            '定价': price,
            '出版日期': (datetime(2020, 1, 1) + timedelta(days=random.randint(0, 1000))).strftime('%Y-%m-%d')
        })

books_df = pd.DataFrame(books)
books_df.to_csv('data/books.csv', index=False, encoding='utf-8-sig')
print(f"生成了 {len(books_df)} 本图书信息")

start_date = datetime(2025, 1, 1)
sales_data = []
reader_data = []
rating_data = []

for month in range(12):
    current_date = start_date + timedelta(days=month * 30)
    year = current_date.year
    month_num = current_date.month
    
    for channel in channels:
        channel_factor = {'线上电商': 1.2, '线下书店': 0.8, '馆配': 0.6}[channel]
        
        for _, book in books_df.iterrows():
            category_factor = {
                '文学': 1.0, '社科': 0.85, '科技': 0.7, '少儿': 1.1, '教辅': 1.3
            }[book['品类']]
            
            month_factor = 1.0
            if month_num in [1, 2, 9]:
                month_factor = 1.5
            
            base_sales = random.randint(20, 150)
            quantity = int(base_sales * channel_factor * category_factor * month_factor * random.uniform(0.7, 1.3))
            
            discount = {'线上电商': 0.85, '线下书店': 0.95, '馆配': 0.75}[channel]
            revenue = round(quantity * book['定价'] * discount, 2)
            
            sales_data.append({
                '日期': current_date.strftime('%Y-%m-%d'),
                '年份': year,
                '月份': month_num,
                '渠道': channel,
                'ISBN': book['ISBN'],
                '销量': quantity,
                '营收': revenue
            })
            
            for _ in range(min(quantity, random.randint(1, 5))):
                reader_id = f'R{random.randint(10000, 99999)}'
                
                age_probs = {
                    '文学': [0.2, 0.35, 0.25, 0.12, 0.08],
                    '社科': [0.15, 0.3, 0.35, 0.13, 0.07],
                    '科技': [0.3, 0.4, 0.2, 0.07, 0.03],
                    '少儿': [0.05, 0.5, 0.35, 0.08, 0.02],
                    '教辅': [0.4, 0.35, 0.15, 0.07, 0.03]
                }[book['品类']]
                age_group = np.random.choice(age_groups, p=age_probs)
                
                gender_probs = {
                    '文学': [0.35, 0.65],
                    '社科': [0.55, 0.45],
                    '科技': [0.75, 0.25],
                    '少儿': [0.45, 0.55],
                    '教辅': [0.5, 0.5]
                }[book['品类']]
                gender = np.random.choice(genders, p=gender_probs)
                
                purchase_amount = book['定价'] * discount
                if purchase_amount < 50:
                    price_range = '20-50'
                elif purchase_amount < 100:
                    price_range = '50-100'
                else:
                    price_range = '100+'
                
                repurchase_prob = {
                    '文学': 0.25, '社科': 0.2, '科技': 0.35, '少儿': 0.3, '教辅': 0.4
                }[book['品类']]
                repurchase = 1 if random.random() < repurchase_prob else 0
                
                reader_data.append({
                    '读者ID': reader_id,
                    'ISBN': book['ISBN'],
                    '品类': book['品类'],
                    '年龄区间': age_group,
                    '性别': gender,
                    '单次购买力区间': price_range,
                    '复购': repurchase,
                    '购买日期': current_date.strftime('%Y-%m-%d')
                })
                
                if random.random() < 0.3:
                    rating_probs = [0.1, 0.25, 0.4, 0.2, 0.05]
                    rating = np.random.choice([1, 2, 3, 4, 5], p=rating_probs)
                    rating_data.append({
                        '读者ID': reader_id,
                        'ISBN': book['ISBN'],
                        '评分': rating,
                        '评分日期': current_date.strftime('%Y-%m-%d')
                    })

sales_df = pd.DataFrame(sales_data)
sales_df.to_csv('data/sales.csv', index=False, encoding='utf-8-sig')
print(f"生成了 {len(sales_df)} 条销售记录")

readers_df = pd.DataFrame(reader_data)
readers_df.to_csv('data/readers.csv', index=False, encoding='utf-8-sig')
print(f"生成了 {len(readers_df)} 条读者画像记录")

ratings_df = pd.DataFrame(rating_data)
ratings_df.to_csv('data/ratings.csv', index=False, encoding='utf-8-sig')
print(f"生成了 {len(ratings_df)} 条评分记录")

print("\n数据生成完成！文件保存在 data/ 目录下")
