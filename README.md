# Trading Settings
## Aim
The main aim of the repository 
1. make successful trades.
2. Use best strategy
3. Make Telegram based notifications.
4. Use cosmosdb as this will used it
5. Use Azure function to run the code

# configuring cosmos db 
```bash
& "C:\Program Files\Azure Cosmos DB Emulator\CosmosDB.Emulator.exe"
```
# Version and Goals
## version 0.1
### Planing 
add http request connect with telegram
1. Implement price-estimad
2. choosing http-request only for sending telegram based event
3. choosing timer-based that will check price change percentage.
4. choosing cosmo that will continuesly run and each run will increase cost of hosting
5. finally , choosing a database to store the trading history and performance metrics.
6. curretly iam consern with spot trading only

#### implementation
.1 ->  able to run azure functions and run using python 
*   It will tell about what is the price has been fluctuated ?
    like it will send a notification what is the price change of the fluctuation
    I Think this version will only show me the
#### Expectations
after starting application it will make movements based on percentage stategy 
and after making successfull trading send an email notification 
#### Testing 
app will send telegram notification when it feels that the price has beeen changed. and reached it's expected price or percentage

## Version 0.2
### Planning
implementing the Rov version -> that can decide price movement and buy and sell value automatically 


