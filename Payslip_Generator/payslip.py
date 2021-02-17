import os
import csv
from datetime import date

# Payslip Generator

# This is a version of a payslip generator that reads in a timesheet
# from a CSV file and using a latex template builds payslips for each
# employee. The amount that an employee is payed as well as the amount
# of tax that they owe is calculated and written to a temporary latex
# file. The file is then built using latexmk and the resulting pdf is
# renamed and moved to a folder to store all the employee's payslips.


def gross_pay_calculation(employee):
    """
    Function to calculate the gross pay of the employee based on hours
    worked. The final value is the sum of:
        - the number of hours worked during the week
        - the number of holiday hours owed
        - 1.5 times the number of overtime hours

    The number of hours payable is then multiplied by the employee's
    hourly wage to get the final value the employee is payed

    Parameters
        ----------
        employee : dict
            A dictionary with the following keys:
                monday - sunday: float
                    Number hours worked each day of the week.
                overtime: float
                    Number of overtime hours.
                holiday: float
                    Number of holiday hours.
                hourly: float
                    Rate of pay for the employee.

    Returns
        gross_pay : float
            The total amount that the employee is payed
    """

    # Calcualte the number of hours worked during the week
    total_weekday, total_weekend = total_hours(employee)
    total_payable = total_weekday + total_weekend

    # Add the number of hours holiday and overtime
    total_payable = total_payable + (float(employee["overtime"]) * 0.5)
    total_payable = total_payable + float(employee["holiday"])

    # Calcualte the gross pay for the employee using their hourly rate
    gross_pay = total_payable * float(employee["hourly"])

    return gross_pay


def str_replace(text, keyword, string):
    """
    Function to replace a keyword in a string with a replacement string.
    If the replacement is a float then the float is rounded to two
    decimal places.

    Parameters
        ----------
        text : str
            The string with the words that need to be replaced
        keyword : str
            The keyword to be replaced in text
        string : str/int/float
            The replacement string/int/float to be used

    Returns
        text : str
            A string with the words replaced.
    """

    # If the string is a float then it is rounded to two decimal places
    if isinstance(string, float):
        string = "%.2f" % round(string, 2)

    # Return the string with the replacement
    return text.replace(keyword, str(string))


def total_hours(employee):
    """
    Function to calculate the total number of hours by an employee
    during the week. The function returns the sum of the number of hours
    worked each day.

    Parameters
        ----------
        employee : dict
            A dictionary with the following keys:
                monday : float
                    Number of hours worked on Monday.
                tuesday : float
                    Number of hours worked on Tuesday.
                wednesday : float
                    Number of hours worked on Wednesday.
                thursday : float
                    Number of hours worked on Thursday.
                friday : float
                    Number of hours worked on Friday.
                saturday : float
                    Number of hours worked on Saturday.
                sunday : float
                    Number of hours worked on Sunday.

    Returns
        total_weekday: float
            The number of hours that employee worked during the week.

        total_weekend: float
            The number of hours that employee worked during the weekend.
    """

    weekday = ["monday", "tuesday", "wednesday", "thursday", "friday"]
    weekend = ["saturday", "sunday"]

    total_weekday = 0
    total_weekend = 0

    # For each day of the week sum up the number of hours worked
    for day in weekday:
        total_weekday = total_weekday + float(employee[day])

    # For each day of the weekend sum up the number of hours worked
    for end in weekend:
        total_weekend = total_weekend + float(employee[end])

    return total_weekday, total_weekend


def main():

    # Open the weekly timesheet and create a list of dicts for each employee
    with open("timesheet.csv", "r") as csvfile:
        timesheet = list(csv.DictReader(csvfile, delimiter=","))

    # Open the latex payslip template and create a string of the paylip
    with open("payslip_template.tex", "r") as texfile:
        payslip = texfile.read()

    # Calculate the date and week number
    today = date.today().strftime("%Y-%m-%d")
    weeknum = date.today().strftime("%V")

    # For each employee, calculate all the relevant information, replace
    # the keyword in the latex template and save the results to a
    # temporary latex file. Then the temporary latex file is built and
    # the resulting pdf is renamed and moved to a directory with all the
    # employees's paylips
    for employee in timesheet:

        # Re-initialize the latex template string and a empty dictionary
        # to store the payslip information
        payslip_employee = payslip
        payslip_info = {}

        # Calculate hours worked
        hours_weekday, hours_weekend = total_hours(employee)
        payslip_info["+hours-worked+"] = hours_weekday + hours_weekend

        # Calculate gross pay
        payslip_info["+gross-pay+"] = gross_pay_calculation(employee)

        # Flat example tax rate for everyone
        payslip_info["+PAYE+"] = payslip_info["+gross-pay+"] * 0.23
        payslip_info["+USC+"] = payslip_info["+gross-pay+"] * 0.02

        # Gross tax
        payslip_info["+gross-tax+"] = payslip_info["+PAYE+"] + payslip_info["+USC+"]

        # Net pay
        payslip_info["+net-pay+"] = (
            payslip_info["+gross-pay+"] - payslip_info["+PAYE+"] - payslip_info["+USC+"]
        )

        # Hours worked pay
        payslip_info["+hours-worked-pay+"] = payslip_info["+hours-worked+"] * float(
            employee["hourly"]
        )

        # Overtime hours and pay
        payslip_info["+overtime+"] = float(employee["overtime"])
        payslip_info["+overtime-pay+"] = (
            payslip_info["+overtime+"] * float(employee["hourly"]) * 1.5
        )

        # Holiday hours and pay
        payslip_info["+holiday+"] = float(employee["holiday"])
        payslip_info["+holiday-pay+"] = payslip_info["+holiday+"] * float(
            employee["hourly"]
        )

        # Replacing employee info from employee dictionary
        payslip_employee = str_replace(payslip_employee, "+name+", employee["name"])
        payslip_employee = str_replace(payslip_employee, "+PPSN+", employee["pps"])
        payslip_employee = str_replace(payslip_employee, "+number+", employee["number"])
        payslip_employee = str_replace(payslip_employee, "+week-number+", weeknum)
        payslip_employee = str_replace(payslip_employee, "+date+", today)

        # Replacing generated payslip info
        for key in payslip_info.keys():
            payslip_employee = str_replace(payslip_employee, key, payslip_info[key])


        # Open a temporary latex file and write the paylip string to it
        with open("payslip_temp.tex", "w+") as myfile:
            myfile.write(payslip_employee)

        # Run the build latex command for each employee in a temporary latex file
        os.system(
            "latexmk -cd -f -lualatex -interaction=nonstopmode -synctex=1 payslip_temp.tex"
        )

        # Move the built latex pdf to a new directory and name the
        # payslip using the employees number and name
        os.system(
            "mv payslip_temp.pdf payslip_pdfs/%s_%s.pdf"
            % (employee["number"], employee["name"].replace(" ", "_"))
        )


if __name__ == "__main__":
    main()
