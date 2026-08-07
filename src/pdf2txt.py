import argparse
from datetime import datetime
from pypdf import PdfReader
from typing import List, Tuple
import fitz
import utils


def get_run_params() -> Tuple[str, str, str, str, str]:
    parser = argparse.ArgumentParser(
        prog="pdf2txt.py",
        description="Converts bank statement PDFs to TSV/CSV for import into home finance software",
        epilog=(
            f"Copyright (C) 2017, 2023, 2026 Jeremy Squires <jms@mailforce.net> "
            f"License: <https://opensource.org/licenses/MIT>"
        ),
    )
    parser.add_argument(
        "input",
        help="input is the path to a PDF bank eStatement",
    )
    parser.add_argument(
        "filetype",
        choices=["bmo_bank", "bmo_card", "rbc_bank", "rbc_card"],
        help=(
            f"is the type of input bank statement: "
            f"bmo is the Bank of Montreal, "
            f"rbc is the Royal Bank of Canada, "
            f"_bank is a bank current account statement, and "
            f"_card is a MasterCard statement"
        ),
    )
    parser.add_argument(
        "output",
        help=f"output is the path to the CSV/TSV output file",
    )
    parser.add_argument(
        "--capture",
        "-c",
        help=(f"path to a raw data capture output file," f" defaults to <output>.cap"),
        default=None,
    )
    parser.add_argument(
        "--format",
        "-f",
        choices=["pdf", "cap"],
        help=(f"format of input file, default pdf, cap for captures"),
        default="pdf",
    )
    args = parser.parse_args()
    print(args.input, args.filetype, args.output, args.capture or "", args.format or "")
    return args.input, args.filetype, args.output, args.capture or "", args.format or ""


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


def get_raw_text_lines_cap(filename: str) -> List[str]:
    with open(filename, mode="r", encoding="utf8") as file:
        text_lines = [line.rstrip("\r\n") for line in file.readlines()]
    return text_lines


def roll_up_bmo_bank_transactions(text_lines: List[str]) -> List[str]:
    roll_up_lines = ["Date\tDescription\tWithdrawal\tDeposit\tBalance"]
    roll_up = ""
    in_rollup = False
    field_number = 0
    initial_balance = 0.0
    current_balance = 0.0
    parts = []
    end_year = None
    end_month = None
    previous_month = None
    year = None
    date_line_prefix = "For the period ending "
    for text_line in text_lines:
        if date_line_prefix in text_line:
            entry_date_string = text_line.split(date_line_prefix)[1]
            entry_datetime = datetime.strptime(entry_date_string, "%B %d, %Y")
            end_year = entry_datetime.year
            end_month = entry_datetime.month
        text_line = text_line.replace("\t", " ")
        if utils.is_two_part_date(text_line):
            in_rollup = True
            field_number = 0
            dd_mon = utils.normalize_to_dd_mon(text_line)
            entry_datetime = datetime.strptime(dd_mon, "%d %b")
            if previous_month and previous_month > entry_datetime.month:
                year = year + 1
            elif not previous_month and end_month < entry_datetime.month:
                year = end_year - 1
            elif not previous_month and end_month >= entry_datetime.month:
                year = end_year
            previous_month = entry_datetime.month
            roll_up = f"{dd_mon} {year}"
        elif in_rollup:
            field_number += 1
            roll_up = f"{roll_up}\t{text_line}"
        if "Opening balance" in roll_up and field_number == 2:
            in_rollup = False
            parts = roll_up.split("\t")
            initial_balance = float(parts[2].replace(",", ""))
        elif "Closing totals" in roll_up and field_number == 2:
            in_rollup = False
        elif field_number == 3 and in_rollup:
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
    roll_up_lines = ["Date\tDescription\tWithdrawal\tDeposit\tBalance"]
    roll_up = ""
    in_rollup = False
    in_balance = False
    in_date = False
    field_number = 0
    initial_balance = 0.0
    current_balance = 0.0
    partial_balance = 0.0
    current_date = ""
    epsilon = 0.01
    parts = []
    days_entries = []
    year = None
    previous_month = None
    date_line_prefix = "Your opening balance on "
    for text_line in text_lines:
        if date_line_prefix in text_line:
            # rbc bank stmts move forward from the opening balance time
            entry_date_string = text_line.split(date_line_prefix)[1]
            entry_datetime = datetime.strptime(entry_date_string, "%B %d, %Y")
            year = entry_datetime.year
            previous_month = entry_datetime.month
        text_line = text_line.replace("\t", " ")
        if text_line == "Opening Balance":
            in_balance = True
            in_rollup = False
            in_date = False
        elif in_balance:
            initial_balance = float(text_line.replace(",", "").replace("$", ""))
            in_balance = False
            in_rollup = False
            in_date = False
        elif utils.is_dd_mon_date(text_line):
            in_rollup = True
            in_balance = False
            in_date = True
            field_number = 0
            roll_up = ""
            days_entries = []
            dd_mon = utils.normalize_to_dd_mon(text_line)
            entry_datetime = datetime.strptime(dd_mon, "%d %b")
            if previous_month > entry_datetime.month:
                year = year + 1
                previous_month = entry_datetime.month
            current_date = f"{dd_mon} {year}"
        elif in_rollup or in_date:
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
                    value = float(parts[2].replace(",", ""))
                    # no way to determine if it is a + or -
                    # use text to identify common deposits
                    if (
                        "Deposit" in parts[1]
                        or "rebate" in parts[1]
                        or "redemption" in parts[1]
                        or "received" in parts[1]
                    ):
                        partial_balance += value
                        parts.insert(2, "")
                    else:
                        # all others are assumed withdrawals
                        partial_balance -= value
                        parts.insert(3, "")
                    appendit = (
                        "\t".join(utils.trim_parts(parts))
                        + "\t"
                        + "{:,.2f}".format(initial_balance + partial_balance)
                    )
                    roll_up_lines.append(appendit)
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
                roll_up_lines.append("\t".join(utils.trim_parts(parts)))
                # transaction field reset
                initial_balance = current_balance
                partial_balance = 0.0
                field_number = 0
                roll_up = ""
                in_rollup = False
                parts = []
    return roll_up_lines


def roll_up_card_transactions(text_lines: List[str]) -> List[str]:
    roll_up_lines = ["Date\tDescription\tWithdrawal\tDeposit"]
    roll_up = ""
    in_rollup = False
    field_number = 0
    end_year = None
    end_month = None
    year = None
    previous_month = None
    date_range_string = None
    for text_line in text_lines:
        text_line = text_line.strip()
        if text_line.startswith("STATEMENT FROM"):
            # RBC MC
            date_range_string = text_line.split("STATEMENT FROM ")[1]
        elif len(dr_parts := text_line.split(" ")) == 7 and "-" == dr_parts[3]:
            # BMO MC
            date_range_string = text_line
        if date_range_string:
            _, end_date_string = utils.normalize_date_range(date_range_string)
            end_datetime = datetime.strptime(end_date_string, "%b %d, %Y")
            end_year = end_datetime.year
            end_month = end_datetime.month
            date_range_string = None
        text_line = text_line.replace("\t", " ")
        # 2026+ pdfs produce two date lines sometimes
        transaction_date = None
        posted_date = None
        two_date_list = text_line.split(" ")
        if (
            len(two_date_list) == 4 and
            utils.is_two_part_date(trans_date := " ".join(two_date_list[0:2])) and
            utils.is_two_part_date(post_date := " ".join(two_date_list[2:]))
        ):
            transaction_date = trans_date
            posted_date = post_date
        if not in_rollup and (
            utils.is_two_part_date(text_line) or
            (
                transaction_date and posted_date
            )
        ):
            in_rollup = True
            field_number = 0
            mon_dot_dd = transaction_date if transaction_date else text_line
            dd_mon = utils.normalize_to_dd_mon(mon_dot_dd)
            entry_datetime = datetime.strptime(dd_mon, "%d %b")
            if previous_month and previous_month > entry_datetime.month:
                year = year + 1
            elif not previous_month and end_month < entry_datetime.month:
                year = end_year - 1
            elif not previous_month and end_month >= entry_datetime.month:
                year = end_year
            previous_month = entry_datetime.month
            roll_up = f"{dd_mon} {year}"
            if posted_date:
                field_number = 1
        elif in_rollup:
            field_number += 1
            if field_number == 1:
                # posted date, not interesting, but check if description is appended
                f1_parts = text_line.split(" ")
                if len(f1_parts) > 2:
                    f1_description = " ".join(f1_parts[2:])
                    roll_up = f"{roll_up}\t{f1_description}"
                    # already added a tab, so increment field
                    field_number = 2
            elif utils.is_int(text_line):
                # reference number
                roll_up = f"{roll_up} {text_line}"
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


def process():
    input, filetype, output, capture, input_format = get_run_params()
    transaction_lines = []
    if input_format == "pdf":
        raw_text_lines = get_raw_text_lines_mupdf(input)
    else:
        raw_text_lines = get_raw_text_lines_cap(input)
    if capture:
        output_lines(raw_text_lines, capture)
    if filetype == "bmo_bank":
        # checking
        transaction_lines = roll_up_bmo_bank_transactions(raw_text_lines)
    elif filetype == "bmo_card":
        # master card
        transaction_lines = roll_up_card_transactions(raw_text_lines)
    elif filetype == "rbc_bank":
        # checking
        transaction_lines = roll_up_rbc_bank_transactions(raw_text_lines)
    elif filetype == "rbc_card":
        # master card
        transaction_lines = roll_up_card_transactions(raw_text_lines)

    output_lines(transaction_lines, output)


if __name__ == "__main__":
    process()
