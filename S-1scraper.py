#crontab to run every weekday at 4
import requests
import os
import urllib2 #used for parsing the text file
#TODO incorporate dates? Or check if the accessionnumber is already there then ignore
# Make a directory with all the downloaded files in it, then go through directory and make csv.

def main():
    if not (os.path.exists("data")):
        os.makedirs("data")
    urlRetriever()
    csvMaker()



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
        if "/Archives" in line and ".txt" in line:  # and ".htm" in line: #attempt to reduce errors that may occur is company has .txt in the filing
            urlarg = line.split("href=\"")[2].partition("\"")[0]  # strips out .txt expression from the get request
            url = "https://www.sec.gov" + urlarg
            accessionnumber = urlarg.rpartition("/")[2].split(".txt")[0]
            if not alreadyArchived(accessionnumber):
                accessionnumbersfile.write(accessionnumber+"\n")
                downloadTextFileFromUrl(url,accessionnumber)

    f.close()
    accessionnumbersfile.close()
    os.remove("browse.txt")


def downloadTextFileFromUrl(url,id):
    #id will act as file name for the dir
    f = open("data/"+id+".txt","w")
    response = urllib2.urlopen(url)
    f.write(response.read())
    #print response.read()
    #raw_input()




def alreadyArchived(num):
    with open("accessionnumbers.txt","r") as f:
        for line in f:
            if num in line:
                print "already there \n"
                return True

        return False


if __name__ == "__main__":
    main()

