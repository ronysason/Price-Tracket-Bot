import json
import requests
import re
# import os
from bs4 import BeautifulSoup
from telegram.ext import Updater, CommandHandler


def price_check(url, attribute, attr_val):
    content = requests.get(url)
    soup = BeautifulSoup(content.text, 'html.parser')
    price = soup.find(attribute, attr_val)
    return get_price_from_str(price.get_text())


def get_price_from_str(s):
    return float(re.sub("[^0-9.]", "", s))


class ItemsManager:
    domain_attributes = {
        "www.terminalx.com": ('span', {"class": "price"}),
        "www.nike.com": ('div', {"class": "product-price"}),
        "www.adikastyle.com": ('span', {"class": "price"})
    }

    def get_domain(self, url):
        return url.split("//")[-1].split("/")[0]

    def add_item(self):
        item_url = input("Enter item link:")
        item_target_price = int(input("Enter item target price:"))

        with open('data.json', 'r') as fp:
            data = json.load(fp)

        domain = self.get_domain(item_url)
        if domain in self.domain_attributes:
            data[item_url] = item_target_price

        with open('data.json', 'w') as fp:
            json.dump(data, fp)

        print(f"{item_url} added to list with target price: {item_target_price}")

    def check_target_price(self, url):
        domain = self.get_domain(url)
        attribute = self.domain_attributes[domain][0]
        attr_val = self.domain_attributes[domain][1]
        return price_check(url, attribute, attr_val)

    def check_items_in_list(self):
        with open('data.json', 'r') as fp:
            data = json.load(fp)

        result = []
        for x in data.keys():
            cur_price = self.check_target_price(x)
            if cur_price <= data[x]:
                result.append(x + " current price: ₪" + str(cur_price) + ", target price: ₪" + str(data[x]))

        return result


# Sends the items that their current price is equal or lower than their target price
def run(update, context):
    chat_id = update.message.chat_id
    messages = ItemsManager().check_items_in_list()

    for m in messages:
        context.bot.send_message(chat_id=chat_id, text=m)


def main():
    updater = Updater("TOKEN", use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('run', run))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
