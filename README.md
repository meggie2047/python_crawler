# python_crawler
#Scraping Douban Top 250 Data and Analysis
##Introduction
This project utilizes Selenium4 to scrape data from Douban's Top 250 movies list and performs data analysis using Pandas.

##How to Use
###1. Clone the Project
git clone https://github.com/meggie2047/python_crawler.git
cd your_project
###2. Install Dependencies
Make sure you have Python and pip installed. Then install the project dependencies using the following command:

pip install selenium pandas
###3. Run the Scraper
Execute the following command in the terminal to run the scraper and fetch data from Douban's Top 250 movies list:
v1 is for douban movie info, only including title and url, v2 is for fetching movie detail.

python douban_top250_se_v2.py
###4. Analyze the Data
open douban_top250_pandas.ipynb and run each cell.


File Structure

├── douban_top250_se_v2.py   
├──douban_top250_se_v1.py            
├──douban_top250_pandas.ipynb   
├── data/                     
│   ├── douban_top_250_detail.xlsx    
│   └── douban_top_250_info.xlsx     
└── README.md 

Notes

Before running the scraper, make sure you have Chrome browser installed and download the appropriate version of ChromeDriver, placing it in the project's root directory.
The scraped data may be subject to Douban's anti-scraping mechanisms. Please adjust the scraping frequency appropriately and adhere to the website's terms of use.

