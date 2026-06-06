# 餐厅评价资料分析平台

## 一、专题名称

餐厅评价资料分析平台  
Restaurant Review Data Analysis Platform

## 二、专题简介

本系统是一个餐厅评价资料服务平台，主要用于收集、查询与分析餐厅资料。

系统会将餐厅名称、地区、类型、评分、价格区间、地址等资料储存到 SQLite 资料库中，并提供网页查询功能与 JSON API 服务。

## 三、系统功能

### 1. 餐厅资料查询
使用者可以查看全部餐厅资料。

### 2. 餐厅类型筛选
可以依照餐厅类型查询，例如火锅、日式料理、烧肉等。

### 3. 评分筛选
可以查询评分 4.3 分以上的餐厅。

### 4. 资料分析
系统可以分析：
- 餐厅总数量
- 平均评分
- 最高评分餐厅
- 各类型餐厅数量

### 5. JSON API 服务
系统提供 API，让外部系统可以取得餐厅资料。

## 四、使用技术

- Python
- Flask
- SQLite
- HTML
- CSS
- Git / GitHub
- uv

## 五、专案结构

```text
final_demo/
├── app/
├── api/
├── database/
│   └── restaurant.db
├── static/
│   └── style.css
├── utils/
├── main.py
├── README.md
└── environment_setup.md