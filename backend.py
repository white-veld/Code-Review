import requests
import re
from bs4 import BeautifulSoup as BS
from database import DataAccessObject


class Parser:
    headers = {
        "Accept": "*/*",
        "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, "
        "like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }
    url = "https://bgu.ru/student/timetable.aspx"
    dictionary = {}
    groups = []

    def get_groups(self) -> None:
        req = requests.get(self.url, headers=self.headers)
        soup = BS(req.content, 'lxml')
        groups_data = soup.find(class_="groups list-group shadow w-100")
        for i in groups_data:
            i_text = i.text
            i_href = i.get("href")
            self.dictionary[i_text] = i_href
        return

    def check_group(self, group) -> bool:
        if group in self.dictionary.keys():
            return True
        else:
            return False

    def parser(self, group):
        if self.check_group(group):
            new_url = self.url
            for i in self.dictionary.keys():
                if group == i:
                    new_url += self.dictionary[i]
            new_req = requests.get(new_url, headers=self.headers)
            new_soup = BS(new_req.content, 'lxml')
            lessons_data = new_soup.find(id="nav-ses-1").find_all("tr")
            check = True
            for group in self.groups:
                if group == group:
                    check = False
                    break
            list_lessons = {}
            if check:
                for item in lessons_data:
                    lessons_tds = item.find_all("td")
                    if len(lessons_tds) == 1:
                        start = lessons_tds[0].text
                        list_lessons[start] = None
                    else:
                        start = lessons_tds[0].text
                        discipline = lessons_tds[1].text
                        discipline = re.sub('([А-Я])', r' \1', discipline)
                        auditorium = lessons_tds[2].text
                        teacher = lessons_tds[3].text
                        if (len(list_lessons.keys()) != 0 and list_lessons[list(list_lessons.keys())[-1]] is
                                None):
                            list_lessons[list(list_lessons.keys())[-1]] = [
                                [start, discipline, auditorium, teacher]]
                        elif len(list_lessons.keys()) != 0:
                            list_lessons[list(list_lessons.keys())[-1]].append(
                                [start, discipline, auditorium, teacher])
                        else:
                            list_lessons['headers'] = [start, discipline, auditorium, teacher]
            self.groups.append(group)
            dao = DataAccessObject()
            for i in list_lessons.keys():
                if i == 'headers':
                    dao.create(None,
                               None,
                               list_lessons[i][0],
                               list_lessons[i][1],
                               list_lessons[i][2],
                               list_lessons[i][3])
                    continue
                if list_lessons[i] is None:
                    break
                for j in range(len(list_lessons[i])):
                    dao.create(group,
                               i,
                               list_lessons[i][j][0],
                               list_lessons[i][j][1],
                               list_lessons[i][j][2],
                               list_lessons[i][j][3])
            return dao.show_base(group)
        else:
            return 'Введи корректно название группы'
