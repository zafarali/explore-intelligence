import urllib2
import json
import requests

# input : first name as string
# output : "male", "female" or "unknown"
def get_gender_from_first_name(target): 
	link = "https://gender-api.com/get?name="+target+"&key=vAWELffoPRkNLrEQmP"
	response = urllib2.urlopen(link).read()
	info = json.loads(response)
	return info["gender"]

# input : text in string 
# output : probability of emtoion (negative, pos, neutral)
def extract_sentiment_from_text(text):
	
	headers={
	    "X-Mashape-Key": "IU46bNJOn7mshkhc76CW7qDGGHxxp1Av9YWjsnz5Xa674bLo4n",
	    "Content-Type": "application/x-www-form-urlencoded",
	    "Accept": "application/json"
  	}
  	payload = {
	  	"language": "english",
	    "text": text
  	}

	url = "https://japerk-text-processing.p.mashape.com/sentiment/"
	# request = urllib2.Request(url, data)
	# response = urllib2.urlopen(request).read()

	response = requests.post(url, headers=headers, data=payload)
	info = json.loads(response.content)
	return info["probability"]["neg"], info["probability"]["pos"], info["probability"]["neutral"]

