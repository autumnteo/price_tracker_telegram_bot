# lambda_selenium_bot

`@price_checkerr_bot` is a telegram bot that tracks scrapes websites and sends you a message once the item's price is within your budget. 

The webpage that was tracked in this project is a [Nintendo Switch sold on Amazon](https://www.amazon.com/Nintendo-32GB-Switch-Gray-Controllers/dp/B07YFKM7N6/ref=sr114?dchild=1&keywords=switch&qid=1596442560&sr=8-14) (But you can of course change it to whatever website/item you want to track). Since Amazon's webpage uses Javascript to dynamically generate the content, [Selenium](https://selenium-python.readthedocs.io/), and Python, was used as the webscraper. <br>
The webscraper is hosted on [AWS Lambda](https://aws.amazon.com/lambda/) where it scrapes the webpage every minute and informs you: 
1. Once the item is below your target price
2. Of the item's price everyday at Noon (as sort of a sanity check that the webscraper is still working)
3. If something goes with the webscraper

It will not message you otherwise.

This readme will NOT focus on how to develop the script. <br> Instead, it focuses on how to host your Python Selenium script on AWS Lambda if you are using a WINDOWS machine.


