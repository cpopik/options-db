import pandas
import requests

def main():

	url = "http://www.biopharmcatalyst.com/fda-calendar/"
	response = requests.get(url).text.encode('ascii', 'ignore')

	df = pandas.read_html(response)[0]

	writer = pandas.ExcelWriter('output.xlsx')
	df.to_excel(writer,'Sheet1')
	writer.save()

main()