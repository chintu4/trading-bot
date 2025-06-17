# Trading Settings

## ⚠️ Live Trading Disclaimer

**Please read this carefully before enabling live trading with real funds.**

Algorithmic trading carries significant financial risk. The strategies and code provided in this repository are for educational and experimental purposes only.

-   **No Guarantees:** There is no guarantee that the bot will generate profits. Market conditions can change rapidly, and past performance is not indicative of future results.
-   **Financial Loss:** You could lose some or all of your invested capital. Only trade with funds that you can afford to lose.
-   **Bugs and Errors:** Software, including this trading bot, may contain bugs or errors that could lead to unexpected behavior or financial losses.
-   **Test Thoroughly:** Before trading with real money, it is crucial to:
    -   Thoroughly test the bot and your strategies in a simulated environment or with very small, non-critical amounts of capital.
    -   Understand the code and the strategies you are deploying.
    -   Be aware of the specific risks associated with the markets and assets you are trading (e.g., cryptocurrencies are highly volatile).
-   **Exchange Risks:** Be aware of the risks associated with using cryptocurrency exchanges, including API limitations, downtime, and security vulnerabilities.
-   **API Keys:** Secure your API keys. Do not commit them to the repository. Use the `.env` file as instructed.

**By using this software for live trading, you acknowledge these risks and agree that you are solely responsible for all trading decisions and their outcomes.** The maintainers and contributors of this repository are not liable for any financial losses you may incur.

**Always start with small amounts and monitor performance closely.**

### Testing Live Functionality Safely

Before letting the bot trade with significant capital using the live order placement features, it's critical to test its live trading functionality cautiously. Since a dedicated paper trading mode via API might not be available or easily accessible for spot trading on all exchanges:

1.  **Configuration Double-Check**:
    *   Verify that your `COINDCX_API_KEY` and `COINDCX_API_SECRET` in your `.env` file are correct and have the necessary trading permissions on the exchange.
    *   Ensure `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` are correct so you receive timely notifications.
    *   Confirm your Cosmos DB connection details are correct if you are relying on it for logging.

2.  **Use Minimum Tradable Quantities**:
    *   When you decide to test with real funds, start with the **absolute minimum tradable quantity** allowed by CoinDCX for your chosen trading pair (e.g., for BTC/INR, find the smallest fraction of BTC you can trade). This minimizes potential financial loss during testing. You'll need to check CoinDCX's documentation or interface for these minimums.

3.  **Consider a Low-Value Test Symbol**:
    *   If you're apprehensive, you could conduct your very first live tests on a highly liquid pair with a very low unit value, if available.

4.  **Monitor Closely**:
    *   Run the strategy that triggers the live trading logic (e.g., by running a script that calls the `PercentageStrategy().execute(...)` method with appropriate parameters).
    *   Carefully observe the application's console logs for messages related to order placement attempts, successes (with order IDs), or failures.
    *   Check for Telegram notifications, which should mirror these events.

5.  **Verify on the Exchange**:
    *   After the bot attempts to place an order, log in to your CoinDCX account directly through their website or app.
    *   Manually verify if the order appears in your open orders or trade history. Check its status, fill details, and any fees. This is the ultimate confirmation.

6.  **Understand Strategy Behavior**:
    *   The `PercentageStrategy` included is a basic example. Make sure you understand its logic (when it decides to buy or sell based on percentage changes) before allowing it to manage real funds.

7.  **Start/Stop Mechanism**:
    *   Have a clear way to start and, more importantly, **stop** the bot or the script that's triggering live trades. Do not leave it running unattended until you are highly confident in its behavior.

By following these steps, you can gain more confidence in the bot's live trading capabilities while minimizing risk.

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


