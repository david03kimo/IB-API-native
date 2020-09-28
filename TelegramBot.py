import requests
import json
import configparser
import urllib.request as req
class telegram_bot():
	
	def __init__(self):
		self.token,self.chatid = self.read_token()
		self.base='https://api.telegram.org/bot{}/'.format(self.token)
	
	def read_token(self):
		config=configparser.ConfigParser()
		config.read('/Users/davidliao/Documents/code/Github/MyProject/data/config.cfg')
		token=config.get('Section_A','token')
		chatid=config.get('Section_A','chatid')
		return token,chatid

	def send(self,text):
		
		resp = requests.post(self.base+'sendMessage?chat_id={}&text={}'.format(self.chatid,text))
		resp.raise_for_status()
	

	def GetUpdates(self,offset=None):
		url=self.base+'/getUpdates?timeout=100'
		if offset:
			url=url+'&offset={}'.format(offset+1)
		r=requests.get(url)
		return json.loads(r.content)

	def webhook(self):
		url="https://api.telegram.org/bot1232434797:AAFsd_ZaC0SmVTrtp2Irz35d7SJZrpVrRUg/setWebhook?url="
		request=req.Request(url,headers={})
with req.urlopen(request) as response:
    data=response.read().decode("utf-8")
print(data)

	def MakeReply(msg):
		reply='Okey'
		return reply


def main():
	app=telegram_bot()
	while 1:
		t=app.GetUpdates()
		print(t)
	#update_id=None
	# while True:
	# 	updates=app.GetUpdates(offset=update_id)
	# 	updates=updates['result']
	# 	if updates:
	# 		for item in updates:
	# 			update_id=item['update_id']
	# 			try:
	# 				message=item['message']['text']
	# 			except:
	# 				message=None
	# 			from_=item['message']['from']['id']
	# 			reply=app.MakeReply(message)
	# 			app.send(reply)
				
			#print(message)



	# app.send('py sent message')


if __name__=="__main__":
    main()
