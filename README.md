# Vaccine slot crawler

***


## Setup

* Clone the repo

      git clone git@github.com:viksharma1987/vaccineslotcrawler.git

* Install python dependencies, make sure you have python installed.
      
      cd vaccineslotcrawler
      pip install -r requirements.txt
      
## Input json schema

```
{
  "cowin": {
    "calender_api_url": "https://cdn-api.co-vin.in/api/v2/appointment/sessions/calendarByDistrict?district_id={0}&date={1}",
    "calender_api_public_url": "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id={0}&date={1}"
  },
  "telegram": {
    "bot_api_key": "<provide telegram bot token>",
    "telegram_chat_url": "https://api.telegram.org/bot{}/sendMessage?parse_mode=markdown&chat_id={}&text={}"
  },
  "districts": {
    "jaipur I": {
      "district_ids": [
        "505"
      ],
      "min_age": 18,
      "min_slots": 5,
      "refresh_rate": 1,
      "telegram_channel_id": "@upwinder"
    }
  }
}
```

1. `bot_api_key` - Provide your telegram bot token.
2. `jodhpur` - Replace it with the district you want to crawl for.
3. `district_ids` - Provide all district ids for the target district. You can find all state codes [here](https://cdn-api.co-vin.in/api/v2/admin/location/states), pick your state code and use it [here](https://cdn-api.co-vin.in/api/v2/admin/location/districts/16) to get all district details in that state. 
4. `min_age` - Minimum eligible age to filter the slots, currently values can be either 18 or 45, as slots are devided for the two categories. Default is 18.
5. `min_slots` - Minimum number of slots for which you want to send a notification. Default is 5.
6. `refresh_rate` - At what interval do you want to poll cowin servers. Default is 5 (seconds), That means every 5 seconds code will check new slots avaibility. 
7. `telegram_channel_id` - Provide your telegram channel id to be notified.

How to create a Telegram bot and how to send text message to a telegram group/channel, Learn [here](https://dev.to/rizkyrajitha/get-notifications-with-telegram-bot-537l)

## Run the code

* Update `input.json` as per above schema. 
* Run below commands

      cd src
      python -u app.py -d <district_name>
      
      example 
      python -u app.py -d jaipur
      
* Run below command for help.
     
      python -u app.py --help
      
* If you are running the code on a windows or linux machine and if slots are available, it will make a beep sound, to stop the sound comment this [line](https://github.com/covid-opensource/vaccineslotcrawler/blob/2d9f94c1232474616a36b2045270a571b79ad257/src/api.py#L111).


## Run as docker container
      
      cd vaccineslotcrawler
      export version="v1"
      
      # Docker build
      docker build -t cowin:$version .

      # Docker run      
      docker run -it cowin:$version
      
      # Docker tag and push over docker registry.
      docker tag cowin:$version <your_docker_registry>:$version
      docker push <your_docker_registry>:$version
