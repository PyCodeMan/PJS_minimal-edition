from html.parser import HTMLParser
import urllib.request as ureq
from urllib.parse import urljoin


class MyHTMLParser(HTMLParser):
    def __init__(self, tag, class_name, start_index, end_index, base_url):
        super().__init__()
        self.tag = tag
        self.class_name = class_name
        self.data = ""
        self.target_data = []
        self.target_links = []
        self.current_index = 0
        self.start_index = start_index
        self.end_index = end_index
        self.base_url = base_url
        self.found_start_tag = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == self.tag and 'class' in attrs and attrs['class'] == self.class_name:
            self.current_index += 1
            self.found_start_tag = True
            if self.current_index >= self.start_index and self.current_index <= self.end_index:
                self.data = ""

        if self.found_start_tag and self.current_index == self.end_index and tag == 'a':
            href = attrs.get('href')
            if href:
                self.target_links.append(urljoin(self.base_url, href))

    def handle_data(self, data):
        if self.found_start_tag and self.current_index >= self.start_index and self.current_index <= self.end_index:
            self.data += data

    def handle_endtag(self, tag):
        if self.found_start_tag and tag == self.tag:
            if self.current_index >= self.start_index and self.current_index <= self.end_index:
                self.target_data.append(self.data)
                self.found_start_tag = False
                self.data = ""

    def get_target_data(self):
        return self.target_data, self.target_links


def scrape(url, tag, class_, start_index, end_index):
    with ureq.urlopen(url) as response:
        parser = MyHTMLParser(tag, class_, start_index, end_index, url)
        parser.feed(response.read().decode('utf-8'))

    data, links = parser.get_target_data()
    texts = ''
    for element in data:
        texts += element

    return texts.replace('  ', '').replace('\n\n\n\n', ''), links


def parsing():
    text = ''
    for i in range(1, 6):
        freelance_text, freelance_links = scrape('https://freelance.ru/project/search/pro?c=&c%5B%5D=116&c%5B%5D=4&q=&m=or&e=&a=0&a=1&v=0&f=&t=&o=0&o=1&b=', 'a', 'description', i, i)
        link = freelance_links.pop() if freelance_links else None
        text += f'{freelance_text}\n\n, link: {link if link else ""}\n\n\n'
    return text.replace('\n,', '')


if __name__ == '__main__':
    print(parsing())
