import asyncio
import aiohttp
import json
import time
import pymysql

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
        data_country = all_data["areaTree"]  # list 25个国家
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

async def conn():
    conn = pymysql.connect(host='xxxx',
                            port=3306,
                            user='xxxx',
                            password='xxxx',
                            db='text',
                            charset='utf8')
    return conn



async def main():
    async with aiohttp.ClientSession() as session:
        url_1 = 'https://view.inews.qq.com/g2/getOnsInfo?name=disease_other'
        url_2 = 'https://view.inews.qq.com/g2/getOnsInfo?name=disease_h5'
        crawl_tasks = [asyncio.create_task(crawl_1(session, url_1)),
                       asyncio.create_task(crawl_2(session, url_2))]
        done, pending = await asyncio.wait(crawl_tasks)

    for task in done:
        print(task.result())


if __name__  == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())