# Azure Function for Time Series Forecasting

This Azure Function performs time series forecasting using the NeuralProphet library and uploads the forecasted data as a JSON file to Azure Blob Storage.

## Overview

This Azure Function is designed to perform the following tasks:

1. Receive an HTTP request with input parameters for time series forecasting.
2. Download a CSV file containing time series data from Azure Blob Storage.
3. Generate a time series forecast using the NeuralProphet library.
4. Convert the forecasted data into a JSON format.
5. Upload the JSON file to Azure Blob Storage.

## Prerequisites

Before you can deploy and use this Azure Function, you'll need the following:

- An Azure Function App set up in your Azure subscription.
- Azure Blob Storage for storing input and output data.
- Python 3.7+ and the required Python libraries installed.

## Configuration

To configure and use this Azure Function, you'll need to set the following environment variables:

- `AzureWebJobsStorage`: The connection string for your Azure Storage account.
- `container_name`: The name of the Azure Blob Storage container where the input and output files will be stored.

## Usage

1. Deploy the Azure Function App to your Azure subscription.

2. Send an HTTP POST request to the Azure Function with the following JSON payload:

   ```json
   {
       "input_csv_name": "input.csv",
       "result_json_name": "output",
       "forecast_periods": 365 * 3,
       "historic_predictions": true,
       "epochs": null,
       "freq": "D"
   }
   ```
   
## Local Development
Replace local.setting.json.local to local.setting.json
Replace requirements.txt.local to requirements.txt

Send an HTTP POST request to the Azure Function with the following JSON payload:

   ```json
        curl -X POST -H "Content-Type: application/json" -d '{
            "input_csv_name": "sample_historical_data.csv",
        "result_json_name": "forcasting_result_data",
            "forecast_periods": 30,
            "historic_predictions": true,
            "epochs": 100,
            "freq": "D"
        }' http://localhost:7071/api/ForcastingTrigger
   ```
