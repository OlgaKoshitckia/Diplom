import vk_api
from datetime import date
from config import ACCES_TOKEN

class VkTools():
    def __init__(self, token):
        self.api = vk_api.VkApi(token=token)
        self.offset = 0

    def get_info(self, id):
        """Получние данных об анкете из ВК"""
        data_info = {'id': id, 'name': None, 'city': None, 'age': 0, 'sex': 0, 'relation': 0}
        info = self.api.method('users.get', {'user_ids': id,
                                'fields': ('bdate, city, sex, relation'),})
        if info:
            info = info[0]
            data_info['name'] = f"{info.get('first_name')} {info.get('last_name')}"
            city = info.get('city')
            if city:
                data_info['city'] = city.get('title')
            age = info.get('bdate')
            if age: 
                age = int(age.split('.')[-1])
                data_info['age'] = date.today().year - age
            data_info['sex'] = info.get('sex')
            data_info['relation'] = info.get('relation', 0)
        return data_info

    def search_user(self, params):
        """Получение анкет по совпадениям"""
        fields = {'count': 5, 
                  'offset': self.offset,
                  'age_from': params['age'] - 5,
                  'age_to': params['age'] + 5,
                  'sex': 1 if params['sex'] == 2 else 2,
                  'hometown': params['city'], 
                  'has_photo': 1,
                  'status': params['relation'], 
                  'is_closed': False}
        self.offset += 5
        users = self.api.method('users.search', fields)
        result = []
        try:
            users = users['items']
            for user in users:
                if not user['is_closed']:
                    result.append({'id': user['id'],
                                   'name': f'{user["first_name"]} {user["last_name"]}'})
        except KeyError:
            ...
        return result
        
    def get_photos(self, id):
        """Получение фото из анкеты"""
        photos = self.api.method('photos.get', {'user_id': id,
                                                    'album_id': 'profile',
                                                    'extended': 1})
        result = []

        try:
            photos = photos['items']
        except KeyError:
            return result
        
        for photo in photos:
            result.append((photo['id'], 
                           photo['likes']['count'] + photo['comments']['count']))
        result.sort(key=lambda x: x[1], reverse=True)
        attach = ','.join(f'photo{id}_{photo[0]}' for photo in result[:3])
        return attach


if __name__ == '__main__':
    me = VkTools(ACCES_TOKEN)
    print(me.search_user({'age': 25, 'sex': 1, 'city': 'Санкт-Петербург', 'relation': 0}))
    print(me.get_photos(111111))
