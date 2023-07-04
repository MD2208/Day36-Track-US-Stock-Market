import requests
import datetime as dt
from twilio.rest import Client

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"

## STEP 1: Use https://www.alphavantage.co
# When STOCK price increase/decreases by 5% between yesterday and the day before yesterday then print("Get News").

#Get yesterday and the day before yesterday date in format yyyy-mm-dd
now = dt.datetime.now()
# yesterday = now - dt.timedelta(1)
# yesterday = yesterday.date()
# the_day_before = now - dt.timedelta(2)
# the_day_before = the_day_before.date()
last_week = str(now - dt.timedelta(7))


alpha_api_key = 'your-api-key'
alpha_api_url = 'https://www.alphavantage.co/query'

alpha_params = {
    'function': 'TIME_SERIES_DAILY_ADJUSTED',
    'symbol' : STOCK,
    'apikey': alpha_api_key
}

alpha_req = requests.get(alpha_api_url,params=alpha_params)
alpha_req.raise_for_status()
stock_price_data = alpha_req.json()['Time Series (Daily)']

count = 0 
closing_prices = []
for key in stock_price_data:
    closing_prices.append( stock_price_data[key]['4. close'] )
    count+=1
    if count ==2:
        break

closing_price_1 = float(closing_prices[0])
closing_price_2 = float(closing_prices[1])
price_diff_perc = (closing_price_1-closing_price_2)*100/closing_price_2

if price_diff_perc> 5 or price_diff_perc < -5:        
    ## STEP 2: Use https://newsapi.org
    # Instead of printing ("Get News"), actually get the first 3 news pieces for the COMPANY_NAME.
    if price_diff_perc > 5:
        headline = f'TESLA 🔺 {int(price_diff_perc)}%'
    else: 
        headline = f'TESLA 🔻 {int(price_diff_perc)}%'
    news_api_key = 'your-api-key' 
    news_url = 'https://newsapi.org/v2/everything'

    news_params = {
        'q' : COMPANY_NAME,
        'from':last_week,
        'sortBy':'relevancy',
        'language':'en',
        'apiKey':news_api_key
    }

    news_req = requests.get(news_url, params=news_params)
    news_data = news_req.json()['articles'][0:3]
    news_formatted = { item['title']:item['description'] for item in news_data}
    details=''
    for item in news_formatted:
        details += f"Headline:{item}\nBrief:{news_formatted[item]}\n"
    
    ## STEP 3: Use https://www.twilio.com
    # Send a seperate message with the percentage change and each article's title and description to your phone number. 

    account_sid = 'your-twilio-sid'
    auth_token = 'your-twilio-token'
    client = Client(account_sid, auth_token)

    message = client.messages.create(
                        body=f"{headline}. Here comes the news;\n{details}",
                        from_='your-twilio-number',
                        to='reciever-number')
#Optional: Format the SMS message like this: 
"""
TSLA: 🔺2%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
or
"TSLA: 🔻5%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
"""

