import pandas as pd
import requests

def getCurrentWeeklyNames():
    # target URL
    url = 'http://www.cboe.com/tradtool/symbols/symbolweeklys.aspx'

    # Scrape the HTML at the url
    html = requests.get(url).text
    df = pd.read_html(html)[1]

    return df['Symbol'].tolist()


def main():
    print('Found ', len(getCurrentWeeklyNames()), ' names')

if __name__ == "__main__":
    main()
