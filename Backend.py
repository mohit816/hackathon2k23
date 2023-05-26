import csv
import mysql.connector
import os
import logging
from flask import request, jsonify


class Backend:
    def __init__(self):
        self.setup_database()
        self.logger = logging.getLogger(__name__)

    def setup_database(self):
        self.cnx = mysql.connector.connect(
            host='localhost',
            user='root',
            password='mohit',
            database='hackathon'
        )
        self.cursor = self.cnx.cursor()
        self.create_table()

    def authenticate(self, username, password):
        # Implement your authentication logic here
        # Example authentication logic:
        if username == 'studio' and password == 'password':
            return 'studio'
        elif username == 'concept' and password == 'password':
            return 'concept'
        else:
            return None

    def create_table(self):
        create_table_query = """
            CREATE TABLE IF NOT EXISTS csv_data (
                id INT AUTO_INCREMENT PRIMARY KEY,
                concept VARCHAR(255),
                product_origin VARCHAR(255),
                inward_base_product_id VARCHAR(255),
                inward_date DATE,
                ean_code VARCHAR(255),
                status VARCHAR(255),
                comments VARCHAR(255),
                photographer VARCHAR(255),
                shoot_date DATE,
                stylist VARCHAR(255),
                reasons VARCHAR(255)
            )
        """
        try:
            self.cursor.execute(create_table_query)
        except mysql.connector.errors.ProgrammingError as e:
            self.logger.error(e)

    def process_uploaded_csv(self, concept, product_origin, filename):
        filepath = os.path.join('uploads', filename)
        data = []
        with open(filepath, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                row['concept'] = concept
                row['product_origin'] = product_origin
                data.append(dict(row))

        self.logger.info("Extracted Data:")
        for row in data:
            self.logger.info(row)

        cnx = mysql.connector.connect(
            host='localhost',
            user='root',
            password='mohit',
            database='hackathon'
        )
        cursor = cnx.cursor()

        insert_query = """
            INSERT INTO csv_data
            (concept, product_origin, inward_base_product_id, inward_date, ean_code, status, comments, photographer, shoot_date, stylist, reasons)
            VALUES
            (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        try:
            for row in data:
                values = (
                    row['concept'],
                    row['product_origin'],
                    row['Inward Base Product ID'],
                    row['Inward Date'],
                    row['Ean Code'],
                    row['Status'],
                    row['Comments'],
                    row['Photographer'],
                    row['Shoot Date'],
                    row['Stylist'],
                    row['Reasons']
                )
                self.logger.info("Inserting values:")
                self.logger.info(values)
                cursor.execute(insert_query, values)
            cnx.commit()
            cursor.close()
            cnx.close()
        except mysql.connector.errors.IntegrityError as e:
            self.logger.error("Error while inserting data into the database: %s", e)
    
    def get_csv_data(self):
        select_query = """
            SELECT * FROM csv_data
        """
        try:
            self.cursor.execute(select_query)
            data = self.cursor.fetchall()
        except mysql.connector.errors.ProgrammingError as e:
            self.logger.error(e)
        return data
