import requests
from bs4 import BeautifulSoup
import pandas as pd
from fake_useragent import UserAgent

# Define the URL and parameters
url = "https://www.amazon.com/s?k=guitar+cable"
ua = UserAgent(browsers=['Chrome'])
print(f"Fake Agents: {ua.random}")
# Send a GET request
response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})

# Check if the request was successful
if response.status_code != 200:
    print("Failed to retrieve the page")
    exit(1)

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(response.content, "html.parser")

# Find all product containers
product_containers = soup.find_all("div", {"class": "s-result-item"})

# Initialize lists to store product information
product_titles = []
product_prices = []
product_ratings = []

# Iterate over each product container
for container in product_containers:
    # Extract the product title
    title = container.find("h2", {"class": "a-size-base"}).text.strip()
    product_titles.append(title)

    # Extract the product price
    price = container.find("span", {"class": "a-price-whole"}).text.strip()
    product_prices.append(price)

    # Extract the product rating
    rating = container.find("span", {"class": "a-icon-alt"}).text.strip()
    product_ratings.append(rating)

# Create a pandas DataFrame to store the product information
df = pd.DataFrame({
    "Title": product_titles,
    "Price": product_prices,
    "Rating": product_ratings
})

# Print the DataFrame
print(df)