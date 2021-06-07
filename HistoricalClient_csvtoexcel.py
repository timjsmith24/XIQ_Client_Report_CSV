from __future__ import division
import csv
import os
import datetime
import xlsxwriter
import argparse
from pprint import pprint
import pandas as pd

parser = argparse.ArgumentParser()

parser.add_argument('sitename', help = 'The name of the site the report will be generated for with "quotes" around it.')
parser.add_argument('filename', help = 'The csv filename: it must be in the same directory as this script')

args = parser.parse_args()

sitename = '{}'.format(args.sitename)
filename = '{}'.format(args.filename)

PATH = os.path.dirname(os.path.abspath(__file__))


def csv_import(filename):
    with open(filename, 'r') as file:
        reader = csv.reader(file, delimiter=',')
        # remove header line from CSV
        next(reader)
        next(reader)
        loc_params = next(reader)
        # Build list of location dictionaries
        client_list = []
        for row in reader:
            # location dictionary
            data = {}
            for x in range(len(loc_params)):
                # for each location parameters add key and value to dictionary
                data[loc_params[x]] = str(row[x])
            client_list.append(data)
        return client_list

print('gathering data from csv')
client_list = csv_import(filename)
print('processing data')

df = pd.DataFrame(client_list)
del df['client_ip']
del df['associate_vlan']
del df['client_host_name']
del df['client_os_name']
del df['bssid']

data = df.to_dict('index')
monthlist = []
yearlist = []
timelist = []
parent = {}
child = {}
for row in data.values():
    if row['location'] not in parent:
        parent[row['location']] = []
    if row['sublocation'] not in parent[row['location']]:
        parent[row['location']].append(row['sublocation'])
    if row['sublocation'] not in child:
        child[row['sublocation']]={}
        child[row['sublocation']]['session_count'] = 0
        child[row['sublocation']]['unique_count'] = []
        child[row['sublocation']]['connected_time'] = 0
    child[row['sublocation']]['session_count'] += 1
    child[row['sublocation']]['unique_count'].append(row['client_mac'])
    start_time = row['start_time']
    timelist.append(start_time)
    #start_time = datetime.datetime.strptime(start_time, '%m/%d/%y %H:%M')
    start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
    monthlist.append(start_time.strftime('%B'))
    yearlist.append(start_time.strftime('%Y'))
    end_time = row['end_time']
    #end_time = datetime.datetime.strptime(end_time, '%m/%d/%y %H:%M')
    end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
    connected_time = (end_time - start_time).total_seconds()
    child[row['sublocation']]['connected_time'] += int(connected_time)

for loc in child:
    set_list = set(child[loc]['unique_count'])
    child[loc]['unique_count'] = len(set_list)

monthset = set(monthlist)
monthset = sorted(monthset, key=lambda monthset: datetime.datetime.strptime(monthset, "%B"))
yearset = set(yearlist)
yearset = sorted(yearset, key=lambda yearset: datetime.datetime.strptime(yearset, "%Y"))
monthstr = ''
monthstr += "{} -".format(monthset[-1])
monthstr += " {}".format(yearset[-1])

# Used for start and end times off to the side of report
timeset = set(timelist)
#timeset = sorted(timeset, key=lambda timeset: datetime.datetime.strptime(timeset, '%m/%d/%y %H:%M'))
timeset = sorted(timeset, key=lambda timeset: datetime.datetime.strptime(timeset, '%Y-%m-%d %H:%M:%S'))


print("creating excel report")
excelname = os.path.splitext(filename)[0]
workbook = xlsxwriter.Workbook('{}.xlsx'.format(excelname))
workbook.set_size(1600, 2000)
worksheet = workbook.add_worksheet('Report')
# Widen the first column to make the text clearer.
worksheet.set_column('A:A', 20.5)
worksheet.set_column('B:F', 14.8)
worksheet.set_row(1, 13)
worksheet.set_row(2, 13)
worksheet.set_row(3, 13)
worksheet.set_row(4, 13)
worksheet.set_row(5, 13)
worksheet.set_row(6, 13)

# Create a format to use in the merged range.
merge_format = workbook.add_format({
    'align': 'center',
    'valign': 'vcenter',
    'fg_color': '5C5B5A',
    'font_color': 'white',
    'font_size': 14})

Label_format = workbook.add_format({
    'align': 'center',
    'valign': 'vcenter',
    'fg_color': '5C5B5A',
    'font_color': 'white',
    'font_size': 12,
    'text_wrap': 1
})
header_format = workbook.add_format({
    'align': 'center',
    'valign': 'vcenter',
    'fg_color': '5C5B5A',
    'font_color': 'white',
    'font_size': 10
})
centered_hyp_format = workbook.add_format({
    'align': 'center',
    'color': '#0000EE',
    'underline': 1,
    'font_size': 10
})
bold_format = workbook.add_format({
    'align': 'center',
    'font_size': 10,
    'bold': 1
})
#center_format = workbook.add_format({
#    'align': 'center'
#})
bottom_border_title = workbook.add_format({
    'align': 'center',
    'font_size': 10,
    'underline': 1
})
main_site_format = workbook.add_format({
    'bold':1,
    'bottom':1,
    'font_size': 10,
    'bottom_color': '#0000EE',
    'align': 'right',
    'num_format': '#,###,##0'
})
main_site_location_format = workbook.add_format({
    'bold':1,
    'bottom':1,
    'font_size': 10,
    'bottom_color': '#0000EE',
    'align': 'left'
})
sub_site_format = workbook.add_format({
    'align':'right',
    'font_size': 10,
    'num_format': '#,###,##0'
})
sub_site_location_format = workbook.add_format({
    'align':'left',
    'font_size': 10
})
bold_only_format = workbook.add_format({
    'bold': 1
})
# Merge cells on row 1.
worksheet.merge_range('A1:E1', '{} - WiFi Statistics Summary Report'.format(monthstr), merge_format)
worksheet.merge_range('A2:A7','{}'.format(sitename),Label_format)
worksheet.merge_range('B2:E2','')
worksheet.write_url('B2', 'http://www.library.ca.gov/Content/pdf/services/toLibraries/SurveyInstructions2017-18.pdf', centered_hyp_format)
worksheet.write('B4', 'Client User Summary',bold_format)
worksheet.write('B5', 'Number of Sessions', bottom_border_title)
worksheet.write('C5', 'Number of Users', bottom_border_title)
worksheet.write('D5', 'Sum of Time (hours)', bottom_border_title)
worksheet.write('E5', 'Sum of Time (minutes)', bottom_border_title)
# Build Table header
worksheet.write('A8', 'Locations', header_format)
worksheet.write('B8', 'Number of Sessions', header_format)
worksheet.write('C8', 'Number or Users', header_format)
worksheet.write('D8', 'Sum of Time (hours)', header_format)
worksheet.write('E8', 'Sum of Time (minutes)', header_format)

# Print Start and End times off to the side of the Report
worksheet.write('G3', 'Time Stamps from Client Summary', bold_only_format)
worksheet.write('G4', 'Start time:')
worksheet.write('H4', ' {}'.format(timeset[0]))
worksheet.write('G5', 'End time:')
worksheet.write('H5',' {}'.format(timeset[-1]))

cursor_line = 8
main_site_list = []
for name, locations in sorted (parent.items()):
    main_session_count = 0
    main_unique_count = 0
    main_connected_time = 0
    for site in locations:
        main_session_count += child[site]['session_count']
        main_unique_count += child[site]['unique_count']
        main_connected_time += child[site]['connected_time']
    cursor_line += 1
    main_site_list.append(cursor_line)
    worksheet.write('A{}'.format(cursor_line), "    {}".format(name), main_site_location_format)
    worksheet.write('B{}'.format(cursor_line), main_session_count, main_site_format)
    worksheet.write('C{}'.format(cursor_line), main_unique_count, main_site_format)
    worksheet.write('D{}'.format(cursor_line), round(main_connected_time/3600), main_site_format)
    worksheet.write('E{}'.format(cursor_line), round(main_connected_time/60), main_site_format)
    for site in locations:
        cursor_line += 1
        worksheet.write('A{}'.format(cursor_line), "        {}".format(site), sub_site_location_format)
        worksheet.write('B{}'.format(cursor_line), child[site]['session_count'], sub_site_format)
        worksheet.write('C{}'.format(cursor_line), child[site]['unique_count'], sub_site_format)
        worksheet.write('D{}'.format(cursor_line), round(child[site]['connected_time']/3600), sub_site_format)
        worksheet.write('E{}'.format(cursor_line), round(child[site]['connected_time']/60), sub_site_format)
main_site_str = ''
for row in main_site_list:
    main_site_str += '<Column>{},'.format(row)
# Number of Sessions Total
mainb = main_site_str.replace('<Column>','B')
worksheet.write('B6', '=SUM({})'.format(mainb), sub_site_format)
# Number of Users Total
mainb = main_site_str.replace('<Column>','C')
worksheet.write('C6', '=SUM({})'.format(mainb), sub_site_format)
# Sum of Time (hours) Total
mainb = main_site_str.replace('<Column>','D')
worksheet.write('D6', '=SUM({})'.format(mainb), sub_site_format)
# Sum of Time (minutes) Total
mainb = main_site_str.replace('<Column>','E')
worksheet.write('E6', '=SUM({})'.format(mainb), sub_site_format)
workbook.close()
print("completed")
