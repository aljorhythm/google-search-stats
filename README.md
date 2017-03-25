# google-search-stats

Crawls into each google search result and obtain
1. Images stats
	- Total count
	- Count of images with alt
2. Youtube stats
	- Embeded youtube videos
	- Thumbs up and thumbs down

## Run

### All
`sh run_all.sh`

### crawls into every search result of url
python scraper.py -searchurl https://www.google.com.sg/search?q=*\<query string\>*

### crawls into every search result of saved search results
python scraper.py -searchfile *\<filename\>*

### stats from youtube
python scraper.py -youtube http://www.youtube.com/watch?v=*\<video id\>*

### image stats from url
python scraper.py -images *\<url\>*

## Demo output files
in [output/](output/) folder
