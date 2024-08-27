import random
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot ,GroupMessageEvent
from nonebot_plugin_saa import Image, Text
from nonebot.matcher import Matcher
import time
import numpy as np


_matcher = on_command("群友bingo", aliases={"群友bingo4","群友bingo9","群友bingo16","群友bingo25","群友bingo36","群友bingo49","群友bingo64","群友bingo81"},block=True, priority=5,)
@_matcher.handle()
async def _(bot:Bot, matcher:Matcher, event:GroupMessageEvent):
    group_id = event.group_id

    num = 25
    if(event.get_plaintext() != "群友bingo"):
        num = int(event.get_plaintext().replace("群友bingo",""))

    # 获取最近一个月内发言的群友
    member_list = await bot.get_group_member_list(group_id=group_id)
    bingo_ids = [ user_id  for member in member_list  if (user_id := member["user_id"])  and member["last_sent_time"] > time.time() - 30 * 24 * 60 * 60 ]
    
    # 移除发送者
    bingo_ids.remove(event.user_id)

    # 群友数量不足需求数量，返回提示
    if(len(bingo_ids) < num):
        await Text(f"群友数量不足{num}人，请重新选择").finish(reply=True)

    # 随机抽取 9/16/25/36/49/64/81 个群友
    chosen_ids = random.sample(bingo_ids, k=num)

    # 开方
    line = int(num ** 0.5)

    # 转为二维
    bingo_array = np.array(chosen_ids).reshape(line, line).tolist()

    html_str = get_base_html(create_bingo_table(bingo_array),line)

    from nonebot_plugin_htmlrender import html_to_pic
    pic = await html_to_pic(html_str, type='jpeg', quality=70, viewport={"width": 100, "height": 100})

    await Image(pic).finish(reply=True)


def create_bingo_table(bingo_array):
    # 创建表格
    table = "<table>"
    for row in bingo_array:
        table += "<tr>"
        for qq in row:
            table += f"<td><img src='http://q1.qlogo.cn/g?b=qq&nk={qq}&s=640' /></td>"
        table += "</tr>"
    table += "</table>"
    return table


def get_base_html(table,line):
    return f'''
        <!DOCTYPE html>
        <html lang="cn">
            <head>
                <meta charset="UTF-8" />
                <meta name="viewport" content="width=device-width, initial-scale=1.0" />
                <title>Document</title>
            </head>
            <body>
                <div class="title">
                    <div style="font-size: 100px" id="title">你群活跃宾果游戏</div>
                    <div style="font-size: 20px" id="title2">你群活跃宾果游戏</div>
                </div>
                {table}
            </body>
            <script>
                const lineNum = {line};
                const spacing = 3;

                const _imgWidth = 15 * (15 - lineNum) + 60;
                const imgWidth = "width:" + _imgWidth + "px";
                document.querySelectorAll("img").forEach((img) => (img.style = imgWidth));

                document.querySelector("table").style =
                    "border-spacing:" + spacing + "px";

                const BodyWith = _imgWidth * lineNum + spacing * 2 * (lineNum - 1);
                document.body.style = "width:" + BodyWith + "px";

                document.querySelector("#title").style =
                    "font-size:" + Math.floor(BodyWith / 9) + "px; text-align: center;";
                document.querySelector("#title2").style =
                    "font-size:" + Math.floor(BodyWith / 18) + "px; text-align: center;";
            </script>
        </html>
  '''