#crontab to run every weekday at 4
import requests
import os
import urllib2 #used for parsing the text file
import xlsxwriter
import time
from bs4 import BeautifulSoup
import unittest
import lxml
# Make a directory with all the downloaded files in it, then go through directory and make csv.

url_lookup = {}

def main():
    current = str((time.strftime("%m_%d_%Y")))
    os.makedirs("data"+"_"+current)
    urlRetriever()
    csvMaker()



def urlRetriever():
    r = requests.get('https://www.sec.gov/cgi-bin/browse-edgar?company=&CIK=&type=S-1&owner=include&count=100&action=getcurrent')
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
            url_lookup[accessionnumber] = url.split(".txt")[0]+("-index.htm")
            if not alreadyArchived(accessionnumber):
                accessionnumbersfile.write(accessionnumber+"\n")
                downloadTextFileFromUrl(url,accessionnumber)

    f.close()
    accessionnumbersfile.close()
    os.remove("browse.txt")


def downloadTextFileFromUrl(url,id):
    #id will act as file name for the dir
    current = str((time.strftime("%m_%d_%Y")))
    data_folder = "data"+"_"+current+"/"
    f = open(data_folder+id+".txt","w")
    response = urllib2.urlopen(url)
    f.write(response.read())
    f.close()
    #print response.read()
    #raw_input()




def alreadyArchived(num):
    with open("accessionnumbers.txt","r") as f:
        for line in f:
            if num in line:
                #print "already there \n"
                return True

        return False

def csvMaker():
    """This function will go through the data/ directory, rip out all relevant fields, and put them in a spreadsheet
    Fields that are currently relevant:
     Company name DONE
    Address DONE
    Tel DONE
    CEO and any other named officers.
    Advisors - bank, PE sponsor, any others, with details.
    Date of filing DONE
    $ size of intended raise
    Sector
    Size of co    -   pro-forma market cap
    # employees"""
    current = str((time.strftime("%m_%d_%Y")))
    workbook = xlsxwriter.Workbook(current+".xlsx")
    worksheet = workbook.add_worksheet()
    fields = ["Type","Date of Filing", "Company Conformed Name", "Sector", "Street", "City", "State", "Zip", "Telephone"
        ,"Link","Offering Amount", "Chief Executive Officer", "Underwriters"]
    for i in range(0,len(fields)):
        worksheet.write(0,i,fields[i])

    directoryCrawler(worksheet)
    workbook.close()

def directoryCrawler(book):
    row = 1
    col = 0
    current_time = str((time.strftime("%m_%d_%Y")))
    data_folder = "data"+"_"+current_time
    for file in os.listdir(os.getcwd()+"/"+data_folder):
        with open(os.getcwd()+"/"+data_folder+"/"+file,"r") as f:
            datalist = dataParser(f)
            if datalist[0] != "S-1" or hasNumbers(datalist[6]): #This leaves out S-1/A and international companies
                print datalist[2]
                #continue
            else:
                for i in datalist:
                    book.write(row,col,i)
                    col = col + 1
                row = row + 1
                col = 0

def hasNumbers(pair):
    return any(i.isdigit() for i in pair)

def dataParser(file):
    """This function will return an array of information it gathers from the text file"""
    retlist = []
    fileCopy = file
    soup = BeautifulSoup(fileCopy,"lxml")
    tableParser(soup)
    key = file.name.split("/")[6].strip(".txt")
    banks = ["credit suisse","deutsche bank","goldman sachs","j.p. morgan","morgan stanley"]
    bankstring = ""
    businessaddress = False
    sectorBool = False
    for line in file:
        if "SUBMISSION TYPE" in line:
            retlist.append((line.split(":")[1]).lstrip("\t").rstrip("\n"))
        elif any(b in line for b in banks):
            print "BANKS"
        elif "UNDERWRITERS" in line:
            bankstring = line
        elif "COMPANY CONFORMED NAME" in line:
            retlist.append((line.split(":")[1]).lstrip("\t").rstrip("\n"))
        elif "STANDARD INDUSTRIAL CLASSIFICATION" in line:
            retlist.append((line.split(":")[1]).lstrip("\t").rstrip("\n"))
            sectorBool = True
        elif "BUSINESS ADDRESS" in line:
            businessaddress = True
        elif "STREET 1" in line and businessaddress:
            if not sectorBool:
                retlist.append("") #some forms won't have a sector, so this will clean that up, so as not to mess with spreadsheet
            retlist.append((line.split(":")[1]).lstrip("\t").rstrip("\n"))
        elif "CITY" in line and businessaddress:
            retlist.append((line.split(":")[1]).lstrip("\t").rstrip("\n"))
        elif "STATE" in line and businessaddress:
            retlist.append((line.split(":")[1]).lstrip("\t").rstrip("\n"))
        elif "ZIP" in line and businessaddress:
            retlist.append((line.split(":")[1]).lstrip("\t").rstrip("\n"))
        elif "BUSINESS PHONE" in line and businessaddress:
            number = (line.split(":")[1]).lstrip("\t").rstrip("\n")
            telephoneNumber = ""
            for i in number:
                if i.isdigit():
                    telephoneNumber = telephoneNumber + i
            if (len(telephoneNumber) == 10):
                telephoneNumber = telephoneNumber[0:3]+"-"+telephoneNumber[3:6]+"-"+telephoneNumber[6:10]
            elif (len(telephoneNumber) == 11):
                telephoneNumber = telephoneNumber[0] + "-"+ telephoneNumber[1:4] + "-" + \
                                  telephoneNumber[4:7] + "-" + telephoneNumber[7:11]
            elif (len(telephoneNumber) == 12):
                telephoneNumber = telephoneNumber[0:2] + "-" + telephoneNumber[2:5] + "-" + \
                                  telephoneNumber[5:8] + "-" + telephoneNumber[8:12]
            else:
                telephoneNumber = telephoneNumber[0:3] + "-" + telephoneNumber[3:6] + "-" + \
                                  telephoneNumber[6:9] + "-" + telephoneNumber[9:13]
            retlist.append(telephoneNumber)
        elif "MAIL ADDRESS" in line:
            businessaddress = False
            continue
        elif "FILED AS OF DATE" in line:
            date = (line.split(":")[1]).lstrip("\t").rstrip("\n")
            date = date[4:6] + "/" + date[6:8] + "/" + date[0:4]
            retlist.append(date)
        else:
            continue
    try:
        url = url_lookup[key]
    except KeyError, e:
        return retlist
    retlist.append(url)
    retlist.append(bankstring)
    return retlist


def tableParser(soup):
    bankstring = ''
    banks = ["credit suisse", "deutsche bank", "goldman sachs", "j.p. morgan", "morgan stanley", "stifel"]
    table = soup.find(class_ = 'dataframe')
    for row in table.find_all('tr')[1:]:
        col = row.find_all('td')
        for i in col:
            for b in banks:
                if i.string().strip().lower() == b:
                    bankstring = bankstring + i.string().strip()

    print bankstring


class TableParserTestCase(unittest.TestCase):

    def test_test(self):
        self.assertTrue(True)

    def test_TableParser(self):
        f = open("/Users/JAlbers/Projects/S-1scraper/TestData/0001193125-17-216619.txt")
        soup = BeautifulSoup(f,'lxml')
        tableParser(soup)




if __name__ == "__main__":
    unittest.main()
    #main()

