import requests
from lxml import html

# Send a GET request to the webpage
url = 'https://my-calend.ru/holidays'
response = requests.get(url)

# Parse the HTML content
tree = html.fromstring(response.content)

# Extract all <li> elements matching the XPath
li_elements = tree.xpath('/html/body/div[1]/main/div[1]/article/section[1]/ul/li')

# Create a dictionary to store input value as key and corresponding li_element as value
sorted_li_elements_dict = {}

# Iterate through each <li> element and extract the input value
for li_element in li_elements:
    input_value = li_element.xpath('./form/input[@type="hidden"]/@value')
    if input_value:
        input_value_int = int(input_value[0])
        sorted_li_elements_dict[input_value_int] = li_element

# Sort the dictionary by input value
sorted_li_elements_dict = dict(sorted(sorted_li_elements_dict.items()))

# Now you have the sorted dictionary
for input_value, li_element in sorted_li_elements_dict.items():
    # Do whatever you want with each input_value and li_element
    print(f"Input Value: {input_value}")
    print(html.tostring(li_element, pretty_print=True))