import csv
import os
import streamlit as st
import pandas as pd
import plotly.express as px
from ESLData import esl_data
from SDATData import sdat_data

# for Streamlit Theming
st.set_page_config(layout="wide")
CURRENT_THEME = "light"


def export_to_csv(data, filename, directory):
    """Export data to a CSV file, replacing 'Bezug' with 'ID742' in the output."""
    # Create the directory if it doesn't exist
    os.makedirs(directory, exist_ok=True)

    # Combine directory and filename to create a full path
    file_path = os.path.join(directory, filename)

    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Write header
        writer.writerow(['Sensor_ID', 'DateTime', 'Value'])
        # Write data
        for entry in data:
            # Replace 'Bezug' with 'ID742' in the label for the CSV output
            label = entry[0]
            if label == 'Bezug':
                label = 'ID742'
            else:
                label = 'ID735'
            writer.writerow([label, entry[1], entry[2]])


def daily_data():
    data = sdat_data()
    sequences_cumulative = data[0]
    sequences_daily = data[1]

    # Convert to DataFrame for easier manipulation
    df_cumulative = pd.DataFrame(sequences_cumulative, columns=['Label', 'Datum', 'Wert'])
    df_daily = pd.DataFrame(sequences_daily, columns=['Label', 'Datum', 'Wert'])

    # Convert 'Date' columns to datetime format
    df_cumulative['Datum'] = pd.to_datetime(df_cumulative['Datum'])
    df_daily['Datum'] = pd.to_datetime(df_daily['Datum'])

    # Sort the DataFrames by 'Date'
    df_cumulative.sort_values(by='Datum', inplace=True)
    df_daily.sort_values(by='Datum', inplace=True)

    # Display cumulative data
    st.subheader("Tabelle der Daten (Kumulativ)")
    st.write(df_cumulative)

    # Plotting Cumulative Data as Line Chart
    st.subheader("Datenvisualisierung (Kumulativ)")
    fig_cumulative = px.line(df_cumulative,
                             x='Datum',
                             y='Wert',
                             color='Label',
                             title='Daten (Kumulative)',
                             labels={'Cumulative': 'Cumulative Value'},
                             markers=True,
                             color_discrete_sequence=["#ff0000", "#00ff00"])  # Adding markers for clarity
    fig_cumulative.update_layout(xaxis_title='Datum', yaxis_title='Wert')
    st.plotly_chart(fig_cumulative)

    # Display daily data
    st.subheader("Tabelle der Daten")
    st.write(df_daily)

    # Plotting Daily Data
    st.subheader("Datenvisualisierung")
    fig_daily = px.bar(df_daily,
                       x='Datum',
                       y='Wert',
                       color='Label',
                       title='Daten',
                       labels={'Daily': 'Daily Value'},
                       text='Wert',
                       color_discrete_sequence=["#ff0000", "#00ff00"])
    fig_daily.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    fig_daily.update_layout(xaxis_title='Datum', yaxis_title='Wert', barmode='stack')
    st.plotly_chart(fig_daily)


def monthly_data():
    data = esl_data()
    sorted_data_cumulative = data[0]
    data_month = data[1]

    # Convert to DataFrame for easier manipulation
    df_cumulative = pd.DataFrame(sorted_data_cumulative)
    df_monthly = pd.DataFrame(data_month)

    # Display cumulative data
    st.subheader("Tabelle der monatlichen Daten (Kumulativ)")
    st.write(df_cumulative)

    # Plotting Cumulative Data as Line Chart
    st.subheader("Monatliche Datenvisualisierung")
    fig_cumulative = px.line(df_cumulative,
                             x='TimePeriod',
                             y=['Bezug', 'Einspeisung'],
                             title='Monatliche Datenvisualisierung (Kumulative)',
                             labels={'value': 'Cumulative Value'},
                             markers=True,
                             color_discrete_sequence=["#ff0000", "#00ff00"])  # Adding markers for clarity
    fig_cumulative.update_layout(xaxis_title='Datum', yaxis_title='Wert')
    st.plotly_chart(fig_cumulative)

    # Display monthly data
    st.subheader("Monatliche Daten")
    st.write(df_monthly)

    # Plotting Monthly Data
    st.subheader("Monatliche Datenvisualisierung")
    fig_monthly = px.bar(df_monthly,
                         x='TimePeriod',
                         y=['Bezug', 'Einspeisung'],
                         title='Monatliche Datenvisualisierung',
                         labels={'value': 'Monthly Value'},
                         text='value',
                         barmode='group',
                         color_discrete_sequence=["#ff0000", "#00ff00"])  # Change to group
    fig_monthly.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    fig_monthly.update_layout(xaxis_title='Datum', yaxis_title='Wert')
    st.plotly_chart(fig_monthly)


def yearly_data():
    # Call the esl_data function and unpack the returned tuple
    data = esl_data()

    # --- First Chart: Processing the first dataset ---
    # Convert the first element (sorted cumulative data) into a DataFrame for the first chart
    df_yearly = pd.DataFrame(data[0])

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
    yearly_last_month['Kumulative Bezug'] = yearly_last_month['Bezug'].cumsum()
    yearly_last_month['Kumulative Einspeisung'] = yearly_last_month['Einspeisung'].cumsum()

    # Debug: Display the yearly data for confirmation
    st.subheader("Tabelle der Jährlichen Daten (Kumulativ)")
    st.write(yearly_last_month)

    # --- First Chart: Plot Yearly Last Month Data as Line Chart ---
    st.subheader("Jährliche Datenvisualisierung (Kumulativ)")
    fig_yearly = px.line(
        yearly_last_month,
        x='Year',
        y=['Bezug', 'Einspeisung'],
        title='Jährliche Datenvisualisierung',
        labels={'value': 'Yearly Value'},
        markers=True, # Add markers for each data point for better clarity
        color_discrete_sequence=["#ff0000", "#00ff00"]
    )
    fig_yearly.update_layout(xaxis_title='Jahr', yaxis_title='Wert')
    st.plotly_chart(fig_yearly)

    # --- Second Chart: Year-over-Year Difference Calculation ---
    # Calculate year-over-year difference for Bezug and Einspeisung
    yearly_last_month['Bezug Differenz'] = yearly_last_month['Bezug'].diff().fillna(yearly_last_month['Bezug'])
    yearly_last_month['Einspeisung Differenz'] = yearly_last_month['Einspeisung'].diff().fillna(yearly_last_month['Einspeisung'])

    # Display the Year-over-Year Differences
    st.subheader("Tabelle der Jährlichen Daten")
    st.write(yearly_last_month[['Year', 'Bezug', 'Einspeisung']])

    # --- Second Chart: Bar Chart for Year-over-Year Differences ---
    st.subheader("Jährliche Datenvisualisierung")
    fig_difference = px.bar(
        yearly_last_month,
        x='Year',
        y=['Bezug Differenz', 'Einspeisung Differenz'],
        barmode='group',  # Grouped bar chart to compare values side-by-side
        title='Jährliche Daten',
        labels={'value': 'Differenz'},
        color_discrete_sequence=["#ff0000", "#00ff00"]
    )
    fig_difference.update_layout(xaxis_title='Jahr', yaxis_title='Wert')
    st.plotly_chart(fig_difference)


# Streamlit app
def main():
    st.title('Voltaflow Energie Visualizer')

    # User selection for time granularity
    time_granularity = st.selectbox('Wählen Sie eine Zeitspanne aus', ('Monatlich', 'Jährlich', 'Täglich'))

    # Resample data based on user selection (yearly or monthly)
    if time_granularity == 'Jährlich':
        yearly_data()
    if time_granularity == 'Monatlich':
        monthly_data()
    if time_granularity == 'Täglich':
        daily_data()


if __name__ == '__main__':
    main()
    # Call the function to execute
    cumulative_data, daily_data = sdat_data()
    # Export both cumulative and daily data to CSV files
    export_to_csv(cumulative_data, 'cumulative_data.csv', 'Exports')
    export_to_csv(daily_data, 'daily_data.csv', 'Exports')
