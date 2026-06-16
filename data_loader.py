import pandas as pd
import os

DATA_DIR = 'data'

def load_data():
    books_df = pd.read_csv(os.path.join(DATA_DIR, 'books.csv'), encoding='utf-8-sig', dtype={'ISBN': str})
    sales_df = pd.read_csv(os.path.join(DATA_DIR, 'sales.csv'), encoding='utf-8-sig', dtype={'ISBN': str})
    readers_df = pd.read_csv(os.path.join(DATA_DIR, 'readers.csv'), encoding='utf-8-sig', dtype={'ISBN': str})
    ratings_df = pd.read_csv(os.path.join(DATA_DIR, 'ratings.csv'), encoding='utf-8-sig', dtype={'ISBN': str})
    return books_df, sales_df, readers_df, ratings_df

def filter_sales_by_date(sales_df, books_df, start_year, start_month, end_year, end_month):
    sales_with_books = sales_df.merge(books_df[['ISBN', '品类', '书名', '定价']], on='ISBN', how='left')
    
    def is_in_range(row):
        if row['年份'] < start_year or row['年份'] > end_year:
            return False
        if row['年份'] == start_year and row['月份'] < start_month:
            return False
        if row['年份'] == end_year and row['月份'] > end_month:
            return False
        return True
    
    filtered = sales_with_books[sales_with_books.apply(is_in_range, axis=1)].copy()
    filtered['年月'] = filtered.apply(lambda x: f"{x['年份']}-{x['月份']:02d}", axis=1)
    return filtered

def get_monthly_sales_trend(filtered_sales, category=None):
    if category and category != '全部':
        filtered_sales = filtered_sales[filtered_sales['品类'] == category]
    
    monthly = filtered_sales.groupby(['年月', '品类']).agg({
        '销量': 'sum',
        '营收': 'sum'
    }).reset_index()
    
    return monthly.sort_values('年月')

def get_category_sales_summary(filtered_sales):
    summary = filtered_sales.groupby('品类').agg({
        '销量': 'sum',
        '营收': 'sum'
    }).reset_index()
    summary['平均单价'] = (summary['营收'] / summary['销量']).round(2)
    return summary.sort_values('销量', ascending=False)

def get_channel_sales(filtered_sales):
    channel_summary = filtered_sales.groupby(['渠道', '品类']).agg({
        '销量': 'sum',
        '营收': 'sum'
    }).reset_index()
    return channel_summary

def get_reader_profile_by_category(readers_df, categories):
    age_groups = ['18-25', '26-35', '36-45', '46-55', '55+']
    price_ranges = ['20-50', '50-100', '100+']
    
    profiles = {}
    
    for category in categories:
        cat_readers = readers_df[readers_df['品类'] == category]
        total = len(cat_readers)
        
        if total == 0:
            continue
        
        age_dist = {}
        for age in age_groups:
            age_dist[age] = len(cat_readers[cat_readers['年龄区间'] == age]) / total
        
        gender_dist = {
            '男': len(cat_readers[cat_readers['性别'] == '男']) / total,
            '女': len(cat_readers[cat_readers['性别'] == '女']) / total
        }
        
        price_dist = {}
        for pr in price_ranges:
            price_dist[pr] = len(cat_readers[cat_readers['单次购买力区间'] == pr]) / total
        
        repurchase_rate = cat_readers['复购'].mean()
        
        profiles[category] = {
            'age_dist': age_dist,
            'gender_dist': gender_dist,
            'price_dist': price_dist,
            'repurchase_rate': repurchase_rate,
            'total_readers': total
        }
    
    return profiles

def get_radar_data(profiles, categories):
    radar_data = []
    
    for category in categories:
        if category not in profiles:
            continue
        
        profile = profiles[category]
        
        data = {
            '品类': category,
            '18-25岁': profile['age_dist'].get('18-25', 0) * 100,
            '26-35岁': profile['age_dist'].get('26-35', 0) * 100,
            '36-45岁': profile['age_dist'].get('36-45', 0) * 100,
            '46-55岁': profile['age_dist'].get('46-55', 0) * 100,
            '55岁以上': profile['age_dist'].get('55+', 0) * 100,
            '男性比例': profile['gender_dist'].get('男', 0) * 100,
            '女性比例': profile['gender_dist'].get('女', 0) * 100,
            '20-50元': profile['price_dist'].get('20-50', 0) * 100,
            '50-100元': profile['price_dist'].get('50-100', 0) * 100,
            '100元以上': profile['price_dist'].get('100+', 0) * 100,
            '复购率': profile['repurchase_rate'] * 100
        }
        radar_data.append(data)
    
    return pd.DataFrame(radar_data)

def get_book_by_isbn(sales_df, books_df, ratings_df, isbn):
    book_info = books_df[books_df['ISBN'] == isbn].iloc[0] if len(books_df[books_df['ISBN'] == isbn]) > 0 else None
    
    if book_info is None:
        return None
    
    book_sales = sales_df[sales_df['ISBN'] == isbn].copy()
    book_sales['年月'] = book_sales.apply(lambda x: f"{x['年份']}-{x['月份']:02d}", axis=1)
    
    monthly_sales = book_sales.groupby('年月').agg({
        '销量': 'sum',
        '营收': 'sum'
    }).reset_index().sort_values('年月')
    
    channel_dist = book_sales.groupby('渠道').agg({
        '销量': 'sum',
        '营收': 'sum'
    }).reset_index()
    
    book_ratings = ratings_df[ratings_df['ISBN'] == isbn]
    
    rating_dist = {
        '五星': len(book_ratings[book_ratings['评分'] == 5]),
        '四星': len(book_ratings[book_ratings['评分'] == 4]),
        '三星及以下': len(book_ratings[book_ratings['评分'] <= 3])
    }
    
    avg_rating = book_ratings['评分'].mean() if len(book_ratings) > 0 else 0
    
    return {
        'info': book_info,
        'monthly_sales': monthly_sales,
        'channel_dist': channel_dist,
        'rating_dist': rating_dist,
        'avg_rating': avg_rating,
        'total_ratings': len(book_ratings),
        'total_sales': book_sales['销量'].sum(),
        'total_revenue': book_sales['营收'].sum()
    }

def get_book_rankings(sales_df, books_df):
    book_total_sales = sales_df.groupby('ISBN').agg({
        '销量': 'sum',
        '营收': 'sum'
    }).reset_index()
    
    book_total_sales = book_total_sales.merge(books_df[['ISBN', '书名', '品类']], on='ISBN', how='left')
    
    top_10_percent = int(len(book_total_sales) * 0.1)
    bottom_10_percent = int(len(book_total_sales) * 0.1)
    
    best_sellers = book_total_sales.nlargest(top_10_percent, '销量').copy()
    worst_sellers = book_total_sales.nsmallest(bottom_10_percent, '销量').copy()
    
    best_sellers['标签'] = '畅销书'
    worst_sellers['标签'] = '滞销书'
    
    return best_sellers, worst_sellers

def get_available_years(sales_df):
    return sorted(sales_df['年份'].unique())

def get_available_months():
    return list(range(1, 13))
