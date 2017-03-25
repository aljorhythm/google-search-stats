from HTMLParser import HTMLParser
from htmlentitydefs import name2codepoint
import urllib2
import pprint
import sys
import csv

if(len(sys.argv) <= 2):
	print "python images_scraper.py -searchurl|-searchfile|-images|-youtube <url|google search url|google search filename> <output filename>"
	exit()

# logging
pp = pprint.PrettyPrinter(indent=4)
log = pp.pprint

# http/https get requester
opener = urllib2.build_opener()
opener.addheaders = [('User-agent', 'Mozilla/5.0')] # cannot get if user agent not set

class StatsParser(HTMLParser, object):
	def get_stats(self, html):
		raise Exception("Not implemented error")

class LinksParser(HTMLParser, object):
	def get_links(self, html):
		raise Exception("Not implemented error")

# get links from html: get_links()
# naive assumption of "h3.r" elements containing no other "h3.r"s
class LinksFromGoogleSearchHTML(LinksParser, object):
	def handle_starttag(self, tag, attrs):
		if(tag == "h3" and any([(attr[0] == "class" and "r" in attr[1].split(' ')) for attr in attrs])): 	# don't get unwanted links
																											# attributes are in tuples (attribute name, attribute value). search for tuple with [0] == "class" and "r" in [1]
			self.noOfChildren = 0			# turn on recording start get_statsing child nodes that are traversed
			self.recording = True			# @RT ^
		elif(self.recording and tag == "a"):
			self.links.append([attr[1] for attr in attrs if attr[0] == 'href'][0]) 							# get href from <a> tags if recording is on
		if(self.recording): 				# increment child node traversed
			self.noOfChildren += 1
	def handle_endtag(self, tag):
		if(self.recording): 				# exit child node, decrement get_stats
			self.noOfChildren -= 1
			if(self.noOfChildren == 0): 	# back to .h3 node, stop recording
				self.recording = False
	def get_links(self, html):
		self.recording = False 				# reset recording
		self.links = [] 					# reset links
		self.feed(html)
		self.links = ["https://www.google.com" + link if (link[0] == "/") else link for link in self.links]
		return self.links

# count images from HTML fed to parser
class CountImages(StatsParser, object):
	def handle_starttag(self, tag, attrs):
		if(tag == "img"):
			self.imgCount += 1                              # increment image
		if any([attr[0] == 'alt' for attr in attrs]):
			self.imgWithAltCount += 1                       # increment image with alt
	def get_stats(self, html):
		self.imgCount = 0
		self.imgWithAltCount = 0
		try:
			self.feed(html.decode('utf-8', errors='ignore'))
			return { 'total': self.imgCount, 'with alt': self.imgWithAltCount }
		except Exception as e:
			return e

class YoutubeStats(StatsParser, object):
	def handle_starttag(self, tag, attrs):
		for key, value in self.recording.iteritems():
			self.recording[key] += 1 if self.recording[key] >= 0 else 0
		for attr in attrs:
			if(attr[0] == "class" and "like-button-renderer" in attr[1].split(' ')): #like button
				self.recording['likes'] = 0
				return
			if(attr[0] == "class" and "watch-view-count" in attr[1].split(' ')): #views
				self.recording['views'] = 0
				return
	def handle_data(self, data):
		for key, value in self.recording.iteritems():
			if(self.recording[key] >= 0):
				if(not key in self.stats):
					self.stats[key] = ""
				self.stats[key] += data
	def handle_endtag(self, tag):
		for key, value in self.recording.iteritems():
			self.recording[key] = self.recording[key] - 1
	def get_stats(self, html):
		self.recording = {
			'likes' : -1,
			'views' : -1
		}
		self.stats = {}
		self.feed(html.decode('utf-8', errors='ignore'))
		try:
			#likes
			raw = self.stats['likes'].split('\n')
			list_values = []
			for val in raw:
				try:
					list_values.append(int(val.replace(',', '')))
				except:
					pass
			self.stats['likes'] = {'ups': list_values[0], 'downs': list_values[2]}
			#views
			self.stats['views'] = int(self.stats['views'].split(' ')[0].replace(',', ''))
		except Exception as e:
			return e
		return self.stats

class YoutubeStatsOfURL(YoutubeStats):
	def get_stats(self, url):
		try:		
			html = opener.open(url).read()
		except Exception as e:
			return e
		return super(YoutubeStatsOfURL, self).get_stats(html)

# get_stats youtube embeds from HTML fed to parser
class YoutubeLinks(StatsParser, object):
	def __init__(self, youtube_parser):
		self.youtube_parser = youtube_parser
		super(YoutubeLinks, self).__init__()
	def sanitize_src(self, src):
		src = src.replace('/embed/','/watch?v=').replace('/v/','/watch?v=')
		if(src[0:2] == "//"):
			src = "http:" + src
		return src
	def handle_starttag(self, tag, attrs):
		if(tag == "iframe"):
			for attr in attrs:
				if(attr[0] == "src" and "youtube.com" in attr[1]):
					self.youtube_srcs.append(self.sanitize_src(attr[1]))
					return
		if(tag == "param"):
			for attr in attrs:
				if(attr[0] == "value" and "youtube.com" in attr[1]):
					self.youtube_srcs.append(self.sanitize_src(attr[1]))
					return
	def get_stats(self, html):
		self.youtube_srcs = []
		try:
			self.feed(html.decode('utf-8', errors='ignore'))
		except Exception as e:
			return e
		return [(src, self.youtube_parser.get_stats(src)) for src in self.youtube_srcs]

class YoutubeLinksOfURL(YoutubeLinks):
	def get_stats(self, url):
		try:		
			html = opener.open(url).read()
		except Exception as e:
			return e
		return super(YoutubeLinksOfURL, self).get_stats(html)

class GoogleSearchResultsStats(StatsParser):
	def __init__(self, parsers):
		self.getLinksParser = LinksFromGoogleSearchHTML()
		self.parsers = parsers
		self.events = {}
	def on_event(self, event_name, event_handler):
		self.events[event_name] = event_handler
	def fire_event(self, event_name, data):
		if(event_name in self.events):
			self.events[event_name](data)
	def get_stats(self, html): # hrefs from live result as of OCT 26 are in the form of /url/... which expects user to be redirected from google.com
		links = self.getLinksParser.get_links(html)
		results = {}
		for i in range(0, len(links)):
			link = links[i]
			try:
				results[link] = {parser_type : parser.get_stats(opener.open(link).read()) for parser_type, parser in self.parsers.iteritems()}
			except Exception as e:
				results[link] = e
			self.fire_event("on_scrape", ((str(i + 1) + " / " + str(len(links))), link, results[link])) # fire 'on_scrape' event
		return results
	def get_stats_file(self, filename):
		return self.get_stats(open(filename, 'r').read())
	def get_stats_url(self, url):
		try:		
			html = opener.open(url).read()
		except Exception as e:
			return e
		return self.get_stats(html)

# instance of parsers
youtube_stats_parser = YoutubeStatsOfURL()
youtube_srcs_parser = YoutubeLinks(youtube_stats_parser)
count_images = CountImages()
search_results_parser = GoogleSearchResultsStats({'youtube': youtube_srcs_parser, 'images': count_images})

# print while scraping multiple links to see progress
search_results_parser.on_event('on_scrape', log)

# main

# begin
search_URL_or_filename = sys.argv[2]

if("-searchfile" in sys.argv):
	results = search_results_parser.get_stats_file(search_URL_or_filename)
	log(results)
	if (len(sys.argv) > 3):
		print "writing to " + sys.argv[3]
		with open(sys.argv[3], 'wb') as csvfile:
			csv_writer = csv.writer(csvfile, delimiter=',')
			for link, data in results.iteritems():
				print data
				continue
				try:
					csv_writer.writerow([link, get_statss['total'], get_statss['with alt']])
				except:
					csv_writer.writerow([link, get_statss])					
elif("-searchurl" in sys.argv):
	results = search_results_parser.get_stats_url(search_URL_or_filename)
	log(results)
elif("-images" in sys.argv):
	print count_images.get_stats(opener.open(search_URL_or_filename).read())
elif("-youtube" in sys.argv):
	print youtube_stats_parser.get_stats(search_URL_or_filename)
#BYE
exit()

#EXAMPLES:

print imagesParser.get_stats("https://github.com")
print imagesParser.get_stats("https://www.google.com.sg/search?q=visual+basic")
