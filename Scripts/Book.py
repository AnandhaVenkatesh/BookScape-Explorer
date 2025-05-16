import mysql.connector
import requests
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

plt.style.use("ggplot")

# Connect to MySQL
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Venkat123",
    database="dummy",
    autocommit=True
)
mycursor = mydb.cursor()

# Create a books table
mycursor.execute("""
CREATE TABLE IF NOT EXISTS books (
    book_id VARCHAR(255) PRIMARY KEY,
    search_key VARCHAR(255),
    book_title VARCHAR(500),
    book_subtitle TEXT,
    book_authors TEXT,
    book_description TEXT,
    industryIdentifiers TEXT,
    text_readingModes BOOLEAN,
    image_readingModes BOOLEAN,
    pageCount INT,
    categories TEXT,
    language VARCHAR(20),
    imageLinks TEXT,
    ratingsCount INT,
    averageRating DECIMAL(3,2),
    country VARCHAR(10),
    saleability VARCHAR(100),
    isEbook BOOLEAN,
    amount_listPrice DECIMAL(10,2),
    currencyCode_listPrice VARCHAR(10),
    amount_retailPrice DECIMAL(10,2),
    currencyCode_retailPrice VARCHAR(10),
    buyLink TEXT,
    year TEXT,
    publisher TEXT
)
""")
#mycursor.execute("alter table books add column is_Ebook BOOLEAN;")
#mycursor.execute("DROP TABLE IF EXISTS books")

# Function to fetch and insert books into MySQL
def get_and_store_books(query, max_results=39):
    api_key = 'AIzaSyDn8K9RO4OgmFbjINon5Pk67pglsP610VE'
    url = f'https://www.googleapis.com/books/v1/volumes?q={query}&maxResults={max_results}&key={api_key}'

    response = requests.get(url)

    if response.status_code == 200:
        books = response.json().get('items', [])
        for book in books:
            volume_info = book.get('volumeInfo', {})
            sale_info = book.get('saleInfo', {})
            access_info = book.get('accessInfo', {})

            book_id = book.get('id', 'unknown')
            search_key = query
            book_title = volume_info.get('title', 'No title available')
            book_subtitle = volume_info.get('subtitle', None)
            book_authors = ', '.join(volume_info.get('authors', [])) or None
            book_description = volume_info.get('description', None)
            industryIdentifiers = ', '.join([id['identifier'] for id in volume_info.get('industryIdentifiers', [])]) or None
            text_readingModes = access_info.get('textToSpeechPermission') != 'NONE'
            image_readingModes = 'image' in access_info.get('readingModes', {})
            pageCount = volume_info.get('pageCount', None)
            categories = ', '.join(volume_info.get('categories', [])) or None
            language = volume_info.get('language', None)
            imageLinks = volume_info.get('imageLinks', {}).get('thumbnail', None)
            ratingsCount = volume_info.get('ratingsCount', None)
            averageRating = volume_info.get('averageRating', None)
            country = sale_info.get('country', None)
            saleability = sale_info.get('saleability', None)
            isEbook = sale_info.get('isEbook', False)
            amount_listPrice = sale_info.get('listPrice', {}).get('amount', None)
            currencyCode_listPrice = sale_info.get('listPrice', {}).get('currencyCode', None)
            amount_retailPrice = sale_info.get('retailPrice', {}).get('amount', None)
            currencyCode_retailPrice = sale_info.get('retailPrice', {}).get('currencyCode', None)
            buyLink = sale_info.get('buyLink', None)
            year = volume_info.get('publishedDate', '')[:4]
            publisher = volume_info.get('publisher', None)

            insert_query = """
    INSERT INTO books (
        book_id, search_key, book_title, book_subtitle, book_authors, book_description,
        industryIdentifiers, text_readingModes, image_readingModes, pageCount, categories,
        language, imageLinks, ratingsCount, averageRating, country, saleability, isEbook,
        amount_listPrice, currencyCode_listPrice, amount_retailPrice, currencyCode_retailPrice,
        buyLink, year, publisher
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        search_key = VALUES(search_key),
        book_title = VALUES(book_title),
        book_subtitle = VALUES(book_subtitle),
        book_authors = VALUES(book_authors),
        book_description = VALUES(book_description),
        industryIdentifiers = VALUES(industryIdentifiers),
        text_readingModes = VALUES(text_readingModes),
        image_readingModes = VALUES(image_readingModes),
        pageCount = VALUES(pageCount),
        categories = VALUES(categories),
        language = VALUES(language),
        imageLinks = VALUES(imageLinks),
        ratingsCount = VALUES(ratingsCount),
        averageRating = VALUES(averageRating),
        country = VALUES(country),
        saleability = VALUES(saleability),
        isEbook = VALUES(isEbook),
        amount_listPrice = VALUES(amount_listPrice),
        currencyCode_listPrice = VALUES(currencyCode_listPrice),
        amount_retailPrice = VALUES(amount_retailPrice),
        currencyCode_retailPrice = VALUES(currencyCode_retailPrice),
        buyLink = VALUES(buyLink),
        year = VALUES(year),
        publisher = VALUES(publisher)
"""


            values = (
                book_id, search_key, book_title, book_subtitle, book_authors, book_description,
                industryIdentifiers, text_readingModes, image_readingModes, pageCount, categories,
                language, imageLinks, ratingsCount, averageRating, country, saleability, isEbook,
                amount_listPrice, currencyCode_listPrice, amount_retailPrice, currencyCode_retailPrice,
                buyLink, year, publisher
            )

            mycursor.execute(insert_query, values)

        print(f"{len(books)} books inserted successfully!")
    else:
        print(f"Error: {response.status_code} - {response.text}")


# Fetch and display books in Streamlit DataFrame
mycursor.execute("SELECT * FROM books")
book_records = mycursor.fetchall()
book_list = [list(book) for book in book_records]

columns = [
    'book_id', 'search_key', 'book_title', 'book_subtitle', 'book_authors',
    'book_description', 'industryIdentifiers', 'text_readingModes', 'image_readingModes',
    'pageCount', 'categories', 'language', 'imageLinks', 'ratingsCount',
    'averageRating', 'country', 'saleability', 'isEbook',
    'amount_listPrice', 'currencyCode_listPrice', 'amount_retailPrice', 'currencyCode_retailPrice',
    'buyLink', 'year', 'publisher'
]

book_df = pd.DataFrame(book_list, columns=columns)

col = st.sidebar.selectbox("Select a column",['Home page','First page','Queries page'])

st.write(col)

if col == "Home page":
    st.markdown("<h1 style='color: red;'>📚 BookScape Explorer</h1>", unsafe_allow_html=True)
    st.image("D:/Project/image.jpg", caption="Explore Your Favorite Books", use_container_width=True)

elif col == "First page":

    # Take user input
    getting_books = st.text_input("Enter a book name")

    # Button to trigger the fetch
    if st.button("Search and Fetch Books"):
        if getting_books.strip():  # check it's not empty
            get_and_store_books(getting_books)
            st.success(f"Books related to '{getting_books}' have been fetched and stored.")
        else:
            st.warning("Please enter a valid book name.")

    st.subheader("Books Data")
    st.dataframe(book_df)

elif col == "Queries page":
    st.subheader("Query Results")


    #st.dataframe(query)
    original_list = st.selectbox("Select a Queary",["1. Availability of eBooks vs Physical Books","2. Publisher with the Most Books Published",
                                                    "3. Publisher with Highest Average Rating","4. Top 5 Most Expensive Books by Retail Price",
                                                    "5. Books After 2010 with ≥ 500 Pages", "6. Books with > 20% Discount",
                                                    "7. Average Page Count: eBooks vs Physical", "8. Top 3 Authors with Most Books",
                                                    "9. List Publishers with More than 10 Books","10. Find the Average Page Count for Each Category",
                                                    "11. Retrieve Books with More than 3 Authors","12. Books with Ratings Count Greater Than the Average",
                                                    "13. Books with the Same Author Published in the Same Year","14. Books with a Specific Keyword in the Title",
                                                    "15. Year with the Highest Average Book Price","16. Count Authors Who Published 3 Consecutive Years",
                                                    "17. Authors Who Published in the Same Year Under Different Publishers","18. Average Retail Price of eBooks vs Physical Books",
                                                    "19. Books with Rating > 2 Standard Deviations from Average", "20. Publisher with Highest Average Rating (Only if >10 Books)"])

    if original_list == "1. Availability of eBooks vs Physical Books":
        st.write("Availability of eBooks vs Physical Books")
        mycursor.execute("SELECT isEbook, COUNT(*) AS total_books FROM books GROUP BY isEbook;")
        result = mycursor.fetchall()
        df = pd.DataFrame(result, columns=["isEbook", "Total Books"])
        df["isEbook"] = df["isEbook"].replace({1: "eBook",
                                                0: "Physical Book",
                                                True: "eBook",
                                                False: "Physical Book"})
        st.dataframe(df)

        st.write("Chart View")
        fig, ax = plt.subplots()
        ax.pie(df["Total Books"], labels=df["isEbook"], autopct="%1.1f%%", startangle=90)
        ax.axis("equal")
        st.pyplot(fig)


    elif original_list == "2. Publisher with the Most Books Published":
        st.write("Publisher with the Most Books Published")
        mycursor.execute("SELECT publisher, COUNT(*) AS total_books FROM books GROUP BY publisher ORDER BY total_books DESC LIMIT 1;")
        result = mycursor.fetchall()
        df_1 = pd.DataFrame(result, columns=["publisher","Most Books published"])
        df_1["publisher"] = df_1["publisher"].replace({1: "publisher list", True: "publisher list"})
        st.dataframe(df_1)

    elif original_list == "3. Publisher with Highest Average Rating":
        st.write("Publisher with Highest Average Rating")
        mycursor.execute("SELECT publisher, AVG(averageRating) AS avg_rating FROM books WHERE averageRating IS NOT NULL GROUP BY publisher ORDER BY avg_rating DESC LIMIT 1;")
        result = mycursor.fetchall()
        df_3 = pd.DataFrame(result, columns=["publisher","Average Rating"])
        df_3["publisher"] = df_3["publisher"].replace({1: "ratings", True: "ratings"})
        st.dataframe(df_3)

    elif original_list == "4. Top 5 Most Expensive Books by Retail Price":
        st.write("Top 5 Most Expensive Books by Retail Price")
        mycursor.execute("SELECT book_title, amount_retailPrice, currencyCode_retailPrice FROM books WHERE amount_retailPrice IS NOT NULL ORDER BY amount_retailPrice DESC LIMIT 5;")
        result = mycursor.fetchall()
        df_4 = pd.DataFrame(result, columns=["Book Title","Amount retail price","Currency Code"])
        df_4["Book Title"] = df_4["Book Title"].replace({1: "Book Title",
                                                         2: "Amount retail price",
                                                         3 : "Currency Code",
                                                          True: "Book Title",
                                                          True : "Amount retail price",
                                                          True: "Currency Code"})
        st.dataframe(df_4)

    elif original_list == "5. Books After 2010 with ≥ 500 Pages":
        st.write("Books After 2010 with ≥ 500 Pages")
        mycursor.execute("SELECT book_title, year, pageCount FROM books WHERE year > '2010' AND pageCount >= 500;")
        result = mycursor.fetchall()
        df_5 = pd.DataFrame(result, columns=["Book Title","Year","Page Count"])
        df_5["Book Title"] = df_5["Book Title"].replace({0: "Book Title",
                                                         1: "Year",
                                                         2: "Page Count",
                                                         True: "Book Title",
                                                         True: "Year",
                                                         True: "Page Count"})
        st.dataframe(df_5)
    elif original_list == "6. Books with > 20% Discount":
        st.write("Books with > 20% Discount")
        mycursor.execute("""SELECT book_title, amount_listPrice, amount_retailPrice,
                                    ROUND((amount_listPrice - amount_retailPrice)/amount_listPrice * 100, 2) AS discount_percent
                            FROM books
                            WHERE amount_listPrice > 0
                                AND (amount_listPrice - amount_retailPrice)/amount_listPrice >= 0.2;""")
        result = mycursor.fetchall()
        df_6 = pd.DataFrame(result, columns=["Book Title","Amount List Price","Amount Retail Price","Discount (%)"])
        df_6["Book Title"] = df_6["Book Title"].replace({0: "Book Title",
                                                         1: "Amount List Price",
                                                         2: "Amount Retail Price",
                                                         3: "Discount (%)",
                                                         True: "Book Title",
                                                         True: "Amount List Price",
                                                         True: "Amount Retail Price",
                                                         True: "Discount (%)"})
        st.dataframe(df_6)

    elif original_list == "7. Average Page Count: eBooks vs Physical":
        st.write("Average Page Count: eBooks vs Physical")
        mycursor.execute("SELECT isEbook, AVG(pageCount) AS avg_page_count FROM books WHERE pageCount IS NOT NULL GROUP BY isEbook;")
        result = mycursor.fetchall()
        df_7 = pd.DataFrame(result, columns=["isEbook","Average Page Count"])
        df_7["isEbook"] = df_7["isEbook"].replace({0: "Ebook",
                                                    1: "Physical",
                                                    True: "isEbook",
                                                    True: "Physical"})

        st.dataframe(df_7)

    elif original_list == "8. Top 3 Authors with Most Books":
        st.write("Top 3 Authors with Most Books")
        mycursor.execute("SELECT book_authors, COUNT(*) AS total_books FROM books GROUP BY book_authors ORDER BY total_books DESC LIMIT 3;")
        result = mycursor.fetchall()
        df_8 = pd.DataFrame(result, columns=["Boook Authors","Total Books"])
        st.dataframe(df_8)

    elif original_list == "9. List Publishers with More than 10 Books":
        st.write("List Publishers with More than 10 Books")
        mycursor.execute("SELECT publisher, COUNT(*) AS total_books FROM books GROUP BY publisher HAVING COUNT(*) > 10;")
        result = mycursor.fetchall()
        df_9 = pd.DataFrame(result, columns=["Publisher","Total Books"])
        st.dataframe(df_9)

    elif original_list == "10. Find the Average Page Count for Each Category":
        st.write("Find the Average Page Count for Each Category")
        mycursor.execute("SELECT categories, AVG(pageCount) AS avg_page_count FROM books WHERE pageCount IS NOT NULL GROUP BY categories;")
        result = mycursor.fetchall()
        df_10 = pd.DataFrame(result, columns=["Categories","Average Page Count"])
        st.dataframe(df_10)

    elif original_list == "11. Retrieve Books with More than 3 Authors":
        st.write("Retrieve Books with More than 3 Authors")
        mycursor.execute("SELECT book_title, book_authors FROM books WHERE LENGTH(book_authors) - LENGTH(REPLACE(book_authors, ',', '')) + 1 > 3;")
        result = mycursor.fetchall()
        df_11 = pd.DataFrame(result, columns=["Book Title","Book Authors"])
        st.dataframe(df_11)

    elif original_list == "12. Books with Ratings Count Greater Than the Average":
        st.write("Books with Ratings Count Greater Than the Average")
        mycursor.execute("""SELECT book_title, ratingsCount
                            FROM books
                            WHERE ratingsCount > (
                            SELECT AVG(ratingsCount)
                            FROM books
                            WHERE ratingsCount IS NOT NULL);
                            """)
        result = mycursor.fetchall()
        df_12 = pd.DataFrame(result, columns=["Book Title","Ratings Count"])
        st.dataframe(df_12)

    elif original_list == "13. Books with the Same Author Published in the Same Year":
        st.write("Books with the Same Author Published in the Same Year")
        mycursor.execute("SELECT book_authors, year, COUNT(*) AS book_count FROM books GROUP BY book_authors, year HAVING COUNT(*) > 1;")
        result = mycursor.fetchall()
        df_13 = pd.DataFrame(result, columns=["Book Authors","Year","Book Count"])
        st.dataframe(df_13)

    elif original_list == "14. Books with a Specific Keyword in the Title":
        st.write("Books with a Specific Keyword in the Title")
        mycursor.execute("SELECT book_title FROM books WHERE book_title LIKE 'Geography';")
        result = mycursor.fetchall()
        df_14 = pd.DataFrame(result, columns=["Book Title"])
        st.dataframe(df_14)

    elif original_list == "15. Year with the Highest Average Book Price":
        st.write("Year with the Highest Average Book Price")
        mycursor.execute("""SELECT year, AVG(amount_retailPrice) AS avg_price
                            FROM books
                            WHERE amount_retailPrice IS NOT NULL
                            GROUP BY year
                            ORDER BY avg_price DESC
                            LIMIT 1;""")
        result = mycursor.fetchall()
        df_15 = pd.DataFrame(result, columns=["Year","Average Price"])
        st.dataframe(df_15)

    elif original_list == "16. Count Authors Who Published 3 Consecutive Years":
        st.write("Count Authors Who Published 3 Consecutive Years")
        mycursor.execute("""SELECT COUNT(DISTINCT book_authors) AS authors_count
                            FROM (
                            SELECT book_authors, year
                            FROM books
                            GROUP BY book_authors, year
                            ) AS sub
                            GROUP BY book_authors
                            HAVING COUNT(DISTINCT year) >= 3;
                            """)
        result = mycursor.fetchall()
        df_16 = pd.DataFrame(result, columns=["Authors Count"])
        st.dataframe(df_16)

    elif original_list == "17. Authors Who Published in the Same Year Under Different Publishers":
        st.write("Authors Who Published in the Same Year Under Different Publishers")
        mycursor.execute("""SELECT book_authors, year, COUNT(DISTINCT publisher) AS publisher_count
                            FROM books
                            GROUP BY book_authors, year
                            HAVING COUNT(DISTINCT publisher) > 1;
                            """)
        result = mycursor.fetchall()
        df_17 = pd.DataFrame(result, columns=["Book Authors Count","Year","Publisher Count"])
        st.dataframe(df_17)

    elif original_list == "18. Average Retail Price of eBooks vs Physical Books":
        st.write("Average Retail Price of eBooks vs Physical Books")
        mycursor.execute("""SELECT ROUND(AVG(CASE WHEN isEbook = TRUE THEN amount_retailPrice END), 2) AS avg_ebook_price,
                            ROUND(AVG(CASE WHEN isEbook = FALSE THEN amount_retailPrice END), 2) AS avg_physical_price
                            FROM books;
                            """)
        result = mycursor.fetchall()
        df_18 = pd.DataFrame(result, columns=["Average Ebook Price","Average Physical Book Price"])
        st.dataframe(df_18)

    elif original_list == "19. Books with Rating > 2 Standard Deviations from Average":
        st.write("Books with Rating > 2 Standard Deviations from Average")
        mycursor.execute("""SELECT book_title, averageRating, ratingsCount
                            FROM books
                            WHERE averageRating IS NOT NULL
                            AND averageRating > (
                            SELECT AVG(averageRating) + 2 * STDDEV(averageRating)
                            FROM books
                            WHERE averageRating IS NOT NULL)
                            OR averageRating < (
                            SELECT AVG(averageRating) - 2 * STDDEV(averageRating)
                            FROM books
                            WHERE averageRating IS NOT NULL);
                            """)
        result = mycursor.fetchall()
        df_19 = pd.DataFrame(result, columns=["Book Title","Average Rating","Rating Count"])
        st.dataframe(df_19)

    elif original_list == "20. Publisher with Highest Average Rating (Only if >10 Books)":
        st.write("Publisher with Highest Average Rating (Only if >10 Books)")
        mycursor.execute("""SELECT publisher, AVG(averageRating) AS average_rating, COUNT(*) AS total_books
                            FROM books
                            WHERE averageRating IS NOT NULL
                            GROUP BY publisher
                            HAVING COUNT(*) > 10
                            ORDER BY average_rating DESC
                            LIMIT 1;
                            """)
        result = mycursor.fetchall()
        df_20 = pd.DataFrame(result, columns=["Publisher","Average Rating","Total Books"])
        st.dataframe(df_20)


