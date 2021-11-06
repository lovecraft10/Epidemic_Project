import asyncio
import aiohttp
import json
import time
import pymysql
import traceback


async def crawl_1(session, url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36'
    }
    async with session.get(url=url, headers=headers) as response:
        res = await response.text()
        res = json.loads(res)
        all_data = json.loads(res["data"])

        global history
        history = {}
        # 历史记录
        for i in all_data["chinaDayList"]:
            ds = i['y']+ '.'+ i["date"]
            tup = time.strptime(ds, "%Y.%m.%d")  # 匹配时间
            ds = time.strftime("%Y-%m-%d", tup)  # 改变时间输入格式，不然插入数据库会报错，数据库是datatime格式
            confirm = i["confirm"] # 确诊人数
            suspect = i["suspect"] # 怀疑确诊人数
            heal = i["heal"]  # 治愈人数
            dead = i["dead"] # 死亡人数
            history[ds] = {"confirm": confirm, "suspect": suspect, "heal": heal, "dead": dead}
        # 历史新增
        for i in all_data["chinaDayAddList"]:
            ds = i['y']+ '.'+ i["date"]
            tup = time.strptime(ds, "%Y.%m.%d")  # 匹配时间
            ds = time.strftime("%Y-%m-%d", tup)  # 改变时间输入格式，不然插入数据库会报错，数据库是datatime格式
            confirm = i["confirm"]
            suspect = i["suspect"]
            heal = i["heal"]
            dead = i["dead"]
            history[ds].update({"confirm_add": confirm, "suspect_add": suspect, "heal_add": heal, "dead_add": dead})
    return history

async def crawl_2(session, url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36'
    }
    async with session.get(url=url, headers=headers) as response:
        res = await response.text()
        res = json.loads(res)
        all_data = json.loads(res["data"])

        details = []
        update_time = all_data["lastUpdateTime"] # 最后更新时间
        data_country = all_data["areaTree"]
        data_province = data_country[0]["children"]  # 中国各省
        for pro_infos in data_province:
            province = pro_infos["name"]  # 省名
            for city_infos in pro_infos["children"]:
                city = city_infos["name"] # 各省的市级名
                confirm = city_infos["total"]["confirm"] # 各省的市级确诊人数
                confirm_add = city_infos["today"]["confirm"] # 某天的各省的市级的确诊人数
                heal = city_infos["total"]["heal"] # 累计治愈
                dead = city_infos["total"]["dead"] # 累计死亡
                details.append([update_time, province, city, confirm, confirm_add, heal, dead])
    return details

async def crawl_3(session, url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36'
    }
    async with session.get(url=url, headers=headers) as response:
        res = await response.text()
        res = json.loads(res)
        data_dic= {}
        data_list = res["Result"][0]['items_v2'][0]['aladdin_res']['DisplayData']['result']['items']
        for data in data_list:
            title = data['eventDescription']
            eventTime = int(data['eventTime'])  # 时间戳 转 时间
            timeArray = time.localtime(eventTime)
            otherStyleTime = time.strftime("%Y-%m-%d %H:%M", timeArray)
            eventUrl = data['eventUrl']
            data_dic[otherStyleTime] = {title:eventUrl}
    return data_dic


def con():
    conn = pymysql.connect(host='192.168.204.128',
                            port=3306,
                            user='Coisini',
                            password='Wxylkxy0415.@',
                            db='Cov',
                            charset='utf8'
                           )
    return conn

def close_conn(conn):
    conn.close()

def update_details(data, conn):
    try:
        li = data
        cursor = conn.cursor()
        sql = "insert into details(update_time,province,city,confirm,confirm_add,heal,dead) values(%s,%s,%s,%s,%s,%s,%s)"
        sql_query = "select %s=(select update_time from details order by id desc limit 1)"  # 对比当前最大时间戳
        # 对比当前最大时间戳
        cursor.execute(sql_query, li[0][0])
        if not cursor.fetchone()[0]:
            print(f"{time.asctime()}开始更新数据")
            for item in li:
                cursor.execute(sql, item)
            conn.commit()
            print(f"{time.asctime()}更新到最新数据")
        else:
            print(f"{time.asctime()}已是最新数据！")
    except:
        # traceback.print_exc()来代替print e 来输出详细的异常信息
        traceback.print_exc()
    finally:
        close_conn(conn)

def insert_history(data, conn):
    try:
        dic = data #0代表历史数据字典
        cursor = conn.cursor()
        print(f"{time.asctime()}开始插入历史数据")
        sql = "insert into history values (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        for k,v in dic.items():
            cursor.execute(sql,[k, v.get("confirm"),v.get("confirm_add"),v.get("suspect"),
                           v.get("suspect_add"),v.get("heal"),v.get("heal_add"),
                           v.get("dead"),v.get("dead_add")])
        conn.commit()
        print(f"{time.asctime()}插入历史数据完毕")
    except:
        traceback.print_exc()
    finally:
        close_conn(conn)

def update_information(data_dic, conn):
    for key, values in data_dic.items():
        for k, v in values.items():
            cursor = conn.cursor()
            sql = "insert into guonei_dynamic(dt, content, detail) values(%s,%s,%s)"
            cursor.execute(sql, (key, k, v))

    conn.commit()
    close_conn(conn)

def empty():
    conn = con()
    cursor = conn.cursor()
    sql1 = 'TRUNCATE guonei_dynamic;'
    cursor.execute(sql1)
    sql2 = 'TRUNCATE history;'
    cursor.execute(sql2)
    conn.commit()
    close_conn(conn)




async def main():
    empty()
    async with aiohttp.ClientSession() as session:
        url_1 = 'https://view.inews.qq.com/g2/getOnsInfo?name=disease_other'
        url_2 = 'https://view.inews.qq.com/g2/getOnsInfo?name=disease_h5'
        url_3 = 'https://opendata.baidu.com/data/inner?tn=reserved_all_res_tn&dspName=iphone&from_sf=1&dsp=iphone' \
                '&resource_id=28565&alr=1&query=%E5%9B%BD%E5%86%85%E6%96%B0%E5%9E%8B%E8%82%BA%E7%82%8E%E6%9C%80%E6%96' \
                '%B0%E5%8A%A8%E6%80%81'
        crawl_tasks = [asyncio.create_task(crawl_1(session, url_1), name='历史记录'),
                       asyncio.create_task(crawl_2(session, url_2), name='当日数据'),
                       asyncio.create_task(crawl_3(session, url_3), name='国内资讯')]
        done, pending = await asyncio.wait(crawl_tasks)
    # 因为谁先完成谁先返回 所以设计对应
    list1 = [task.get_name() for task in done]
    list2 = [task.result() for task in done]
    dic = dict(zip(list1, list2))

    conn = con()
    update_details(dic['当日数据'], conn)

    conn = con()
    insert_history(dic['历史记录'], conn)

    conn = con()
    update_information(dic['国内资讯'], conn)

    print('全部完成')


if __name__  == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
