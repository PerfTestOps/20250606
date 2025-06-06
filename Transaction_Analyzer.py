import streamlit as st
import pandas as pd
from docx import Document
from fpdf import FPDF
import plotly.express as px
import matplotlib.pyplot as plt
from docx.shared import Inches
from datetime import datetime

def transaction_analysis_page():
    # st.set_page_config(page_title="Transaction Analyzer",
    #                 page_icon=":bar_chart:",
    #                 )
    
    st.title("Transaction Analyzer")
    # (Rest of your transaction analysis logic...)

    #import matplotlib.pyplot as plt

    

    #Define a function for generating a pie chart for different runs
    def generatepiechart(filtered_df1):

        num_rowsPie, num_colsPie = filtered_df1.shape
        print(f"{num_rowsPie}    {num_colsPie}")

        for i in range(1, num_colsPie):
            print(f"{i}")
            if i < num_colsPie:                 
                sla_column = filtered_df1.columns[1]        #SLA Values column
                current_column = filtered_df1.columns[i]
                sla_breach_count = 0

                if i >= 2:                                 #this code makes sure that we are reading the runs column
                    for value, SLAValue in zip(filtered_df1[current_column], filtered_df1[sla_column]):
                    #print(f"")
                        #print(f"SLA Value = {SLAValue} Current Column Values: {value}")
                        if value > SLAValue:
                            sla_breach_count = sla_breach_count + 1
                    print(f"No of Transactions braching SLA is {sla_breach_count }")
                    labels = ['SLA Met', 'SLA Breached']
                    sizes = [num_rowsPie - sla_breach_count, sla_breach_count]
                    colors = ['green', 'red']
                    explode = (0.1, 0)
                    fig, ax = plt.subplots(figsize=(0.8, 0.8), dpi=1000)
                    ax.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=140, textprops={'fontsize': 5})
                    plt.title(f"{current_column}", fontsize=6)
                    st.pyplot(fig)


    # Define a function to apply styling
    def highlight_cells(col_data,sla_value):
        print(f"Value is {col_data} and SLA is {sla_value}")
        color = 'red' if col_data > sla_value else 'green'
        return 'color: %s' % color

    def generate_report(filtered_df1,graph_path):
        
            # Code to generate Word report

        
            # Create a Word document
            doc = Document()
        
            # Add a title
            doc.add_heading("DataFrame Content", level=1)

            #st.dataframe(filtered_df1)
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"PerformanceTestReport_{timestamp}.docx"
            # Add a table
            table = doc.add_table(rows=1, cols=len(filtered_df1.columns))
            table.style = "Table Grid"

            hdr_cells = table.rows[0].cells
            for j, col in enumerate(filtered_df1.columns):
                    hdr_cells[j].text = col
                
            for i, row in filtered_df1.iterrows():
                    row_cells = table.add_row().cells
                    for j, value in enumerate(row):
                        row_cells[j].text = str(value)


            doc.add_heading("Observations", level=1)

            #the code for comparison between different runs will go in here
            #1st Step - Determine the number of rows and columns in the 'filtered_df1' data set

            num_rows, num_cols = filtered_df1.shape

            #2nd Step - Read the data frame row wise till the data is reached
            #for row in filtered_df1.iterrows():
                #print(f"{row}") 

            if num_cols == 4:                            #Logic for generating text based o/p for 2 test run comparison
                print("Two run Comparison")

                totalAvg90PercentRespTime1 = 0
                totalAvg90PercentRespTime2 = 0
                runSLA = 0
                run1SLAMeetingCount = 0
                run2SLAMeetingCount = 0

                for row_index, row in filtered_df1.iterrows():
                    column_counter = 0
                    
                    
                    for col_index, value in row.items():
                        column_counter = column_counter + 1
                        #print(f"Row {row_index}, Column {col_index}: {value}")
                        
                        if column_counter == 2:  
                            runSLA = int(f"{value}")         #this variable holds the SLA value against each transaction
                            print(int(runSLA))
                            

                    #totalAvg90PercentRespTime1 = totalAvg90PercentRespTime1 + 
                        if column_counter == 3 :             #Add the response time for 3rd column txns for response times referred to as Run 1
                            #print(column_counter)
                            run1Name = f"{col_index}"
                            tempTranRespTime = value         #this variable holds the resp time for each transaction for Run 1 for each iteration of for loop

                            #print(f"Column {col_index}: {value}")
                            totalAvg90PercentRespTime1 = totalAvg90PercentRespTime1 + value
                            #print(run1Name)

                            if tempTranRespTime < runSLA:
                                run1SLAMeetingCount = run1SLAMeetingCount + 1
                            
                        if column_counter == 4 :             #Add the response time for 3rd column txns for response times referred to as Run 2
                            #print(column_counter)
                            run2Name = f"{col_index}"
                            tempTranRespTime = value
                            #print(f"Column {col_index}: {value}")
                            totalAvg90PercentRespTime2 = totalAvg90PercentRespTime2 + value

                            if tempTranRespTime < runSLA:
                                run2SLAMeetingCount = run2SLAMeetingCount + 1
                
                        #respTimeDifference = totalAvg90PercentRespTime2
                
                if(totalAvg90PercentRespTime1 > totalAvg90PercentRespTime2):
                            respTimeDifference = ((totalAvg90PercentRespTime1 - totalAvg90PercentRespTime2)*100)/totalAvg90PercentRespTime1
                            #print(f"{run1Name} is degraded compared to {run2Name} by {respTimeDifference}%")
                            line = f"1. {run1Name} is degraded compared to {run2Name} by {respTimeDifference}%"
                            doc.add_paragraph(line)
                            line2 = f"2. {run1Name} has {run1SLAMeetingCount} transactions meeting SLA"
                            doc.add_paragraph(line2)
                            line3 = f"3. {run2Name} has {run2SLAMeetingCount} transactions meeting SLA"
                            doc.add_paragraph(line3)

                if(totalAvg90PercentRespTime2 > totalAvg90PercentRespTime1):
                            respTimeDifference = ((totalAvg90PercentRespTime2 - totalAvg90PercentRespTime1)*100)/totalAvg90PercentRespTime1
                            #print(f"{run2Name} is degraded compared to {run1Name} by {respTimeDifference}%")
                            line = f"1. {run2Name} is degraded compared to {run1Name} by {respTimeDifference}%"
                            doc.add_paragraph(line)
                            line2 = f"2. {run1Name} has {run1SLAMeetingCount} transactions meeting SLA"
                            doc.add_paragraph(line2)
                            line3 = f"3. {run2Name} has {run2SLAMeetingCount} transactions meeting SLA"
                            doc.add_paragraph(line3)

                if(totalAvg90PercentRespTime2 == totalAvg90PercentRespTime1):
                            #respTimeDifference = ((totalAvg90PercentRespTime2 - totalAvg90PercentRespTime1)*100)/totalAvg90PercentRespTime1
                            print(f"1. Run 2 is similar in performance Run 1")
                            doc.add_paragraph("1. {run2Name} is similar in performance {run1Name}")
                            line2 = f"2. {run1Name} has {run1SLAMeetingCount} transactions meeting SLA"
                            doc.add_paragraph(line2)
                            line3 = f"3. {run2Name} has {run2SLAMeetingCount} transactions meeting SLA"
                            doc.add_paragraph(line3)
                
            
            elif num_cols == 5:
                print("Three Run Comparison")
            elif num_cols > 5:
                #print("Comparison Only allowed for 2 or 3 Runs selection")  ##We have to fix this code for later so that word document doesnt get generated
                st.error("Comparison Only allowed for 2 or 3 Runs selection")
                return
            else:
                #print("Not Enough data for comparison")    ##We have to fix this code for later so that word document doesnt get generated
                st.error("Not Enough data for comparison")
                #st.button("Submit Wrong Input")
                return
        


            doc.add_heading("Graph Exported from Table", level=1)
            doc.add_picture(graph_path, width=Inches(5))

        

            # Save the document
            #doc.save("output.docx")
            doc.save(filename)
            st.success(f"Word document saved successfully")
            #print("DataFrame saved in 'output.docx'.")


    # Load Excel file
    uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx", "txt"])

    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file, index_col=None)

        # Streamlit app
        st.title("Data Query and Graph Generator")

    
        #st.dataframe(filtered_df)
        with st.expander("View DataFrame"):
            st.dataframe(df)

        # Get the list of columns
        columns = df.columns.tolist()

        # Select column to filter
        #st.sidebar.header("Please Filter Here:")
        #column_to_filter = st.sidebar.selectbox("Select column to filter", columns)
        column_to_filter = st.selectbox("Select column to filter", columns)

        # Get unique values in the selected column
        unique_values = df[column_to_filter].unique()

        # Select value to filter by
        #st.sidebar.header("Please Filter Here:")
        #filter_value = st.sidebar.selectbox("Select value to filter by", unique_values)
        filter_value = st.selectbox("Select value to filter by", unique_values)

        # Filter the DataFrame
        filtered_df = df[df[column_to_filter] == filter_value]

        # Display the filtered DataFrame
        #st.write("### Filtered Data")
        #st.dataframe(filtered_df)
        with st.expander("View Filetred DataFrame"):
            st.dataframe(filtered_df)

        del filtered_df['Status']

        

        st.sidebar.header("Please Filter Here:")
        selected_columns = st.sidebar.multiselect("Select columns to include", filtered_df.columns.tolist(), default=filtered_df.columns.tolist())



        if selected_columns:
            
            filtered_df1 = filtered_df[selected_columns]
        st.write("Filtered Table:")
        
        show_message = st.checkbox('Highlight SLA Deviations')

        # Dropdown options
        option = st.sidebar.selectbox(
        'SLA Tolerance Percentage',
        ['0','10', '20', '30']
        )

        # Display selected option
        st.write(f'You selected: {option}')


        def highlight_sla(row):
            sla = row['SLA']
            styles = []

            for col in row.index:
                if col not in ['Status', 'TransactionName', 'SLA']:
                    try:
                        value = float(row[col])
                        if value <= sla:
                            styles.append('background-color: lightgreen')
                        else:
                            styles.append('background-color: lightcoral')
                    except:
                        styles.append('')
                else:
                    styles.append('')
            return styles


        if show_message:
            styled_df = filtered_df1.style.apply(highlight_sla, axis=1)
            st.dataframe(styled_df)
            #st.write('Checkbox is checked!')
        else:
            st.dataframe(filtered_df1)
            #st.write('Checkbox is unchecked!')


        
        st.title(":bar_chart:  Transaction Analysis")
        st.bar_chart(filtered_df1.set_index('TransactionName'), stack=False) 
        
    
        plt.title("Generated Graph")


        #this is code for bar chart
        # Plotting the bar chart
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(filtered_df1['TransactionName'], filtered_df1['SLA'], marker='o',label='SLA', color='red', linewidth=2)
        bar_width = 0.2  # Width of each bar
        x_indexes = range(len(filtered_df1['TransactionName']))

        # Plot each y-column as grouped bars
        for i, column in enumerate(filtered_df1.columns[2:]):
            ax.bar(
                [x + i * bar_width for x in x_indexes],
                filtered_df1[column],
                bar_width,
                label=column
                )

        ax.set_xlabel('Transaction Names')
        ax.set_ylabel('90 Percent Response Times (secs)')
        ax.set_title('Bar Chart with Fixed X-axis and Varying Y-columns')
        ax.set_xticks([x + bar_width for x in x_indexes])
        ax.set_xticklabels(filtered_df1['TransactionName'])
        ax.legend()
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        plt.savefig('plot.png', format='png')
        # Display the plot in the Streamlit app
        st.pyplot(fig)



        graph_path = "plot.png"
        fig.savefig(graph_path)

        #insert code to generate pie chart

        generatepiechart(filtered_df1)

        if st.button('Generate Report'):
        #generate_report(filtered_df1) 
            #st.bar_chart(filtered_df1.set_index('TransactionName'), stack=False) 
            
            generate_report(filtered_df1,graph_path) 

    else:
        st.write("")
