import streamlit as st
import pandas as pd
from docx import Document
import matplotlib.pyplot as plt
from docx.shared import Inches
from datetime import datetime
from io import BytesIO

def transaction_analysis_page():
    def generatepiechart(filtered_df1):
        num_rowsPie, num_colsPie = filtered_df1.shape
        for i in range(1, num_colsPie):
            if i < num_colsPie:
                sla_column = filtered_df1.columns[1]
                current_column = filtered_df1.columns[i]
                sla_breach_count = 0
                if i >= 2:
                    for value, SLAValue in zip(filtered_df1[current_column], filtered_df1[sla_column]):
                        if value > SLAValue:
                            sla_breach_count += 1
                    labels = ['SLA Met', 'SLA Breached']
                    sizes = [num_rowsPie - sla_breach_count, sla_breach_count]
                    colors = ['green', 'red']
                    explode = (0.1, 0)
                    fig, ax = plt.subplots(figsize=(0.8, 0.8), dpi=1000)
                    ax.pie(sizes, explode=explode, labels=labels, colors=colors,
                           autopct='%1.1f%%', shadow=True, startangle=140, textprops={'fontsize': 5})
                    plt.title(f"{current_column}", fontsize=6)
                    st.pyplot(fig)

    def generate_report(filtered_df1, graph_path):
        doc = Document()
        doc.add_heading("DataFrame Content", level=1)

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
        num_rows, num_cols = filtered_df1.shape

        if num_cols == 4:
            totalAvg90PercentRespTime1 = 0
            totalAvg90PercentRespTime2 = 0
            run1SLAMeetingCount = 0
            run2SLAMeetingCount = 0

            for _, row in filtered_df1.iterrows():
                runSLA = int(row[1])
                value1 = row[2]
                value2 = row[3]

                totalAvg90PercentRespTime1 += value1
                totalAvg90PercentRespTime2 += value2

                if value1 <= runSLA:
                    run1SLAMeetingCount += 1
                if value2 <= runSLA:
                    run2SLAMeetingCount += 1

            if totalAvg90PercentRespTime1 > totalAvg90PercentRespTime2:
                diff = ((totalAvg90PercentRespTime1 - totalAvg90PercentRespTime2) * 100) / totalAvg90PercentRespTime1
                doc.add_paragraph(f"1. Run 1 is degraded compared to Run 2 by {diff:.2f}%")
            elif totalAvg90PercentRespTime2 > totalAvg90PercentRespTime1:
                diff = ((totalAvg90PercentRespTime2 - totalAvg90PercentRespTime1) * 100) / totalAvg90PercentRespTime1
                doc.add_paragraph(f"1. Run 2 is degraded compared to Run 1 by {diff:.2f}%")
            else:
                doc.add_paragraph("1. Both runs have similar performance.")

            doc.add_paragraph(f"2. Run 1 has {run1SLAMeetingCount} transactions meeting SLA")
            doc.add_paragraph(f"3. Run 2 has {run2SLAMeetingCount} transactions meeting SLA")
        else:
            doc.add_paragraph("Please compare only 2 runs for detailed analysis.")

        doc.add_heading("Graph Exported from Table", level=1)
        doc.add_picture(graph_path, width=Inches(5))

        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer

    uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx", "txt"])

    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file, index_col=None)

        st.title("Data Query and Graph Generator")
        with st.expander("View DataFrame"):
            st.dataframe(df)

        columns = df.columns.tolist()
        column_to_filter = st.selectbox("Select column to filter", columns)
        unique_values = df[column_to_filter].unique()
        filter_value = st.selectbox("Select value to filter by", unique_values)

        filtered_df = df[df[column_to_filter] == filter_value]
        with st.expander("View Filtered DataFrame"):
            st.dataframe(filtered_df)

        if 'Status' in filtered_df.columns:
            del filtered_df['Status']

        st.sidebar.header("Please Filter Here:")
        selected_columns = st.sidebar.multiselect("Select columns to include",
                                                  filtered_df.columns.tolist(),
                                                  default=filtered_df.columns.tolist())

        if selected_columns:
            filtered_df1 = filtered_df[selected_columns]
        else:
            st.warning("Please select at least one column.")
            return

        st.write("Filtered Table:")
        show_message = st.checkbox('Highlight SLA Deviations')

        option = st.sidebar.selectbox('SLA Tolerance Percentage', ['0', '10', '20', '30'])
        st.write(f'Selected SLA tolerance: {option}%')

        def highlight_sla(row):
            sla = row['SLA']
            styles = []
            for col in row.index:
                if col not in ['TransactionName', 'SLA']:
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
        else:
            st.dataframe(filtered_df1)

        st.title(":bar_chart: Transaction Analysis")
        st.bar_chart(filtered_df1.set_index('TransactionName'), use_container_width=True)

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(filtered_df1['TransactionName'], filtered_df1['SLA'], marker='o',
                label='SLA', color='red', linewidth=2)

        bar_width = 0.2
        x_indexes = range(len(filtered_df1['TransactionName']))

        for i, column in enumerate(filtered_df1.columns[2:]):
            ax.bar(
                [x + i * bar_width for x in x_indexes],
                filtered_df1[column],
                bar_width,
                label=column
            )

        ax.set_xlabel('Transaction Names')
        ax.set_ylabel('90 Percent Response Times (secs)')
        ax.set_title('Transaction Performance Comparison')
        ax.set_xticks([x + bar_width for x in x_indexes])
        ax.set_xticklabels(filtered_df1['TransactionName'])
        ax.legend()
        ax.grid(axis='y', linestyle='--', alpha=0.7)

        graph_path = "plot.png"
        fig.savefig(graph_path)
        st.pyplot(fig)

        generatepiechart(filtered_df1)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"PerformanceTestReport_{timestamp}.docx"
        word_buffer = generate_report(filtered_df1, graph_path)

        st.download_button(
            label="Generate Report",
            data=word_buffer,
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    else:
        st.info("")


