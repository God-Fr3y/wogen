"""A WORDLIST GENERATOR TOOL DEDICATED FOR A SINGLE TARGET
# GATHER AVAILABLE DATA FROM THE TARGET
# THEN COMBINE ALL COLLECTED DATA
#
# EG.
#       DATA:
#           name, middlename, lastname,  age
#
# THEN COMBINE:
#       namemiddlename
#       namelastname
#       nameage
#       middlenamename
#       middlenamelastname
#       middlenameage
#       lastnamename
#       lastnamemiddlename
#       lastnameage
#       agename
#       agemiddlename
#       agelastname
#
# PUT ALL THE COMBINED DATA INTO A WORDLIST.TXT FILE
# GENERATING A WORDLIST MAY TAKE TIME
# DEPENDING ON THE DATA COLLECTED
# THE MORE DATA THE LONGER IT TAKES
#
#
#
#
#
# - GODFR3YP4DU4"""


# Make sure that the required module are in the system
# before running the whole program
# try importing the module if not found, install it
import time
import os
import sys
import threading
import re
import datetime
import itertools
import shutil
import phonenumbers
from phonenumbers.phonenumberutil import NumberParseException
from phonenumbers import format_number as frmt_no
from phonenumbers import PhoneNumberFormat as CpNoFrmt


# get width and height of terminal for future references
width, height = shutil.get_terminal_size()


COLOR_GREEN = "\033[1;32;40m"  # green font
COLOR_RED = "\033[1;31;40m"  # red font
COLOR_RESET = "\033[0;37;40m"  # reset font coloring


def timer(func):
    """TIMER DECORATOR"""
    def wrapper(*args, **kwargs):
        # start timer
        timer_start = time.time()

        # run main function
        return_value = func(*args, **kwargs)

        # end timer
        timer_end = time.time()

        # timer result
        timer = round(timer_end - timer_start)
        timer = datetime.timedelta(seconds=timer)

        print(f"\nProgram finish in {timer} seconds!")

        return return_value
    return wrapper


class Validator:
    """Class of function to validate user input
    in order to avoid any error while running the program
    and enhance the result of this tool"""

    def invalid(self):
        """Print Invalid Message"""

        print(COLOR_RED + "Invalid input. Please try again." + COLOR_RESET)

    def name(self, data):
        """Get user input and
        Filter it for a better result
        Check name if two words and validate it
        Check name if in alphabet
        If not, repeat the question"""

        if "username" in data:
            name = input(f"\n-》{data.capitalize()}: ")
        else:
            while True:
                name = input(f"\n-》{data.capitalize()}: ")
                if name:
                    name = name.replace(" ", "")
                    if not name.isalpha():
                        self.invalid()
                        continue
                    break
                if not name:
                    break
        return name

    def age(self, data):
        """Get user input and
        Filter it for a better result
        Check if age is valid
        If not, repeat the question"""

        while True:
            age = input(f"\n-》{data.capitalize()}: ")
            if not age:
                break

            try:
                age = int(age)
                if age < 0 or age > 99:
                    self.invalid()
                    continue
            except ValueError:
                self.invalid()
                continue
            break
        return age

    def dob(self, data):
        """Get the user input and
        Filter it for a better result
        Check if DOB is valid
        If not, repeat the question"""

        while True:
            dob = input(f"\n-》{data.capitalize()} (MM/DD/YYYY): ")
            if not dob:
                break

            pattern = r"(0[1-9]|1[012])/(0[1-9]|[12]\d|3[01])/(19|20)\d\d"
            fullmatch = re.fullmatch(pattern, dob)
            if not fullmatch:
                self.invalid()
                continue
            if fullmatch:
                break
        return dob

    def email(self, data):
        """Get the user input and
        Filter it for a better result
        Check if email is valid
        If not, repeat the question"""

        while True:
            email = input(f"\n-》{data.capitalize()}: ")
            if not email:
                break

            pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"

            fullmatch = re.match(pattern, email)
            if not fullmatch:
                self.invalid()
            elif fullmatch:
                break

        return email

    def phone(self, data):
        """Get the user input and
        Filter it for a better result
        Check if DOB is valid
        If not, repeat the question"""

        while True:
            cp_no = input(f"\n-》{data.capitalize()} (+639123456789): ")
            if not cp_no:
                break

            try:
                cp_no = phonenumbers.parse(f"{cp_no}")
                if phonenumbers.is_valid_number(cp_no):
                    cp_no = frmt_no(cp_no, CpNoFrmt.NATIONAL).replace(" ", "")
                    break

            except NumberParseException:
                print(COLOR_RED + "Invalid number. Please try again.")
                print(COLOR_RESET)
                continue

        return cp_no

    def symbols(self, data):
        """Get the user input and
        Filter it for a better result
        Check if symbol is valid
        If not, repeat the question"""

        print("\n")
        msg = "Put some symbols to strengthen your wordlist"
        syms = "@#$_&-+()/"
        print(msg.center(width))
        print(syms.center(width))

        while True:
            symbols = input(f"\n-》{data.capitalize()}: ")
            if not symbols:
                break

            if not re.match(r"\W", symbols):
                self.invalid()
                continue
            break

        symbol_list = []
        for symbol in iter(symbols):
            symbol_list.append(symbol)

        return symbol_list

    def additional_words(self, data):
        """Get the user input and
        Filter it for a better result"""

        print("\n")
        msgs = [
            "Add some words that can be a possible password",
            "Like favorite food, place, pet name, etc",
            "Press enter to skip",
        ]

        for msg in msgs:
            print(msg.center(width))

        print("\n")

        words = []

        while True:
            word = input(f"\n-》{data.capitalize()}: ")
            if word:
                word = word.replace(" ", "")
                words.append(word)
            else:
                break

        return words


class WoGen(Validator):
    """The main group of function to generate a wordlist"""

    def __init__(self):
        self.run_loading = None

    def banner(self):
        """Show the banner
        clear the terminal before showing the WOGEN banner"""

        if os.name == "nt":  # if windows system
            os.system("cls")  # clear terminal
        else:  # For Unix/Linux/MacOS
            os.system("clear")

        banner = [
            "......................................................",
            "'##:::::'##::'#######:::'######:::'########:'##::: ##:",
            " ##:'##: ##:'##.... ##:'##... ##:: ##.....:: ###:: ##:",
            " ##: ##: ##: ##:::: ##: ##:::..::: ##::::::: ####: ##:",
            " ##: ##: ##: ##:::: ##: ##::'####: ######::: ## ## ##:",
            " ##: ##: ##: ##:::: ##: ##::: ##:: ##...:::: ##. ####:",
            " ##: ##: ##: ##:::: ##: ##::: ##:: ##::::::: ##:. ###:",
            ". ###. ###::. #######::. ######::: ########: ##::. ##:",
            ":...::...::::.......::::......::::........::..::::..::",
            "'''''''''''''’''''''''''''''''''''''''''''''''''''''''",
        ]

        for design in banner:
            print(COLOR_GREEN + design.center(width) + COLOR_RESET)

        print(COLOR_RED + "- GODFR3Y".center(width + 30) + COLOR_RESET)
        print("\n\n\n\n")

    def get_data(self):
        """Collect data from user and
        Validate it using Validator module"""

        print("\n\n\n\nPut everything you know then press enter")
        print("Press enter to skip\n")

        target_info = []
        # get the target personal info
        target_names = ["firstname", "middlename", "lastname", "nickname", "username"]
        for name in target_names:
            target_info.append(self.name(name))

        dob = self.dob("dob").replace("/", "")
        target_info.append(dob)
        target_info.append(dob[:2])
        target_info.append(dob[2:4])
        target_info.append(dob[4:])
        target_info.append(self.age("age"))
        target_info.append(self.phone("phonenumber"))
        target_info.append(self.email("email"))

        print("\n")
        msgs = [
            "Some additional information base on the",
            "target life partner can be useful",
            "to enhance your wordlist",
        ]
        for msg in msgs:
            print(msg.center(width))

        # get the target partner info
        target_partner_names = [
            "partner's firstname",
            "partner's middlename",
            "partner's lastname",
            "partner's nickname",
            "partner's username",
        ]
        for names in target_partner_names:
            target_info.append(self.name(names))

        target_info.append(self.age("partner' age"))
        partner_dob = self.dob("dob").replace("/", "")
        target_info.append(partner_dob)
        target_info.append(partner_dob[:2])
        target_info.append(partner_dob[2:4])
        target_info.append(partner_dob[4:])
        target_info.append(self.phone("partner's phonenumber"))
        target_info.append(self.email("partner's email"))
        date_engaged = self.dob("date engaged").replace("/", "")
        target_info.append(date_engaged)
        target_info.append(date_engaged[:2])
        target_info.append(date_engaged[2:4])
        target_info.append(date_engaged[4:])

        # additional words can also be useful
        target_info.extend(self.additional_words("words"))

        # additional symbols can also be useful
        target_info.extend(self.symbols("symbols"))

        # filter target_info list to remove None value item
        # and store it to a new tuple then return
        target_info = tuple(str(item) for item in target_info if item)

        return target_info

    def min_pass_len(self):
        """Get a minimum password length
        Validate the user input to avoid any error"""

        while True:
            try:
                min_char = int(input("\nMinimum password length: "))
                if min_char <= 0:
                    self.invalid()
                    continue
                break
            except ValueError:
                self.invalid()

        return min_char

    def max_pass_len(self, min_char):
        """Get a maximum password length
        Validate the user input and check if not less from
        minimum password length to avoid any error"""

        while True:
            try:
                max_char = int(input("\nMaximum password length: "))
                if max_char <= 0 or max_char <= min_char:
                    self.invalid()
                    continue
                break
            except ValueError:
                self.invalid()

        return max_char

    def word_to_combine(self):
        """get the maximum number of data to combined
        validate it for a better result"""

        msgs = [
            "\n",
            "\b",
            "Data:  a b c d",
            "\n",
            "2       3       4",
            "ab      abc     abcd",
            "ac      abd     abdc",
            "ad      acb     acbd",
            "ba      acd     acdb",
        ]

        for msg in msgs:
            print(msg.center(width))
        print("\n\n" + "WARNING! The higher the number,")
        print("the longer it takes to create.".center(width))

        while True:
            try:
                num = int(input("\nUp to how many data to combine: "))
            except ValueError:
                self.invalid()
                continue
            break
        return num

    def gen_pass(self, min_char, max_char, data, word_to_combine):
        ''' GENERATOR FOR MILLIONS OF PASS '''

        for num in range(1, word_to_combine + 1):
            for datas in itertools.permutations(data, num + 1):
                # join data in lowercase
                passw = "".join(datas)

                if len(passw) <= max_char and len(passw) >= min_char:
                    # join data in capitalize
                    cap_passw = "".join(datas).capitalize()

                    # join data in title
                    title_passw = "".join(dat.title() for dat in datas)

                    if passw not in (cap_passw, title_passw):
                        yield passw
                        yield cap_passw
                        yield title_passw

    def create(self, min_char, max_char, data, word_to_combine):
        """Open a new Wordlist.txt file
        Then put all created possible password
        Using permutation from the data gathered"""

        data = sorted(data, key=len)
        with open("Wordlist.txt", "w+", encoding="utf-8") as wordlist:
            for passw in self.gen_pass(min_char, max_char, data, word_to_combine):
                wordlist.write(passw + "\n")

    def count_line(self):
        """Open the Wordlist.txt and read
        to determined how many passwords are created"""

        with open("Wordlist.txt", "r", encoding="utf-8") as wordlist:
            count = sum(1 for line in wordlist)
            print(
                f"""\n\n
{COLOR_GREEN} {count:,} password has been successfuly saved to
{COLOR_RESET}\'Wordlist.txt\' {COLOR_GREEN} in the same directory
{COLOR_RESET}

{COLOR_RED}The developer of this code is not responsible for any
misuse of this tools.

You have been warn! {COLOR_RESET}""")

    def loading(self):
        """Display loading icon while generating"""

        for icon in itertools.cycle(["|", "/", "-", "\\", "-"]):
            if not self.run_loading:
                break
            sys.stdout.write("\rGenerating ... " + icon)
            sys.stdout.flush()
            time.sleep(0.1)

    @timer
    def main(self):
        """Get the target info from the user by calling data() func
        Ask the user for minimum and maximum password length
        While creating show some motivational message
        If done, show how many password has been create"""

        # get data from user
        data = self.get_data()

        # get the minimum password length of chatacter
        min_char = self.min_pass_len()

        # get the maximum password length of character
        max_char = self.max_pass_len(min_char)

        # get the max number of data to combine
        word_to_combine = self.word_to_combine()

        # ask the user to generate or not
        # if y generate elif n quit else ask again
        while True:
            generate = input("\n\nGenerate a wordlist? [Y|N]: ").upper()
            if generate == "Y":
                self.run_loading = True
                loading = threading.Thread(target=self.loading)
                loading.start()

                self.create(min_char, max_char, data, word_to_combine)

                self.run_loading = False
                break

            if generate == "N":
                sys.exit()
            else:
                self.invalid()

        # count create password
        self.count_line()


if '__main__' == __name__:
    WoGen().banner()
    WoGen().main()
