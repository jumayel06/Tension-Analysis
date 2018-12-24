'''
This class processes interview transcripts and generates question-answer pairs
NOTE: The pre processing requires a timestamp just before the beginning of a conversation. Some of the transcripts have
the timestamps, some don't. In case, a transcript doesn't have the timestamp, it is required to put the timestamp
manually there in order to use the following procedure
'''

from packages import *

class Process:
    def __init__(self, corpus):
        with open(corpus, "rb") as docx_file:
            self.html = mammoth.convert_to_html(docx_file).value

        self.processed_html = ""
        self.ques_ans = []

    def process_html(self):
        soup = BeautifulSoup(self.html, 'html.parser')
        paragraphs = soup.find_all('p')
        initial_time_index = -1

        for i in range(1, len(paragraphs)):
            try:
                if paragraphs[i].get_text().split()[0].count(':') == 2:
                    initial_time_index = i
                    break
            except:
                continue

        for i in range(initial_time_index + 1, len(paragraphs)):
            if paragraphs[i].get_text().split()[0].count(':') == 2:
                continue
            else:
                self.processed_html += str(paragraphs[i])

    def extract_ques_ans(self):
        soup = BeautifulSoup(self.processed_html, 'html.parser')

        for paragraph in soup.find_all('p'):
            if paragraph.get_text().split()[0].count(':') == 2:
                paragraph.extract()

        paragraphs = soup.find_all('p')
        checker = []

        for paragraph in paragraphs:
            if paragraph.find('strong') != None:
                checker.append(1)
            else:
                checker.append(0)

        expected = 1
        temp_list = []
        for i in range(len(paragraphs)):
            if checker[i] == expected:
                temp_list.append(paragraphs[i].get_text())
                expected ^= 1
            else:
                temp_list[len(temp_list) - 1] = temp_list[len(temp_list) - 1] + ' ' + paragraphs[i].get_text()

        for i in range(0,len(temp_list),2):
            ques = temp_list[i].replace(temp_list[i].split()[0], '').strip()
            if i + 1 == len(temp_list):
                ans = ''
            else:
                ans = temp_list[i + 1].replace(temp_list[i + 1].split()[0], '').strip()

            self.ques_ans.append((ques, ans))

        return self.ques_ans