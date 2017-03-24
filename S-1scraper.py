#crontab to run every weekday at 4
import requests
import os
import urllib2 #used for parsing the text file
#TODO incorporate dates? Or check if the accessionnumber is already there then ignore

def main():
    urlRetriever()

def urlRetriever():
    r = requests.get('https://www.sec.gov/cgi-bin/browse-edgar?company=&CIK=&type=S-1&owner=include&count=40&action=getcurrent')
    accessNumberRetriever(r.text)

def accessNumberRetriever(text):
    if not (os.path.exists("accessionnumbers.txt")):
        print "not here, create it"
        createfile = open("accessionnumbers.txt", "w")
        createfile.close()
    f = open("browse.txt","w")
    f.write(text)
    f.close()
    f = open("browse.txt","r") #used so that lines can be accessed by array index
    accessionnumbersfile = open("accessionnumbers.txt","a+")
    for line in f:
        if "Accession Number" in line:
            accessionnumbersfile.write(line.split("Accession Number: ")[1].split(" &nbsp")[0]+"\n") # returns only the accession numbers
    f.close()
    f = open("browse.txt", "r") # Got to start at the top again
    for line in f:
        if "/Archives" in line and ".txt" in line: # and ".htm" in line: #attempt to reduce errors that may occur is company has .txt in the filing
            urlarg = line.split("href=\"")[2].partition("\"")[0] #strips out .txt expression from the get request
            url = "https://www.sec.gov"+ urlarg
            downloadTextFileFromUrl(url)
    accessionnumbersfile.close()
    #raw_input()
    os.remove("browse.txt")
    os.remove("accessionnumbers.txt")


#def fileRetrievalByAccessionNumber(accessionNumber):
    #arg1 = accessionNumber.split('-')[0].lstrip("0")
    #arg1 = arg1.lstrip("0")#first 7 digits of the accession number, and strip leading zeros
    #arg2 = accessionNumber.replace("-","")
    #arg2 is often the full accessionnumber without dashes

    #example "https://www.sec.gov/Archives/edgar/data/1684506/000168450617000002/0001684506-17-000002.txt""
    #url = "https://www.sec.gov/Archives/edgar/data/"+arg1+"/"+arg2+"/"+accessionNumber+".txt"
    #downloadTextFileFromUrl(url)
    #print url

def downloadTextFileFromUrl(url):
    print url
    response = urllib2.urlopen(url)
    print response.read()
    raw_input()

if __name__ == "__main__":
    main()

