import streamlit as st
import pandas as pd
import plotly.express as px
from ESLData import esl_data  # Assuming the ESL data processing function is in ESLData.py


# Function to process the ESL data
def process_esl_data():
    # Parse the ESL files and convert them to two DataFrames: cumulative and monthly
    cumulative_data, monthly_data = esl_data()

    # Convert both lists to DataFrames
    df_cumulative = pd.DataFrame(cumulative_data)
    df_monthly = pd.DataFrame(monthly_data)

    # Convert 'TimePeriod' to datetime for easier resampling
    df_cumulative['TimePeriod'] = pd.to_datetime(df_cumulative['TimePeriod'], format='%Y-%m')
    df_monthly['TimePeriod'] = pd.to_datetime(df_monthly['TimePeriod'], format='%Y-%m')

    return df_cumulative, df_monthly


# Streamlit app
def main():
    st.title('Voltaflow Energie Visualizer')

    # Parse the ESL data
    df_cumulative, df_monthly = process_esl_data()

    if not df_cumulative.empty and not df_monthly.empty:
        # User selection for time granularity
        time_granularity = st.selectbox('Wählen sie eine Zeitspanne aus', ('Monatlich', 'Jährlich'))

        # Visualization for cumulative data
        st.subheader('Cumulative Energy Data (Bezug and Einspeisung)')
        st.dataframe(df_cumulative)

        fig_cumulative = px.line(df_cumulative, x='TimePeriod', y=['Bezug', 'Einspeisung'],
                                 labels={'value': 'Energie (kWh)', 'TimePeriod': 'Zeitspanne'},
                                 title=f'Kumulativer Energiebezug und Einspeisung')

        # Customize x-axis for cumulative data
        fig_cumulative.update_layout(
            autosize=True,
            margin=dict(l=40, r=40, b=100, t=80),
            xaxis=dict(
                tickmode='linear',
                dtick="M1",  # Monthly ticks
                tickformat="%b %Y",  # Show month and year
                tickangle=-45,
                title_font=dict(size=14),
                tickfont=dict(size=12)
            ),
            yaxis=dict(
                title_font=dict(size=14),
                tickfont=dict(size=12)
            )
        )

        # Display the cumulative plot
        st.plotly_chart(fig_cumulative, use_container_width=True)

        # Visualization for monthly data using a bar chart (beam diagram)
        st.subheader('Monatliche Energiestatistik (Bezug and Einspeisung)')
        st.dataframe(df_monthly)

        # Bar chart for monthly energy consumption
        fig_monthly = px.bar(df_monthly, x='TimePeriod', y=['Bezug', 'Einspeisung'],
                             barmode='group',
                             labels={'value': 'Energie (kWh)', 'TimePeriod': 'Monat'},
                             title='Monatlicher Energiebezug und Einspeisung')

        # Customize x-axis for monthly data
        fig_monthly.update_layout(
            autosize=True,
            margin=dict(l=40, r=40, b=100, t=80),
            xaxis=dict(
                tickmode='linear',
                dtick="M1",  # Monthly ticks
                tickformat="%b %Y",  # Show month and year
                tickangle=-45,
                title_font=dict(size=14),
                tickfont=dict(size=12)
            ),
            yaxis=dict(
                title_font=dict(size=14),
                tickfont=dict(size=12)
            )
        )

        # Display the monthly bar chart
        st.plotly_chart(fig_monthly, use_container_width=True)

    else:
        st.warning('Keine Daten zum Visualisieren')


if __name__ == '__main__':
    main()
