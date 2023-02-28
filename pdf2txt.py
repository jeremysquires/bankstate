import argparse
from pypdf import PdfReader
from typing import List, Tuple
import fitz
import utils


def get_run_params() -> Tuple[str, str, str]:
    parser = argparse.ArgumentParser(
        prog="pdf2txt.py",
        description="Converts bank statement PDFs to TSV/CSV for import into home finance software",
        epilog= f"Copyright (C) 2017, 2023 Jeremy Squires <jms@mailforce.net> "
                f"License: <https://opensource.org/licenses/MIT>",
    )
    parser.add_argument(
        "filename", help="filename is the path to a PDF bank eStatement"
    )
    parser.add_argument(
        "filetype",
        choices=["bmo_bank", "bmo_mc", "rbc_bank", "rbc_mc"],
        default="bmo_bank",
        help=(
            f"is the type of input bank statement: "
            f"bmo is the Bank of Montreal, "
            f"rbc is the Royal Bank of Canada, "
            f"_bank is a bank current account statement, and "
            f"_mc is a MasterCard statement"
        ),
    )
    parser.add_argument("output", help=f"output is the path to the CSV/TSV output file")
    args = parser.parse_args()
    print(args.filename, args.filetype, args.output)
    return args.filename, args.filetype, args.output


def get_raw_text_lines_pypdf(filename: str) -> List[str]:
    """
    get_raw_text_lines_pypdf returns single lines per transaction
    raw_text_lines = get_raw_text_lines_pypdf(filename)
    transaction_lines = filter(utils.is_transaction_line, raw_text_lines)
    Numbers are preceded by slash, special chars are encoded
    /2c = , - /2e = . - etc.
    Nov /0/6 Opening balance /2/2c/0/0/0/2e/0/0
    Nov /0/8 Online Bill Payment/2c HEAT /2/0/0/2e/0/0 /2/2c/1/2e/8/0/0/2e/0/0
    """
    pdfObject = open(filename, "rb")
    pdfReader = PdfReader(pdfObject)
    text_lines = []
    for pageObject in pdfReader.pages:
        page = pageObject.extract_text()
        text_lines.extend(page.split("\n"))
    # TODO: clean up special characters, add spaces where necessary
    return text_lines


def get_raw_text_lines_mupdf(filename: str) -> List[str]:
    doc = fitz.open(filename)
    text_lines = []
    for pageObject in doc:
        page = pageObject.get_text()  # .encode("utf8")
        text_lines.extend(page.split("\n"))
    return text_lines


def roll_up_bmo_bank_transactions(text_lines: List[str]) -> List[str]:
    roll_up_lines = ["Date\tDescription\tDebit\tCredit\tBalance"]
    roll_up = ""
    in_rollup = False
    field_number = 0
    initial_balance = 0.0
    current_balance = 0.0
    parts = []
    for text_line in text_lines:
        # TODO: find year and append to date
        text_line = text_line.replace("\t", " ")
        if utils.is_mon_dd_date(text_line):
            in_rollup = True
            field_number = 0
            roll_up = text_line
        elif in_rollup:
            field_number += 1
            roll_up = f"{roll_up}\t{text_line}"
        if "balance" in roll_up and field_number == 2:
            in_rollup = False
            parts = roll_up.split("\t")
            initial_balance = float(parts[2].replace(",", ""))
        if field_number == 3:
            in_rollup = False
            parts = roll_up.split("\t")
            current_balance = float(parts[3].replace(",", ""))
            if current_balance > initial_balance:
                # add empty debit element
                parts.insert(2, "")
            elif current_balance < initial_balance:
                # add empty credit element
                parts.insert(3, "")
            roll_up = "\t".join(parts)
            roll_up_lines.append(roll_up)
            # transaction field reset
            initial_balance = current_balance
            field_number = 0
            roll_up = ""
            parts = []
    return roll_up_lines


def roll_up_rbc_bank_transactions(text_lines: List[str]) -> List[str]:
    roll_up_lines = ["Date\tDescription\tDebit\tCredit\tBalance"]
    roll_up = ""
    in_rollup = False
    in_balance = False
    field_number = 0
    initial_balance = 0.0
    current_balance = 0.0
    partial_balance = 0.0
    current_date = ""
    epsilon = 0.01
    parts = []
    days_entries = []
    for text_line in text_lines:
        # TODO: find year and append to date
        text_line = text_line.replace("\t", " ")
        if text_line == "Opening Balance":
            in_balance = True
            in_rollup = False
        elif in_balance:
            initial_balance = float(text_line.replace(",", "").replace("$", ""))
            in_balance = False
        elif utils.is_dd_mon_date(text_line):
            in_rollup = True
            in_balance = False
            field_number = 0
            roll_up = ""
            days_entries = []
            current_date = text_line
        elif in_rollup:
            field_number += 1
            if field_number == 1:
                roll_up = f"{current_date}\t{text_line}"
            elif field_number == 2:
                if not utils.is_currency(text_line):
                    field_number = 1
                    roll_up = f"{roll_up} {text_line}"
                else:
                    roll_up = f"{roll_up}\t{text_line}"
            elif field_number == 3:
                if not utils.is_currency(text_line):
                    # skipping balance
                    days_entries.append(roll_up)
                    field_number = 1
                    roll_up = f"{current_date}\t{text_line}"
                    continue
                partial_balance = 0.0
                for day_entry in days_entries:
                    parts = day_entry.split("\t")
                    # no way to determine if it is a + or -
                    # use text to identify common deposits
                    if (
                        "Deposit" in parts[1]
                        or "rebate" in parts[1]
                        or "redemption" in parts[1]
                    ):
                        partial_balance += float(parts[2].replace(",", ""))
                        parts.insert(2, "")
                    else:
                        # all others are assumed withdrawals
                        partial_balance -= float(parts[2].replace(",", ""))
                        parts.insert(3, "")
                    day_entry = "\t".join(parts)
                    roll_up_lines.append(day_entry)
                    # TODO: sanity check the final balance below, flag an error if mismatch
                    days_entries = []
                roll_up = f"{roll_up}\t{text_line}"
                in_rollup = False
                parts = roll_up.split("\t")
                current_balance = float(parts[3].replace(",", ""))
                if current_balance > (initial_balance + partial_balance):
                    # add empty debit element
                    partial_balance += float(parts[2].replace(",", ""))
                    parts.insert(2, "")
                elif current_balance < (initial_balance + partial_balance):
                    # add empty credit element
                    partial_balance -= float(parts[2].replace(",", ""))
                    parts.insert(3, "")
                final_balance = initial_balance + partial_balance
                if abs(current_balance - final_balance) > epsilon:
                    parts[1] += " ERR:BALANCE"
                roll_up = "\t".join(parts)
                roll_up_lines.append(roll_up)
                # transaction field reset
                initial_balance = current_balance
                partial_balance = 0.0
                field_number = 0
                roll_up = ""
                in_rollup = False
                parts = []
    return roll_up_lines


def roll_up_mc_transactions(text_lines: List[str]) -> List[str]:
    roll_up_lines = ["Date\tDescription\tDebit\tCredit"]
    roll_up = ""
    in_rollup = False
    field_number = 0
    for text_line in text_lines:
        # TODO: find year and append to date
        text_line = text_line.replace("\t", " ")
        if not in_rollup and (
            utils.is_mon_dot_dd_date(text_line) or utils.is_mon_dd_date(text_line)
        ):
            in_rollup = True
            field_number = 0
            roll_up = text_line.replace(".", "")
        elif in_rollup:
            field_number += 1
            if field_number == 1:
                pass
            elif utils.is_int(text_line):
                # reference number: roll_up = f"{roll_up}\t{text_line}"
                pass
            elif utils.is_currency(text_line):
                text_line = text_line.replace(",", "").replace("$", "")
                if text_line.startswith("-"):
                    text_line = text_line.replace("-", "")
                    roll_up = f"{roll_up}\t\t{text_line}"
                else:
                    roll_up = f"{roll_up}\t{text_line}\t"
                roll_up_lines.append(roll_up)
                field_number = 0
                roll_up = ""
                in_rollup = False
            elif text_line.endswith("CR"):
                roll_up = f"{roll_up}\t\t{text_line[0:-3]}"
                roll_up_lines.append(roll_up)
                field_number = 0
                roll_up = ""
                in_rollup = False
            else:
                if field_number == 2:
                    roll_up = f"{roll_up}\t{text_line}"
                else:
                    roll_up = f"{roll_up} {text_line}"
    return roll_up_lines


def output_lines(transaction_lines: List[str], output: str) -> None:
    with open(output, "w") as output_file:
        for line in transaction_lines:
            output_file.write(f"{line}\n")


# __main__: starts here
filename, filetype, output = get_run_params()
transaction_lines = []
if filetype == "bmo_bank":
    # checking
    raw_text_lines = get_raw_text_lines_mupdf(filename)
    transaction_lines = roll_up_bmo_bank_transactions(raw_text_lines)
elif filetype == "bmo_mc":
    # master card
    raw_text_lines = get_raw_text_lines_mupdf(filename)
    transaction_lines = roll_up_mc_transactions(raw_text_lines)
elif filetype == "rbc_bank":
    # checking
    raw_text_lines = get_raw_text_lines_mupdf(filename)
    transaction_lines = roll_up_rbc_bank_transactions(raw_text_lines)
elif filetype == "rbc_mc":
    # master card
    raw_text_lines = get_raw_text_lines_mupdf(filename)
    transaction_lines = roll_up_mc_transactions(raw_text_lines)

output_lines(transaction_lines, output)
