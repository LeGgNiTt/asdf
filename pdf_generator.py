from fpdf import FPDF
import os

class PDFGenerator(FPDF):
    def header(self):
        # Set header font and title
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, self.title, 0, 1, 'C')
        self.ln(10)

    def footer(self):
        # Add a footer with page number
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, 'Seite ' + str(self.page_no()), 0, 0, 'C')

    def chapter_title(self, label):
        # Optional: Add a chapter title
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, label, 0, 1)
        self.ln(4)

    def generate_pdf(self, filename, title, data, headers, total):
        self.title = title
        self.add_page()
        self.set_fill_color(200, 220, 255)
        
        # Define column widths
        # Assuming the last 3 columns should be narrower
        col_widths = [self.w / len(headers)] * len(headers)  # Default width for each column
        narrower_col_width = col_widths[0] * 0.75  # Last three columns are 75% of default width
        for i in range(-3, 0):  # Adjust the width of the last three columns
            col_widths[i] = narrower_col_width
        
        # Header
        self.set_font('Arial', 'B', 10)
        for i, header in enumerate(headers):
            self.cell(col_widths[i], 10, header, 1, 0, 'C', 1)
        self.ln()

        # Data rows
        self.set_font('Arial', '', 10)
        for row in data:
            for i, header in enumerate(headers):
                self.cell(col_widths[i], 10, str(row[header]), 1)
            self.ln()
        
        self.set_font('Arial', 'B', 12)
        self.ln(10)  # Ensure there's a bit of space before printing the total
        total_formatted = f"{total:.2f}.-"
        self.cell(0, 10, f'Total: {total_formatted}', 0, 1, 'R')
        
        # Save PDF to file
        self.output(filename)

    def generate_landscape_pdf(self, filename, title, data, headers, subtotal, total):
        self.title = title
        self.add_page(orientation='L')
        self.set_fill_color(200, 220, 255)
        
        # Define column widths
        # Assuming the last 3 columns should be narrower
        col_widths = [self.w / len(headers)] * len(headers)  # Default width for each column
        narrower_col_width = col_widths[0] * 0.5  # Last three columns are 75% of default width
        for i in range(-3, 0):  # Adjust the width of the last three columns
            col_widths[i] = narrower_col_width
        #Adjust the width of the firs colum
        col_widths[2] = col_widths[2] * 2

        # Header
        self.set_font('Arial', 'B', 10)
        for i, header in enumerate(headers):
            self.cell(col_widths[i], 10, header, 1, 0, 'C', 1)
        self.ln()

        # Data rows
        self.set_font('Arial', '', 10)
        for row in data:
            for i, header in enumerate(headers):
                self.cell(col_widths[i], 10, str(row[header]), 1)
            self.ln()
        
        self.set_font('Arial', 'B', 12)
        self.ln(10)  # Ensure there's a bit of space before printing the total
        subtotal_formatted = f"{subtotal:.2f}.-"
        self.cell(0, 10, f'Umsatz: {subtotal_formatted}', 0, 1, 'R')
        self.ln(10)  # Ensure there's a bit of space before printing the total
        total_formatted = f"{total:.2f}.-"
        self.cell(0, 10, f'Total: {total_formatted}', 0, 1, 'R')
        
        # Save PDF to file
        self.output(filename)