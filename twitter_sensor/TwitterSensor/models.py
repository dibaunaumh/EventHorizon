class Story():
    text = ''
    user_external_id = 0
    external_id = 0
    external_url = ''
    in_reply_to_story = ''
    in_reply_to_user = ''
    last_update = ''
    def __unicode__(self):
        return self.text

class User():
    external_id = 0
    external_url = ''
    name = ''
    screen_name = ''
    url = ''
    location = ''
    description = ''
    image = ''
    def __unicode__(self):
        return self.name
  
