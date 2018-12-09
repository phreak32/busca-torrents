# Falta manejar paginacion con lista larga de resultados

import requests
import re
from html.parser import HTMLParser

class Phase1Parser(HTMLParser):
	inicio = 0
	captura_url = 0
	start_item = 0
	num = 0
	num2 = 0
	pos = 0
	def handle_starttag(self, tag, attrs):
		if tag == "ul":
			d = dict(attrs)
			if 'class' in d.keys():
				if d['class'] == "buscar-list":
					self.inicio = 1
				
		if self.inicio == 1:
			if tag == "div":
				d = dict(attrs)
				if 'class' in d.keys():
					if d['class'] == "info":
						self.start_item = 1
						self.num=self.num+1;
						print("detectado div en : ",self.getpos());
		if tag == 'a':
			if self.inicio == 1:
				if self.start_item == 1:
					d = dict(attrs)
					url_torrent.append(d['href'])
					url_quality.append("Not defined");
					self.pos = self.pos + 1;
					self.num2=self.num2+1
					print("estoy en : ",self.getpos());

	def handle_endtag(self, tag):
		if tag == "a":
			if self.inicio == 1:
				if self.start_item == 1:
					self.start_item = 0;
					print("cerrando : ",self.getpos());
				

	def handle_data(self, data):
		if self.inicio == 1:
			if self.start_item == 1:
				print('datos');
				match=re.search(r"\[ (.+) \]",data);
				if match:
					url_quality[self.pos-1]=match.group(1);
					

	def handle_comment(self, data):
		if data == " end .buscar-list ":
			print('>>>>fin');
			self.inicio = 0

#    def handle_comment(self, data):
#        if data == " end .buscar-list ":
#            print('>>>>fin');
#            self.inicio = 0

inicio = 0;
start_item = 0;
captura_url = 0;
url_torrent = [];
url_quality = [];

# Stage 1 : Get search results

parser = Phase1Parser()
url = "http://torrentrapid.com/buscar"
head = {'Content-Type':'application/x-www-form-urlencoded', 'Referer':'http://torrentrapid.com'}
#search_string=input("Input search string:   ");
#payload = 'q='+search_string


#----------------

language=[('Español Castellano','1'),('Ingles','2'),('Portugues','3'),('Multilenguaje','5'),('Español Latino','6'),('Frances','7'),('Japones','8'),('Ingles Subtitulado','9'),('Japones Subtitulado','10'),('Español LINE','11')];
quality=[('Todos',''),('HDTV','HDTV'),('HDTV','HDTV'),('HDTV 720p AC3 5.1','HDTV 720p AC3 5.1'),('HDTV 1080p AC3 5.1','HDTV 1080p AC3 5.1'),('DVDRip','DVDRIP'),('DVDRIP AC3 5.1','DVDRIP AC3 5.1'),('BLuRayRip','BLuRayRip'),('BluRayRip AC3 5.1','BluRayRip AC3 5.1'),('BluRay 720p','BluRay 720p'),('BluRay 1080p','BluRay 1080p'),('BluRay MicroHD','BluRay MicroHD'),('BluRay 3D 1080p','BluRay 3D 1080p'),('HDTV-Screener','HDTV-Screener'),('TS-Screener','TS-Screener'),('CAMRIP','CAMRIP'),('DVD-Screener','DVD-Screener'),('BluRay-Screeener','BluRay-Screeener'),('DVD5','DVD5'),('DVD9','DVD9'),('ISO','ISO'),('MP3','MP3')]
type=[('Juegos','47'),('Software','125'),('Peliculas Castellano','757'),('Series','767'),('Series V.O','775'),('Peliculas V.O','778'),('Documentales','780'),('Deportes','822'),('Varios','827'),('Miniseries - ES','924'),('Cine Alta Definicion HD','1027'),('Series Alta Definicion HD','1469'),('Peliculas Latino','1527'),('Peliculas en 3D HD','1599'),('Todas las Categoria','All')]
order=[('Lo Ultimo','Lo Ultimo'),('Fecha','Fecha'),('Nombre','Nombre'),('Tamaño','Tamaño')]

pg_sel=''

idx=0
for i in type:
	print(idx,' .',i[0]);
	idx=idx+1

type_sel=type[int(input("Content type ? :"))];
	
idx=0
for i in language:
	print(idx,' .',i[0]);
	idx=idx+1
language_sel=language[int(input("Language ? :"))];

idx=0
for i in quality:
	print(idx,' .',i[0]);
	idx=idx+1
quality_sel=quality[int(input("Quality ? :"))];

idx=0
for i in order:
	print(idx,' .',i[0]);
	idx=idx+1
order_sel=order[int(input("Order ? :"))];

inon_sel='Ascendente'

search_string=input("Input search string:   ");

datos=dict(pg=pg_sel,categoryIDR=type_sel,idioma=language_sel,calidad=quality_sel,ordenar=order_sel,inon=inon_sel,q=search_string);

payload=datos

#---------------------


print("Searching torrents...");
r=requests.post(url, data = payload, headers = head);

open("/home/pi/respuesta", 'wb').write(r.content);
print("Parsing response stage 1 ...");
parser.feed(r.text)

urls = zip(url_torrent,url_quality);

print("Found the following content:");
cont = 1

for i in urls:
	print(cont,'.',"Torrent : ",i[0]);
	print("     Quality : ",i[1]);
	print(" ");
	cont=cont+1

	
selection = int(input('Select content to download:  '));

print("Selected: ",url_torrent[selection-1]);

# If result of Stage 1 is a series season there is an intermediate stage 
# similar to stage 1 to select the episode

cadena='series'
match=re.search(cadena,url_torrent[selection-1]);
if match:
	parser = Phase1Parser()
	url = url_torrent[selection-1]
	
	print("Getting episodes ...");
	r=requests.get(url);
	
	print("Parsing response stage 1,5 ...");
	url_torrent = [];
	parser.feed(r.text)
	
	print("Found the following content:");
	cont = 1
	for item in url_torrent:
		print (cont,'. ',item);
		cont=cont+1
	
	selection = int(input('Select content to download:  '));
	
	print("Selected: ",url_torrent[selection-1]);


# Stage 2 : Get the content detail page and parse for final url

url = url_torrent[selection-1] 

print("Opening content detail page");

r=requests.get(url);
cadena = 'window.location.href = "(.+)"'

print("Parsing content detail page");
match=re.search(cadena,r.text);
if not match:
	print("Error parsing content detail page");
	exit(1);

	
print("Downloading: ",match.group(1));
url=match.group(1);
r=requests.get(url);
if r.status_code == requests.codes.ok:
	filename='/home/pi/torrent_file.torrent'
	open(filename, 'wb').write(r.content);
	print("File downloaded: ",filename);
else:
	print("Error en la respuesta", r.status_code);


