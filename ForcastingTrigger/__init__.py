import io
import json
import os
import azure.functions as func
import pandas as pd
from azure.storage.blob import BlobServiceClient
from neuralprophet import NeuralProphet
import asyncio
import datetime
from azure.storage.blob import ContentSettings


def generate_y_forecast(df: pd.DataFrame, freq: str, forecast_periods: int, 
                        historic_predictions: bool = True,
                        epochs: int = None):
    # Initialize NeuralProphet model and fit data
    neural_prophet = NeuralProphet(n_forecasts=forecast_periods, collect_metrics=True, epochs=epochs)
    metrics = neural_prophet.fit(df, freq=freq)

    # Make future dataframe and forecast
    future = neural_prophet.make_future_dataframe(df, periods=forecast_periods, n_historic_predictions=historic_predictions)
    forecast = neural_prophet.predict(future).round(2)
    return forecast.round(2)


def create_and_upload_blob(blob_service_client, result_csv_blob_name, forecast_data):
    csv_buffer = io.StringIO()
    forecast_data.to_csv(csv_buffer, index=False)
    with open(result_csv_blob_name, "w") as csv_file:
        csv_file.write(csv_buffer.getvalue())

    upload_blob_client = blob_service_client.get_blob_client(container=os.environ['container_name'], blob=result_csv_blob_name)
    with open(result_csv_blob_name, "rb") as data:
        content_settings = ContentSettings(content_type='text/csv')
        upload_blob_client.upload_blob(data, overwrite=True, content_settings=content_settings)

        
async def execute_forecast(df, freq, forecast_periods, historic_predictions, epochs, blob_service_client, result_csv_blob_name):
    forecast = generate_y_forecast(df, freq, forecast_periods, historic_predictions, epochs)
    current_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    # Append the timestamp to the result_csv_blob_name
    result_csv_blob_name_with_time = result_csv_blob_name + current_time + ".csv"
    create_and_upload_blob(blob_service_client, result_csv_blob_name_with_time, forecast)



async def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Read input parameters from the HTTP request
        req_body = req.get_json()
        input_csv_blob_name = req_body.get('input_csv_name')
        result_csv_blob_name = req_body.get('result_csv_name')

        forecast_periods = req_body.get('forecast_periods', 365 * 3)
        historic_predictions = req_body.get('historic_predictions', True)
        epochs = req_body.get('epochs', None)
        freq = req_body.get('freq', 'D')

        # Connect to your Azure Blob Storage account
        blob_service_client = BlobServiceClient.from_connection_string(os.environ['AzureWebJobsStorage'])
        download_blob_client = blob_service_client.get_blob_client(container=os.environ['container_name'], blob=input_csv_blob_name)

        # Download the CSV file from Blob Storage
        csv_data = download_blob_client.download_blob()
        csv_text = csv_data.content_as_text(encoding='utf-8')
        df = pd.read_csv(io.StringIO(csv_text))
        df['ds'] = pd.to_datetime(df['ds'])

        asyncio.create_task( 
            execute_forecast(df, freq, forecast_periods, historic_predictions, epochs, blob_service_client, result_csv_blob_name)
        )
        # Return the forecast as JSON
        #forecast['ds'] = forecast['ds'].dt.strftime('%Y-%m-%d %H:%M:%S')  # Customize the date format as needed
        #return func.HttpResponse(json.dumps(forecast.to_dict(orient='split')), mimetype='application/json')
        return func.HttpResponse("Forcasting triggered successful.",status_code=200)

    except Exception as e:
        return func.HttpResponse(f"An error occurred: {str(e)}", status_code=500)
