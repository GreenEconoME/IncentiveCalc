# Import dependencies
import pandas as pd
import copy
from io import BytesIO

def format_metadata(df):
    df = copy.deepcopy(df)  # Ensure we don't modify the original dataframe
    df['Building GFA'] = df['Building GFA'].apply(lambda x: f"{x:,.0f}")
    df['Tax Rate'] = df['Tax Rate'].apply(lambda x: f"{x:.0%}")
    df['Efficiency Gain Over Baseline (%)'] = df['Efficiency Gain Over Baseline (%)'].apply(lambda x: f"{x * .01:.0%}")
    df['179D Deduction per sqft ($)'] = df['179D Deduction per sqft ($)'].apply(lambda x: f"${x:,.2f}")
    df['Total 179D Deduction ($)'] = df['Total 179D Deduction ($)'].apply(lambda x: f"${x:,.0f}")
    return df

# Define function to generate the export
def gen_export(meta_orig, inc):
    export_data = BytesIO()
    meta = format_metadata(meta_orig)
    meta_df = meta.T
    meta_df.reset_index(inplace = True)
    meta_df.columns = ['Variable', 'Value']
    incent_df = copy.deepcopy(inc)
    incent_df.reset_index(inplace = True)
    reports = {'Metadata' : meta_df, 
               'Incentive Data' : incent_df}
    with pd.ExcelWriter(export_data) as writer:
        workbook  = writer.book

        # Define a format for the headers
        header_format = workbook.add_format({'bold': True, 
                                             'bg_color': '#006400', 
                                             'font_color': 'white', 
                                             'text_wrap': True})
        for title, report in reports.items():
            if title == 'Incentive Data':
                currency_format = workbook.add_format({'num_format': '$#,##0'})
            report.to_excel(writer, sheet_name = title, startrow = 1, header = False, index = False)

            worksheet = writer.sheets[title]

            num_rows, num_cols = report.shape

            column_settings = [{'header': col, 'header_format': header_format} for col in report.columns]

            worksheet.add_table(0, 0, num_rows, num_cols - 1, {'columns': column_settings})
            
            # Set the width of columns (adjust the width as needed)
            for i, col in enumerate(report.columns):
                col_width = max(report[col].astype(str).apply(len).max(), len(col)) + 2
                worksheet.set_column(i, i, col_width)

            # Write header row separately with original formatting
            for col_num, col_name in enumerate(report.columns):
                worksheet.write(0, col_num, col_name, header_format)

            # Write cell values with appropriate formatting
            for row in range(1, report.shape[0] + 1):
                for col in range(report.shape[1]):
                    value = report.iloc[row - 1, col]
                    if title == 'Incentive Data':
                        worksheet.write(row, col, value, currency_format)
                    else:
                        worksheet.write(row, col, value)
    workbook = export_data.getvalue()
    return workbook