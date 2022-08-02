import vk
import vk_api
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id
from vk_api.longpoll import VkLongPoll, VkEventType
from datetime import datetime

groups = [
    -62441045,
    -203102543,
    -184648211,
    -68829811,
    -204517084,
    -212824275,
    -157615038,
    -151598880,
    -146665911,
    -130150864,
    -134416509,
    -158969191,
    -146655979,
    -202176632,
    -199963188,
    -210879159,
    -203748128,
    -128118706,
    -147002621,
    -200896907,
    -207857905,
    -203303458,
    -204514980,
    -7241540,
    -208243426,
    -144614991,
    -200357122,
    -91335741,
    -156878704]

def vk_auth():
    global login
    global password
    global token
    global group_vk_session
    global api

    with open("config.cfg") as config:
        data = config.readlines()[0].split(",")
        login = data[0]
        password = data[1]
        token = data[2].replace("\n", "")


    group_vk_session = vk_api.VkApi(token="vk1.a.CrhvHZXvMl3FisRv_W2XflSSPdfF8QgEzbJyAPSV2Fo8vUTys8_5u1GmU86LgbjE97OQutXsNLtR6gIV0uVGVtE0PmFxXqq95oxyqvMIJM-A-BazaVTHg3nh5Gznkm1fo6gjM8qF8CB7uk0N3V-e8OPNu1EHgRkNSSEvtqu2p9WIouJuO488r5c7VDiXuRrS")

    api = vk.UserAPI(user_password=password, user_login=login, v="5.131", client_id=8233295)

vk_auth()

def get_all_posts():
    global group_posts
    global posts
    posts = []

    for group in groups:
        try:
            group_posts = api.wall.get(owner_id=group, count=100)
        except:
            continue
        for post in group_posts["items"]:
            try:
                post_text = post["text"]
                post_signer = post["signer_id"]
                post_date = post["date"]
                attachments = []
                post_id_d = post["id"]
                for attachment in post["attachments"]:
                    owner_id = attachment["photo"]["owner_id"]
                    post_id = attachment["photo"]["id"]
                    attachments.append(f"photo{owner_id}_{post_id}")
                posts_dict = {"group": f"vk.com/club{group*-1}", "date": post_date, "text": post_text, "signer": f"vk.com/id{post_signer}", "attachments": attachments, "link": f"vk.com/id{group*-1}?w=wall{group}_{post_id_d}"}
                posts.append(posts_dict)
            except:
                continue
    return posts

def get_hour_posts():
    global hour_posts
    hour_posts = []
    
    for post in get_all_posts():
        post_time = datetime.fromtimestamp(post["date"])
        today_time = datetime.now()
        days_from = today_time - post_time

        if days_from.days == 0 and today_time.hour-post_time.hour <= 1:
            hour_posts.append(post)
        else:
            continue

    return hour_posts

def get_daily_posts():
    global daily_posts
    daily_posts = []
    
    for post in get_all_posts():
        post_time = datetime.fromtimestamp(post["date"])
        today_time = datetime.now()
        days_from = today_time - post_time

        if days_from.days < 1:
            daily_posts.append(post)
    
    return daily_posts

def get_past_day_posts():
    global past_day_posts
    past_day_posts = []
    
    for post in get_all_posts():
        post_time = datetime.fromtimestamp(post["date"])
        today_time = datetime.now()
        days_from = today_time - post_time

        if days_from.days == 1:
            past_day_posts.append(post)

    return past_day_posts

group_api = group_vk_session.get_api()
group_lp = VkLongPoll(group_vk_session)

keyboard = VkKeyboard()
keyboard.add_button('1 Час', color=VkKeyboardColor.NEGATIVE)
keyboard.add_button('Сегодня', color=VkKeyboardColor.NEGATIVE)
keyboard.add_button('Вчера', color=VkKeyboardColor.NEGATIVE)

print("Бот запущен!")
print("Иди хуярь")

for event in group_lp.listen():
   
    if event.type == VkEventType.MESSAGE_NEW and event.text and event.to_me:
        
        if event.text.lower() == '1 час' or event.text.lower() == "1":
            
            group_api.messages.send(keyboard=keyboard.get_keyboard(), user_id=event.user_id, random_id=get_random_id(), message="Подготавливаю посты...")
            
            for post in get_hour_posts():
                post_date = datetime.fromtimestamp(post["date"])
                post_text = post["text"]
                post_signer = post["signer"]
                attachments = post["attachments"]
                post_link = post["link"]
                group_api.messages.send(keyboard=keyboard.get_keyboard(), user_id=event.user_id, random_id=get_random_id(), message=f"{post_date}\nТекст поста: {post_text}\nСоздатель поста: {post_signer}\nСсылка на пост: {post_link}", attachment=attachments)
            
            group_api.messages.send(keyboard=keyboard.get_keyboard(), user_id=event.user_id, random_id=get_random_id(), message="Готово!")

        elif event.text.lower() == 'сегодня' or event.text.lower() == "2":
            
            group_api.messages.send(keyboard=keyboard.get_keyboard(), user_id=event.user_id, random_id=get_random_id(), message="Подготавливаю посты...")

            for post in get_daily_posts():
                post_date = datetime.fromtimestamp(post["date"])
                post_text = post["text"]
                post_signer = post["signer"]
                attachments = post["attachments"]
                post_link = post["link"]
                group_api.messages.send(keyboard=keyboard.get_keyboard(), user_id=event.user_id, random_id=get_random_id(), message=f"{post_date}\nТекст поста: {post_text}\nСоздатель поста: {post_signer}\nСсылка на пост: {post_link}", attachment=attachments)
                group_api.messages.send(keyboard=keyboard.get_keyboard(), user_id=event.user_id, random_id=get_random_id(), message="Готово!")

        elif event.text.lower() == 'вчера' or event.text.lower() == "3":
            
            group_api.messages.send(keyboard=keyboard.get_keyboard(), user_id=event.user_id, random_id=get_random_id(), message="Подготавливаю посты...")

            for post in get_past_day_posts():
                post_date = datetime.fromtimestamp(post["date"])
                post_text = post["text"]
                post_signer = post["signer"]
                attachments = post["attachments"]
                post_link = post["link"]
                group_api.messages.send(keyboard=keyboard.get_keyboard(), user_id=event.user_id, random_id=get_random_id(), message=f"{post_date}\nТекст поста: {post_text}\nСоздатель поста: {post_signer}\nСсылка на пост: {post_link}", attachment=attachments)

            group_api.messages.send(keyboard=keyboard.get_keyboard(), user_id=event.user_id, random_id=get_random_id(), message="Готово!")

        else:
            group_api.messages.send(keyboard=keyboard.get_keyboard(), user_id=event.user_id, random_id=get_random_id(), message="Хуйню сморозил")
