## Copy this code from the UPs  machine 
## code currently store data in to the Google sheet and send email alert when the price of the stock goes above the target price.

import gspread

gc = gspread.service_account(filename="pn-ups-tmp-sa.json")

spreadsheet = gc.open_by_key('1T_DkjFRMRhErDy4Z6drj9zlcucO1Q6WOEBqJ9qITpu4')
sheet = spreadsheet.worksheet('Sheet1')

sheet.append_row(['Hello', 'World1'])

print("Row added")
