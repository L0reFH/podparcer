import vk
import vk_api
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id
from vk_api.longpoll import VkLongPoll, VkEventType
from datetime import datetime

groups = [-91335741,-136625171,-209909314,-48872504,-107458847,-217813769,-199963188,-128118706, -158969191,-132834760,-207586899,-209320732,-68829811,-207857905,-210879159,-122786169,-216635445,-149249014,-214263012,-135449780,-189488412,-213792727,-183882105,-146665911,-213207337,-217761326,-193671013,-156832663,-206231498,-207367796,-200357122,-212824275,-184648211,-200896907,-202176632,-203748128,-204514980,-203102543,-74825865,-146655979,-154600335,-215734224,-216345125,-62441045,-156878704,-204517072,-157615038,-143096800,-208243426,-189059681,-144614991,-192879202,-204517084,-134416509,-217054599,-147906757]

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


    group_vk_session = vk_api.VkApi(token=token)

    api = vk.UserAPI(user_password=password, user_login=login, v="5.131", client_id=8233295)

vk_auth()

def get_all_posts():
    global group_posts
    global posts
    posts = []

    for group in groups:
        try:
            group_posts = api.wall.get(owner_id=group, count=70)
        except:
            continue
        for post in group_posts["items"]: 
            if "signer_id" in post and "attachments" in post:
                post_text = post["text"]
                post_signer = post["signer_id"]
                post_date = post["date"]
                attachments = []
                post_id_d = post["id"]
                for attachment in post["attachments"]:
                    if attachment["type"] == "photo":
                        owner_id = attachment["photo"]["owner_id"]
                        post_id = attachment["photo"]["id"]
                        attachments.append(f"photo{owner_id}_{post_id}")
                    elif attachment["type"] == "video":
                        owner_id = attachment["video"]["owner_id"]
                        post_id = attachment["video"]["id"]
                        attachments.append(f"video{owner_id}_{post_id}")
                posts_dict = {"group": f"vk.com/club{group*-1}", "date": post_date, "text": post_text, "signer": f"vk.com/id{post_signer}", "attachments": attachments, "link": f"vk.com/club{group*-1}?w=wall{group}_{post_id_d}"}
                posts.append(posts_dict)

            elif "copy_history" in post or "is_pinned" in post:
                continue

            else:
                post_text = post["text"]
                post_signer = post["from_id"]
                post_date = post["date"]
                attachments = []
                post_id_d = post["id"]
                
                if "attachments" in post: 
                    for attachment in post["attachments"]:
                        if attachment["type"] == "photo":
                            owner_id = attachment["photo"]["owner_id"]
                            post_id = attachment["photo"]["id"]
                            attachments.append(f"photo{owner_id}_{post_id}")                            
                        elif attachment["type"] == "video":
                            owner_id = attachment["video"]["owner_id"]
                            post_id = attachment["video"]["id"]
                            attachments.append(f"video{owner_id}_{post_id}")

                                              
                    posts_dict = {"group": f"vk.com/club{group*-1}", "date": post_date, "text": post_text, "signer": f"vk.com/id{post_signer}", "attachments": attachments, "link": f"vk.com/club{group*-1}?w=wall{group}_{post_id_d}"}
                    posts.append(posts_dict)
                    
    return posts

def get_hour_posts():
    global hour_posts
    hour_posts = []
    
    signers = []
    
    for post in get_all_posts():
        post_time = datetime.fromtimestamp(post["date"])
        today_time = datetime.now()
        days_from = today_time - post_time
        post_signer = post["signer"]
        
        if post_signer in signers:
            continue
        else:
            if days_from.days == 0 and today_time.hour-post_time.hour >= 0 and today_time.hour-post_time.hour <= 2:
                hour_posts.append(post)
                signers.append(post_signer)
            else:
                continue

    return hour_posts

def get_daily_posts():
    global daily_posts
    daily_posts = []
    signers = []
    
    for post in get_all_posts():
        post_time = datetime.fromtimestamp(post["date"])
        today_time = datetime.now()
        post_signer = post["signer"]
        
        if post_signer in signers: 
            continue
            
        else:
            if today_time.day - post_time.day == 0 and today_time.month-post_time.month == 0:
                daily_posts.append(post)
                signers.append(post_signer)
            else: 
                continue
                
    return daily_posts

def get_past_day_posts():
    global past_day_posts
    past_day_posts = []
    signers = []
  
    for post in get_all_posts():
        post_time = datetime.fromtimestamp(post["date"])
        today_time = datetime.now()
        post_signer = post["signer"]
        
        if post_signer in signers:
            continue
        else:
            if today_time.day - post_time.day == 1 and today_time.month - post_time.month == 0:
                past_day_posts.append(post)                             
                signers.append(post_signer)
        
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
