import tweepy


# Api Authentication Details
consumer_key = '5E2oMO7ZHGElss9cdaLY34x7b'
consumer_secret = 'fwjNRItWWRZ4ftRfwxBSHCwpGY5rth7cKKiZqY06Rru0KECfxi'
access_token = '1031238436064243718-YKGcYZF1yAKAcJTttGNXhAWpHWA4oh'
access_token_secret = 'U0u3Lq29f7PpOfO12q3fHX4nPhtlOV9fqXpEqDHlFbOqt'


def authenticate_api():
    # Authenticating the Application
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    return api


def get_five_top_users(username):
    api = authenticate_api()
    users = api.search_users(username)
    return users[:5]
