import json
import time
from telebot import TeleBot
import vk
import random
import requests


groups = [
    -91335741,
    -136625171,
    -209909314,
    -48872504,
    -107458847,
    -217813769,
    -199963188,
    -128118706,
    -158969191,
    -132834760,
    -207586899,
    -209320732,
    -68829811,
    -207857905,
    -210879159,
    -122786169,
    -216635445,
    -149249014,
    -214263012,
    -135449780,
    -189488412,
    -213792727,
    -183882105,
    -146665911,
    -213207337,
    -217761326,
    -193671013,
    -156832663,
    -206231498,
    -207367796,
    -200357122,
    -212824275,
    -184648211,
    -200896907,
    -202176632,
    -203748128,
    -204514980,
    -203102543,
    -74825865,
    -146655979,
    -154600335,
    -215734224,
    -216345125,
    -62441045,
    -156878704,
    -204517072,
    -157615038,
    -143096800,
    -208243426,
    -189059681,
    -144614991,
    -192879202,
    -204517084,
    -134416509,
    -217054599,
    -147906757]

class AuthException(Exception):
    pass

def vk_auth():
    i = 0
    global password
    global phone
    global vk_session
    global user_id
    global token


    with open("config.cfg", "r") as config:
        data = config.readlines()[0].split(",")
        phone = data[0]
        password = data[1]
        user_id = data[2]
        token = data[3].replace("\n", "")

    vk_session = vk.UserAPI(user_login=phone, user_password=password, scope="wall, photos, friends, groups", v="5.131", client_id=8203325)

    print("Бот успешно запущен!")
    print("Иди клепай свои объявления, шизик")


vk_auth()

tb = TeleBot(token)
@tb.message_handler(commands=["пост"])
def request_post_text(message):

    if message.text.lower == "отмена":
        tb.send_message(user_id, "Отменяю")
        return

    send = tb.send_message(user_id, "Пришли текст поста(Описание и цена)")
    tb.register_next_step_handler(send, request_post_photo)

def request_post_photo(message):
    if message.text:
        global post_text
        post_text = message.text
        if message.text.lower() == "отмена":
            tb.send_message(user_id, 'Отменяю')
            return

        send = tb.send_message(user_id, "Пришли фотографию подиков")
        tb.register_next_step_handler(send, create_post)
    else:
        send = tb.send_message(user_id, "Пришли текст поста(Описание и цена)")
        tb.register_next_step_handler(send, request_post_photo)

def create_post(message):
    if message.photo:
        photo_info = tb.get_file(message.photo[len(message.photo)-1].file_id)
        global downloaded_photo
        downloaded_photo = tb.download_file(photo_info.file_path)
        
        tb.send_message(user_id, "Проверь пост перед отправкой")
        tb.send_message(user_id, post_text)
        tb.send_photo(user_id, message.photo[-1].file_id)
        send = tb.send_message(user_id, "Если нужно переделать пост, пиши 'ред', если пост готов и его нужно запостить, пиши 'пост'")
        tb.register_next_step_handler(send, send_post)
        
    else: 
        send = tb.send_message(user_id, "Пришли фотографию подиков")
        tb.register_next_step_handler(send, create_post)

def send_post(message):
    if message.text:
        if message.text.lower() == 'ред':
            send = tb.send_message(user_id, "Пришли текст поста(Описание и цена)")
            tb.register_next_step_handler(send, request_post_photo)

        elif message.text.lower() == "пост":
            attachments = []
            vk_session = vk.UserAPI(user_login=phone, user_password=password, scope="wall, photos, friends, groups", v="5.131", client_id=8203325)
            up_url = vk_session.photos.getWallUploadServer()["upload_url"]
                
            
            with open("img_0.jpg", "wb") as file:
                file.write(downloaded_photo)
                file.close()
            
            # загрузка фото на сервер 
            with open("img_0.jpg", "rb") as file:
                resp = requests.post(f"{up_url}", files={"file": file})
                saveWallPhoto = vk_session.photos.saveWallPhoto(server=resp.json()["server"], photo=resp.json()["photo"], hash=resp.json()["hash"])
                attachments = []
                attachments.append("photo{}_{}".format(saveWallPhoto[0]["owner_id"], saveWallPhoto[0]["id"]))
                

                for group in groups:
                    try: 
                        vk_session.wall.post(message=post_text, owner_id=group, attachments=attachments)
                        tb.send_message(user_id, f"Удачный пост в группу: https://vk.com/club{group*-1}")
                        time.sleep(1)
                        

                    except:
                        tb.send_message(user_id, f"Неудачный пост в группу: https://vk.com/club{group*-1}")
                        continue

                tb.send_message(user_id, "Работа окончена")
                return
        else:
            send = tb.send_message(user_id, "Если нужно переделать пост, пиши 'ред', если пост готов и его нужно запостить, пиши 'пост'")
            tb.register_next_step_handler(send, send_post)   

    else:
        send = tb.send_message(user_id, "Если нужно переделать пост, пиши 'ред', если пост готов и его нужно запостить, пиши 'пост'")
        tb.register_next_step_handler(send, send_post)
    
tb.polling()