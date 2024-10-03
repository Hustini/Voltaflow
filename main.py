import streamlit as st
import pandas as pd
import plotly.express as px
from ESLData import esl_data
from SDATData import sdat_data
import psutil
import os
import time

# for Streamlit Theming
st.set_page_config(layout="wide")
CURRENT_THEME = "light"


# Function to process the ESL data
def process_esl_data():
    # Parse the ESL files and convert them to two DataFrames: cumulative and monthly
    cumulative_data, monthly_data = esl_data()

    # Convert both lists to DataFrames
    df_cumulative = pd.DataFrame(cumulative_data)
    df_monthly = pd.DataFrame(monthly_data)
    #exporting esl data
    df_cumulative.to_csv("esl_export/cumulative_data.csv", index=False)
    df_cumulative.to_json("esl_export/cumulative_data.json", orient="records")
    df_monthly.to_csv("esl_export/monthly_data.csv", index=False)
    df_monthly.to_json("esl_export/monthly_data.json", orient="records")
    # Convert 'TimePeriod' to datetime for easier resampling
    df_cumulative['TimePeriod'] = pd.to_datetime(df_cumulative['TimePeriod'], format='%Y-%m')
    df_monthly['TimePeriod'] = pd.to_datetime(df_monthly['TimePeriod'], format='%Y-%m')

    return df_cumulative, df_monthly


def daily_data():
    data = sdat_data()
    sequences_cumulative = data[0]
    sequences_daily = data[1]

    # Convert to DataFrame for easier manipulation
    df_cumulative = pd.DataFrame(sequences_cumulative, columns=['Label', 'Date', 'Cumulative'])
    df_daily = pd.DataFrame(sequences_daily, columns=['Label', 'Date', 'Daily'])

    # Display cumulative data
    st.subheader("Cumulative Data")
    st.write(df_cumulative)

    # Display daily data
    st.subheader("Daily Data")
    st.write(df_daily)

    # Plotting Cumulative Data
    st.subheader("Cumulative Data Visualization")
    fig_cumulative = px.bar(df_cumulative,
                            x='Date',
                            y='Cumulative',
                            color='Label',
                            title='Cumulative Data Over Time',
                            labels={'Cumulative': 'Cumulative Value'},
                            text='Cumulative')
    fig_cumulative.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    fig_cumulative.update_layout(xaxis_title='Date', yaxis_title='Cumulative Value', barmode='stack')
    st.plotly_chart(fig_cumulative)

    # Plotting Daily Data
    st.subheader("Daily Data Visualization")
    fig_daily = px.bar(df_daily,
                       x='Date',
                       y='Daily',
                       color='Label',
                       title='Daily Data Over Time',
                       labels={'Daily': 'Daily Value'},
                       text='Daily')
    fig_daily.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    fig_daily.update_layout(xaxis_title='Date', yaxis_title='Daily Value', barmode='stack')
    st.plotly_chart(fig_daily)


def monthly_data():
    data = esl_data()
    sorted_data_cumulative = data[0]
    data_month = data[1]

    # Convert to DataFrame for easier manipulation
    df_cumulative = pd.DataFrame(sorted_data_cumulative)
    df_monthly = pd.DataFrame(data_month)

    # Display cumulative data
    st.subheader("Cumulative Data")
    st.write(df_cumulative)

    # Plotting Cumulative Data as Line Chart
    st.subheader("Cumulative Data Visualization")
    fig_cumulative = px.line(df_cumulative,
                             x='TimePeriod',
                             y=['Bezug', 'Einspeisung'],
                             title='Cumulative Data Over Time',
                             labels={'value': 'Cumulative Value'},
                             markers=True)  # Adding markers for clarity
    fig_cumulative.update_layout(xaxis_title='Time Period', yaxis_title='Cumulative Value')
    st.plotly_chart(fig_cumulative)

    # Display monthly data
    st.subheader("Monthly Data")
    st.write(df_monthly)

    # Plotting Monthly Data
    st.subheader("Monthly Data Visualization")
    fig_monthly = px.bar(df_monthly,
                         x='TimePeriod',
                         y=['Bezug', 'Einspeisung'],
                         title='Monthly Data Over Time',
                         labels={'value': 'Monthly Value'},
                         text='value',
                         barmode='group')  # Change to group
    fig_monthly.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    fig_monthly.update_layout(xaxis_title='Time Period', yaxis_title='Monthly Value')
    st.plotly_chart(fig_monthly)


def yearly_data():
    # Call the esl_data function
    data = esl_data()

    # Convert the sorted cumulative data into a DataFrame
    df_yearly = pd.DataFrame(data[0])  # Use the first element of the returned tuple

    # Convert TimePeriod to datetime for proper sorting and visualization
    df_yearly['TimePeriod'] = pd.to_datetime(df_yearly['TimePeriod'], format='%Y-%m')

    # Extract Year and Month for grouping
    df_yearly['Year'] = df_yearly['TimePeriod'].dt.year
    df_yearly['Month'] = df_yearly['TimePeriod'].dt.month

    # Get the last month of each year
    last_month_data = df_yearly[df_yearly.groupby('Year')['Month'].transform('max') == df_yearly['Month']]

    # Aggregate values for the last month of each year
    yearly_last_month = last_month_data.groupby('Year').agg({
        'Bezug': 'sum',
        'Einspeisung': 'sum'
    }).reset_index()

    # Calculate cumulative values based on the last month's values
    yearly_last_month['Cumulative Bezug'] = yearly_last_month['Bezug'].cumsum()
    yearly_last_month['Cumulative Einspeisung'] = yearly_last_month['Einspeisung'].cumsum()

    # Debug: Display the yearly data for confirmation
    st.subheader("Yearly Last Month Data Table")
    st.write(yearly_last_month)

    # Plotting Cumulative Yearly Data as Line Chart
    st.subheader("Cumulative Yearly Last Month Data Visualization")
    fig_cumulative_yearly = px.line(
        yearly_last_month,
        x='Year',
        y=['Cumulative Bezug', 'Cumulative Einspeisung'],
        title='Cumulative Yearly Last Month Data Over Time',
        labels={'value': 'Cumulative Value'},
        markers=True  # Adding markers for clarity
    )
    fig_cumulative_yearly.update_layout(xaxis_title='Year', yaxis_title='Cumulative Value')
    st.plotly_chart(fig_cumulative_yearly)

    # Plotting Yearly Last Month Data as Bar Chart
    st.subheader("Yearly Last Month Data Visualization")
    fig_yearly = px.bar(
        yearly_last_month,
        x='Year',
        y=['Bezug', 'Einspeisung'],
        title='Yearly Last Month Data Overview',
        labels={'value': 'Yearly Value'},
        text_auto=True,  # Show values on both bars
        barmode='group'  # Grouped bar mode
    )
    fig_yearly.update_layout(xaxis_title='Year', yaxis_title='Value')
    st.plotly_chart(fig_yearly)


# Streamlit app
def main():
    st.title('Voltaflow Energie Visualizer')

    # Parse data
    df_cumulative, df_monthly = process_esl_data()

    if not df_cumulative.empty and not df_monthly.empty:
        # User selection for time granularity
        time_granularity = st.selectbox('Wählen Sie eine Zeitspanne aus', ('Monatlich', 'Jährlich', 'Täglich'))

        # Resample data based on user selection (yearly or monthly)
        if time_granularity == 'Jährlich':
            yearly_data()
        if time_granularity == 'Monatlich':
            monthly_data()
        if time_granularity == 'Täglich':
            daily_data()

        # Builtin Healthcheck features
        # Get the current process ID
        pid = os.getpid()

        # Use psutil to access process information
        process = psutil.Process(pid)

        # Function to get RAM and CPU usage
        def print_usage():
            # Get the memory usage in MB
            memory_usage = process.memory_info().rss / (1024 * 1024)
            # Get the CPU usage in percentage
            cpu_usage = process.cpu_percent(interval=1)

            print(f"Memory Usage: {memory_usage:.2f} MB")
            print(f"CPU Usage: {cpu_usage:.2f}%")

        # Simulating a long-running task
        while True:
            # Do some computation here
            time.sleep(30)  # Simulating a delay
            print_usage()


    else:
        st.warning('Keine Daten zum Visualisieren')


if __name__ == '__main__':
    main()
