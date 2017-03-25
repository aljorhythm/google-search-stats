echo terminal "source run_all.sh"
echo use source command
echo use CTR+C to proceed to next

# crawls into every search result of url
echo "python scraper.py -searchurl https://www.google.com.sg/search?q=best+acapella > output/searchurl.out"
python scraper.py -searchurl https://www.google.com.sg/search?q=best+acapella > output/searchurl.out

# crawls into every search result of saved search results
echo "python scraper.py -searchfile bffs.html > output/searchfile.out"
python scraper.py -searchfile bffs.html > output/searchfile.out

# stats from youtube
echo "python scraper.py -youtube http://www.youtube.com/watch?v=UyqpjkCwEI4 > output/youtube.out"
python scraper.py -youtube http://www.youtube.com/watch?v=UyqpjkCwEI4 > output/youtube.out

# stats from youtube
echo "python scraper.py -images http://www.youtube.com/watch?v=UyqpjkCwEI4 > output/images.out"
python scraper.py -images http://www.youtube.com/watch?v=UyqpjkCwEI4 > output/images.out
