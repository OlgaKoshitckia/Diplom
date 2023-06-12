import vk_api
from vk_api.longpoll import VkEventType, VkLongPoll
from vk_api.utils import get_random_id

from config import ACCES_TOKEN, GROUP_TOKEN
from core import VkTools
from data_store import create_db, VkEngine
import answers

class BotInterface():

    def __init__(self):
        self.interface = vk_api.VkApi(token=GROUP_TOKEN)
        self.api = VkTools(ACCES_TOKEN)
        self.db = VkEngine()
        self.worksheets = None
        self.params = None
        self.flag = None
        create_db()

    def message_send(self, user_id, message, attachment=None):
        """автоотвечтик"""
        self.interface.method('messages.send',
                                {'user_id': user_id,
                                'message': message,
                                'attachment': attachment,
                                'random_id': get_random_id()})
        
    def check_profile(self):
        """обработка профиля"""
        while True:
            if self.worksheets:
                worksheet = self.worksheets.pop()
                worksheet_id = worksheet['id']
                worksheet_name = worksheet['name']
                if self.db.search_id(profile_id=self.params['id'], worksheet_id=worksheet_id):
                    continue
                else:
                    self.db.add_view(profile_id=self.params['id'], worksheet_id=worksheet_id)
                    attach = self.api.get_photos(worksheet_id)
                    stroke = f'{worksheet_name}: vk.com/id{worksheet_id}'
                    return stroke, attach
            else:
                self.worksheets = self.api.search_user(self.params)

        
    def event_handler(self):
        """отслеживание событий в чате"""
        longpoll = VkLongPoll(self.interface)
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                message = event.text.lower()
                if not self.flag and message:
                    self.flag = 'first_ans'
                    self.params = self.api.get_info(id=event.user_id)
                    self.message_send(event.user_id, (f'Здравствуй, {self.params["name"]}\n'
                                                      f'{answers.first_ans}'))
                
                elif message in answers.finish:
                    self.params = None
                    self.flag = None
                    self.message_send(user_id=event.user_id, message=answers.last_ans) 

                elif self.flag == 'first_ans':
                    if not self.params['city'] or message in answers.city:
                        self.flag = 'city'
                        self.message_send(user_id=event.user_id, message='Введите город поиска')
                    elif not self.params['age'] or message in answers.age:
                        self.flag = 'age'
                        self.message_send(user_id=event.user_id, message='Введите возраст для поиска')
                    elif message in answers.next_:
                        self.flag = 'searching'
                        self.message_send(user_id=event.user_id, message=answers.fourth_ans)
                    elif self.params['age'] and self.params['city']:
                        self.message_send(user_id=event.user_id, 
                                          message=(f'{answers.second_ans}'
                                          f'Возраст: {self.params["age"]}, '
                                          f'Город: {self.params["city"]}\n'
                                          f'{answers.third_ans}'))

                elif self.flag == 'city':
                    if not message.isdigit():
                        self.params['city'] = message.capitalize()
                        self.flag = 'first_ans'
                        self.message_send(user_id=event.user_id, 
                                          message=f'Город изменен\n{answers.third_ans}')
                    else:
                        self.message_send(user_id=event.user_id, 
                                          message='Пожалуйста уточните')

                elif self.flag == 'age':
                    if message.isdigit():
                        self.params['age'] = int(message)
                        self.flag = 'first_ans'
                        self.message_send(user_id=event.user_id, 
                                          message=f'Возраст изменен\n{answers.third_ans}')
                    else:
                        self.message_send(user_id=event.user_id, 
                                          message='Пожалуйста уточните')

                elif self.flag == 'searching':
                    msg, att = self.check_profile()
                    self.message_send(event.user_id, message=msg, attachment=att)



if __name__ == '__main__':
    bot =  BotInterface()
    bot.event_handler()
