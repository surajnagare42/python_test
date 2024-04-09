# Dependency and Running this project
You need docker installed to run this project (No other dependencies required)
docker version >= 3

*Note*: Since, the free version of https://manage.exchangeratesapi.io/ only allows to call one date per API call and only allows 250 overall API calls, This project was only limited to 10 rows. If in future the overheads needs to be changed then:

1. Update the .env file for new API Key
2. Change the start & end date

## To run this project

First Ensure the START_DATE and END_DATE in the .env file is updated to the expected Date Range.
```bash
1. sudo docker-compose build

2. docker-compose up
