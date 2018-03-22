# import scraping libraries and utilities
import urllib2
from bs4 import BeautifulSoup
import re
import time
import pandas as pd

#set page url template, replace "!" with page number and "@" with the season year
template_url = 'http://insider.espn.com/nba/hollinger/statistics/_/page/!/year/@'

#Note that the 2017-2018 season is represented by 2018
data = []
start_year = 2008
end_year = 2018

#Get player efficiency ratings for years (start, end)
for year in range(start_year, end_year+1):
    
    #These ratings are found across multiple pages, so loop over pages
    page = 1
    
    while True:
        
        #Get the table for a specific year+page and parse it into beautifulsoup
        page_url = template_url.replace('!', str(page)).replace('@', str(year))
        html = urllib2.urlopen(page_url)
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find('table', attrs={'class':'tablehead'}).find_all('tr', attrs={'class':re.compile('player')})
    
        #If the table is empty, break
        if not table:
            break
        
        #Loop through the table and get player names and their PER
        for row in table:
            cells = row.find_all('td')
            name = cells[1].get_text().split(',')[0]
            PER = cells[11].get_text()
            minutes =  cells[3].get_text()
            data.append([int(year), str(name), float(PER), float(minutes)])
            
        page = page+1
        
        #Wait for a second before sending another url request so I don't get banned from espn
        time.sleep(2)

data_pd = pd.DataFrame(data, columns=['season_year','player_name','player_efficiency_rating', 'minutes'])
data_pd.to_csv('per_data.csv', index=False)