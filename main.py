import streamlit as st
import pandas as pd
import plotly.express as px
from ESLData import esl_data
from SDATData import sdat_data

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

    # Plotting Cumulative Data as Line Chart
    st.subheader("Cumulative Data Visualization")
    fig_cumulative = px.line(df_cumulative,
                             x='Date',
                             y='Cumulative',
                             color='Label',
                             title='Cumulative Data Over Time',
                             labels={'Cumulative': 'Cumulative Value'},
                             markers=True)  # Adding markers for clarity
    fig_cumulative.update_layout(xaxis_title='Date', yaxis_title='Cumulative Value')
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
    yearly_last_month['Cumulative Bezug'] = yearly_last_month['Bezug'].cumsum()
    yearly_last_month['Cumulative Einspeisung'] = yearly_last_month['Einspeisung'].cumsum()

    # Debug: Display the yearly data for confirmation
    st.subheader("Cumulative Yearly Data Table")
    st.write(yearly_last_month)

    # First Chart: Plot Yearly Last Month Data as Line Chart (using the first value from the tuple)
    st.subheader("Cumulative Yearly Data Visualization")
    fig_yearly = px.line(
        yearly_last_month,
        x='Year',
        y=['Bezug', 'Einspeisung'],
        title='Yearly Last Month Data Overview',
        labels={'value': 'Yearly Value'},
        markers=True  # Add markers for each data point for better clarity
    )
    fig_yearly.update_layout(xaxis_title='Year', yaxis_title='Value')
    st.plotly_chart(fig_yearly)


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
    process_esl_data()
