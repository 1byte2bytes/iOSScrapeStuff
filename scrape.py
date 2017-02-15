import scrapy

from scrapy.selector import HtmlXPathSelector

class iOSRelease():
    device = ""
    release_date = ""
    download = ""
    size = ""
    release_type = ""
    prereq_release = ""

def getNextRelease(currentRelease):
    release = currentRelease.split(",")
    devices = ["iPod", "iPhone", "iPad"]
    device = ""
    for letter in release[0]:
        try:
            int(letter)
            index = release[0].index(letter)
            device = release[0][:index]
            release[0] = release[0][index:]
            break
        except Exception as e:
            pass

    if int(release[1]) < 4:
        release[1] = str(int(release[1]) + 1)
    elif int(release[0]) < 12:
        release[0] = str(int(release[0]) + 1)
        release[1] = "0"
    else:
        release[0] = "0"
        release[1] = "0"
        if devices.index(device)+1 > len(devices):
            return ""
        else:
            return "{}{},{}".format(devices[device.index(device)+1], release[0], release[1])

    return "{}{},{}".format(device, release[0], release[1])


class QuotesSpider(scrapy.Spider):
    handle_httpstatus_list = [404]
    name = "quotes"
    start_urls = [
        'https://ipsw.me/otas/iPod1,1',
    ]

    def parse(self, response):
        currentRelease = response.url.split("/")
        currentRelease = currentRelease[len(currentRelease)-1]
        nextRelease = getNextRelease(currentRelease)
        print("---=========---")
        print("WORKING ON RELEASE ", currentRelease)
        print("---=========---")
        if response.status != 200:
            if nextRelease == "":
                return
            else:
                next_page = response.urljoin('https://ipsw.me/otas/' + nextRelease)
                yield scrapy.Request(next_page, callback=self.parse)
        sel = response.selector
        for tr in sel.css("table>tr"):
            print(tr)
            row = []
            row.append(currentRelease)

            for td in tr.xpath('td'):
                rowContents = ' '.join(td.extract().strip().split())
                rowText = ""
                if rowContents.startswith("<td> <a"):
                    rowText = td.xpath("a/text()").extract()
                else:
                    rowText = td.xpath("text()").extract()
                rowText = ' '.join(rowText[0].strip().split())
                row.append(rowText)

            if len(row) != 7:
                print("Mismatched array sizing")
            else:
                yield {
                    "device": row[0],
                    "firmware": row[1],
                    "release_date": row[2],
                    "download": row[3],
                    "size": row[4],
                    "release_type": row[5],
                    "prerequisites": row[6],
                }

        if nextRelease == "":
            return
        else:
            next_page = response.urljoin('https://ipsw.me/otas/' + nextRelease)
            yield scrapy.Request(next_page, callback=self.parse)