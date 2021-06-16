import requests
from datetime import datetime
import config


class FriendsParser:

    client_id = 7881208
    client_secret = config.client_secret
    display = 'page'
    scope = 'friends'

    def __init__(self):

        print('Parser object was created...')
        self.token = ''
        self.access_token = ''
        self.user_screen_names = []
        self.profiles = []
        self.user_ids = []
        self.mutual_ids = []
        self.mutual_friends = []

    def output_result(self):

        if self.mutual_friends:
            print("Mutual friends:")
            for (count, mutual_friend) in enumerate(self.mutual_friends):
                print(f"{count+1}) {mutual_friend['profile_url']} {mutual_friend['name']} {mutual_friend['photo_id']}")
        else:
            print("0 Mutual friends were found")

    def get_info_by_ids(self):

        step = 999
        for i in range(0, len(self.mutual_ids), step):
            user_ids_str = ','.join(self.mutual_ids[:i+step])
            fields = 'photo_id,nickname,screen_name'
            api_users_get = f'https://api.vk.com/method/users.get?user_ids={user_ids_str}&fields={fields}' \
                            f'&access_token={self.access_token}&v=5.131'
            resp = requests.get(api_users_get)
            response = resp.json()
            if 'error' in response:
                print(f'Error #{response["error"]["error_code"]}', response['error']['error_msg'])
            else:
                for profile_info in response['response']:
                    photo_url = 'https://vk.com/images/camera_200.png'
                    nickname = ''
                    if 'photo_id' in profile_info:
                        photo_url = f'https://vk.com/{profile_info["screen_name"]}?photo={profile_info["photo_id"]}' \
                                    f'&z=photo{profile_info["photo_id"]}'
                    if 'nickname' in profile_info:
                        nickname = f' {str(profile_info["nickname"])}'  # there is space before nickname
                    mutual_friend = {
                        'profile_url': f"https://vk.com/id{str(profile_info['id'])}",
                        'name': f"{profile_info['first_name']} {profile_info['last_name']}{nickname}",
                        'photo_id': photo_url,
                        'screen_name': profile_info['screen_name']
                    }
                    self.mutual_friends.append(mutual_friend)

    def check_mutual(self):

        step = 99
        for i in range(0, len(self.user_ids), step):
            source_uid = self.user_ids[i]
            to_count = i+step
            target_uids = ','.join(self.user_ids[i+1:to_count])

            api_vk_getmutual = f'https://api.vk.com/method/friends.getMutual?source_id={source_uid}' \
                               f'&target_uids={target_uids}&access_token={self.access_token}&v=5.131'
            resp = requests.get(api_vk_getmutual)
            response = resp.json()
            if 'error' in response:
                print(f'Error #{response["error"]["error_code"]}', response['error']['error_msg'])
            else:
                for mutual_dict in response['response']:
                    for mutual_id in mutual_dict['common_friends']:
                        if mutual_id not in self.mutual_ids:
                            self.mutual_ids.append(str(mutual_id))  # mutual id is str

    def input_profiles(self):

        step = 999
        raw_input = str(input('Enter VK profile urls separated by space: '))
        profile_urls = raw_input.split(' ')
        for i in range(0, len(profile_urls), step):
            user_screen_names = []
            for profile_url in profile_urls[i:i+step]:
                user_screen_names.append(profile_url.split('/')[-1])
            user_screen_names_str = ','.join(user_screen_names)

            api_users_get = f'https://api.vk.com/method/users.get?user_ids={user_screen_names_str}' \
                            f'&access_token={self.access_token}&v=5.131'
            resp = requests.get(api_users_get)
            response = resp.json()
            if 'error' in response:
                print(f'Error #{response["error"]["error_code"]}', response['error']['error_msg'])
                return False
            else:
                for profile in response['response']:
                    self.user_ids.append(str(profile['id']))  # profile id is str
                return True

    def get_token(self):

        url = f'https://oauth.vk.com/authorize?client_id={self.client_id}&display={self.display}&scope={self.scope}' \
              f'&response_type=code&v=5.131'
        print('Go to url below and copy CODE from address row')
        print(url)
        self.token = str(input('Enter code: '))
        if len(self.token):
            access_url = f"https://oauth.vk.com/access_token?client_id={self.client_id}" \
                         f"&client_secret={self.client_secret}&code={self.token}"
            resp = requests.get(access_url)
            if resp.status_code != 200:
                print(f'Error #{resp.status_code}', resp.json()['error_description'])
                return False
            else:
                self.access_token = resp.json()['access_token']
                print('Access token for VK received')
                return True

    def run(self):

        got_token = self.get_token()
        while not got_token:
            got_token = self.get_token()
        profiles_entered = self.input_profiles()
        while not profiles_entered:
            profiles_entered = self.input_profiles()
        start_time = datetime.now()
        self.check_mutual()
        self.get_info_by_ids()
        self.output_result()
        end_time = datetime.now()
        print(f"Functions calls in {end_time-start_time} seconds")


p = FriendsParser()
p.run()
