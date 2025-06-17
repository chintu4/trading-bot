# Trading Settings
## Aim
The main aim of the repository 
1. make successful trades.
2. Use best strategy
3. Make Telegram based notifications.
4. Use cosmosdb as this will used it
5. Use Azure function to run the code

## Using Azure Cosmos DB Emulator (Local Development)

As noted in previous sections, this project can connect to Azure Cosmos DB. For local development and testing, you can use the Azure Cosmos DB Emulator.

**1. Start the Emulator:**
   Open PowerShell or your command line and run the command you've noted for starting the emulator (typically found in its installation directory):
   ```bash
   # Example command (verify path on your system):
   & "C:\Program Files\Azure Cosmos DB Emulator\CosmosDB.Emulator.exe"
   ```
   Ensure the emulator is running before starting the application if you intend to connect to it.

**2. Configure Connection Details:**
   The Cosmos DB Emulator uses a default endpoint and key:
   *   **Endpoint:** `https_://localhost:8081/`
   *   **Primary Key:** `C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==`

   To allow the application to connect to the local emulator, create a file named `.env` in the root directory of this project (if you haven't already for other settings). Add the following lines to it:

   ```env
   COSMOS_DB_ENDPOINT="https_://localhost:8081/"
   COSMOS_DB_KEY="C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw=="
   ```

   The application's `config/settings.py` is set up to read these values from the `.env` file to configure the connection in `services/cosmosdb_service.py`.

**3. Accessing Emulator Data:**
   When the emulator is running, you can usually open a web browser and navigate to `https_://localhost:8081/_explorer/index.html` to view and manage your data directly.

**Note:** The `.env` file is included in `.gitignore`, so your local credentials will not be committed to the repository. Remember to configure your actual Azure Cosmos DB credentials in your production environment's settings.

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


