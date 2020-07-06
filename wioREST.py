import requests

def wioREST(url):

   r = requests.get(url)

   #print(r.status_code)
   #print(r.json())

# return (str.replace(str(r.json()),"u'","'"))

   if  r.status_code == 200 :
      return r.json()
   else:
      return "ERROR" 
