import redis


def send_notification():
    r = redis.Redis(host='127.0.0.1', port=6379, db=0)
    message = "Новое уведомление для пользователя!"
    r.publish('notifications', message)

for i in range(10):
  send_notification()