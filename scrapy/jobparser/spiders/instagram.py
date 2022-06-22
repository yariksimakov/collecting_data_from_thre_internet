from urllib.parse import urlencode
from copy import deepcopy
from scrapy.http import HtmlResponse
from jobparser.items import InstaparserItem
import scrapy
import re
import json

with open('../password_me.text', 'r', encoding='utf-8') as f:
    password_file = f.read()


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['https://www.instagram.com/']
    inst_authorization_link = 'https://www.instagram.com/accounts/login/ajax/'
    # username = 'Onliskill_udm'
    username = 'yariksimakov'
    password = password_file
    # profile_name = 'techskills_2022'
    profile_names = ['geekbrains.ru', 'useful.sweety']
    graph_link = 'https://www.instagram.com/graphql/query/?'
    post_query_hash = '69cba40317214236af40e7efa697781d'
    api_link_follower = 'https://i.instagram.com/api/v1/friendships/--/followers/?'
    api_link_following = 'https://i.instagram.com/api/v1/friendships/--/following/?'

    def parse(self, response: HtmlResponse):
        csrf_token = self.get_csrf_token(response.text)
        yield scrapy.FormRequest(
            self.inst_authorization_link,
            method='POST',
            callback=self.login,
            formdata={'username': self.username, 'enc_password': self.password},
            headers={'X-CSRFToken': csrf_token}
        )

    def login(self, response: HtmlResponse):
        json_response = response.json()
        if json_response['authenticated']:
            for profile_name in self.profile_names:
                yield response.follow(
                    f'https://www.instagram.com/{profile_name}/',
                    callback=self.get_followers_and_followings,
                    cb_kwargs={'profile_name': profile_name}
                )
        else:
            raise Exception('You was not authenticated')


    def get_followers_and_followings(self, response: HtmlResponse, profile_name):
        user_id = self.get_user_id(response.text, profile_name)
        api_link_follower = self.api_link_follower.replace('--', f'{user_id}')
        url_get = f'{api_link_follower}count=12&search_surface=follow_list_page'
        yield response.follow(url_get,
                              callback=self.continue_get_data,
                              cb_kwargs={'user_id': user_id,
                                         'user_classification': 'follower',
                                         'profile_name': profile_name},
                              headers={'User-Agent': 'Instagram 155.0.0.37.107'}
                              )

        api_link_following = self.api_link_following.replace('--', f'{user_id}')
        url_get = f'{api_link_following}count=12'
        yield response.follow(url_get,
                              callback=self.continue_get_data,
                              cb_kwargs={'user_id': user_id,
                                         'user_classification': 'following',
                                         'profile_name': profile_name},
                              headers={'User-Agent': 'Instagram 155.0.0.37.107'}
                              )

    def continue_get_data(self, response: HtmlResponse, user_id, user_classification, profile_name):
        json_information = response.json()
        next_max_id = json_information.get('next_max_id')
        if next_max_id:
            if user_classification == 'follower':
                api_link = self.api_link_follower.replace('--', f'{user_id}')
                url_get = f'{api_link}count=12&max_id={next_max_id}&search_surface=follow_list_page'
                yield response.follow(url_get,
                                      callback=self.continue_get_data,
                                      cb_kwargs={'user_id': user_id,
                                                 'user_classification': user_classification,
                                                 'profile_name': profile_name},
                                      headers={'User-Agent': 'Instagram 155.0.0.37.107'}
                                      )
            else:
                api_link_following = self.api_link_following.replace('--', f'{user_id}')
                url_get = f'{api_link_following}count=12&max_id={next_max_id}'
                yield response.follow(url_get,
                                      callback=self.continue_get_data,
                                      cb_kwargs={'user_id': user_id,
                                                 'user_classification': user_classification,
                                                 'profile_name': profile_name},
                                      headers={'User-Agent': 'Instagram 155.0.0.37.107'}
                                      )
        follow_data = json_information.get('users')
        for follow in follow_data:
            follower_id = follow['pk']
            follower_name = follow['full_name']
            follower_username = follow['username']
            follower_photo = follow['profile_pic_url']
            yield InstaparserItem(user_classification=user_classification,
                                  profile_name=profile_name,
                                  follow_id=follower_id,
                                  follow_name=follower_name,
                                  follow_username=follower_username,
                                  follow_photo=follower_photo
                                  )

    # def user_post_start(self, response: HtmlResponse, username):
    #     user_id = self.get_user_id(response.text, username)
    #     variables = {'id': user_id,
    #                  'first': 12}
    #     url_post = f'{self.graph_link}query_hash={self.post_query_hash}&{urlencode(variables)}'
    #     yield response.follow(url_post,
    #                           callback=self.user_posts,
    #                           cb_kwargs={'username': username,
    #                                      'user_id': user_id,
    #                                      'variables': deepcopy(variables)})

    # def user_posts(self, response: HtmlResponse, username, user_id, variables):
    #     json_information = response.json()
    #     page_data = json_information.get('data').get('user').get('edge_owner_to_timeline_media').get('page_info')
    #     if page_data['has_next_page']:
    #         variables['after'] = page_data['end_cursor']
    #         url_post = f'{self.graph_link}query_hash={self.post_query_hash}&{urlencode(variables)}'
    #         yield response.follow(url_post,
    #                               callback=self.user_posts,
    #                               cb_kwargs={'username': username,
    #                                      'user_id': user_id,
    #                                      'variables': deepcopy(variables)},
    #                               headers={'User-Agent': 'Instagram 155.0.0.37.107'}
    #                               )
    #     posts = json_information.get('data').get('user').get('edge_owner_to_timeline_media').get('edges')
    #     for post in posts:
    #         yield InstaparserItem(
    #             user_id=user_id,
    #             username=username,
    #             photo=post.get('node').get('display_url'),
    #             likes=post.get('node').get('edge_media_preview_like').get('count'),
    #             post_data=post.get('node')
    #         )

    def get_csrf_token(self, text):
        param = re.search(r'"csrf_token":"\w+"', text).group().split(':').pop()
        return re.sub(r'"', '', param, 2)

    def get_user_id(self, text, username):
        try:
            matched = re.search(
                r'{"id":"\d+","username":"%s"}' % username, text
            ).group()
            return json.loads(matched).get('id')
        except:
            return re.findall(r'"id":"\d+"', text)[-1].split('"')[-2]
