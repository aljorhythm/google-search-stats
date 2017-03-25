echo terminal "source run_all.sh"
echo use source command
echo use CTR+C to proceed to next
echo "python scraper.py -searchurl https://www.google.com.sg/search?q=best+acapella"
python scraper.py -searchurl https://www.google.com.sg/search?q=best+acapella
echo "python scraper.py -searchfile bffs.html"
python scraper.py -searchfile bffs.html
echo "python scraper.py -youtube http://www.youtube.com/watch?v=UyqpjkCwEI4"
python scraper.py -youtube http://www.youtube.com/watch?v=UyqpjkCwEI4
echo "python scraper.py -images http://www.youtube.com/watch?v=UyqpjkCwEI4"
python scraper.py -youtube http://www.youtube.com/watch?v=UyqpjkCwEI4