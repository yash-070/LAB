# Lab 5: Static Code Analysis — Hotel Booking System

**Your file:** `hotel_booking_system.py`

Follow the lab handout for the full instructions.

## About the program

A hotel room reservation and inventory manager. It tracks room types, handles guest bookings, releases room reservations, computes seasonal surge pricing, and exports hotel ledgers.

The code works, but only just. It has quality, style and security problems of the kind Pylint, Flake8 and Bandit are built to find.

## What to do

1. **Run it first** and read the output carefully:

   ```bash
   python hotel_booking_system.py
   ```

   It asks one question. Press Enter to use the default, then try a few inputs of your own. Not every problem in this file is something a tool will flag, so pay attention to output that looks wrong.

2. **Install the tools:**

   ```bash
   pip install pylint bandit flake8
   ```

3. **Run the analysis** and save the reports:

   ```bash
   pylint hotel_booking_system.py > pylint_report.txt
   bandit -r hotel_booking_system.py > bandit_report.txt
   flake8 hotel_booking_system.py > flake8_report.txt
   ```

4. **Document the issues** in `issues.md` using this table (at least 4 rows, high and medium severity first):

   | Issue | Type | Line(s) | Description | Fix Approach |
   | ----- | ---- | ------- | ----------- | ------------ |
   | ...   | ...  | ...     | ...         | ...          |

5. **Fix the code.** Fix at least 4 of the issues you documented, then rerun all three tools to confirm they are gone. Repeat until you are satisfied. The program should still do its job when you are done.

6. **Reflect.** Answer the four reflection questions from the handout in `reflection.md`.

## Deliverables

1. `hotel_booking_system.py`: your cleaned version, with at least 4 issues fixed.
2. `issues.md`: the completed issue table.
3. `reflection.md`: your answers to the reflection questions.

**Target:** aim for a Pylint score above 9.5 on your final file. A perfect 10.00/10 is very good.

Be ready to explain the bugs you found and how you fixed them. You may be called on to present.

## Completed review

### Changes in the cleaned code

The cleaned program keeps the booking and ledger behavior while addressing issues found in the original version. It replaces the mutable default booking log, renames `bookRoom` to `book_room`, narrows the cancellation exception to `KeyError`, removes unused variables, and replaces `eval` with a numeric seasonal multiplier. It also uses SHA-256 for guest IDs, `secrets` for booking references, a context manager with an explicit encoding for the ledger, and removes shell-based output. The secret is read from `HOTEL_SECRET_KEY` instead of being embedded in the source.

### Static analysis results

| Tool   | Before     | After     | Finding still shown in the saved report                                                                                              |
| ------ | ---------- | --------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| Pylint | 5.32/10    | 9.78/10   | Missing final newline at line 82                                                                                                     |
| Flake8 | 7 findings | 1 finding | Missing final newline at line 82                                                                                                     |
| Bandit | 6 findings | 1 finding | B105 flags the `NOT_SET` environment-variable fallback at line 78 as a possible hardcoded password (low severity, medium confidence) |

The remaining newline warning can be cleared by adding a newline at the end of `CODE/hotel_booking_system.py`. To avoid Bandit's placeholder-string warning, read `HOTEL_SECRET_KEY` without a string sentinel and check whether the result is `None`. The saved reports are in [REPORT](REPORT/).
