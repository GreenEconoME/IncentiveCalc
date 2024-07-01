# Import dependencies
import pandas as pd
from io import BytesIO

# Define function to generate the export
def gen_export(meta, inc):
    export_data = BytesIO()
    with pd.ExcelWriter(export_data) as writer:
        meta.T.to_excel(writer, sheet_name = 'Metadata')
        inc.to_excel(writer, sheet_name = 'Incentive Data', index = False)
    workbook = export_data.getvalue()
    return workbook