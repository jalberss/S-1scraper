#crontab to run every weekday at 4
import requests
import os
import urllib2 #used for parsing the text file


def main():
    urlRetriever()

def urlRetriever():
    r = requests.get('https://www.sec.gov/cgi-bin/browse-edgar?company=&CIK=&type=S-1&owner=include&count=40&action=getcurrent')
    accessNumberRetriever(r.text)

def accessNumberRetriever(text):
    #f = open("workfile.txt","w")
    #f.write(text)
    #f.close()
    f = open("workfile.txt","r") #used so that lines can be accessed by array index
    for line in f:
        if "Accession Number" in line:
            fileRetrievalByAccessionNumber(line.split("Accession Number: ")[1].split(" &nbsp")[0]) # returns only the accession numbers
    f.close()

def fileRetrievalByAccessionNumber(accessionNumber):
    arg1 = accessionNumber.split('-')[0].lstrip("0")
    #arg1 = arg1.lstrip("0")#first 7 digits of the accession number, and strip leading zeros
    arg2 = accessionNumber.replace("-","")
    #arg2 is the full accessionnumber without dashes
    #example "https://www.sec.gov/Archives/edgar/data/1684506/000168450617000002/0001684506-17-000002.txt""
    url = "https://www.sec.gov/Archives/edgar/data/"+arg1+"/"+arg2+"/"+accessionNumber+".txt"
    print url
    raw_input()

if __name__ == "__main__":
    main()

